# pylint: disable=invalid-name
# pylint: disable=duplicate-code
# the above line is used to disable the invalid-name error for the file name.
# Capital letters needed as Streamlit inherits case for page name from file name
# Duplicate code being used for styling of streamlit file
"""
This module creates and generates the state comprehensive laws page for the streamlit app
"""

import streamlit as st

st.set_page_config(page_title="Privacy Laws Explorer", layout="wide")

STYLING_FOR_FEDERAL_PAGE = """
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


st.markdown(STYLING_FOR_FEDERAL_PAGE, unsafe_allow_html=True)


def main():
    """
    This function runs the federal privacy laws page.
    """
    st.session_state.reset_state_page = True
    _, logo_column, title_column = st.columns(
        [0.01, 0.05, 0.94], gap="small", vertical_alignment="bottom"
    )
    with logo_column:
        st.image("./app/images/federal.png", width=75)
    with title_column:
        st.title("Explore Federal Privacy Laws")

    st.write("")
    st.write("")
    st.write("")
    content_column, image_column = st.columns([0.35, 0.65])
    with content_column:
        st.subheader("The main message on Federal Privacy Laws", divider=True)
        st.write(
            """Federal bills cover almost every corner of privacy—from consumer
rights, workplace and health data, to financial, children’s, and even governmental
privacy obligations. This segmentation shows that lawmakers are trying to tackle every
issue separately rather than unifying them under one umbrella."""
        )
        st.write("")
        st.write(
            """Heading into 2025, comprehensive federal privacy and AI regulations seem
stalled as post-election shifts favor other priorities. Persistent splits over private rights,
federal preemption, and civil rights—with leaders leaning toward innovation—have left both privacy 
and AI policies in limbo. Meanwhile, the FTC is expected to pivot under new leadership,
even as state legislatures push ahead with their own privacy reforms, especially in health care."""
        )

        st.subheader("The crucial ongoing debate", divider=True)
        st.write(
            """One of the hottest debates is whether a federal law should override the diverse
state laws or simply set a floor for minimum standards. Some proposals preempt state
laws, while others are designed to coexist with them—highlighting a fundamental
disagreement on how to streamline privacy protections."""
        )
        st.write("")

        st.subheader("Emerging Technology and Data Practices", divider=True)
        st.write(
            """There’s a clear focus on modern challenges—data minimization, privacy by
design, algorithmic accountability, and issues around emerging tech like facial
recognition and biometric data. These proposals reflect the need to catch up with
fast-evolving technologies."""
        )
    with image_column:
        _, main_image_column, _ = st.columns([0.2, 0.6, 0.2])
        with main_image_column:
            st.image("./app/images/federallaws.webp")


if __name__ == "__main__":
    main()
