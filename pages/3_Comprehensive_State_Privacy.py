"""
This module creates and generates the state comprehensive laws page for the streamlit app
"""

import streamlit as st
from streamlit_pdf_viewer import pdf_viewer
import pandas as pd
from langchain.docstore.document import Document
from components.experimental_llm_manager import (
    load_faiss_index,
    get_conversational_chain,
    get_confirmation_result_chain,
    obtain_text_of_chunk,
    llm_simplify_chunk_text,
)


# List of US states.
us_states = [
    "Alabama",
    "Alaska",
    "Arizona",
    "Arkansas",
    "California",
    "Colorado",
    "Connecticut",
    "Delaware",
    "Florida",
    "Georgia",
    "Hawaii",
    "Idaho",
    "Illinois",
    "Indiana",
    "Iowa",
    "Kansas",
    "Kentucky",
    "Louisiana",
    "Maine",
    "Maryland",
    "Massachusetts",
    "Michigan",
    "Minnesota",
    "Mississippi",
    "Missouri",
    "Montana",
    "Nebraska",
    "Nevada",
    "New Hampshire",
    "New Jersey",
    "New Mexico",
    "New York",
    "North Carolina",
    "North Dakota",
    "Ohio",
    "Oklahoma",
    "Oregon",
    "Pennsylvania",
    "Rhode Island",
    "South Carolina",
    "South Dakota",
    "Tennessee",
    "Texas",
    "Utah",
    "Vermont",
    "Virginia",
    "Washington",
    "West Virginia",
    "Wisconsin",
    "Wyoming",
]

st.set_page_config(page_title="Privacy Laws Explorer", layout="wide")

styling_for_home_page = """
<style>
    [data-testid = "stAppViewContainer"]{
    background-color: #fefae0;
    opacity: 1;
    background-image:  radial-gradient(#ccd5ae 1.1000000000000001px, transparent 1.1000000000000001px), 
    radial-gradient(#ccd5ae 1.1000000000000001px, #fefae0 1.1000000000000001px);
    background-size: 56px 56px;
    background-position: 0 0,28px 28px;
    color: #000;
    }

[data-testid="stSidebar"] * {
    background-color: #dda15e;
    opacity: 1;
    color: #000 !important;
    font-weight: bold;
}

[data-testid = "stSidebarNav"] * {
    font-size: 18px;
    padding-bottom:5px;
    padding-top:5px;
}


[data-testid = "stExpander"] * {
    background-color: #eece9f;
    color: #000;
    font-weight: bold;
    font-size: 1.5 em;
}
</style>
"""


st.markdown(styling_for_home_page, unsafe_allow_html=True)

def main():
    empty_column, logo_column, title_column = st.columns([0.01,0.05,0.94], gap="small", vertical_alignment="bottom")
    with logo_column:
        st.image("images/law.png", width=75)
    with title_column:
        st.title("Explore Comprehensive State Privacy Laws")

    st.write("")
    st.write("")
    st.write("")
    content_column, image_column = st.columns([0.35,0.65])
    with content_column:
        st.subheader("Current state of Comprehensive Privacy Laws", divider = True)
        st.write("State-level privacy regulation has expanded considerably, with 19 comprehensive laws currently in "
        "effect per IAPP’s criteria. In 2024 alone, seven new laws were enacted, a significant rise from just 2 bills "
        "in 2018 and a peak of 59 bills in 2022–2023.")
        st.write("")
        st.write("An independent evaluation by EPIC of 14 state laws found that nearly half received failing grades, with none "
        "achieving the highest standards. This numerical and qualitative variability underscores the fragmented nature "
        "of state privacy protections and the pressing need for more uniform federal standards.")

        st.write("")
        st.write("")
        st.subheader("Level of Privacy Activity in the states", divider = True)
        st.image("images/comprehensive.png")
    with image_column:
        st.image("images/statetracker.png")

if __name__ == "__main__":
    main()
