"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, und was jedes Preset zeigen soll."""

import math

import zvg_algorithm as A
import zvg_constants as C
import zvg_evaluation as ev
import zvg_presets as P

HAND, ALL_ONE, TIE, SQ_WORSE, BIG = list(C.PRESETS)


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_slider_bounds():
    for preset in C.PRESETS.values():
        assert C.N_MIN <= preset["n"] <= C.N_MAX and 0 <= preset["family"] < len(C.FAMILIES) and 0 <= preset["seed"] <= C.SEED_MAX


def test_default_preset_equals_the_default_settings():
    assert ev.Settings(**C.PRESETS[HAND]) == ev.Settings()


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)


def _analysis(name):
    return ev.analyse(ev.Settings(**C.PRESETS[name]))


def test_handbeispiel_preset_shows_three_different_plans():
    a = _analysis(HAND)
    assert a.distinct == 3 and a.tie_size == 1 and a.plans_total == 24


def test_all_agree_preset_shows_one_plan():
    assert _analysis(ALL_ONE).distinct == 1


def test_tie_preset_has_many_maximum_optima_and_at_least_two_plans():
    a = _analysis(TIE)
    assert a.tie_size > 10 and a.distinct >= 2


def test_square_worse_preset_has_a_larger_maximum_under_the_squares_than_under_the_sum():
    a = _analysis(SQ_WORSE)
    assert a.results["sumsq"].peak > a.results["sum"].peak + C.TOL


def test_big_preset_is_not_enumerated_and_each_plan_wins_under_its_own_goal():
    """Jeder Plan ist unter seinem eigenen Ziel am besten; eine Ordnung der Summen von Quadrat- und Maximum-Plan ist NICHT garantiert
    (in diesem Preset hat der Maximum-Plan die kleinere Summe als der Quadrat-Plan, die Summe des Optimums ist nicht monoton in p)."""
    a = _analysis(BIG)
    assert not a.enumerated and a.distinct == 3
    s, q, m = (a.results[g] for g in C.GOALS)
    assert s.total <= min(q.total, m.total) + C.TOL
    assert q.squares <= min(s.squares, m.squares) * (1 + C.REL_TOL) + C.TOL
    assert m.peak <= min(s.peak, q.peak) + C.TOL
    assert m.total < q.total


def test_p_rows_cover_every_exponent_and_end_at_the_maximum():
    rows = ev.p_rows(ev.Settings())
    assert [r["p"] for r in rows] == list(C.P_VALUES)
    assert rows[0]["plan"] == A.solve(ev.make_instance(4, 0, 358), 1.0).plan
    assert rows[-1]["peak"] == min(r["peak"] for r in rows)


def test_frequency_rows_are_consistent_and_deterministic():
    rows = ev.frequency_rows(1)
    assert rows == ev.frequency_rows(1)
    assert [r["n"] for r in rows] == list(C.SWEEP_SIZES)
    for r in rows:
        assert r["seeds"] == len(C.SWEEP_SEEDS)
        assert 0 <= r["same_all"] <= r["same_sq"] <= r["seeds"] and 0 <= r["max_ties"] <= r["seeds"] and 0 <= r["sq_worse_peak"] <= r["seeds"]
