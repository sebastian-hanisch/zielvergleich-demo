"""PDF-Export des aktuellen Ergebnisses (fpdf2). Kernschriften sind latin-1: Umlaute gehen, Sonderzeichen werden ersetzt."""

from __future__ import annotations

from fpdf import FPDF

import zvg_constants as C
from zvg_evaluation import Analysis, Settings, de

_REPLACE = {"→": "->", "–": "-", "—": "-", "−": "-", "≤": "<=", "≥": ">=", "·": "*", "×": "x", "Δ": "Delta", "↔": "<->", "„": '"', "“": '"', "²": "2", "∞": "unendlich"}


def _s(text) -> str:
    out = str(text).replace("**", "").replace("`", "")
    for old, new in _REPLACE.items():
        out = out.replace(old, new)
    return out.encode("latin-1", "replace").decode("latin-1")


def build_pdf(s: Settings, a: Analysis) -> bytes:
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 9, _s("Dasselbe Problem, drei Ziele"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5, _s(f"{s.n} Personen, {s.n} Aufgaben, Familie: {C.FAMILIES[s.family]}, Seed {s.seed}. Alles simuliert."), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    widths = (40, 40, 35, 35, 35)
    head = ("Ziel", "Plan (Person -> Aufgabe)", "Summe", "Quadratsumme", "Maximum")
    pdf.set_font("Helvetica", "B", 9)
    for w, h in zip(widths, head):
        pdf.cell(w, 6, _s(h), border=1)
    pdf.ln()
    pdf.set_font("Helvetica", "", 9)
    for g in C.GOALS:
        r = a.results[g]
        plan = ", ".join(f"{i + 1}->{j + 1}" for i, j in enumerate(r.plan)) if s.n <= 8 else "(zu lang)"
        for w, v in zip(widths, (C.GOAL_NAMES[g], plan, de(r.total), de(r.squares), de(r.peak))):
            pdf.cell(w, 5.5, _s(v), border=1)
        pdf.ln()
    pdf.ln(3)
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(0, 4, _s("Gleichstandsregel beim Maximum: erst kleinstes Maximum, dann kleinste Summe. Quelle: zielvergleich-demo, Sebastian Hanisch."), new_x="LMARGIN", new_y="NEXT")
    return bytes(pdf.output())
