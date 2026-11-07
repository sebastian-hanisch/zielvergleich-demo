"""Kennzahlen, Verdikt-Logik und Sweeps. Verdikte sind reine Funktionen (Art, Text); jede Zahl im Text kommt aus der Rechnung."""

import math
from dataclasses import dataclass

import zvg_algorithm as A
import zvg_constants as C
from zvg_scenario import Instance, make_instance


def de(x: float, digits: int = 1) -> str:
    """Zahl mit Dezimalkomma."""
    return f"{x:.{digits}f}".replace(".", ",")


@dataclass(frozen=True)
class Settings:
    n: int = C.DEFAULT_N
    family: int = C.DEFAULT_FAMILY
    seed: int = C.DEFAULT_SEED


@dataclass(frozen=True)
class Analysis:
    inst: Instance
    results: dict            # Ziel ("sum", "sumsq", "max") -> A.Result
    distinct: int            # Zahl verschiedener Pläne unter den drei Zielen
    plans_total: int | None  # n!, nur bei Aufzählung
    tie_size: int | None     # Optimalmenge des Maximums (vor der zweiten Regel), nur bei Aufzählung
    enumerated: bool


def analyse(settings: Settings) -> Analysis:
    inst = make_instance(settings.n, settings.family, settings.seed)
    results = {g: A.solve(inst, A.goal_p(g)) for g in C.GOALS}
    for r in results.values():
        assert A.check_feasible(r.plan, inst.n)
    enumerated = inst.n <= C.ENUM_MAX
    distinct = len({r.plan for r in results.values()})
    tie = int(len(A.optimal_set(inst.array(), math.inf))) if enumerated else None
    total = math.factorial(inst.n) if enumerated else None
    return Analysis(inst, results, distinct, total, tie, enumerated)


def p_rows(settings: Settings) -> list[dict]:
    """Optimum für Summe b^p, p = 1 bis unendlich: Plan, Summe, Quadratsumme, Maximum."""
    inst = make_instance(settings.n, settings.family, settings.seed)
    rows = []
    for p in C.P_VALUES:
        r = A.solve(inst, p)
        rows.append({"p": p, "plan": r.plan, "total": r.total, "squares": r.squares, "peak": r.peak})
    return rows


def frequency_rows(family: int, sizes=C.SWEEP_SIZES, seeds=C.SWEEP_SEEDS) -> list[dict]:
    """Je Instanzgröße über die festen Instanzen SWEEP_SEEDS (alle aufgezählt): wie oft ändert das Ziel den Plan?

    same_sq: das Quadrat-Optimum ist in der Summe so gut wie das Summen-Optimum; same_all: das gilt auch für das Maximum-Optimum;
    sq_worse_peak: das Quadrat-Optimum hat ein größeres Maximum als das Summen-Optimum; max_ties: das Maximum hat mehr als einen optimalen Plan;
    p_falls: die Summe des Optimums sinkt irgendwo mit wachsendem p (über C.P_VALUES)."""
    rows = []
    for n in sizes:
        same_sq = same_all = worse = ties = falls = 0
        for seed in seeds:
            inst = make_instance(n, family, seed)
            c = inst.array()
            s = A.enumerate_optimum(c, 1.0)
            q = A.enumerate_optimum(c, 2.0)
            m = A.enumerate_optimum(c, math.inf)
            eq_q = math.isclose(q.total, s.total, rel_tol=0.0, abs_tol=C.TOL)
            eq_m = math.isclose(m.total, s.total, rel_tol=0.0, abs_tol=C.TOL)
            same_sq += eq_q
            same_all += eq_q and eq_m
            worse += q.peak > s.peak + C.TOL
            ties += len(A.optimal_set(c, math.inf)) > 1
            totals = [A.enumerate_optimum(c, p).total for p in C.P_VALUES]
            falls += any(b < a - C.TOL for a, b in zip(totals, totals[1:]))
        rows.append({"n": n, "seeds": len(seeds), "same_sq": same_sq, "same_all": same_all, "sq_worse_peak": worse, "max_ties": ties, "p_falls": falls})
    return rows


