"""
This module creates and generates the EU GDPR page for the streamlit app
"""

import streamlit as st
from streamlit_pdf_viewer import pdf_viewer
import pandas as pd
from langchain.docstore.document import Document


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
        st.image("./app/images/europe.png", width=75)
    with title_column:
        st.title("Explore the GDPR")

    st.write("")
    st.write("")
    st.write("")
    content_column, image_column = st.columns([0.35,0.65])
    with content_column:
        st.subheader("Overview of GDPR", divider = True)
        st.write("The General Data Protection Regulation (GDPR) is a comprehensive data protection law enacted by the "
        "European Union (EU) to safeguard individuals' personal data and regulate its free movement within the EU "
        "and European Economic Area (EEA). Adopted on April 14, 2016, and enforced from May 25, 2018, GDPR replaced "
        "the Data Protection Directive 95/46/EC, establishing uniform data protection rules across member states.")
        st.write("")

        st.write("")
        st.write("")
        st.subheader("Key Principles of GDPR", divider = True)
        # Creating a list for display
        list_of_GDPR_principles = ["Lawfulness, Fairness, and Transparency: Data must be processed legally, fairly, "
        "and transparently, ensuring individuals are informed about how their data is used.", "Purpose Limitation: "
        "Data should be collected for specified, explicit, and legitimate purposes and not processed in a manner "
        "incompatible with those purposes.", "Data Minimization: Only data necessary for the intended purpose should be "
        "collected and processed.", "Accuracy: Personal data must be accurate and kept up to date; inaccuracies "
        "should be corrected or deleted promptly.", "Storage Limitation: Data should not be kept longer than "
        "necessary for the purposes for which it is processed.", "Integrity and Confidentiality: Data must be processed "
        "securely to protect against unauthorized or unlawful processing, accidental loss, destruction, or damage.", 
        "Accountability: Data controllers are responsible for demonstrating compliance with these principles."]

        markdown_list = '\n'.join(f'- {item}' for item in list_of_GDPR_principles)

        st.markdown(markdown_list)

    with image_column:
        st.image("./app/images/gdpr.jpeg")

if __name__ == "__main__":
    main()
