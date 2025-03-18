import datetime
import streamlit as st
import tempfile

# List of US states for the dropdown
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

sector_list = [
    "Health",
    "Education",
    "Finance",
    "Telecommunications & Technology",
    "Government & Public Sector",
    "Retail & E-Commerce",
    "Employment & HR",
    "Media & Advertising",
    "Critical Infrastructure (Energy, Transportation, etc.)",
    "Children’s Data Protection",
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

[data-testid = "stRadio"] * {
    color: #083b72;
    font-weight:bold;
}

[data-testid = "stCaptionContainer"] * {
    color: #111;
}
</style>
"""

st.markdown(styling_for_home_page, unsafe_allow_html=True)


def main():
    st.session_state.reset_state_page = True
    empty_column, logo_column, title_column = st.columns(
        [0.01, 0.05, 0.94], gap="small", vertical_alignment="bottom"
    )
    with logo_column:
        st.image("./app/images/add.png", width=75)
    with title_column:
        st.title("Add a Document to our Database of Laws")

    st.write("")
    st.write("")
    st.write("")

    input_1, input_2, input_3, input_4 = st.columns([0.25, 0.25, 0.25, 0.25])
    with input_1:
        st.subheader("Select the type of law", divider=True)
        level_of_law = st.radio(
            "",
            [
                "State-level sectoral",
                "State-level Comprehensive",
                "Federal level",
                "GDPR",
            ],
            captions=[
                "Choose if the law is a state law focusing on one specific issue",
                "Choose if the law is a state law focusing on a broad set of issues",
                "Choose if the federal government created this law",
                "Choose if your law is related to EU's GDPR",
            ],
            index=None,
        )
        st.write("")
        st.write("Type of law selection:", level_of_law)

    with input_2:
        st.subheader("Enter sector of this law / NA", divider=True)
        sector = st.selectbox(
            "Select a state to explore their privacy law", sector_list, index=None
        )
        st.write("")
        st.write("State selection:", sector)

    with input_3:
        st.subheader("Enter relevant US state / NA", divider=True)
        selected_state = st.selectbox(
            "Select a state to explore their privacy law", us_states, index=None
        )
        st.write("")
        st.write("State selection:", selected_state)

    with input_4:
        st.subheader("Date of law taking effect", divider=True)
        effective_date = st.date_input("When did this law take effect?", value=None)
        st.write("")
        st.write("Date entered:", effective_date)

    st.write("")
    st.write("")
    st.write("")
    empty_col, button_col, empty_col2 = st.columns([0.25, 0.5, 0.25])
    with button_col:
        if button_col.button(
            "Validate and Submit Inputs",
            type="primary",
            use_container_width=True,
            icon=":material/place_item:",
        ):
            button_col.markdown("Clicked the button")


if __name__ == "__main__":
    main()
