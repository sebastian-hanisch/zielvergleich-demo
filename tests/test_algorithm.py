"""Kern an Handwerten, Eigenschaften und Gegenproben (DEMO-PLAYBOOK §1b, ORACLE-PLAYBOOK §5)."""

import math

import numpy as np
import pytest

import zvg_algorithm as A
import zvg_constants as C
from zvg_scenario import Instance, make_instance


def test_handbeispiel_gives_three_different_optimal_plans(hand):
    s, q, m = A.solve(hand, 1.0), A.solve(hand, 2.0), A.solve(hand, math.inf)
    assert s.plan == (0, 2, 3, 1) and q.plan == (1, 2, 3, 0) and m.plan == (3, 2, 1, 0)
    assert (s.total, s.squares, s.peak) == (14.0, 66.0, 7.0)
    assert (q.total, q.squares, q.peak) == (15.0, 65.0, 6.0)
    assert (m.total, m.squares, m.peak) == (16.0, 66.0, 5.0)
    assert s.burdens == (7.0, 3.0, 2.0, 2.0) and q.burdens == (6.0, 3.0, 2.0, 4.0) and m.burdens == (5.0, 3.0, 4.0, 4.0)


def test_all_plans_enumerates_every_permutation_once():
    for n, expected in ((1, 1), (2, 2), (3, 6), (4, 24), (6, 720)):
        plans = A.all_plans(n)
        assert len(plans) == expected
        assert len({tuple(p) for p in plans.tolist()}) == expected
        assert all(A.check_feasible(p, n) for p in plans.tolist())


def test_check_feasible_rejects_every_kind_of_wrong_plan():
    assert A.check_feasible((2, 0, 1), 3)
    assert not A.check_feasible((0, 0, 1), 3)      # Aufgabe doppelt
    assert not A.check_feasible((0, 1), 3)         # zu kurz
    assert not A.check_feasible((0, 1, 3), 3)      # Aufgabe existiert nicht
    assert not A.check_feasible((0, 1, 2, 3), 3)   # zu lang
    assert not A.check_feasible((-1, 0, 1), 3)


def test_make_result_refuses_an_infeasible_plan(hand_array):
    with pytest.raises(ValueError):
        A.make_result(hand_array, (0, 0, 1, 2))


def test_the_tie_rule_for_the_maximum_is_lexicographic():
    """Person 2 muss Aufgabe 2 nehmen (Belastung 5): das Maximum ist in beiden Plänen 5, die Summe 7 gegen 9; gewählt wird die Summe 7."""
    c = np.array([[1.0, 2.0, 9.0], [2.0, 1.0, 9.0], [9.0, 9.0, 5.0]])
    assert len(A.optimal_set(c, math.inf)) == 2
    r = A.enumerate_optimum(c, math.inf)
    assert r.plan == (0, 1, 2) and r.peak == 5.0 and r.total == 7.0


def test_the_tie_rule_for_the_sum_is_the_smallest_plan():
    """Alle Einträge gleich: jeder Plan ist optimal, gewählt wird der erste in der Reihenfolge von itertools.permutations."""
    c = np.full((3, 3), 4.0)
    for p in (1.0, 2.0, math.inf):
        assert A.enumerate_optimum(c, p).plan == (0, 1, 2)
    assert len(A.optimal_set(c, 1.0)) == 6 and len(A.optimal_set(c, math.inf)) == 6


def test_the_hungarian_route_matches_the_enumerated_value():
    for n in (3, 4, 5, 6):
        for seed in range(25):
            for family in range(3):
                c = make_instance(n, family, seed).array()
                for p in (1.0, 2.0, 3.0):
                    lap = A.solve_lap(c, p)
                    enum = A.enumerate_optimum(c, p)
                    assert sum(b ** p for b in lap.burdens) == pytest.approx(sum(b ** p for b in enum.burdens), rel=1e-9)


def test_the_bottleneck_route_matches_the_enumerated_lexicographic_optimum():
    for n in (3, 4, 5, 6, 7):
        for seed in range(25):
            for family in range(3):
                c = make_instance(n, family, seed).array()
                lex = A.solve_bottleneck_lex(c)
                enum = A.enumerate_optimum(c, math.inf)
                assert lex.peak == pytest.approx(enum.peak) and lex.total == pytest.approx(enum.total), (n, seed, family)
                assert lex.peak == pytest.approx(A.bottleneck_value(c))


