import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="DCF Annahmen Sandbox", layout="centered")

DISCOUNT_RATE = 0.20
NZZ_RED = "#AF1A1D" 

# ---------- Instructions ----------
st.markdown("""
### Verwendung dieses Tools
- Wählen Sie eines der Szenarien aus dem Dropdown-Menü.
- Die jährlichen Zahlungsströme können in den Feldern angepasst werden (**Angaben in Mio. Dollar**).
- Das Diagramm und das Bewertungsergebnis werden automatisch aktualisiert.
""")

# ---------- Preset scenarios (umgerechnet in Mio.) ----------
SCENARIOS = {
    "Advisor Base": [2.76, 3.15, 3.53, 3.90, 4.14],
    "Advisor Case 1": [3.85, 3.36, 3.28, 3.17, 2.98],
    "Advisor Case 2": [3.85, 3.44, 3.70, 4.01, 3.82],
    "Bank Base": [3.85, 3.61, 4.54, 5.69, 5.50],
}

years = [1, 2, 3, 4, 5]

# ---------- Scenario selection ----------
st.subheader("Eingabe der Zahlungsströme")

selected_scenario = st.selectbox(
    "Wähle eine Entwicklung der Zahlungsströme",
    options=list(SCENARIOS.keys())
)

if "cf_values" not in st.session_state or "previous_scenario" not in st.session_state or selected_scenario != st.session_state.previous_scenario:
    st.session_state.cf_values = SCENARIOS[selected_scenario].copy()
    st.session_state.previous_scenario = selected_scenario

# ---------- Manual inputs (In Mio. Dollar) ----------
col1, col2 = st.columns(2)

with col1:
    for i in range(3):
        st.session_state.cf_values[i] = st.number_input(
            f"Jahr {i+1} (in Mio. Dollar)",
            value=float(st.session_state.cf_values[i]),
            step=0.1,
            format="%.2f"
        )

with col2:
    for i in range(3, 5):
        st.session_state.cf_values[i] = st.number_input(
            f"Jahr {i+1} (in Mio. Dollar)",
            value=float(st.session_state.cf_values[i]),
            step=0.1,
            format="%.2f"
        )

cash_flows = st.session_state.cf_values
df = pd.DataFrame({"Jahr": years, "Zahlungsströme": cash_flows})

# ---------- Chart ----------
st.subheader("Verlauf der Zahlungsströme")

bars = (
    alt.Chart(df)
    .mark_bar(color=NZZ_RED)
    .encode(
        x=alt.X("Jahr:O", title="Jahr", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("Zahlungsströme:Q", title="Zahlungsströme (in Mio. Dollar)"),
        tooltip=[
            alt.Tooltip("Jahr:O", title="Jahr"),
            alt.Tooltip("Zahlungsströme:Q", title="Betrag (Mio. Dollar)", format=".2f"),
        ],
    )
)
st.altair_chart(bars, use_container_width=True)

# ---------- Valuation ----------
present_values = [cf / ((1 + DISCOUNT_RATE) ** (year - 1)) for cf, year in zip(cash_flows, years)]
valuation_mio = sum(present_values)

st.subheader("Bewertung")

# Schweizer NZZ-Standard für Währungsbeträge: Punkt als Dezimaltrenner
st.metric("Unternehmenswert", f"USD {valuation_mio:.2f} Mio.")
