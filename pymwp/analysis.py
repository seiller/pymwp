# -----------------------------------------------------------------------------
# Copyright (c) 2020-2024 C. Aubert, T. Rubiano, N. Rusch and T. Seiller.
#
# This file is part of pymwp.
#
# pymwp is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# pymwp is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# pymwp. If not, see <https://www.gnu.org/licenses/>.
# -----------------------------------------------------------------------------

import logging
from typing import List, Tuple, Union

from . import Coverage, Variables, FindLoops, COM_RES
from . import DeltaGraph, Polynomial, RelationList, Result, Bound
# noinspection PyPep8Naming
from .parser import Parser as pr
from .result import FuncResult, LoopResult
from .semiring import POLY_MWP

logger = logging.getLogger(__name__)


class Analysis:
    """MWP analysis implementation."""

    CHOICE_DOMAIN = [0, 1, 2]

    @staticmethod
    def run(ast: pr.Node, res: Result = None, fin: bool = False,
            strict: bool = False, **kwargs) -> Result:
        """Run MWP analysis on AST.

        Arguments:
            ast (pr.Node): Parsed C source code AST Node.
            res (Result): Pre-initialized result object.
            fin (bool): Always run to completion.
            strict (bool): Require supported syntax.

        Returns:
            Analysis Result object.
        """
        result: Result = res or Result()
        logger.debug("started analysis")
        result.on_start()
        for f_node in [f for f in ast if pr.is_func(f)]:
            if Analysis.syntax_check(f_node, strict):
                func_res = Analysis.func(f_node, not fin)
                func_res.func_code = pr.to_c(f_node, True)
                result.add_relation(func_res)
        result.on_end().log_result()
        return result

    @staticmethod
    def func(node: pr.FuncDef, stop: bool) -> FuncResult:
        """Analyze a function.

        Arguments:
            node: parsed C source code function node
            stop: terminate if no bound exists

        Returns:
              Analysis result for provided function.
        """
        assert pr.is_func(node)
        name = node.decl.name
        logger.info(f"Analyzing {name}")
        result = FuncResult(name).on_start()

        # setup for function analysis
        variables, body = Variables(node).vars, node.body.block_items
        relations = RelationList.identity(variables=variables)
        total, num_v = len(body), len(variables)
        show_vars = ', '.join(variables) if num_v <= 5 else num_v
        logger.debug(f"{name} variables: {show_vars}")
        logger.debug(f"{total} top-level commands to analyze")

        # analyze body commands
        delta_infty, index = Analysis.cmds(relations, 0, body, stop)

        # evaluate choices + calculate a bound
        evaluated, choices, bound = False, None, None
        if not delta_infty:
            choices = relations.first.eval(Analysis.CHOICE_DOMAIN, index)
            if not choices.infinite:
                bound = Bound().calculate(
                    relations.first.apply_choice(*choices.first))
            evaluated = True
        # infinite by delta graph or by choice
        infinite = delta_infty or (evaluated and choices.infinite)

        # record results
        result.index = index
        result.infinite = infinite
        result.vars = relations.first.variables
        if not (infinite and stop):
            result.relation = relations.first
        if infinite and not stop:
            var_choices = relations.first.var_eval(
                Analysis.CHOICE_DOMAIN, index)
            result.inf_flows = relations.first.infty_pairs(
                [v for v, c in var_choices.items() if c.infinite])
        if not infinite:
            result.bound = bound
            result.choices = choices
        result.on_end()
        return result

    @staticmethod
    def cmds(relations: RelationList, index: int, nodes: list[pr.Node],
             stop: bool = True) -> Tuple[bool, int]:
        """Analyze some list of commands, typically body block statements.

        Arguments:
            relations (RelationList): Initialized relation list.
            index (int): Derivation index.
            nodes (list[pr.Node]): List of AST nodes to analyze.
            stop (bool): Set True to terminate early.

        Returns:
            True if nodes lead to infinity by delta graph.
        """
        delta_infty, total, dg = False, len(nodes), DeltaGraph()
        for i, node in enumerate(nodes):
            logger.debug(f'computing relation...{i} of {total}')
            index, rel_list, delta_infty_ = Analysis \
                .compute_relation(index, node, dg)
            delta_infty = delta_infty or delta_infty_  # cannot erase
            if stop and delta_infty:
                logger.debug('delta_graphs: infinite -> Exit now')
                break
            logger.debug(f'computing composition...{i} of {total}')
            relations.composition(rel_list)
        return delta_infty, index

    @staticmethod
    def syntax_check(node: pr.Node, strict: bool) -> bool:
        """Analyze function syntax and conditionally modify.

        Arguments:
            node (pr.Node): An AST node.
            strict (bool): When true, AST will not be modified.

        Returns:
            True if analysis can be performed and False otherwise.
        """
        name = node.decl.name if pr.is_func(node) else 'node'
        cover = Coverage(node).report()
        if not cover.full and strict:
            logger.info(f"{name} is not analyzable")
            return False
        if not cover.full:
            cover.ast_mod()  # removes unsupported commands
            logger.warning(f"{name} syntax was modified")
        return True

    @staticmethod
    def compute_relation(index: int, node: pr.Node, dg: DeltaGraph) -> COM_RES:
        """Create a relation list corresponding for all possible matrices
        of an AST node.

        Arguments:
            index (int): Delta index.
            node (pr.Node): AST node to analyze.
            dg (DeltaGraph): DeltaGraph instance.

        Returns:
            Updated index value, relation list, and an exit flag.
        """

        logger.debug("in compute_relation")
        if isinstance(node, pr.Decl):
            return index, RelationList(), False
        if isinstance(node, pr.Assignment) and \
                isinstance(node.lvalue, pr.ID):
            if isinstance(node.rvalue, pr.BinaryOp):
                return Analysis.binary_op(index, node)
            if isinstance(node.rvalue, pr.Constant):
                return Analysis.constant(index, node.lvalue.name)
            if isinstance(node.rvalue, pr.UnaryOp):
                return Analysis.unary_asgn(index, node)
            if isinstance(node.rvalue, pr.ID):
                return Analysis.id(index, node)
        if isinstance(node, pr.UnaryOp):
            return Analysis.unary_op(index, node, dg)
        if isinstance(node, pr.If):
            return Analysis.if_stmt(index, node, dg)
        if isinstance(node, pr.While):
            return Analysis.while_loop(index, node, dg)
        if isinstance(node, pr.DoWhile):
            return Analysis.while_loop(index, node, dg)
        if isinstance(node, pr.For):
            return Analysis.for_loop(index, node, dg)
        if isinstance(node, pr.Compound):
            return Analysis.compound(index, node, dg)
        if isinstance(node, pr.Break):  # => skip
            return index, RelationList(), False
        if isinstance(node, pr.Continue):  # => skip
            return index, RelationList(), False
        if isinstance(node, pr.Return):  # => skip
            return index, RelationList(), False
        if (isinstance(node, pr.FuncCall)
                and isinstance(node.name, pr.ID)
                and node.name.name == 'assert'):
            return index, RelationList(), False
        if isinstance(node, pr.EmptyStatement):
            return index, RelationList(), False

        Analysis._unsupported(pr.to_c(node))
        return index, RelationList(), False

    @staticmethod
    def id(index: int, node: pr.Assignment) -> COM_RES:
        """Analyze x = y, where data flows between two variables.

        Arguments:
            index: delta index
            node: AST node representing a simple assignment

        Returns:
            Updated index value, relation list, and an exit flag.
        """

        # ensure we have distinct variables on both sides of x = y
        if not isinstance(node.lvalue, pr.ID) \
                or isinstance(node.rvalue, pr.Constant) \
                or node.lvalue.name == node.rvalue.name:
            return index, RelationList(), False

        x, y = node.lvalue.name, node.rvalue.name
        vars_list = [[x], [y]]
        logger.debug(f'Computing relation {x} = {y}')

        # create a vector of polynomials based on operator type
        #     x   y
        # x | o   o
        # y | m   m
        vector = [  # because x != y
            Polynomial('o'), Polynomial('m')]

        # build a list of unique variables
        variables = vars_list[0]
        for var in vars_list[1]:
            if var not in variables:
                variables.append(var)

        # create relation list
        rel_list = RelationList.identity(variables)
        rel_list.replace_column(vector, x)

        return index, rel_list, False

    @staticmethod
    def binary_op(index: int, node: pr.Assignment) -> COM_RES:
        """Analyze binary operation, e.g. `x = y + z`.

        Arguments:
            index: delta index
            node: AST node representing a binary operation

        Returns:
            Updated index value, relation list, and an exit flag.
        """
        logger.debug('Computing Relation: binary op')
        x, y, z = node.lvalue, node.rvalue.left, node.rvalue.right
        non_constants = tuple([v.name if hasattr(v, 'name') else None
                               for v in [x, y, z]])
        if not ((isinstance(y, pr.Constant) or isinstance(y, pr.ID)) and
                (isinstance(z, pr.Constant) or isinstance(z, pr.ID))):
            Analysis._unsupported(pr.to_c(node))
            return index, RelationList(), False

        # create a vector of polynomials based on operator type
        index, vector = Analysis.create_vector(
            index, node.rvalue.op, non_constants)

        # build a list of unique variables but maintain order
        variables = list(dict.fromkeys(non_constants))

        # create relation list
        rel_list = RelationList.identity(variables)
        if hasattr(x, 'name'):
            rel_list.replace_column(vector, x.name)

        return index, rel_list, False

    @staticmethod
    def constant(index: int, variable_name: str) -> COM_RES:
        """Analyze a constant assignment of form `x = c` where x is some
        variable and c is constant.

        !!! info "From \"A Flow Calculus of mwp-Bounds...\""

            To deal with constants, just replace the program’s constants by
            variables and regard the replaced constants as input to these
            variables.

        Arguments:
            index: delta index
            variable_name: name of variable to which constant is being assigned

        Returns:
            Updated index value, relation list, and an exit flag.
        """
        logger.debug('Constant value node')
        return index, RelationList([variable_name]), False

    @staticmethod
    def unary_asgn(index: int, node: pr.Assignment) -> COM_RES:
        """Assignment where right-hand-size is a unary op e.g. `x = y++`.

        Arguments:
            index: delta index
            node: Assignment, where the right-side is a unary operation.

        Returns:
            Updated index value, relation list, and an exit flag.
        """
        logger.debug('Computing Relation: unary')
        tgt, unary, op = node.lvalue, node.rvalue, node.rvalue.op
        if isinstance(unary.expr, pr.Constant):
            return Analysis.constant(index, tgt.name)
        if isinstance(unary.expr, pr.ID):
            exp = unary.expr.name
            if op in Coverage.INC_DEC:
                # expand unary incr/decr to a binary op
                # this ignores the +1/-1 applied to exp, but this is ok since
                # constants are irrelevant
                op_code = '+' if op in ('p++', '++') else '-'
                dsp = op.replace('p', exp) if ('p' in op) else f'{op}{exp}'
                logger.debug(f'{dsp} converted to {exp}{op_code}1')
                r_node = pr.BinaryOp(
                    op_code, pr.ID(exp), pr.Constant('int', 1))
                return Analysis.binary_op(
                    index, pr.Assignment('=', tgt, r_node))
            if op == '!':
                # negation ! of an integer gives either 0 or 1
                logger.debug(f'int negation of {exp} is a constant')
                return Analysis.id(index, pr.Assignment(
                    '=', tgt, pr.Constant('int', 1)))
            if op == 'sizeof':
                # sizeof gets variable's size in bytes
                # for all integers, the value is 8--64
                # https://en.wikipedia.org/wiki/C_data_types
                logger.debug(f'sizeof({exp}) is a constant')
                return Analysis.id(index, pr.Assignment(
                    '=', tgt, pr.Constant('int', 64)))
            if op == '+':  # does nothing; just an explicit sign
                return Analysis.id(index, pr.Assignment('=', tgt, unary.expr))
            if op == '-':  # flips variable sign
                r_node = pr.BinaryOp('*', pr.ID(exp), pr.Constant('int', -1))
                logger.debug(f'{op}{exp} converted to -1*{exp}')
                return Analysis.binary_op(
                    index, pr.Assignment('=', tgt, r_node))

        # unary address of "&" will fall through
        # expr not in {ID, Constant} will fall through
        Analysis._unsupported(type(node))
        return index, RelationList(), False

    @staticmethod
    def unary_op(index: int, node: pr.UnaryOp, dg: DeltaGraph) -> COM_RES:
        """Analyze a standalone unary operation.

        Arguments:
            index (int): Delta index.
            node (pr.UnaryOp): AST node to analyze.
            dg (DeltaGraph): DeltaGraph instance.

        Returns:
            Updated index value, relation list, and an exit flag.
        """
        if not (isinstance(node.expr, pr.Constant) or
                isinstance(node.expr, pr.ID)):
            return Analysis.compute_relation(index, node.expr, dg)

        op, exp = node.op, node.expr.name
        if op in Coverage.INC_DEC:
            # expand unary incr/decr to a binary op
            op_code = '+' if op in ('p++', '++') else '-'
            dsp = op.replace('p', exp) if ('p' in op) else f'{op}{exp}'
            logger.debug(f'{dsp} expanded to {exp}={exp}{op_code}1')
            r_node = pr.BinaryOp(op_code, pr.ID(exp), pr.Constant('int', 1))
            return Analysis.binary_op(index, pr.Assignment('=', exp, r_node))
        # all other unary ops do nothing ("skip") without assignment.
        return index, RelationList(), False

    @staticmethod
    def if_stmt(index: int, node: pr.If, dg: DeltaGraph) -> COM_RES:
        """Analyze an if statement.

        Arguments:
            index (int): Delta index.
            node (pr.If): if-statement AST node.
            dg (DeltaGraph): DeltaGraph instance.

        Returns:
            Updated index value, relation list, and an exit flag.
        """
        logger.debug('computing relation (conditional case)')
        true_relation, false_relation = RelationList(), RelationList()

        index, exit_ = Analysis.if_branch(
            index, node.iftrue, true_relation, dg)
        if exit_:
            return index, true_relation, True
        index, exit_ = Analysis.if_branch(
            index, node.iffalse, false_relation, dg)
        if exit_:
            return index, false_relation, True

        relations = false_relation + true_relation
        return index, relations, False

    @staticmethod
    def if_branch(index: int, node: pr.If, relation_list: RelationList,
                  dg: DeltaGraph) -> Tuple[int, bool]:
        """Analyze `if` or `else` branch of a conditional statement.

        This method will analyze the body of the statement and update
        the provided relation. It can handle blocks with or without surrounding
        braces. It will return the updated index value.

        If branch does not exist (when else case is omitted) this
        method does nothing and returns the original index value without
        modification.

        Arguments:
            index (int): Current delta index value.
            node (pr.If): AST if statement branch node.
            relation_list (RelationList): Current relation list state.
            dg (DeltaGraph): DeltaGraph instance.

        Returns:
            Updated index value, relation list, and an exit flag.
        """
        if node is not None:
            for child in (node.block_items or []) \
                    if hasattr(node, 'block_items') else [node]:
                index, rel_list, exit_ = Analysis \
                    .compute_relation(index, child, dg)
                if exit_:
                    return index, exit_
                relation_list.composition(rel_list)
        return index, False

    @staticmethod
    def while_loop(index: int, node: pr.While, dg: DeltaGraph) -> COM_RES:
        """Analyze a while loop.

        Arguments:
            index (int): Delta index.
            node (pr.while): While loop node.
            dg (DeltaGraph): DeltaGraph instance.

        Returns:
            Updated index value, relation list, and an exit flag.
        """
        logger.debug("analysing while")

        relations = RelationList()
        for child in node.stmt.block_items \
                if hasattr(node, 'block_items') else [node.stmt]:
            index, rel_list, exit_ = Analysis.compute_relation(
                index, child, dg)
            if exit_:
                return index, rel_list, exit_
            relations.composition(rel_list)

        logger.debug('while loop fixpoint')
        relations.fixpoint()
        relations.while_correction(dg)
        dg.fusion()

        return index, relations, dg.is_empty

    @staticmethod
    def for_loop(index: int, node: pr.For, dg: DeltaGraph) -> COM_RES:
        """Analyze for loop node.

        Arguments:
            index (int): Delta index.
            node (pr.For): for loop node.
            dg (DeltaGraph): DeltaGraph instance.

        Returns:
            Updated index value, relation list, and an exit flag.
        """
        comp, x_var = Coverage.loop_compat(node)
        if not comp:
            return index, RelationList(), False
        relations = RelationList(variables=[x_var])
        for child in node.stmt.block_items \
                if hasattr(node, 'block_items') else [node.stmt]:
            index, rel_list, exit_ = Analysis.compute_relation(
                index, child, dg)
            if exit_:
                return index, rel_list, True
            relations.composition(rel_list)

        logger.debug('loop fixpoint')
        relations.fixpoint()
        relations.loop_correction(x_var, dg)
        dg.fusion()
        return index, relations, dg.is_empty

    @staticmethod
    def compound(index: int, node: pr.Compound, dg: DeltaGraph) -> COM_RES:
        """Compound AST node contains zero or more children and is
        created by braces in source code.

        We analyze such compound node by recursively analysing its children.

        Arguments:
            index (int): Delta index.
            node (pr.Compound): Compound AST node.
            dg (DeltaGraph): DeltaGraph instance.

        Returns:
            Updated index value, relation list, and an exit flag.
        """
        relations = RelationList()

        if node.block_items:
            for node in node.block_items:
                index, rel_list, exit_ = Analysis.compute_relation(
                    index, node, dg)
                relations.composition(rel_list)
                if exit_:
                    return index, relations, True
        return index, relations, False

    @staticmethod
    def create_vector(index: int, op: str, variables: Tuple[str, ...]) \
            -> Tuple[int, List[Polynomial]]:
        """Build a polynomial vector based on operator and the operands
        of a binary operation statement that has form `x = y (operator) z`.

        For an AST node that represents a binary operation, this method
        generates a vector of polynomials based on the properties of that
        operation. The returned vector depends on the type of operator,
        how many operands are constants, and if the operands are equal.

        Arguments:
            index: delta index
            op: operator
            variables: variables in this operation `x = y (op) z` in order,
                where `y` or `z` is `None` if constant

        Returns:
             Updated index, list of Polynomial vectors
        """

        x, y, z = variables
        supported_op = Coverage.BIN_OPS
        vector = []

        if op not in supported_op:
            Analysis._unsupported(f'{op} operator')
            return index, []

        # when left variable does not occur on right side of assignment
        # x = … (if x not in …), i.e. when left side variable does not
        # occur on the right side of assignment, we prepend 0 to vector
        if x != y and x != z:
            vector.append(Polynomial('o'))

        if op in supported_op and (y is None or z is None):
            vector.append(Polynomial.from_scalars(index, 'm', 'm', 'm'))

        elif op == '*' and y == z:
            vector.append(Polynomial.from_scalars(index, 'w', 'w', 'w'))

        elif op == '*' and y != z:
            vector.append(Polynomial.from_scalars(index, 'w', 'w', 'w'))
            vector.append(Polynomial.from_scalars(index, 'w', 'w', 'w'))

        elif op in {'+', '-'} and y == z:
            vector.append(Polynomial.from_scalars(index, 'p', 'p', 'w'))

        elif op in {'+', '-'} and y != z:
            vector.append(Polynomial.from_scalars(index, 'm', 'p', 'w'))
            vector.append(Polynomial.from_scalars(index, 'p', 'm', 'w'))

        return index + 1, vector

    @staticmethod
    def _unsupported(command: any):
        """Handle unsupported command."""
        warning, endc = '\033[93m', '\033[0m'
        fmt_str = str(command or "").strip()
        logger.warning(f'{warning}Unsupported syntax{endc} '
                       f'not evaluated: {fmt_str}')


