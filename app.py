"""Dasselbe Problem, drei Ziele - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück 1 der Reihe „Zielfunktionsdesign“: n Personen, n Aufgaben, Belastung je Paar. Summe, Quadratsumme und Maximum der Belastungen
wählen verschiedene Pläne; alle Pläne werden bis n = 8 aufgezählt, darüber rechnen die Ungarische Methode und ein Engpassverfahren exakt.

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import zvg_algorithm as A
import zvg_constants as C
from zvg_evaluation import (
    Settings,
    analyse,
    de,
    frequency_rows,
    p_rows,
    verdict_frequency,
    verdict_goals,
    verdict_landscape,
    verdict_p,
)
from zvg_layout import dunkles_design, kopf_css
from zvg_pdf_export import build_pdf
from zvg_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from zvg_scenario import make_instance
from zvg_visualization import build_frequency, build_goal_bars, build_landscape, build_matrix, build_p_lines, p_label

st.set_page_config(page_title="Dasselbe Problem, drei Ziele – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner=False)
def _landscape(settings):
    return A.landscape(make_instance(settings.n, settings.family, settings.seed).array())


@st.cache_data(show_spinner=False)
def _p_rows(settings):
    return p_rows(settings)


@st.cache_data(show_spinner=False)
def _frequency(family):
    return frequency_rows(family)


def _plan_text(r, n):
    return ", ".join(f"P{i + 1}→A{j + 1}" for i, j in enumerate(r.plan)) if n <= 12 else "siehe Diagramm"


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in zvg_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🧩 Dasselbe Problem, drei Ziele")
st.markdown(
    """
**Ein Ziel ist keine Nebensache.** Hier steht dieselbe Aufgabe vor jedem Ziel: **n Personen** übernehmen **n Aufgaben**, jede Paarung hat eine Belastung.
Drei Ziele sehen denselben Plan unterschiedlich an: die **Summe** der Belastungen, die **Quadratsumme** (Ausreißer zählen mehr) und das **Maximum** (nur der Schwerste zählt).
Dieselbe Instanz, derselbe Löser, nur das Ziel wechselt: Wie oft wechselt dann der Plan, und woran hängt es?

