"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import math

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import zvg_constants as C

TEXT_MAX_N = 10    # bis hierher stehen die Zahlen in den Zellen der Matrix
SYMBOLS = {"sum": "circle", "sumsq": "square", "max": "diamond"}


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=360):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=-0.2), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def p_label(p: float) -> str:
    return "∞" if math.isinf(p) else (str(int(p)) if float(p).is_integer() else str(p).replace(".", ","))


def build_matrix(inst, results):
    """Belastungsmatrix als Heatmap (Zeile Person, Spalte Aufgabe); die drei gewählten Pläne als Marken (Kreis Summe, Quadrat Quadratsumme, Raute Maximum)."""
    n = inst.n
    fig = go.Figure(go.Heatmap(z=[list(row) for row in inst.c], x=list(range(1, n + 1)), y=list(range(1, n + 1)), colorscale="Blues", showscale=False,
                               text=[[f"{v:.0f}" for v in row] for row in inst.c] if n <= TEXT_MAX_N else None,
                               texttemplate="%{text}" if n <= TEXT_MAX_N else None, hovertemplate="Person %{y}, Aufgabe %{x}: %{z:.1f}<extra></extra>"))
    offsets = {"sum": -0.22, "sumsq": 0.0, "max": 0.22}
    for g in C.GOALS:
        plan = results[g].plan
        fig.add_trace(go.Scatter(x=[j + 1 + (offsets[g] if n <= TEXT_MAX_N else 0) for j in plan], y=[i + 1 for i in range(n)], mode="markers",
                                 marker=dict(symbol=SYMBOLS[g], size=14 if n <= TEXT_MAX_N else 7, color=C.GOAL_COLORS[g], line=dict(width=1, color="white")),
                                 name=C.GOAL_NAMES[g], hovertemplate=C.GOAL_NAMES[g] + ": Person %{y} → Aufgabe %{x}<extra></extra>"))
    fig.update_xaxes(title_text="Aufgabe", dtick=1 if n <= 20 else None, side="top")
    fig.update_yaxes(title_text="Person", autorange="reversed", dtick=1 if n <= 20 else None)
    return _base(fig, height=420 if n <= TEXT_MAX_N else 520)


def build_goal_bars(inst, results):
    """Belastung je Person unter den drei Plänen; gleiche Achse, damit die Balken vergleichbar sind."""
    n = inst.n
    top = max(max(r.burdens) for r in results.values()) * 1.1
    fig = make_subplots(rows=1, cols=3, shared_yaxes=True, subplot_titles=[C.GOAL_NAMES[g] for g in C.GOALS])
    labels = [f"P{i + 1}" for i in range(n)]
    for col, g in enumerate(C.GOALS, start=1):
        r = results[g]
        fig.add_trace(go.Bar(x=labels, y=list(r.burdens), marker_color=C.GOAL_COLORS[g], name=C.GOAL_NAMES[g], showlegend=False,
                             hovertemplate="%{x}: %{y:.1f}<extra></extra>"), row=1, col=col)
        fig.add_hline(y=r.peak, line=dict(color="rgba(0,0,0,0.45)", dash="dot", width=1), row=1, col=col)
    fig.update_yaxes(range=[0, top], title_text="Belastung", row=1, col=1)
    fig.update_xaxes(showticklabels=n <= 20)
    return _base(fig, height=340)


def build_landscape(sums, maxes, results):
    """Alle Pläne als Punkte (Summe gegen Maximum); die drei Optima hervorgehoben."""
    fig = go.Figure(go.Scattergl(x=list(map(float, sums)), y=list(map(float, maxes)), mode="markers", marker=dict(size=4, color=C.COLOR_OTHER), name="alle Pläne",
                                 hovertemplate="Summe %{x:.1f}, Maximum %{y:.1f}<extra></extra>"))
    for g in C.GOALS:
        r = results[g]
        fig.add_trace(go.Scatter(x=[r.total], y=[r.peak], mode="markers", marker=dict(symbol=SYMBOLS[g], size=14, color=C.GOAL_COLORS[g], line=dict(width=1, color="white")),
                                 name=C.GOAL_NAMES[g] + "-Optimum", hovertemplate=C.GOAL_NAMES[g] + ": Summe %{x:.1f}, Maximum %{y:.1f}<extra></extra>"))
    fig.update_xaxes(title_text="Summe der Belastungen")
    fig.update_yaxes(title_text="Maximum der Belastungen")
    return _base(fig, height=400)


def build_p_lines(rows):
    """Summe und Maximum des Optimums von Summe b^p über p (Text-Achse, damit ∞ und 1,5 gleich breit stehen)."""
    xs = [p_label(r["p"]) for r in rows]
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Summe des Optimums", "Maximum des Optimums"))
    fig.add_trace(go.Scatter(x=xs, y=[r["total"] for r in rows], mode="lines+markers", line=dict(color=C.COLOR_SUM, width=3), name="Summe", showlegend=False,
                             hovertemplate="p = %{x}: %{y:.1f}<extra></extra>"), row=1, col=1)
    fig.add_trace(go.Scatter(x=xs, y=[r["peak"] for r in rows], mode="lines+markers", line=dict(color=C.COLOR_MAX, width=3), name="Maximum", showlegend=False,
                             hovertemplate="p = %{x}: %{y:.1f}<extra></extra>"), row=1, col=2)
    fig.update_xaxes(title_text="p", type="category")
    return _base(fig, height=320)


def build_frequency(rows):
    """Je Instanzgröße: in wie vielen der festen Instanzen tritt der Fall ein (Anzahl, nicht Anteil)."""
    xs = [f"n = {r['n']}" for r in rows]
    spec = (("same_sq", "Quadrat gleichwertig zur Summe", C.COLOR_SUMSQ), ("same_all", "alle drei gleichwertig", C.COLOR_SUM),
            ("max_ties", "Maximum nicht eindeutig", C.COLOR_MAX), ("sq_worse_peak", "Quadrat mit größerem Maximum", "rgba(120,120,120,0.9)"),
            ("p_falls", "Summe sinkt mit p", "rgba(230,160,40,0.95)"))
    fig = go.Figure([go.Bar(x=xs, y=[r[k] for r in rows], name=label, marker_color=color, hovertemplate=label + ": %{y}<extra></extra>") for k, label, color in spec])
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text=f"Instanzen von {rows[0]['seeds']}", range=[0, rows[0]["seeds"]])
    return _base(fig)
