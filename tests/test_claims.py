"""Jede Zahl aus dem README wird hier nachgerechnet (DEMO-PLAYBOOK §4). Die Zahlen sind exakt (Aufzählung ist deterministisch)."""

import math
from pathlib import Path

import pytest

import zvg_constants as C
import zvg_evaluation as ev

README = (Path(__file__).resolve().parent.parent / "README.md").read_text(encoding="utf-8")


def _col(rows, key):
    return [r[key] for r in rows]


@pytest.fixture(scope="module")
def freq():
    return {f: ev.frequency_rows(f) for f in range(3)}      # 0 ganze Zahlen, 1 gleichverteilt, 2 Personeneffekt


def test_sweep_instances_and_sizes_are_the_documented_ones():
    assert C.SWEEP_SEEDS == tuple(range(100000, 100020)) and C.SWEEP_SIZES == (4, 6, 8)
    assert "Seeds 100000 bis 100019" in README and "8! = 40 320" in README


def test_handbook_example_claims():
    a = ev.analyse(ev.Settings(4, 0, 358))
    s, q, m = (a.results[g] for g in C.GOALS)
    assert a.plans_total == 24 and a.distinct == 3 and a.tie_size == 1
    assert (s.total, s.burdens) == (14.0, (7.0, 3.0, 2.0, 2.0))
    assert (q.squares, q.total, q.burdens) == (65.0, 15.0, (6.0, 3.0, 2.0, 4.0))
    assert (m.peak, m.total, m.burdens) == (5.0, 16.0, (5.0, 3.0, 4.0, 4.0))
    assert len({r["plan"] for r in ev.p_rows(ev.Settings(4, 0, 358))}) == 3
    assert "**Summe 14**" in README and "**Quadratsumme 65** mit Summe 15" in README and "**Maximum 5** mit Summe 16" in README


def test_quadratic_goal_equal_to_the_sum_counts(freq):
    assert [_col(freq[f], "same_sq") for f in (1, 2, 0)] == [[16, 14, 10], [16, 12, 11], [19, 20, 17]]
    for text in ("**16 / 14 / 10**", "**16 / 12 / 11**", "**19 / 20 / 17**"):
        assert text in README


def test_all_three_goals_equal_counts(freq):
    assert [_col(freq[f], "same_all") for f in (1, 2, 0)] == [[14, 13, 5], [11, 8, 4], [18, 20, 17]]
    for text in ("**14 / 13 / 5**", "**11 / 8 / 4**", "**18 / 20 / 17**"):
        assert text in README


def test_maximum_ties_are_the_rule(freq):
    assert [_col(freq[f], "max_ties") for f in (1, 2, 0)] == [[4, 13, 17], [11, 19, 18], [7, 20, 19]]
    for text in ("**4 / 13 / 17**", "**11 / 19 / 18**", "**7 / 20 / 19**"):
        assert text in README


def test_the_square_optimum_with_a_larger_maximum_is_rare(freq):
    assert [_col(freq[f], "sq_worse_peak") for f in (1, 2, 0)] == [[0, 0, 0], [0, 2, 0], [0, 0, 0]]
    assert "**0 / 2 / 0**" in README and "**0 / 0 / 0**" in README
    a = ev.analyse(ev.Settings(**C.PRESETS["Quadrat verschlechtert das Maximum"]))
    assert round(a.results["sum"].peak, 1) == 44.1 and round(a.results["sumsq"].peak, 1) == 47.6
    assert "Maximum 44,1 im Summen-Plan gegen 47,6 im Quadrat-Plan" in README


def test_the_sum_of_the_optimum_falls_somewhere_with_growing_p(freq):
    assert [_col(freq[f], "p_falls") for f in (1, 2, 0)] == [[1, 4, 5], [3, 6, 10], [0, 0, 1]]
    for text in ("**1 / 4 / 5**", "**3 / 6 / 10**", "**0 / 0 / 1**"):
        assert text in README


def test_tie_preset_claims():
    a = ev.analyse(ev.Settings(**C.PRESETS["Gleichstand beim Maximum"]))
    assert a.tie_size == 96 and a.plans_total == 720 and a.results["max"].peak == 8.0
    assert [a.results[g].total for g in C.GOALS] == [18.0, 18.0, 18.0]
    assert [a.results[g].squares for g in C.GOALS] == [92.0, 90.0, 92.0]
    assert "**96** von 720 Plänen" in README and "Quadratsumme 92 / 90 / 92" in README


def test_big_preset_claims():
    a = ev.analyse(ev.Settings(**C.PRESETS["Viele Personen (n = 60)"]))
    totals = [round(a.results[g].total, 1) for g in C.GOALS]
    peaks = [round(a.results[g].peak, 1) for g in C.GOALS]
    assert totals == [1882.9, 1903.4, 1899.8] and peaks == [51.3, 46.3, 44.6]
    assert a.results["max"].total < a.results["sumsq"].total and math.isfinite(a.results["max"].peak)
    for text in ("Summe 1882,9", "1903,4", "1899,8", "Maximum 51,3 / 46,3 / 44,6"):
        assert text in README
