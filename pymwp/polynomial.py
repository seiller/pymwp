# flake8: noqa: W605

from __future__ import annotations

import logging
from typing import Optional, List, Tuple

from .constants import Comparison
from .monomial import Monomial
from .semiring import ZERO_MWP, sum_mwp
from .constants import SetInclusion

logger = logging.getLogger(__name__)


class Polynomial:
    """
    A polynomial is an ordered list of ordered [`Monomials`](monomial.md).

    For polynomials, I introduce a total order on the monomials. This
    eases the computation of the sum: if we want to add a monomial to an
    ordered list of monomials, we compare the monomial to each of the
    elements of the list until we find either an element which is equal
    (and then we sum the scalars) or an element which is larger (and
    then we insert the new monomial there).

    Polynomials use the following ordering: $\\delta(i,j)$
    is smaller than $\\delta(m,n)$ iff either $j<n$ or $(j==n)$ and $(i<m)$.

    This is extended to products (which we consider ordered!) by
    letting $\\prod_k\\delta(i_k,j_k) < \\prod_l\\delta(m_l,n_l)$
    iff $\\delta(i_1,j_1) < \\delta(m_1,n_1)$.
    """

    def __init__(self, monomials: Optional[List[Monomial]] = None):
        """Create a polynomial.

        Example:

        Create polynomial with no monomials

        ```python
        zero = Polynomial()
        ```

        Create polynomial with one default monomial

        ```python
        poly = Polynomial([Monomial()])
        ```

        Create polynomial with two monomials

        ```python
        poly = Polynomial([Monomial('m', [(0, 1)]), Monomial('w', [(1, 1)])])
        ```

        Arguments:
            monomials: list of monomials
        """
        self.list = monomials or [Monomial(ZERO_MWP)]

    def __str__(self):
        values = ''.join(['+' + str(m) for m in self.list]) or ('+' + ZERO_MWP)
        return "  " + values

    def __eq__(self, other):
        return self.equal(other)

    def __add__(self, other):
        return self.add(other)

    def __mul__(self, other):
        return self.times(other)

    @staticmethod
    def contains_filter(list_monom: list, mono: Monomial, i: int) \
            -> Tuple[SetInclusion, int]:
        """TODO: What does this method do, in one sentence?

        (If you need more words to explain it, write here or delete this line.)

        Arguments:
            list_monom: TODO: what is list_monom?
            mono: TODO: what is mono?
            i: TODO: what is i?

        Returns:
            TODO: what does this method return?
        """
        j = 0
        while j < len(list_monom):
            m = list_monom[j]
            incl = m.inclusion(mono)
            # if m ⊆ mono
            if incl == SetInclusion.CONTAINS:
                # We will then add mono so we can remove m
                list_monom.remove(m)
                # If removed monom is before i (where we want to insert mono)
                if j < i:
                    i = i - 1  # shift left position
                continue
            elif incl == SetInclusion.INCLUDED:
                #  We don't want to add mono, inform with CONTAINS
                return SetInclusion.CONTAINS, i
            j = j + 1
        # No inclusion
        return SetInclusion.EMPTY, i

    @staticmethod
    def inclusion(new_list: list, mono: Monomial, i: int = 0) \
            -> Tuple[bool, int]:
        """TODO: What does this method do, in one sentence?

        (If you need more words to explain it, write here or delete this line.)

        Arguments:
            new_list: TODO: what is new list?
            mono: TODO: what is mono?
            i: TODO: what is i?

        Returns:
            TODO: what does "False, i" mean?
            TODO: what does "True, i" mean?
        """
        # XXX new_list will be simplified regarding to mono2 here ↓ XXX
        incl, i = Polynomial.contains_filter(new_list, mono, i)

        # if mono2 ⊆ new_list
        if incl == SetInclusion.CONTAINS:
            # We skip adding mono2 into new_list
            return False, i
        return True, i

    def add_old(self, polynomial: Polynomial) -> Polynomial:
        """Add two polynomials

        - If both lists are empty the result is empty.
        - If one list is empty, the result will be the other list
        of polynomials.

        Otherwise the operation will zip the two lists together
        and return a new polynomial of sorted monomials.

        Arguments:
            polynomial: Polynomial to add to self

        Returns:
            New, sorted polynomial that is a sum of the
            two input polynomials
        """
        # check for empty lists
        if not self.list and not polynomial.list:
            return Polynomial()
        if not self.list:
            return polynomial.copy()
        if not polynomial.list:
            return self.copy()

        i, j = 0, 0
        new_list = self.copy().list
        # self_len = len(new_list)
        poly_len = len(polynomial.list)

        # iterate lists of monomials until the end of shorter list
        while j < poly_len:
            mono2 = polynomial.list[j]
            mono1 = new_list[i]

            check = Polynomial.compare(mono1.deltas, mono2.deltas)

            # move to next when self is smaller
            if check == Comparison.SMALLER:
                i = i + 1

            # insert when the second is smaller
            elif check == Comparison.LARGER:
                new_list.insert(i, mono2)
                i = i + 1
                j = j + 1

            # when both list heads are the same
            # recompute scalar and move to next
            # element
            else:
                new_list[i].scalar = \
                    sum_mwp(mono1.scalar, mono2.scalar)
                j = j + 1

            # handle case where first list is shorter
            # by just appending what remains of the
            # other list of monomials
            if i == len(new_list):
                new_list = new_list + polynomial.list[j:]
                break

        sorted_monomials = Polynomial.sort_monomials(new_list)
        return Polynomial(sorted_monomials)

    def add(self, polynomial: Polynomial) -> Polynomial:
        """Add two polynomials

        - If both lists are empty the result is empty.
        - If one list is empty, the result will be the other list
        of polynomials.

        Otherwise the operation will zip the two lists together
        and return a new polynomial of sorted monomials.

        Arguments:
            polynomial: Polynomial to add to self

        Returns:
            New, sorted polynomial that is a sum of the
            two input polynomials
        """
        # check for empty lists
        if not self.list and not polynomial.list:
            return Polynomial()
        if not self.list:
            return polynomial.copy()
        if not polynomial.list:
            return self.copy()

        i, j = 0, 0
        new_list = self.copy().list
        # self_len = len(new_list)
        poly_len = len(polynomial.list)

        # iterate lists of monomials until the end of shorter list
        while j < poly_len:
            mono2 = polynomial.list[j]

            tobe_inserted, i = Polynomial.inclusion(new_list, mono2, i)

            if not (tobe_inserted):
                j = j + 1
                continue

            # handle case where first list is shorter
            # by just appending what remains of the
            # other list of monomials
            if new_list == []:
                new_list = new_list + polynomial.list[j:]

            # handle case where first list is shorter
            # by just appending what remains of the
            # other list of monomials
            if i == len(new_list):
                for m in polynomial.list[j:]:
                    tobe_inserted, i = Polynomial.inclusion(new_list, m, i)
                    if (tobe_inserted):
                        new_list = new_list + [m]
                break

            mono1 = new_list[i]

            check = Polynomial.compare(mono1.deltas, mono2.deltas)

            # move to next when self is smaller
            if check == Comparison.SMALLER:
                i = i + 1

            # insert when the second is smaller
            elif check == Comparison.LARGER:
                new_list.insert(i, mono2)
                i = i + 1
                j = j + 1

            # when both list heads are the same
            # recompute scalar and move to next
            # element
            else:
                new_list[i].scalar = \
                    sum_mwp(mono1.scalar, mono2.scalar)
                j = j + 1

        sorted_monomials = Polynomial.sort_monomials(new_list)
        return Polynomial(sorted_monomials)

    def times_old(self, polynomial: Polynomial) -> Polynomial:
        """Multiply two polynomials.

        Here we assume at least self is a sorted polynomial,
        and the result of this operation will be sorted.

        This operation works as follows:

        1. We compute a table of all the separated products
            $P.m_1,...,P.m_n$. Each of the elements is itself
            a sorted list of monomials: $P.m_j=m^j_1,...,m^j_k$

        2. We then sort the list of the first (smallest) elements
            of each list. I.e. we sort the list $m^1_1,m^2_1,...,m^n_1$
            and produce the list corresponding list of indexes of
            length n, I.e. a permutation over ${0,...,n}$.

        3. Once all this preparatory operations are done, the main part
           of the algorithm goes as follows:

        4. We consider the first element — say j — of the list of indexes
           and append to the result the first element of the corresponding
           list $P.m_j$ of monomials.

        5. We remove both the first element of the list of index and
           the first element of $P.m_j$.

        6. If $P.m_j$ is not empty, we insert j in the list of index
           at the right position: for this we compare the (new) first
           element of $P.m_j$ to  $m^{i_2}_1$ (as we removed the
           first element, $i_2$ is now the head of the list of indexes),
           then $m^{i_3}_1$, until we reach the index h such that
           $m^{i_h}_1$ is larger than $m^{j}_1$.

        7. We start back at point 4. Unless only one element is left
           in the list of indexes. In this case, we simply append the
           tail of the corresponding list to the result.

        Arguments:
            polynomial: polynomial to multiply with self

        Returns:
            a new polynomial that is the sorted product
            of the two input polynomials
        """

        # 1: compute table of products
        # here we compute P1 x P2 for each polynomial, excluding from the
        # result all monomials that have scalar value 0
        products = [[mono for mono in (m1 * m2 for m1 in self.list)
                     if mono.scalar != ZERO_MWP] for m2 in polynomial.list]
        # filter out empty monomials
        table: List[List[Monomial]] = [p for p in products if p]

        # if table is empty, return zero polynomial
        if not table:
            return Polynomial()

        # 2: create an index lists that represents the ordered
        # monomials in table, ordered by deltas of first monomials
        index_list = [0]
        for i in range(1, len(table)):
            t1 = table[i][0].deltas
            for j in range(len(index_list)):
                t2 = table[index_list[j]][0].deltas
                if Polynomial.compare(t1, t2) == Comparison.SMALLER:
                    index_list.insert(j, i)
                    break
            if i not in index_list:
                index_list.append(i)

        if len(self.list) > 1000 or len(polynomial.list) > 1000:
            logger.debug(f'p1 {len(self.list)}, p2: {len(polynomial.list)}')

        # 3: start main part
        result = []
        while index_list:
            # 4. get first element and append to result
            # 5. remove from index and table
            smallest = index_list.pop(0)
            # TODO 
            mono2 = table[smallest].pop(0)
            # tobe_inserted, _ = Polynomial.inclusion(result, mono2)
            # if tobe_inserted:
            result.append(mono2)

            # 6. when table is non-empty insert j at
            # the right index
            if table[smallest]:
                inserted = False
                t1 = table[smallest][0].deltas
                for j in range(len(index_list)):
                    t2 = table[index_list[j]][0].deltas
                    if Polynomial.compare(t1, t2) == Comparison.LARGER:
                        index_list.insert(j, smallest)
                        inserted = True
                        break
                if not inserted:
                    index_list.append(smallest)
            # 7. repeat until done

        return Polynomial(result)

    def times(self, polynomial: Polynomial) -> Polynomial:
        """Multiply two polynomials.

        Here we assume at least self is a sorted polynomial,
        and the result of this operation will be sorted.

        This operation works as follows:

        1. We compute a table of all the separated products
            $P.m_1,...,P.m_n$. Each of the elements is itself
            a sorted list of monomials: $P.m_j=m^j_1,...,m^j_k$

        2. We then sort the list of the first (smallest) elements
            of each list. I.e. we sort the list $m^1_1,m^2_1,...,m^n_1$
            and produce the list corresponding list of indexes of
            length n, I.e. a permutation over ${0,...,n}$.

        3. Once all this preparatory operations are done, the main part
           of the algorithm goes as follows:

        4. We consider the first element — say j — of the list of indexes
           and append to the result the first element of the corresponding
           list $P.m_j$ of monomials.

        5. We remove both the first element of the list of index and
           the first element of $P.m_j$.

        6. If $P.m_j$ is not empty, we insert j in the list of index
           at the right position: for this we compare the (new) first
           element of $P.m_j$ to  $m^{i_2}_1$ (as we removed the
           first element, $i_2$ is now the head of the list of indexes),
           then $m^{i_3}_1$, until we reach the index h such that
           $m^{i_h}_1$ is larger than $m^{j}_1$.

        7. We start back at point 4. Unless only one element is left
           in the list of indexes. In this case, we simply append the
           tail of the corresponding list to the result.

        Arguments:
            polynomial: polynomial to multiply with self

        Returns:
            a new polynomial that is the sorted product
            of the two input polynomials
        """

        # 1: compute table of products
        # here we compute P1 x P2 for each polynomial, excluding from the
        # result all monomials that have scalar value 0
        products = [[mono for mono in (m1 * m2 for m1 in self.list)
                     if mono.scalar != ZERO_MWP] for m2 in polynomial.list]
        # filter out empty monomials
        table: List[List[Monomial]] = [p for p in products if p]

        # if table is empty, return zero polynomial
        if not table:
            return Polynomial()

        # 2: create an index lists that represents the ordered
        # monomials in table, ordered by deltas of first monomials
        index_list = [0]
        for i in range(1, len(table)):
            t1 = table[i][0].deltas
            for j in range(len(index_list)):
                t2 = table[index_list[j]][0].deltas
                if Polynomial.compare(t1, t2) == Comparison.SMALLER:
                    index_list.insert(j, i)
                    break
            if i not in index_list:
                index_list.append(i)

        if len(self.list) > 1000 or len(polynomial.list) > 1000:
            logger.debug(f'p1 {len(self.list)}, p2: {len(polynomial.list)}')

        # 3: start main part
        result = []
        while index_list:
            # 4. get first element and append to result
            # 5. remove from index and table
            smallest = index_list.pop(0)
            # TODO 
            mono2 = table[smallest].pop(0)
            tobe_inserted, _ = Polynomial.inclusion(result, mono2)
            if tobe_inserted:
                result.append(mono2)

            # 6. when table is non-empty insert j at
            # the right index
            if table[smallest]:
                inserted = False
                t1 = table[smallest][0].deltas
                for j in range(len(index_list)):
                    t2 = table[index_list[j]][0].deltas
                    if Polynomial.compare(t1, t2) == Comparison.LARGER:
                        index_list.insert(j, smallest)
                        inserted = True
                        break
                if not inserted:
                    index_list.append(smallest)
            # 7. repeat until done

        return Polynomial(result)

    def eval(self, argument_list: list[int]) -> str:
        """Evaluate polynomial.

        This method performs map() on each monomial against the argument list
        then reduces the result to a single result determined by
        [`semiring#sum_mwp`](semiring.md#pymwp.semiring.sum_mwp) function.

        Arguments:
            argument_list: list of indices of deltas to evaluate

        Returns:
            scalar value
        """
        result = ZERO_MWP
        for monomial in self.list:
            result = sum_mwp(result, monomial.eval(argument_list))
            if result == 'i':
                break
        return result

    def equal(self, polynomial: Polynomial) -> bool:
        """Determine if two polynomials are equal.

        This method will compare current polynomial (self) to
        another polynomial provided as argument. Result of
        true means both polynomials have an equal number of
        monomials, and element-wise each monomial has the same
        list of deltas. Otherwise the result is false.

        This method is alias of `==` operator.

        Arguments:
            polynomial: polynomial to compare.

        Returns:
            True if polynomials are equal and false otherwise.
        """
        p1, p2 = self.list, polynomial.list

        # the only times deltas are equal is if they contain
        # same values and are equal in length; avoid calling
        # compare because it is more expensive method call; we
        # can do faster equality comparison on deltas this way
        same = [m1.scalar == m2.scalar and m1.deltas == m2.deltas
                for m1, m2 in zip(p1, p2)]

        # if False is in list it means some comparison of
        # deltas was determined not to be equal; do length
        # comparison last because it is almost never False
        return False not in same and len(p1) == len(p2)

    def copy(self) -> Polynomial:
        """Make a deep copy of polynomial."""
        return Polynomial([m.copy() for m in self.list])

    def show(self) -> None:
        """Display polynomial."""
        print(str(self))

    @staticmethod
    def compare(delta_list1: list, delta_list2: list) -> Comparison:
        """
        Compare 2 lists of deltas.

        We compare the initial segment up to the size of the shortest one.
        If the initial segments match, then the result is determined based
        on length. Three outputs are possible:

        - `SMALLER` if the first list is smaller than the second
        - `EQUAL` if both lists are equal in contents and length
        - `LARGER` if the first list is larger than the second

        The return value represents the relation of first
        list to the second one. `Smaller` means either

        - delta values of first list are smaller -or-
        - deltas are equal but first list is shorter in length.

        Larger is the opposite case.

        Arguments:
            delta_list1: first monomial list to compare
            delta_list2: second monomial list to compare

        Returns:
            result of comparison
        """
        # element wise comparison up to length of shorter list
        list_diff = [(a == b) for a, b in zip(delta_list1, delta_list2)]

        # if some difference exists
        if False in list_diff:

            # index of first difference
            idx = list_diff.index(False)

            (i, j), (m, n) = delta_list1[idx], delta_list2[idx]

            if (j < n) or (j == n and i < m):
                return Comparison.SMALLER
            else:
                return Comparison.LARGER

        # If the list coincide on their initial segment up to "max",
        # determine the lengths of the two lists
        first_len, second_len = len(delta_list1), len(delta_list2)

        # determine how first list relates to second list
        if first_len > second_len:
            return Comparison.LARGER
        if first_len < second_len:
            return Comparison.SMALLER
        else:
            return Comparison.EQUAL

    @staticmethod
    def sort_monomials(monomials: list) -> list:
        """Given a list of monomials this method
        will return them in order.

        The sort is performed by first dividing the list of
        monomials into halves recursively until each half
        contains at most one monomial. Then the sort will
        begin to combine (or zip) the halves into a
        sorted list.

        The original list argument is not mutated by
        this sort operation; does not sort in place.

        Arguments:
            monomials: list of monomials to sort

        Returns:
            list of sorted monomials
        """
        list_len = len(monomials)

        # base case
        if list_len < 2:
            if monomials and monomials[0] == ZERO_MWP:
                return []
            return monomials

        # split list into two halves equally
        mid_point = list_len // 2
        left = Polynomial.sort_monomials(monomials[mid_point:])
        right = Polynomial.sort_monomials(monomials[:mid_point])

        # construct sorted list by iteratively combining
        # monomials from left and right halves
        new_list = []
        while left and right:
            lhead, *ltail = left
            rhead, *rtail = right
            comparison = Polynomial.compare(lhead.deltas, rhead.deltas)

            # head of left list is smaller -> add it to list
            if comparison == Comparison.SMALLER:
                new_list.append(lhead)
                left = ltail

            # head of right list is smaller -> add it to list
            if comparison == Comparison.LARGER:
                new_list.append(rhead)
                right = rtail

            # both list heads are equal
            if comparison == Comparison.EQUAL:
                monomial = lhead
                # append to list as long as scalar
                # product is not 0
                monomial.scalar = sum_mwp(
                    lhead.scalar, rhead.scalar)
                if monomial.scalar != ZERO_MWP:
                    new_list.append(monomial)
                left = ltail
                right = rtail

        # either left or right is empty so order
        # doesn't matter; just append whatever
        # remains of left or right tail
        return new_list + right + left
