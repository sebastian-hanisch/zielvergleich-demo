"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets."""

import math

N_MIN, N_MAX, DEFAULT_N = 3, 200, 4
ENUM_MAX = 8                                  # bis hierher werden alle n! Pläne aufgezählt (n = 9 nur als Messwert im README)
SEED_MAX, DEFAULT_SEED = 999999, 358          # Seed 358 mit ganzen Zahlen und n = 4: das Handbeispiel
FAMILIES = ("Ganze Zahlen 1 bis 9", "Gleichverteilt 0 bis 100", "Mit Personeneffekt")
FAMILY_KEYS = ("int", "real", "person")
DEFAULT_FAMILY = 0
SWEEP_SEEDS = tuple(range(100000, 100020))    # feste Instanzen für alle Sweeps: nie ein einzelner Seed als Befund
SWEEP_SIZES = (4, 6, 8)                       # Instanzgrößen des Häufigkeits-Experiments (alle aufgezählt)
P_VALUES = (1.0, 1.5, 2.0, 3.0, 5.0, 10.0, math.inf)
GOALS = ("sum", "sumsq", "max")
GOAL_NAMES = {"sum": "Summe", "sumsq": "Quadratsumme", "max": "Maximum"}
TOL = 1e-9                                    # Gleichstände beim Maximum und bei der Summe: absolut
REL_TOL = 1e-12                               # Gleichstände bei Potenzsummen: relativ

COLOR_SUM = "#2F6B65"
COLOR_SUMSQ = "#4c78a8"
COLOR_MAX = "#c0504d"
COLOR_OTHER = "rgba(150,150,150,0.35)"
GOAL_COLORS = {"sum": COLOR_SUM, "sumsq": COLOR_SUMSQ, "max": COLOR_MAX}

PRESETS = {
    "Handbeispiel (n = 4, ganze Zahlen)": {"n": 4, "family": 0, "seed": 358},
    "Alle Ziele einig": {"n": 5, "family": 1, "seed": 0},
    "Gleichstand beim Maximum": {"n": 6, "family": 0, "seed": 175},
    "Quadrat verschlechtert das Maximum": {"n": 6, "family": 1, "seed": 108},
    "Viele Personen (n = 60)": {"n": 60, "family": 2, "seed": 3},
}
PRESET_HELP = {
    "Handbeispiel (n = 4, ganze Zahlen)": "Vier Personen, vier Aufgaben: Summe, Quadratsumme und Maximum wählen drei verschiedene Pläne.",
    "Alle Ziele einig": "Eine Instanz, in der alle drei Ziele denselben Plan wählen: hier ist die Zielwahl egal.",
    "Gleichstand beim Maximum": "Beim Maximum gibt es viele gleich gute Pläne; erst das zweite Ziel (die Summe) entscheidet.",
    "Quadrat verschlechtert das Maximum": "Ein seltener Fall: Das Quadrat-Optimum hat ein größeres Maximum als das Summen-Optimum.",
    "Viele Personen (n = 60)": "Zu groß zum Aufzählen: Ungarische Methode und Engpassverfahren rechnen die drei Optima exakt.",
}
