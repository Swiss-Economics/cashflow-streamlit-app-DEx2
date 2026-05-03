import streamlit as st
import pandas as pd
import altair as alt

# Konfiguration im NZZ-Stil
st.set_page_config(page_title="DCF Annahmen Sandbox", layout="centered")

DISCOUNT_RATE = 0.20
NZZ_RED = "#AF1A1D" 

# ---------- Instructions ----------
st.markdown("""
### Verwendung dieses Tools
- Wählen Sie eines der Szenarien aus dem Dropdown-Menü aus.
- Die jährlichen Zahlungsströme können in den Feldern angepasst werden (**Angaben in Mio. Dollar**).
- Das Diagramm sowie das Bewertungsergebnis werden bei jeder Änderung automatisch aktualisiert.
""")

# ---------- Preset scenarios (in Mio. Dollar) ----------
SCENARIOS = {
    "Advisor Base": [2.76, 3.15, 3.53, 3.90, 4.14],
    "Advisor Case 1": [3.85, 3.36, 3.28, 3.17, 2.98],
    "Advisor Case 2": [3.85, 3.44, 3.70, 4.01, 3.82],
    "Bank Base": [3.85, 3.61, 4.54, 5.69, 5.50],
}

# ---------- Session State Management ----------
# Verhindert das Zurückspringen der Werte bei Klicks auf +/-
if "cf_values" not in st.session_state:
    st.session_state.cf_values = SCENARIOS["Advisor Base"].copy()

def update_scenario():
    """Wird nur aufgerufen, wenn das Szenario im Dropdown geändert wird."""
    st.session_state.cf_values = SCENARIOS[st.session_state.selected_scenario_key].copy()

# ---------- Scenario selection ----------
st.subheader("Eingabe der Zahlungsströme")

st.selectbox(
    "Wähle eine Entwicklung der Zahlungsströme",
    options=list(SCENARIOS.keys()),
    key="selected_scenario_key",
    on_change=update_scenario
)

# ---------- Manual inputs (In Mio. Dollar) ----------
col1, col2 = st.columns(2)

with col1:
    st.session_state.cf_values[0] = st.number_input(
        "Jahr 1 (in Mio. Dollar)",
        value=float(st.session_state.cf_values[0]),
        step=0.10,
        format="%.2f",
        key="year_1"
    )
    st.session_state.cf_values[1] = st.number_input(
        "Jahr 2 (in Mio. Dollar)",
        value=float(st.session_state.cf_values[1]),
        step=0.10,
        format="%.2f",
        key="year_2"
    )
    st.session_state.cf_values[2] = st.number_input(
        "Jahr 3 (in Mio. Dollar)",
        value=float(st.session_state.cf_values[2]),
        step=0.10,
        format="%.2f",
        key="year_3"
    )

with col2:
    st.session_state.cf_values[3] = st.number_input(
        "Jahr 4 (in Mio. Dollar)",
        value=float(st.session_state.cf_values[3]),
        step=0.10,
        format="%.2f",
        key="year_4"
    )
    st.session_state.cf_values[4] = st.number_input(
        "Jahr 5 (in Mio. Dollar)",
        value=float(st.session_state.cf_values[4]),
        step=0.10,
        format="%.2f",
        key="year_5"
    )

# ---------- Data Processing ----------
years = [1, 2, 3, 4, 5]
df = pd.DataFrame({
    "Jahr": years,
    "Zahlungsströme": st.session_state.cf_values
})

# ---------- Chart (Altair) ----------
st.subheader("Verlauf der Zahlungsströme")

bars = (
    alt.Chart(df)
    .mark_bar(color=NZZ_RED)
    .encode(
        x=alt.X("Jahr:O", title="Jahr", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("Zahlungsströme:Q", title="Zahlungsströme (in Mio. Dollar)"),
        tooltip=[
            alt.Tooltip("Jahr:O", title="Jahr"),
            alt.Tooltip("Zahlungsströme:Q", title="Mio. Dollar", format=".2f"),
        ],
    )
    .properties(height=350)
)

st.altair_chart(bars, use_container_width=True)

# ---------- Valuation Logic ----------
present_values = [
    cf / ((1 + DISCOUNT_RATE) ** (year - 1))
    for cf, year in zip(st.session_state.cf_values, years)
]
valuation_mio = sum(present_values)

# ---------- Display Result ----------
st.subheader("Bewertung")

# Schweizer Standard für Währungen im Finanzkontext: USD [Zahl].[Dezimal]
st.metric("Unternehmenswert", f"USD {valuation_mio:.2f} Mio.")

# Kleine Fussnote im NZZ-Stil
st.caption(f"Basis der Berechnung: Diskontsatz von {int(DISCOUNT_RATE*100)}%. Alle Beträge in Mio. Dollar.")
