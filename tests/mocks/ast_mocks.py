"""
Sample ASTs for unit testing Analysis

here we mock the outputs of pycparser.parse_file

These ASTs match the examples in c_files by name, or tests/mocks
"""

from pycparser.c_ast import FileAST, FuncDef, Decl, FuncDecl, TypeDecl, \
    IdentifierType, Compound, Constant, While, BinaryOp, ID, Assignment, If

EMPTY_MAIN = FileAST(ext=[FuncDef(decl=Decl(
    name='main', quals=[], storage=[], funcspec=[],
    type=FuncDecl(args=None, type=TypeDecl(
        declname='main', quals=[], type=IdentifierType(
            names=['int']))), init=None, bitsize=None),
    param_decls=None, body=Compound(block_items=None))])

INFINITE_2C = FileAST(ext=[FuncDef(
    decl=Decl(name='main', quals=[], storage=[], funcspec=[], type=FuncDecl(
        args=None,
        type=TypeDecl(declname='main', quals=[], type=IdentifierType(
            names=['int']))), init=None, bitsize=None), param_decls=None,
    body=Compound(block_items=[Decl(
        name='X0', quals=[], storage=[], funcspec=[],
        type=TypeDecl(declname='X0', quals=[],
                      type=IdentifierType(names=['int'])),
        init=Constant(type='int', value='1'), bitsize=None),
        Decl(name='X1', quals=[], storage=[], funcspec=[], type=TypeDecl(
            declname='X1', quals=[], type=IdentifierType(names=['int'])),
             init=Constant(type='int', value='1'), bitsize=None),
        While(cond=BinaryOp(op='<', left=ID(name='X1'), right=Constant(
            type='int', value='10')), stmt=Compound(block_items=[
            Assignment(
                op='=', lvalue=ID(name='X0'),
                rvalue=BinaryOp(op='*', left=ID(name='X1'),
                                right=ID(name='X0'))),
            Assignment(op='=', lvalue=ID(name='X1'),
                       rvalue=BinaryOp(op='+', left=ID(name='X1'),
                                       right=ID(name='X0')))]))]))])

IF_WO_BRACES = FileAST(ext=[FuncDef(decl=Decl(
    name='main', quals=[], storage=[], funcspec=[],
    type=FuncDecl(args=None, type=TypeDecl(
        declname='main', quals=[], type=IdentifierType(names=['int']))),
    init=None, bitsize=None), param_decls=None,
    body=Compound(block_items=[
        Decl(name='x', quals=[], storage=[], funcspec=[],
             type=TypeDecl(
                 declname='x', quals=[], type=IdentifierType(names=['int'])),
             init=None, bitsize=None),
        Decl(name='y', quals=[], storage=[], funcspec=[],
             type=TypeDecl(
                 declname='y', quals=[],
                 type=IdentifierType(names=['int'])),
             init=None, bitsize=None),
        Assignment(op='=', lvalue=ID(name='x'),
                   rvalue=Constant(type='int', value='1')),
        Decl(name='x1', quals=[], storage=[], funcspec=[],
             type=TypeDecl(declname='x1', quals=[],
                           type=IdentifierType(names=['int'])), init=None,
             bitsize=None),
        Decl(name='x2', quals=[], storage=[], funcspec=[],
             type=TypeDecl(declname='x2', quals=[],
                           type=IdentifierType(names=['int'])),
             init=None, bitsize=None),
        Decl(name='x3', quals=[], storage=[], funcspec=[],
             type=TypeDecl(declname='x3', quals=[],
                           type=IdentifierType(names=['int'])), init=None,
             bitsize=None), Assignment(op='=', lvalue=ID(name='x1'),
                                       rvalue=Constant(type='int', value='1')),
        Assignment(op='=', lvalue=ID(name='x2'),
                   rvalue=Constant(type='int', value='2')), If(
            cond=BinaryOp(op='>', left=ID(name='x'),
                          right=Constant(type='int', value='0')),
            iftrue=Assignment(op='=', lvalue=ID(name='x3'),
                              rvalue=Constant(type='int', value='1')),
            iffalse=Assignment(op='=', lvalue=ID(name='x3'),
                               rvalue=ID(name='x2'))),
        Assignment(op='=', lvalue=ID(name='y'), rvalue=ID(name='x3'))]))
])

