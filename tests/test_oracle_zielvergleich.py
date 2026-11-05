"""Orakel-Test zielvergleich-demo: der Kern gegen einen ANDEREN Rechenweg (ORACLE-PLAYBOOK §2, DEMO-PLAYBOOK §12).

Zwei Wege in beide Richtungen:
  * Die aufgezählten Optima (numpy, alle Pläne) gegen reines Python (itertools, Gleitkommazahlen, keine numpy-Zeile) und gegen scipy.
  * Die Löser (Ungarische Methode, Schwellwertsuche mit Matching) gegen die Aufzählung und gegen reines Python.

Mini-Instanzen n = 3 bis 6, feste Seeds (range statt Zufall), alle drei Instanzfamilien; die Handwerte des Handbeispiels stehen in test_algorithm.py.
"""

import itertools
import math

import pytest

import zvg_algorithm as A
from zvg_scenario import make_instance

scipy_opt = pytest.importorskip("scipy.optimize")


def _brute(c, p):
    """Reines Python: bestes Ziel (Summe b^p bzw. lexikographisch Maximum, dann Summe) über alle Pläne."""
    n = len(c)
    best = None
    for plan in itertools.permutations(range(n)):
        b = [c[i][j] for i, j in enumerate(plan)]
        key = (max(b), sum(b)) if math.isinf(p) else (sum(x ** p for x in b),)
        if best is None or key < best:
            best = key
    return best


def test_enumeration_matches_pure_python_for_sum_squares_and_lexicographic_maximum():
    for n in (3, 4, 5, 6):
        for family in range(3):
            for seed in range(12):
                inst = make_instance(n, family, seed)
                for p in (1.0, 2.0, math.inf):
                    r = A.enumerate_optimum(inst.array(), p)
                    key = (r.peak, r.total) if math.isinf(p) else (sum(b ** p for b in r.burdens),)
                    expected = _brute(inst.c, p)
                    assert key == pytest.approx(expected, rel=1e-9), (n, family, seed, p)


def test_enumeration_matches_scipy_assignment_for_the_sum_and_the_squares():
    for n in (3, 4, 5, 6, 7):
        for family in range(3):
            for seed in range(10):
                c = make_instance(n, family, seed).array()
                for p in (1.0, 2.0):
                    rows, cols = scipy_opt.linear_sum_assignment(c ** p)
                    assert (c ** p)[rows, cols].sum() == pytest.approx(sum(b ** p for b in A.enumerate_optimum(c, p).burdens), rel=1e-9)


def test_the_solvers_match_pure_python_brute_force():
    for n in (3, 4, 5, 6):
        for family in range(3):
            for seed in range(12):
                inst = make_instance(n, family, seed)
                c = inst.array()
                for p in (1.0, 2.0, 3.0):
                    r = A.solve_lap(c, p)
                    assert sum(b ** p for b in r.burdens) == pytest.approx(_brute(inst.c, p)[0], rel=1e-9)
                lex = A.solve_bottleneck_lex(c)
                assert (lex.peak, lex.total) == pytest.approx(_brute(inst.c, math.inf))


def test_bottleneck_value_matches_the_smallest_maximum_over_all_plans():
    for n in (3, 4, 5, 6):
        for family in range(3):
            for seed in range(12):
                inst = make_instance(n, family, seed)
                smallest = min(max(inst.c[i][j] for i, j in enumerate(plan)) for plan in itertools.permutations(range(n)))
                assert A.bottleneck_value(inst.array()) == pytest.approx(smallest)


def test_every_displayed_plan_is_feasible_for_a_range_of_sizes():
    for n in (1, 2, 8, 9, 30):
        for family in range(3):
            inst = make_instance(n, family, 5)
            for p in (1.0, 2.0, math.inf):
                assert A.check_feasible(A.solve(inst, p).plan, n), (n, family, p)
