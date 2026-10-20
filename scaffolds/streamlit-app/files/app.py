"""Streamlit entry point: layout only. Computation lives in the package and is tested there."""
import streamlit as st

from {{package}}.data import summarise

st.title({{purpose_json}})
rows = [{"barn": "A", "deaths": 2}, {"barn": "B", "deaths": 1}, {"barn": "A", "deaths": 1}]
st.table(summarise(rows, by="barn", value="deaths"))