def verdict_goals(a: Analysis) -> tuple[str, str]:
    """Kernfrage: Wandert das Optimum, wenn nur das Ziel wechselt?"""
    s, q, m = (a.results[g] for g in C.GOALS)
    if a.distinct == 1:
        return "info", (f"Alle drei Ziele wählen hier **denselben Plan** (Summe {de(s.total)}, Maximum {de(s.peak)}): bei dieser Instanz ist die Zielwahl egal.")
    if a.distinct == 3:
        return "success", (f"**Drei Ziele, drei Pläne.** Summe: {de(s.total)} (Maximum {de(s.peak)}), Quadratsumme: Summe {de(q.total)} (Maximum {de(q.peak)}), "
                           f"Maximum: Summe {de(m.total)} (Maximum {de(m.peak)}). Wer das Ziel wechselt, wechselt den Plan.")
    return "info", (f"Die drei Ziele wählen **zwei verschiedene Pläne**. Summe: {de(s.total)} (Maximum {de(s.peak)}), Quadratsumme: Summe {de(q.total)} "
                    f"(Maximum {de(q.peak)}), Maximum: Summe {de(m.total)} (Maximum {de(m.peak)}).")


def verdict_landscape(a: Analysis) -> tuple[str, str]:
    """Experiment Alle Pläne: wie groß ist die Optimalmenge beim Maximum?"""
    if not a.enumerated or a.plans_total is None or a.tie_size is None:
        return "info", f"Bei n = {a.inst.n} Personen gibt es zu viele Pläne zum Aufzählen (mehr als {C.ENUM_MAX}!); die drei Optima kommen aus den exakten Lösern."
    if a.tie_size == 1:
        return "info", (f"Von {a.plans_total} Plänen hat genau **einer** das kleinste Maximum {de(a.results['max'].peak)}: der Engpass-Plan ist eindeutig.")
    return "warning", (f"Von {a.plans_total} Plänen haben **{a.tie_size}** das kleinste Maximum {de(a.results['max'].peak)}: Das Maximum allein wählt nicht. "
                       f"Erst die zweite Regel (kleinste Summe) entscheidet; ohne sie wählte der Löser willkürlich.")


def verdict_p(rows: list[dict]) -> tuple[str, str]:
    """Experiment p-Regler: wie viele verschiedene Pläne, und steigt die Summe des Optimums monoton mit p?"""
    plans = len({r["plan"] for r in rows})
    totals = [r["total"] for r in rows]
    falls = any(b < a - C.TOL for a, b in zip(totals, totals[1:]))
    base = f"Über die getesteten Exponenten (Raster p = 1 bis ∞) gibt es **{plans}** verschiedene Optimalpläne."
    if falls:
        return "warning", base + " Die Summe des Optimums **sinkt** zwischen zwei benachbarten Exponenten des Rasters: Der „Preis“ des fairen Ziels wächst nicht gleichmäßig."
    return "info", base + " Die Summe des Optimums sinkt zwischen benachbarten Exponenten des Rasters nirgends."


def verdict_frequency(rows: list[dict]) -> tuple[str, str]:
    """Experiment Häufigkeit: wie oft wechselt das Ziel den Plan?"""
    parts = []
    for r in rows:
        parts.append(f"n = {r['n']}: Quadrat gleichwertig zur Summe in {r['same_sq']} von {r['seeds']}, alle drei gleichwertig in {r['same_all']}, "
                     f"Maximum nicht eindeutig in {r['max_ties']}, Quadrat mit größerem Maximum in {r['sq_worse_peak']}, Summe des Optimums sinkt mit p in {r['p_falls']}")
    kind = "warning" if max(r["sq_worse_peak"] for r in rows) > 0 or max(r["p_falls"] for r in rows) > 0 else "info"
    return kind, "Je " + str(rows[0]["seeds"]) + " feste Instanzen: " + "; ".join(parts) + "."
