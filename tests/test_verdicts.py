"""Verdikte an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Verzweigung steht hier."""

import math

import zvg_algorithm as A
import zvg_evaluation as ev
from zvg_scenario import Instance

INST = Instance(tuple(tuple([1.0] * 4) for _ in range(4)))
S = A.Result((0, 1, 2, 3), (7.0, 3.0, 2.0, 2.0), 14.0, 66.0, 7.0)
Q = A.Result((1, 2, 3, 0), (6.0, 3.0, 2.0, 4.0), 15.0, 65.0, 6.0)
M = A.Result((3, 2, 1, 0), (5.0, 3.0, 4.0, 4.0), 16.0, 66.0, 5.0)


def _analysis(distinct, enumerated=True, tie=1, total=24):
    return ev.Analysis(INST, {"sum": S, "sumsq": Q, "max": M}, distinct, total if enumerated else None, tie if enumerated else None, enumerated)


def test_de_uses_a_decimal_comma():
    assert ev.de(3.14159) == "3,1" and ev.de(2.0, 2) == "2,00" and ev.de(1234.5, 0) in ("1234", "1235", "1234")


def test_verdict_goals_three_plans_names_every_value():
    kind, text = ev.verdict_goals(_analysis(3))
    assert kind == "success"
    assert "Summe: 14,0 (Maximum 7,0)" in text and "Quadratsumme: Summe 15,0 (Maximum 6,0)" in text and "Maximum: Summe 16,0 (Maximum 5,0)" in text


def test_verdict_goals_two_plans():
    kind, text = ev.verdict_goals(_analysis(2))
    assert kind == "info" and "zwei verschiedene Pläne" in text and "Summe: 14,0 (Maximum 7,0)" in text and "Maximum: Summe 16,0 (Maximum 5,0)" in text


def test_verdict_goals_one_plan():
    kind, text = ev.verdict_goals(_analysis(1))
    assert kind == "info" and "denselben Plan" in text and "(Summe 14,0, Maximum 7,0)" in text


def test_verdict_landscape_unique_optimum():
    kind, text = ev.verdict_landscape(_analysis(3, tie=1, total=24))
    assert kind == "info" and "Von 24 Plänen hat genau **einer** das kleinste Maximum 5,0" in text


def test_verdict_landscape_tie_is_a_warning_and_names_the_count():
    kind, text = ev.verdict_landscape(_analysis(3, tie=96, total=720))
    assert kind == "warning" and "Von 720 Plänen haben **96** das kleinste Maximum 5,0" in text and "zweite Regel" in text


def test_verdict_landscape_without_enumeration_names_the_size():
    kind, text = ev.verdict_landscape(_analysis(3, enumerated=False))
    assert kind == "info" and "Bei n = 4 Personen" in text and "mehr als 8!" in text


def test_verdict_p_counts_plans_and_flags_a_falling_sum():
    rows = [{"p": 1.0, "plan": (0, 1), "total": 10.0}, {"p": 2.0, "plan": (1, 0), "total": 12.0}, {"p": math.inf, "plan": (1, 0), "total": 11.0}]
    kind, text = ev.verdict_p(rows)
    assert kind == "warning" and "**2** verschiedene Optimalpläne" in text and "sinkt" in text
    rows[2]["total"] = 12.0                                     # Gleichheit zählt nicht als Fallen
    kind, text = ev.verdict_p(rows)
    assert kind == "info" and "**2** verschiedene Optimalpläne" in text and "an keiner Stelle" in text


def test_verdict_p_tolerates_a_numerical_wiggle():
    rows = [{"p": 1.0, "plan": (0, 1), "total": 10.0}, {"p": 2.0, "plan": (0, 1), "total": 10.0 - 1e-12}]
    assert ev.verdict_p(rows)[0] == "info"


def test_verdict_frequency_names_every_count_and_flags_the_rare_case():
    rows = [{"n": 4, "seeds": 20, "same_sq": 15, "same_all": 9, "max_ties": 7, "sq_worse_peak": 0, "p_falls": 0},
            {"n": 8, "seeds": 20, "same_sq": 11, "same_all": 3, "max_ties": 12, "sq_worse_peak": 1, "p_falls": 4}]
    kind, text = ev.verdict_frequency(rows)
    assert kind == "warning" and text.startswith("Je 20 feste Instanzen:")
    assert "n = 4: Quadrat gleichwertig zur Summe in 15 von 20, alle drei gleichwertig in 9, Maximum nicht eindeutig in 7, Quadrat mit größerem Maximum in 0, Summe des Optimums sinkt mit p in 0" in text
    assert "n = 8: Quadrat gleichwertig zur Summe in 11 von 20, alle drei gleichwertig in 3, Maximum nicht eindeutig in 12, Quadrat mit größerem Maximum in 1, Summe des Optimums sinkt mit p in 4" in text
    rows[1]["sq_worse_peak"] = 0
    assert ev.verdict_frequency(rows)[0] == "warning"        # p_falls > 0 genügt für die Warnung
    rows[1]["p_falls"] = 0
    assert ev.verdict_frequency(rows)[0] == "info"
