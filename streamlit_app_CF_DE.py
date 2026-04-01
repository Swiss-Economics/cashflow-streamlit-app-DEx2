# streamlit_app.py
import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="DCF Annahmen Sandbox", layout="centered")

DISCOUNT_RATE = 0.20
LINE_COLOR = "#AF1A1D"  # RGB (175, 26, 29)

# ---------- Instructions ----------
st.markdown("""
### Verwendung dieses Tools
- Eines der vier Szenarien aus dem Dell-Fall kann im Dropdown-Menü ausgewählt werden.
- Die jährlichen Zahlungsströme können bei Bedarf in den Eingabefeldern angepasst werden.
- Das Diagramm wird automatisch auf Basis der Eingaben aktualisiert.
- Das Bewertungsergebnis wird automatisch berechnet und unterhalb des Diagramms angezeigt.
""")

# ---------- Preset scenarios ----------
SCENARIOS = {
    "Advisor Base": [2760, 3150, 3530, 3900, 4140],
    "Advisor Case 1": [3850, 3360, 3280, 3170, 2980],
    "Advisor Case 2": [3850, 3440, 3700, 4010, 3820],
    "Bank Base": [3850, 3610, 4540, 5690, 5500],
}

years = [1, 2, 3, 4, 5]

# ---------- Scenario selection ----------
st.subheader("Eingabe der Zahlungsströme")

selected_scenario = st.selectbox(
    "Wähle eine Entwicklung der Zahlungsströme",
    options=list(SCENARIOS.keys())
)

# Track previous scenario so values only reset when scenario changes
if "previous_scenario" not in st.session_state:
    st.session_state.previous_scenario = selected_scenario

# Initialize cash flow inputs on first load
if "cf_values" not in st.session_state:
    st.session_state.cf_values = SCENARIOS[selected_scenario].copy()

# If the user changes scenario, replace all five cash flows
if selected_scenario != st.session_state.previous_scenario:
    st.session_state.cf_values = SCENARIOS[selected_scenario].copy()
    st.session_state.previous_scenario = selected_scenario

# ---------- Manual inputs ----------
col1, col2 = st.columns(2)

with col1:
    st.session_state.cf_values[0] = st.number_input(
        "Zahlungsstrom Jahr 1 (Tsd. USD)",
        value=float(st.session_state.cf_values[0]),
        step=1.0,
        format="%.2f"
    )
    st.session_state.cf_values[1] = st.number_input(
        "Zahlungsstrom Jahr 2 (Tsd. USD)",
        value=float(st.session_state.cf_values[1]),
        step=1.0,
        format="%.2f"
    )
    st.session_state.cf_values[2] = st.number_input(
        "Zahlungsstrom Jahr 3 (Tsd. USD)",
        value=float(st.session_state.cf_values[2]),
        step=1.0,
        format="%.2f"
    )

with col2:
    st.session_state.cf_values[3] = st.number_input(
        "Zahlungsstrom Jahr 4 (Tsd. USD)",
        value=float(st.session_state.cf_values[3]),
        step=1.0,
        format="%.2f"
    )
    st.session_state.cf_values[4] = st.number_input(
        "Zahlungsstrom Jahr 5 (Tsd. USD)",
        value=float(st.session_state.cf_values[4]),
        step=1.0,
        format="%.2f"
    )

cash_flows = st.session_state.cf_values

# ---------- Data ----------
df = pd.DataFrame(
    {
        "Jahr": years,
        "Zahlungsströme": cash_flows,
    }
)

# ---------- Chart ----------
st.subheader("Verlauf der Zahlungsströme")

bars = (
    alt.Chart(df)
    .mark_bar(color=LINE_COLOR)
    .encode(
        x=alt.X("Jahr:O", title="Jahr", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("Zahlungsströme:Q", title="Zahlungsströme (Tsd. USD)"),
        tooltip=[
            alt.Tooltip("Jahr:O", title="Jahr"),
            alt.Tooltip("Zahlungsströme:Q", title="Zahlungsströme (Tsd. USD)", format=",.2f"),
        ],
    )
)

st.altair_chart(bars, use_container_width=True)

# ---------- Valuation ----------
present_values = [
    cf / ((1 + DISCOUNT_RATE) ** (year - 1))
    for cf, year in zip(cash_flows, years)
]

valuation = sum(present_values)

st.subheader("Bewertung")
st.metric("Bewertungsergebnis", f"USD {valuation:,.0f}k")
