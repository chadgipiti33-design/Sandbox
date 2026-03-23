# CLAUDE.md

This file provides guidance for AI assistants working in this repository.

## Repository Overview

A focused Python library implementing **multi-objective Pareto dominance ranking** — the algorithmic backbone used in evolutionary multi-objective optimization (e.g., NSGA-II). It has no external dependencies and ships with a full pytest test suite.

## File Structure

```
Sandbox/
├── dominance.py          # Core library — four public functions
├── test_dominance.py     # pytest test suite — 20 unit tests
├── .gitignore            # Excludes __pycache__/, *.pyc, *.pyo, .pytest_cache/
└── CLAUDE.md             # This file
```

## Public API (`dominance.py`)

| Function | Signature | Description |
|---|---|---|
| `dominates` | `(a, b, maximize=False) -> bool` | True if `a` Pareto-dominates `b` |
| `pareto_front` | `(solutions, maximize=False) -> list` | Non-dominated front |
| `rank_solutions` | `(solutions, maximize=False) -> list[tuple[int, sol]]` | Non-dominated sorting, rank 1 = optimal |
| `dominance_count` | `(solutions, maximize=False) -> list[tuple[sol, int]]` | Count of dominators per solution |

All functions accept `maximize: bool | Sequence[bool]` — a single bool applies to all objectives; a list selects direction per objective.

## Key Algorithmic Conventions

- **All objectives are minimization by default.** Maximization is implemented by flipping signs internally (`-v if m else v`) so every algorithm operates in minimization space. Never manually negate values when calling the API.
- `a` dominates `b` iff `a` is **no worse on every objective** AND **strictly better on at least one**.
- `pareto_front` deduplicates identical solutions (preserving order of first occurrence).
- `rank_solutions` implements iterative non-dominated sorting: extract rank-1 front, remove it, repeat. Rank numbering starts at 1.
- `dominance_count` of 0 means the solution is on the Pareto front.

## Complexity

| Function | Time |
|---|---|
| `dominates` | O(k) where k = number of objectives |
| `pareto_front` | O(n²·k) |
| `rank_solutions` | O(n³·k) worst case |
| `dominance_count` | O(n²·k) |

## Development Workflow

### Running Tests

```bash
pytest test_dominance.py -v
```

No build step or dependency installation is required. The library uses only the Python standard library.

### Adding Features

1. Add the implementation to `dominance.py` following existing conventions (pure functions, type hints, NumPy-style docstrings).
2. Add corresponding tests in `test_dominance.py` inside an appropriately named `Test<FeatureName>` class.
3. All existing tests must continue to pass.

### Code Style Conventions

- `from __future__ import annotations` is used for forward-compatible type hints — keep it at the top of every module.
- Type hints use `|` union syntax (PEP 604) and `Sequence[float]` / `Iterable[Sequence[float]]` for numeric inputs.
- Docstrings use NumPy style with `Parameters` and `Returns` sections.
- Functions are pure (no side effects, no global state).
- Input validation raises `ValueError` with a descriptive message.
- Use `list[Sequence[float]]` return types (materialized lists, not generators).

### Testing Conventions

- Test classes are named `Test<FunctionName>` (e.g., `TestDominates`, `TestParetoFront`).
- Test methods are named `test_<scenario>` (e.g., `test_basic_domination`, `test_empty_input`).
- Each test targets one behavior or edge case.
- Cover: basic cases, equal solutions, tradeoffs, single-element input, empty input, mixed maximize flags, and dimension mismatch errors.

## Git Conventions

- Commits are authored as `Claude <noreply@anthropic.com>`.
- Commit messages are concise imperative phrases (e.g., "Add Pareto dominance system with non-dominated sorting").
- Branch naming: `claude/<description>-<session-id-suffix>`.

## What This Repo Does Not Have

- No build system (no `Makefile`, `pyproject.toml`, `setup.py`, or `requirements.txt`).
- No CI/CD pipeline.
- No external dependencies.
- No package installation — import directly from the project root.
