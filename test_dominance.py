"""Tests for the dominance module."""

import pytest
from dominance import dominates, pareto_front, rank_solutions, dominance_count


# ---------------------------------------------------------------------------
# dominates
# ---------------------------------------------------------------------------

class TestDominates:
    def test_clearly_dominates(self):
        assert dominates([1, 1], [2, 2])

    def test_not_dominated_equal(self):
        assert not dominates([1, 1], [1, 1])

    def test_not_dominated_tradeoff(self):
        assert not dominates([1, 2], [2, 1])

    def test_dominates_one_equal(self):
        # [1, 2] vs [2, 2]: equal on obj-2, better on obj-1 → dominates
        assert dominates([1, 2], [2, 2])

    def test_maximise_all(self):
        # higher is better → [3, 3] dominates [1, 1]
        assert dominates([3, 3], [1, 1], maximize=True)
        assert not dominates([1, 1], [3, 3], maximize=True)

    def test_per_objective_direction(self):
        # obj-0 minimise, obj-1 maximise
        # [1, 5] vs [2, 3]: better on obj-0 (1<2) and better on obj-1 (5>3)
        assert dominates([1, 5], [2, 3], maximize=[False, True])

    def test_mismatched_length_raises(self):
        with pytest.raises(ValueError):
            dominates([1, 2], [1, 2, 3])

    def test_maximize_length_mismatch_raises(self):
        with pytest.raises(ValueError):
            dominates([1, 2], [3, 4], maximize=[True])


# ---------------------------------------------------------------------------
# pareto_front
# ---------------------------------------------------------------------------

class TestParetoFront:
    def test_single_solution(self):
        assert pareto_front([[1, 2]]) == [[1, 2]]

    def test_all_dominated_except_one(self):
        solutions = [(1, 1), (2, 2), (3, 3)]
        front = pareto_front(solutions)
        assert front == [(1, 1)]

    def test_multiple_front_members(self):
        solutions = [(1, 3), (2, 2), (3, 1), (4, 4)]
        front = set(map(tuple, pareto_front(solutions)))
        assert front == {(1, 3), (2, 2), (3, 1)}

    def test_all_non_dominated(self):
        solutions = [(1, 2), (2, 1)]
        front = set(map(tuple, pareto_front(solutions)))
        assert front == {(1, 2), (2, 1)}

    def test_duplicates_deduplicated(self):
        solutions = [(1, 1), (1, 1), (2, 2)]
        front = pareto_front(solutions)
        assert len(front) == 1
        assert tuple(front[0]) == (1, 1)

    def test_empty_input(self):
        assert pareto_front([]) == []

    def test_maximise(self):
        solutions = [(1, 1), (3, 3), (2, 2)]
        front = pareto_front(solutions, maximize=True)
        assert tuple(front[0]) == (3, 3)


# ---------------------------------------------------------------------------
# rank_solutions
# ---------------------------------------------------------------------------

class TestRankSolutions:
    def test_basic_ranking(self):
        solutions = [(1, 1), (2, 2), (3, 3)]
        ranked = rank_solutions(solutions)
        by_sol = {tuple(s): r for r, s in ranked}
        assert by_sol[(1, 1)] == 1
        assert by_sol[(2, 2)] == 2
        assert by_sol[(3, 3)] == 3

    def test_tied_front(self):
        solutions = [(1, 2), (2, 1), (3, 3)]
        ranked = rank_solutions(solutions)
        by_sol = {tuple(s): r for r, s in ranked}
        assert by_sol[(1, 2)] == 1
        assert by_sol[(2, 1)] == 1
        assert by_sol[(3, 3)] == 2

    def test_all_same_rank(self):
        solutions = [(1, 3), (2, 2), (3, 1)]
        ranked = rank_solutions(solutions)
        assert all(r == 1 for r, _ in ranked)

    def test_empty(self):
        assert rank_solutions([]) == []


# ---------------------------------------------------------------------------
# dominance_count
# ---------------------------------------------------------------------------

class TestDominanceCount:
    def test_pareto_front_has_zero_count(self):
        solutions = [(1, 1), (2, 2), (3, 3)]
        counts = {tuple(s): c for s, c in dominance_count(solutions)}
        assert counts[(1, 1)] == 0
        assert counts[(2, 2)] == 1
        assert counts[(3, 3)] == 2

    def test_all_zero_for_non_dominated(self):
        solutions = [(1, 2), (2, 1)]
        counts = {tuple(s): c for s, c in dominance_count(solutions)}
        assert counts[(1, 2)] == 0
        assert counts[(2, 1)] == 0