IF_WITH_BRACES = FileAST(ext=[FuncDef(decl=Decl(
    name='main', quals=[], storage=[], funcspec=[],
    type=FuncDecl(args=None, type=TypeDecl(
        declname='main', quals=[],
        type=IdentifierType(names=['int']))),
    init=None, bitsize=None),
    param_decls=None,
    body=Compound(
        block_items=[Decl(
            name='x', quals=[], storage=[], funcspec=[],
            type=TypeDecl(
                declname='x', quals=[],
                type=IdentifierType(names=['int'])),
            init=None, bitsize=None),
            Decl(name='y', quals=[], storage=[], funcspec=[],
                 type=TypeDecl(
                     declname='y', quals=[],
                     type=IdentifierType(names=['int'])),
                 init=None, bitsize=None),
            Assignment(op='=', lvalue=ID(name='x'),
                       rvalue=Constant(type='int', value='1')),
            Decl(
                name='x1', quals=[], storage=[], funcspec=[],
                type=TypeDecl(
                    declname='x1', quals=[],
                    type=IdentifierType(names=['int'])),
                init=None, bitsize=None),
            Decl(
                name='x2', quals=[], storage=[], funcspec=[],
                type=TypeDecl(
                    declname='x2', quals=[],
                    type=IdentifierType(names=['int'])),
                init=None, bitsize=None),
            Decl(
                name='x3', quals=[], storage=[], funcspec=[],
                type=TypeDecl(declname='x3', quals=[],
                              type=IdentifierType(names=['int'])),
                init=None, bitsize=None),
            Assignment(op='=', lvalue=ID(name='x1'),
                       rvalue=Constant(type='int', value='1')),
            Assignment(op='=', lvalue=ID(name='x2'),
                       rvalue=Constant(type='int', value='2')),
            If(cond=BinaryOp(
                op='>', left=ID(name='x'),
                right=Constant(type='int', value='0')),
                iftrue=Compound(block_items=[Assignment(
                    op='=', lvalue=ID(name='x3'),
                    rvalue=Constant(type='int', value='1'))]),
                iffalse=Compound(block_items=[Assignment(
                    op='=', lvalue=ID(name='x3'), rvalue=ID(name='x2'))])),
            Assignment(op='=', lvalue=ID(name='y'),
                       rvalue=ID(name='x3'))]))])

NOT_INFINITE_2C = FileAST(ext=[FuncDef(decl=Decl(
    name='main', quals=[], storage=[], funcspec=[],
    type=FuncDecl(args=None, type=TypeDecl(
        declname='main', quals=[], type=IdentifierType(names=['int']))),
    init=None, bitsize=None), param_decls=None,
    body=Compound(block_items=[Decl(
        name='X0', quals=[], storage=[], funcspec=[],
        type=TypeDecl(declname='X0', quals=[],
                      type=IdentifierType(names=['int'])),
        init=Constant(type='int', value='1'), bitsize=None),
        Decl(name='X1', quals=[], storage=[], funcspec=[],
             type=TypeDecl(declname='X1', quals=[],
                           type=IdentifierType(names=['int'])),
             init=Constant(type='int', value='1'), bitsize=None),
        Assignment(op='=', lvalue=ID(name='X0'),
                   rvalue=BinaryOp(op='*', left=ID(name='X1'),
                                   right=ID(name='X0'))),
        Assignment(op='=', lvalue=ID(name='X1'), rvalue=BinaryOp(
            op='+', left=ID(name='X1'), right=ID(name='X0')))]))])

VARIABLE_IGNORED = FileAST(ext=[FuncDef(decl=Decl(
    name='main', quals=[], storage=[], funcspec=[],
    type=FuncDecl(args=None, type=TypeDecl(
        declname='main', quals=[], type=IdentifierType(names=['int']))),
    init=None, bitsize=None), param_decls=None,
    body=Compound(block_items=[
        Assignment(op='=', lvalue=ID(name='X2'), rvalue=BinaryOp(
            op='+', left=ID(name='X3'), right=ID(name='X1'))),
        Assignment(op='=', lvalue=ID(name='X4'), rvalue=ID(name='X2'))]))])

EXTRA_BRACES = FileAST(ext=[FuncDef(decl=Decl(
    name='main', quals=[], storage=[], funcspec=[],
    type=FuncDecl(args=None, type=TypeDecl(
        declname='main', quals=[],
        type=IdentifierType(names=['int']))),
    init=None, bitsize=None), param_decls=None,
    body=Compound(block_items=[
        Decl(name='x', quals=[], storage=[], funcspec=[],
             type=TypeDecl(declname='x', quals=[],
                           type=IdentifierType(names=['int'])),
             init=None, bitsize=None),
        Decl(name='y', quals=[], storage=[], funcspec=[],
             type=TypeDecl(
                 declname='y', quals=[], type=IdentifierType(names=['int'])),
             init=None, bitsize=None),
        Compound(
            block_items=[If(cond=BinaryOp(
                op='>', left=ID(name='x'), right=ID(name='y')),
                iftrue=Compound(block_items=[Assignment(
                    op='=', lvalue=ID(name='x'), rvalue=ID(name='y'))
                ]), iffalse=None
            )])]))])
