"""Randfälle, an denen Kernroutinen erfahrungsgemäß brechen (DEMO-PLAYBOOK §12)."""

import math

import numpy as np
import pytest

import zvg_algorithm as A
import zvg_constants as C
from zvg_evaluation import Settings, analyse
from zvg_scenario import Instance, make_instance


def test_exactly_two_persons():
    """n = 2: der kleinste Fall, in dem es etwas zu vergleichen gibt."""
    inst = Instance(((1.0, 4.0), (3.0, 2.0)))
    for p in (1.0, 2.0, math.inf):
        r = A.solve(inst, p)
        assert r.plan == (0, 1) and r.total == 3.0 and r.peak == 2.0


def test_single_person_has_the_only_plan():
    inst = Instance(((6.0,),))
    for p in (1.0, 2.0, math.inf):
        r = A.solve(inst, p)
        assert r.plan == (0,) and r.total == r.peak == 6.0 and r.squares == 36.0
    assert len(A.all_plans(1)) == 1 and len(A.optimal_set(inst.array(), math.inf)) == 1


def test_all_entries_equal_make_every_plan_optimal():
    inst = Instance(tuple(tuple([5.0] * 4) for _ in range(4)))
    a = analyse_from(inst)
    assert a.distinct == 1
    assert len(A.optimal_set(inst.array(), math.inf)) == 24 and len(A.optimal_set(inst.array(), 1.0)) == 24


def analyse_from(inst):
    """Auswertung für eine feste Instanz (ohne make_instance), wie in zvg_evaluation.analyse."""
    results = {g: A.solve(inst, A.goal_p(g)) for g in C.GOALS}
    from zvg_evaluation import Analysis
    return Analysis(inst, results, len({r.plan for r in results.values()}), math.factorial(inst.n), len(A.optimal_set(inst.array(), math.inf)), True)


def test_one_very_expensive_task_fixes_the_maximum_for_every_plan():
    """Aufgabe 2 kostet 50 bei jeder Person außer Person 2: die Optimalmenge beim Maximum enthält alle Pläne mit diesem Maximum, und die zweite Regel wählt davon die kleinste Summe."""
    c = np.array([[1.0, 2.0, 50.0], [2.0, 1.0, 50.0], [9.0, 9.0, 5.0]])
    r = A.enumerate_optimum(c, math.inf)
    assert r.peak == 5.0 and r.plan == (0, 1, 2)


def test_integers_with_many_ties_still_give_feasible_plans():
    for seed in range(40):
        a = analyse(Settings(6, 0, seed))
        assert all(A.check_feasible(r.plan, 6) for r in a.results.values())
        assert 1 <= a.distinct <= 3 and a.tie_size >= 1


def test_seed_zero_and_the_largest_seed_work():
    for seed in (0, C.SEED_MAX):
        a = analyse(Settings(5, 1, seed))
        assert a.enumerated and a.plans_total == 120


def test_bounds_are_inclusive():
    """Grenzen gelten inklusive: n = N_MIN, n = ENUM_MAX und n = ENUM_MAX + 1 (erste Größe mit Lösern) sind erlaubt."""
    for n in (C.N_MIN, C.ENUM_MAX, C.ENUM_MAX + 1):
        a = analyse(Settings(n, 1, 7))
        assert a.enumerated == (n <= C.ENUM_MAX)
        assert (a.plans_total is None) == (n > C.ENUM_MAX) and (a.tie_size is None) == (n > C.ENUM_MAX)


def test_enumeration_refuses_sizes_beyond_nine_and_the_hungarian_route_refuses_infinity():
    with pytest.raises(ValueError):
        A.all_plans(10)
    with pytest.raises(ValueError):
        A.all_plans(0)
    with pytest.raises(ValueError):
        A.solve_lap(make_instance(4, 1, 1).array(), math.inf)
    with pytest.raises(ValueError):
        A.solve_lap(make_instance(4, 1, 1).array(), 0.0)


def test_a_large_instance_is_solved_exactly_and_quickly_enough_to_display():
    a = analyse(Settings(C.N_MAX, 1, 3))
    assert not a.enumerated and a.inst.n == C.N_MAX
    assert a.results["sum"].total <= a.results["sumsq"].total + 1e-9 and a.results["max"].peak <= a.results["sum"].peak + 1e-9
