import streamlit as st

input_parameters = st.query_params()
state_name = input_parameters.get("state", "Unknown state")

st.title(f"Exploring Privacy Laws for: {state_name}")