Weiter unten: **🔬 Alle Pläne**, **🔬 Der p-Regler**, **🔬 Wie oft wechselt das Ziel den Plan?**, **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So funktioniert der Vergleich der Ziele", expanded=True):
    st.markdown(
        """
1. **Ein Plan** ordnet jeder Person genau eine Aufgabe zu und ergibt für jede Person eine **Belastung**; zusammen den Vektor der Belastungen.
2. **Ein Ziel** macht aus dem Belastungsvektor **eine Zahl**: Summe, Quadratsumme oder Maximum. Der Optimierer wählt den Plan mit der kleinsten Zahl.
3. **Gleichstände:** Beim Maximum gibt es oft viele gleich gute Pläne, weil nur ein einziger Eintrag zählt. Die Demo wählt dann den mit der **kleinsten Summe** (erst Maximum, dann Summe); sonst wäre die Wahl willkürlich.
4. **Warum das zählt:** Der Plan ist nicht „die“ beste Lösung, sondern die beste unter einem Ziel. Wer das Ziel ändert, ändert die Lösung, und manchmal kaum, manchmal stark.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Instanz**")
    n = st.slider("Personen und Aufgaben n", *bounds("n_slider"), key="n_slider", help=f"Bis n = {C.ENUM_MAX} werden alle Pläne aufgezählt; darüber rechnen exakte Löser.")
    family = st.selectbox("Art der Belastungen", [0, 1, 2], key="family_select", format_func=lambda i: C.FAMILIES[i],
                          help="Ganze Zahlen haben viele Gleichstände; „Mit Personeneffekt“: manche Personen sind systematisch stärker belastet.")
    seed = st.number_input("Zufalls-Seed der Instanz", *bounds("seed_input"), key="seed_input", step=1)
    st.button("🎲 Neue Instanz generieren", width="stretch", on_click=randomize_seed)

sync_query_params({"n_slider": int(n), "family_select": int(family), "seed_input": int(seed)})

settings = Settings(int(n), int(family), int(seed))
a = _analysis(settings)

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis: drei Ziele, drei Pläne")
s_res, q_res, m_res = (a.results[g] for g in C.GOALS)
m1, m2, m3 = st.columns(3)
# Delta immer als „mein Wert minus Referenz“; die Farbe regelt delta_color="inverse" (Vorzeichen-Falle, DEMO-PLAYBOOK §2).
m1.metric("Summe im Summen-Plan (kleinstmöglich)", de(s_res.total), delta="Referenz", delta_color="off")
m2.metric("Summe im Maximum-Plan", de(m_res.total), delta=f"{m_res.total - s_res.total:+.1f} gegen Summen-Plan".replace(".", ","), delta_color="inverse")
m3.metric("Maximum im Maximum-Plan", de(m_res.peak), delta=f"{m_res.peak - s_res.peak:+.1f} gegen Summen-Plan".replace(".", ","), delta_color="inverse")

rows_md = ["| Ziel | Plan (Person → Aufgabe) | Summe | Quadratsumme | Maximum |", "|---|---|---|---|---|"]
for g in C.GOALS:
    r = a.results[g]
    rows_md.append(f"| **{C.GOAL_NAMES[g]}** | {_plan_text(r, a.inst.n)} | {de(r.total)} | {de(r.squares)} | {de(r.peak)} |")
st.markdown("\n".join(rows_md))
st.caption("Jede Zeile ist das Optimum unter ihrem Ziel: In der Spalte des eigenen Ziels steht der kleinste Wert. Maximum: erst kleinstes Maximum, dann kleinste Summe.")

st.plotly_chart(build_matrix(a.inst, a.results), width="stretch", key="matrix_chart")
st.caption("Belastungsmatrix (Zeile Person, Spalte Aufgabe); Marken: Kreis Summe, Quadrat Quadratsumme, Raute Maximum. Je dunkler die Zelle, desto größer die Belastung.")
st.plotly_chart(build_goal_bars(a.inst, a.results), width="stretch", key="bars_chart")
st.caption("Belastung je Person unter den drei Plänen; die gepunktete Linie zeigt das Maximum des jeweiligen Plans.")
st.download_button("📄 Ergebnis als PDF", data=build_pdf(settings, a), file_name="zielvergleich.pdf", mime="application/pdf", key="pdf_download")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Wandert das Optimum, wenn nur das Ziel wechselt?")
kind, text = verdict_goals(a)
getattr(st, kind)(text)

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Alle Pläne: Summe gegen Maximum")
if a.enumerated:
    sums, maxes = _landscape(settings)
    st.plotly_chart(build_landscape(sums, maxes, a.results), width="stretch", key="landscape_chart")
    st.caption(f"Jeder Punkt ist einer der {a.plans_total} Pläne. Links unten ist besser. Beim Maximum liegen viele Pläne auf derselben Höhe: die Optimalmenge.")
else:
    st.info(f"Bei n = {a.inst.n} gibt es zu viele Pläne zum Aufzählen (mehr als {C.ENUM_MAX}!). Die Optima rechnen die Ungarische Methode (Summe, Quadratsumme) und ein Engpassverfahren (Maximum) exakt.")
kind, text = verdict_landscape(a)
getattr(st, kind)(text)

st.markdown("---")

st.subheader("🔬 Der p-Regler: von der Summe zum Maximum")
st.caption("Ziel: Summe der Belastungen hoch p. p = 1 ist die Summe, p = 2 die Quadratsumme, p → ∞ das Maximum. Die Optima werden für jedes p neu gerechnet.")
p_options = [p_label(p) for p in C.P_VALUES]
p_choice = st.select_slider("Exponent p", options=p_options, value="2", key="p_slider")
rows_p = _p_rows(settings)
row = rows_p[p_options.index(p_choice)]
c1, c2 = st.columns(2)
c1.metric("Summe des Optimums", de(row["total"]))
c2.metric("Maximum des Optimums", de(row["peak"]))
st.caption("Plan: " + (", ".join(f"P{i + 1}→A{j + 1}" for i, j in enumerate(row["plan"])) if a.inst.n <= 12 else "siehe Verlauf"))
st.plotly_chart(build_p_lines(rows_p), width="stretch", key="p_chart")
kind, text = verdict_p(rows_p)
getattr(st, kind)(text)

st.markdown("---")

st.subheader("🔬 Wie oft wechselt das Ziel den Plan?")
st.caption(f"Je {len(C.SWEEP_SEEDS)} feste Instanzen (SWEEP_SEEDS) der gewählten Art, alle Pläne aufgezählt; die Zahlen sind Anzahlen von Instanzen, kein Satz.")
freq = _frequency(settings.family)
st.plotly_chart(build_frequency(freq), width="stretch", key="freq_chart")
kind, text = verdict_frequency(freq)
getattr(st, kind)(text)

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Die Belastungen sind bekannt und gelten je Paar unabhängig** | Wechselwirkungen (zwei Aufgaben beim selben Kunden) oder Schätzfehler machen aus dem „Optimum“ eine Näherung | Optimierung unter Unsicherheit |
| **Die Gleichstandsregel ist gesetzt** | Ohne sie wählt der Löser beim Maximum willkürlich; die Folgen für den „Preis“ eines fairen Ziels zeigt Stück 5 | Stück 2 (Preis der Fairness), Stück 5 (Gleichstände) |
| **Das Ziel ist gegeben** | Welches Ziel gelten soll, ist eine Entscheidung und kein Rechenergebnis; die Demo zeigt nur, was sie ändert | alle folgenden Stücke der Reihe |
| **Alle Pläne sind zulässig** | Mindestbesetzung, Qualifikation und Obergrenzen fehlen; sie ändern die Optima | Stück 6 (hart gegen weich) |
| **Aufgezählt wird nur bis n = 8** | Darüber gilt nur die Aussage der exakten Löser, nicht das Bild aller Pläne | – |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Problem.** Gegeben $n$ Personen, $n$ Aufgaben und Belastungen $c_{ij} \ge 0$. Ein Plan ist eine Permutation $\pi$; Person $i$ trägt $b_i = c_{i,\pi(i)}$.

**Ziele.** Summe $\sum_i b_i$, Quadratsumme $\sum_i b_i^2$, Maximum $\max_i b_i$, allgemein $\sum_i b_i^p$ mit $p \ge 1$; für $p \to \infty$ wird aus $\left(\sum_i b_i^p\right)^{1/p}$ das Maximum.

**Lösung.** Bis $n = 8$ werden alle $n!$ Pläne aufgezählt. Darüber löst die Ungarische Methode (`scipy.optimize.linear_sum_assignment`) die Zuordnung mit den Kosten $c_{ij}^p$ exakt, weil $\sum_i b_i^p$ trennbar ist. Das Maximum löst eine Schwellwertsuche: die kleinste Schwelle $t$, bei der die Kanten mit $c_{ij} \le t$ ein perfektes Matching enthalten; unter allen Plänen mit diesem Maximum minimiert eine zweite Zuordnung die Summe (lexikographisch: erst Maximum, dann Summe).

**Gleichstände.** Summe und Quadratsumme (aufgezählt): kleinster Plan in der Reihenfolge von `itertools.permutations`; Maximum: kleinstes Maximum, dann kleinste Summe, dann kleinster Plan.

**Literatur.** Keine Aussage dieser Demo stützt sich auf Literatur; alle Zahlen sind Messungen an den Instanzfamilien der Demo. Rechenverfahren: Ungarische Methode (Kuhn, 1955; hier nicht an der Quelle geprüft).
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