def test_solve_switches_to_the_solvers_above_enum_max():
    """n = 9 liegt über ENUM_MAX: solve rechnet mit den Lösern; die vollständige Aufzählung (erlaubt bis n = 9) bestätigt die Werte."""
    inst = make_instance(C.ENUM_MAX + 1, 1, 11)
    c = inst.array()
    b = A.plan_burdens(c, A.all_plans(9))
    assert A.solve(inst, 1.0).total == pytest.approx(b.sum(axis=1).min())
    assert A.solve(inst, 2.0).squares == pytest.approx((b ** 2).sum(axis=1).min())
    m = A.solve(inst, math.inf)
    assert m.peak == pytest.approx(b.max(axis=1).min())
    assert m.total == pytest.approx(b.sum(axis=1)[b.max(axis=1) <= b.max(axis=1).min() + C.TOL].min())


# --- Eigenschaften -------------------------------------------------------------------------------------------------------------------------


def _values(c):
    return tuple(A.enumerate_optimum(c, p) for p in (1.0, 2.0, math.inf))


def test_permuting_persons_and_tasks_keeps_the_optimal_values():
    rng = np.random.default_rng(0)
    for seed in range(15):
        c = make_instance(5, 1, seed).array()
        rows, cols = rng.permutation(5), rng.permutation(5)
        for a, b in zip(_values(c), _values(c[rows][:, cols])):
            assert (a.total, a.squares, a.peak) == pytest.approx((b.total, b.squares, b.peak))


def test_scaling_scales_sum_and_maximum_linearly_and_squares_quadratically():
    for seed in range(15):
        c = make_instance(5, 2, seed).array()
        for a, b in zip(_values(c), _values(3.0 * c)):
            assert b.plan == a.plan
            assert (b.total, b.squares, b.peak) == pytest.approx((3 * a.total, 9 * a.squares, 3 * a.peak))


def test_adding_a_constant_to_a_row_does_not_change_the_sum_plan():
    """Jeder Plan enthält genau einen Eintrag der Zeile: die Summe aller Pläne wächst um dieselbe Konstante."""
    for seed in range(20):
        c = make_instance(5, 1, seed).array()
        d = c.copy()
        d[2] += 17.0
        a, b = A.enumerate_optimum(c, 1.0), A.enumerate_optimum(d, 1.0)
        assert b.plan == a.plan and b.total == pytest.approx(a.total + 17.0)


def test_the_lexicographic_choice_has_the_smallest_sum_among_all_minimum_maximum_plans():
    for seed in range(30):
        c = make_instance(5, 0, seed).array()
        b = A.plan_burdens(c, A.all_plans(5))
        pick = A.enumerate_optimum(c, math.inf)
        best = b.sum(axis=1)[A.optimal_set(c, math.inf)].min()
        assert pick.total == pytest.approx(best)
        assert pick.peak == pytest.approx(b.max(axis=1).min())


def test_the_optimal_set_is_never_empty_and_contains_the_pick():
    for seed in range(30):
        c = make_instance(4, 0, seed).array()
        for p in (1.0, 2.0, math.inf):
            assert len(A.optimal_set(c, p)) >= 1


def test_landscape_has_one_point_per_plan(hand_array):
    sums, maxes = A.landscape(hand_array)
    assert len(sums) == len(maxes) == 24
    assert sums.min() == 14.0 and maxes.min() == 5.0


def test_goal_p_maps_the_three_goals():
    assert A.goal_p("sum") == 1.0 and A.goal_p("sumsq") == 2.0 and math.isinf(A.goal_p("max"))


def test_instances_are_deterministic_and_inside_their_ranges():
    for family in range(3):
        a, b = make_instance(5, family, 3), make_instance(5, family, 3)
        assert a == b and a != make_instance(5, family, 4)
    ints = make_instance(6, 0, 1).array()
    assert ints.min() >= 1 and ints.max() <= 9 and np.all(ints == ints.round())
    reals = make_instance(6, 1, 1).array()
    assert reals.min() >= 0 and reals.max() <= 100
