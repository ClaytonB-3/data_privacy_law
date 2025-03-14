import streamlit as st
import plotly.express as px
import pandas as pd



def map_generator():

    # Example data: state abbreviations and corresponding number of laws passed
    data = {
        "state": ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", 
              "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
              "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
              "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
              "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"],
        "laws_passed": [10, 5, 15, 8, 30, 20, 18, 4, 25, 12, 6, 7, 22, 16, 9, 
                    11, 13, 14, 5, 17, 19, 21, 15, 8, 10, 6, 7, 12, 5, 20,
                    8, 29, 14, 5, 16, 10, 11, 18, 4, 15, 5, 22, 25, 9, 14, 
                    26, 7, 10, 3, 12]
    }
    df = pd.DataFrame(data)

    # Create the choropleth map
    fig = px.choropleth(
        df,
        locations="state",              # Column with state abbreviations
        locationmode="USA-states",      # Use built-in state codes
        color="laws_passed",            # Column with data for color-coding
        scope="usa",                    # Limit map scope to USA
        color_continuous_scale="Viridis",  # Choose a color scale
        labels={"laws_passed": "Laws Passed"}  # Legend label
    )

    fig.update_layout(
        width=1000,           # Set desired width in pixels
        height=600,           # Set desired height in pixels
        margin={"l": 20, "r": 20, "t": 20, "b": 20},  # Tight margins
        coloraxis_colorbar=dict(
            x=1,         # Move the colorbar closer to the map (adjust as needed)
        )
    )

    # Display the map in your Streamlit app
    st.plotly_chart(fig, use_container_width=True)