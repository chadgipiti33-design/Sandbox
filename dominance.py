"""
Dominance System — multi-objective Pareto dominance ranking.

A solution `a` *dominates* solution `b` when:
  - `a` is no worse than `b` on every objective, AND
  - `a` is strictly better than `b` on at least one objective.

All objectives are treated as minimisation problems by default.
Pass ``maximize=True`` (or a per-objective list) to flip any axis.

Example
-------
>>> from dominance import dominates, pareto_front, rank_solutions
>>> solutions = [(1, 2), (2, 1), (3, 3), (1, 1)]
>>> pareto_front(solutions)
[(1, 1)]
"""

from __future__ import annotations

from typing import Iterable, Sequence


def dominates(
    a: Sequence[float],
    b: Sequence[float],
    maximize: bool | Sequence[bool] = False,
) -> bool:
    """Return True if solution *a* Pareto-dominates solution *b*.

    Parameters
    ----------
    a, b:
        Sequences of objective values with the same length.
    maximize:
        If True, all objectives are maximised.
        A list of booleans selects per-objective direction.
    """
    if len(a) != len(b):
        raise ValueError(f"Solutions must have the same number of objectives, got {len(a)} and {len(b)}")

    if isinstance(maximize, bool):
        flags = [maximize] * len(a)
    else:
        flags = list(maximize)
        if len(flags) != len(a):
            raise ValueError("Length of 'maximize' must match number of objectives")

    # Flip signs so we always minimise
    a_norm = [-v if m else v for v, m in zip(a, flags)]
    b_norm = [-v if m else v for v, m in zip(b, flags)]

    at_least_as_good = all(ai <= bi for ai, bi in zip(a_norm, b_norm))
    strictly_better  = any(ai <  bi for ai, bi in zip(a_norm, b_norm))
    return at_least_as_good and strictly_better


def pareto_front(
    solutions: Iterable[Sequence[float]],
    maximize: bool | Sequence[bool] = False,
) -> list[Sequence[float]]:
    """Return the non-dominated (Pareto-optimal) front.

    Parameters
    ----------
    solutions:
        Iterable of objective-value sequences.
    maximize:
        Direction per objective (see :func:`dominates`).
    """
    pool: list[Sequence[float]] = list(solutions)
    front: list[Sequence[float]] = []

    for candidate in pool:
        dominated = any(dominates(other, candidate, maximize) for other in pool if other is not candidate)
        if not dominated:
            front.append(candidate)

    # Remove duplicates while preserving order
    seen: set[tuple] = set()
    unique: list[Sequence[float]] = []
    for sol in front:
        key = tuple(sol)
        if key not in seen:
            seen.add(key)
            unique.append(sol)
    return unique


def rank_solutions(
    solutions: Iterable[Sequence[float]],
    maximize: bool | Sequence[bool] = False,
) -> list[tuple[int, Sequence[float]]]:
    """Assign a dominance rank to every solution (non-dominated sorting).

    Rank 1 = Pareto-optimal front; rank 2 = optimal after removing rank-1
    solutions; and so on.

    Returns
    -------
    list of ``(rank, solution)`` pairs, sorted by rank then by the original
    order of *solutions*.
    """
    remaining: list[Sequence[float]] = list(solutions)
    ranked: list[tuple[int, Sequence[float]]] = []
    rank = 1

    while remaining:
        front = pareto_front(remaining, maximize)
        front_set = {tuple(s) for s in front}
        for sol in remaining:
            if tuple(sol) in front_set:
                ranked.append((rank, sol))
        remaining = [s for s in remaining if tuple(s) not in front_set]
        rank += 1

    return ranked


def dominance_count(
    solutions: Iterable[Sequence[float]],
    maximize: bool | Sequence[bool] = False,
) -> list[tuple[Sequence[float], int]]:
    """Return each solution with the number of solutions that dominate it.

    A solution with count 0 belongs to the Pareto front.
    """
    pool = list(solutions)
    result: list[tuple[Sequence[float], int]] = []
    for sol in pool:
        count = sum(1 for other in pool if dominates(other, sol, maximize))
        result.append((sol, count))
    return result
