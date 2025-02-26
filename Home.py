import streamlit as st
from components.map import map_generator

st.set_page_config(page_title="Privacy Laws Explorer", layout="wide")

page_background = """
<style>
    [data-testid = "stAppViewContainer"]{
    background-color: #0D2243;
    opacity: 1;
    background-image:  radial-gradient(#00FFA3 1.4000000000000001px, transparent 1.4000000000000001px), radial-gradient(#00FFA3 1.4000000000000001px, #0D2243 1.4000000000000001px);
    background-size: 56px 56px;
    background-position: 0 0,28px 28px;
    }
</style>
"""

sidebar_background = """
<style>
[data-testid="stSidebarContent"] * {
    background-color: #EDAFB8;
    opacity: 1;
    color: #111 !important;
    font-weight: bold;
}
</style>
"""


st.markdown(page_background, unsafe_allow_html=True)
st.markdown(sidebar_background, unsafe_allow_html=True)

us_states = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
    "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
    "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana",
    "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi",
    "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey",
    "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio",
    "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina",
    "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia",
    "Washington", "West Virginia", "Wisconsin", "Wyoming"
]

privacy_topics = [
    "Financial Privacy",
    "Health Data Privacy",
    "Digital Privacy",
    "Internet Privacy",
    "Location Privacy",
    "Workplace Privacy",
    "Social Media Privacy",
    "Consumer Privacy",
    "Biometric Privacy",
    "Government Surveillance"
]



def main():
    st.title("Welcome to the Privacy Laws Explorer")
    st.write("")
    st.write("")
    col1, col2 = st.columns([3, 9])
    with col1:
        st.header("Choose one of the options below to Explore Privacy Laws")

        selected_state = st.selectbox("Select a state to explore their privacy law", 
                                      us_states, 
                                      index=None, 
                                      key="selected_state")
        
        selected_privacy_topic = st.selectbox("Explore a privacy sector",
                                              privacy_topics,
                                              index=None,
                                              key="selected_privacy_topic")

        st.write("")
        if st.button("Explore Federal Privacy Laws", type="primary", use_container_width=True):
            # This will navigate to the Federal Privacy page in the sidebar
            st.experimental_set_query_params(page="Federal Privacy")

        st.write("")
        if st.button("Explore Comprehensive State Privacy Laws", type="primary", use_container_width=True):
            st.experimental_set_query_params(page="Comprehensive Privacy")

        st.write("")
        if st.button("Explore EU's GDPR", type="primary", use_container_width=True):
            st.experimental_set_query_params(page="EU GDPR")

        # Or if you want direct dynamic navigation you can do e.g.:
        # st.session_state["page_name"] = "federal_privacy"
        # st.experimental_rerun()

        st.write("No specific page selected yet.")
        st.write(selected_state)

    with col2:
        map_generator()

if __name__ == "__main__":
    main()