class LoopAnalysis(Analysis):
    """MWP analysis for loops."""

    @staticmethod
    def run(ast: pr.AST, res: Result = None, strict: bool = False, **kwargs):
        """Run loop-invariant analysis.

        Arguments:
            ast (pr.Node): Parsed C source code AST Node.
            res (Result): Pre-initialized result object.
            strict (bool): Require supported syntax.

        Returns:
            Analysis Result object.
        """
        result = res or Result()
        result.on_start()
        logger.debug("Starting loop analysis")
        for func in [f for f in ast if pr.is_func(f)]:
            # 1. find loops: nested loops are duplicated+lifted
            loops = FindLoops(func).loops
            logger.debug(f"Total analyzable loops: {len(loops)}")
            # todo: all of this can be done in parallel
            for loop in loops:
                # 2. check/fix loop body syntax
                if Analysis.syntax_check(loop.stmt, strict):
                    # 3. analyze and record result
                    loop_res = LoopAnalysis.loop(loop)
                    loop_res.func_name = func.decl.name
                    result.add_loop(loop_res)
        result.on_end()
        result.log_result()
        return result

    @staticmethod
    def loop(node: Union[pr.While, pr.DoWhile, pr.For]) -> LoopResult:
        """Analyze the loop (possibly nested).

        Arguments:
            node: A loop AST node (for, while, or do...while).

        Returns:
            Loop analysis result.
        """
        assert pr.is_loop(node)
        result = LoopResult().on_start()

        # setup for loop analysis
        variables = Variables(node).vars
        relations = RelationList.identity(variables=variables)
        # analyze body commands, always run to completion
        infty, index = LoopAnalysis.cmds(relations, 0, [node], stop=False)

        # Evaluation
        # 1. Bound exists? => evaluate whole-matrix
        choices = None if infty else \
            relations.first.eval(Analysis.CHOICE_DOMAIN, index)
        # 2. By-variable eval: find upto w-bounds/variable.
        var_choice = relations.first.var_eval(
            Analysis.CHOICE_DOMAIN, index, POLY_MWP).items()

        fst_ok = next((c for _, c in var_choice if not c.infinite), None)
        if fst_ok:
            print(relations.first.apply_choice(*fst_ok.first))

        print(infty, choices.valid if choices else 'No choice!')
        print('\n'.join([f'{k}, {v.valid} {v.infinite}'
                         for k, v in var_choice]))

        #   todo: 3. Record all <= w bounds;
        #      * if whole-matrix passes, safe to take any.
        #      * otherwise make sure variable does not interfere with a
        #        "bad" variable (0 in matrix).

        # todo: Save results
        result.vars = relations.first.variables
        result.loop_code = pr.to_c(node)
        result.on_end()
        return result
