import streamlit as st
from components.map_generator import map_generator


st.markdown("<h1 style='text-align: center;'>The Privacy Law Compass</h1>", unsafe_allow_html=True)


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



col1, col2 = st.columns([5, 7], gap = "small", vertical_alignment = "center")
with col1:
    selected_state = st.selectbox("Select a state to explore their privacy law", us_states, index = None, placeholder = "Select a state...")

    selected_privacy_topic = st.selectbox("Explore a privacy sector", privacy_topics, index = None, placeholder = "Choose a sector...")

    federal_privacy_laws = st.button("Explore Federal Privacy Laws", help = "Click to explore federal privacy laws", type = "primary", use_container_width = True)

    comprehensive_state_privacy_laws = st.button("Explore Comprehensive State Privacy Laws", help = "Click to explore comprehensive state privacy laws", type = "primary", use_container_width = True)

    EU_GDPR = st.button("Explore EU's GDPR", help = "Click to explore EU's GDPR", type = "primary", use_container_width = True)

    
    # st.write(selected_state)
    # st.write(selected_privacy_topic)

    if selected_state is not None:
        
        st.query_params = {"page": "views.stateview", "state": selected_state}
        st.write(f"Navigating to stateview page for **{selected_state}**...")
        
        st.rerun()

with col2:
    map_generator()
