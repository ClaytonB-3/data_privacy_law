# pylint: disable=invalid-name
# the above line is used to disable the invalid-name error for the file name.
# Capital letters needed for displaying the page name in the sidebar
"""
This module creates and generates the Home page for the streamlit app
"""
import streamlit as st


st.set_page_config(page_title="Privacy Laws Explorer", layout="wide")

STYLING_FOR_HOME_PAGE = """
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

st.markdown(STYLING_FOR_HOME_PAGE, unsafe_allow_html=True)


def main():
    """
    This function runs the Home page.
    """
    st.session_state.reset_state_page = True
    _, logo_column, title_column = st.columns(
        [0.01, 0.05, 0.94], gap="small", vertical_alignment="center"
    )
    with logo_column:
        st.image("./app/images/cardinal-points.png", width=75)
    with title_column:
        st.title("Welcome to the Privacy Law Compass")
    st.divider()

    st.html(
        """
        <p>
            <span style="font-size: 1.2rem; font-weight: bold;">
                Our project aims to clearly illustrate and explain the current landscape \
of US federal and state privacy laws, while providing user-friendly ways to navigate \
their complexities.
            </span>
        </p>
        """
    )

    st.html(
        """
        <p>
            <span style="font-size: 1.2rem; font-weight: bold;">
                We achieve this by organizing files into intuitive categories and \
enabling AI-powered searches for privacy law content. Additionally, we focus on making \
the AI's responses explainable, so you \
can easily understand how results are derived. A PDF viewer is also embedded alongside \
the results for further verification. Happy exploring!
            </span>
        </p>
        """
    )

    st.write("")
    st.write("")
    col1, col2 = st.columns([4, 8])
    with col1:
        col1_container = st.container()
        col1_container.subheader(
            "State of the Privacy Landscape of the USA", divider=True
        )
        col1_container.write(
            "In the United States, privacy regulation is primarily managed at the state level, as \
there is no comprehensive federal privacy law. This has resulted in a patchwork of \
statutes with considerable "
            "variability in scope and rigor across different jurisdictions."
        )
        col1_container.write("")

        col1_container.subheader("Problems Due to Weak Laws", divider=True)
        col1_container.write(
            "The inconsistencies in state-level privacy protections contribute to challenges in "
            "achieving uniform data security and consumer control nationwide. This regulatory \
fragmentation can complicate "
            "efforts to prevent data breaches and adequately safeguard personal information."
        )
        col1_container.write("")

        col1_container.subheader("Where State Privacy Laws Are Failing", divider=True)
        col1_container.write(
            "Many state privacy laws exhibit limitations due to constraints in data minimization "
            "requirements, enforcement provisions, and the clarity of key definitions. These \
deficiencies are often linked "
            "to compromises made during the legislative process, which can dilute the \
intended protections."
        )
        col1_container.write("")

    with col2:
        image1column, image2column = st.columns([0.45, 0.55], gap="small")
        with image1column:
            st.image("./app/images/plawimage1.png")
        with image2column:
            st.image("./app/images/plawimage2.png")

        st.divider()
        st.html(
            """
        <p style = "font-size:1.6rem; font-weight: bold;">
            What comprises an 
            <span style="font-weight: bold; font-style: italic; text-decoration: underline">
                Ideal
            </span> 
            Privacy Law?
        </p>
        """
        )
        # Data Minimization Section
        expander_data_minimization = st.expander("Data Minimization")
        expander_data_minimization.write("""\
            1. Limit data collection to only what is reasonably necessary for \
            the service provided.\n
            2. Restrict the collection of sensitive data (e.g., biometric, genetic, geolocation).\n
            3. Prohibit unnecessary data transfers to third parties.\n
            4. Enforce prompt deletion of data once it is no longer needed.\n
            5. Bar secondary uses of personal data without explicit consent.\n
            6. Implement universal opt-out mechanisms for data sharing.\n
        """
        )

        # Enforcement Section
        expander_enforcement = st.expander("Enforcement")
        expander_enforcement.write("""\
            1. Grant Attorney General rulemaking authority to define and update privacy standards.\n
            2. Empower the Attorney General with strong enforcement powers, including penalties.\n
            3. Provide a private right of action so consumers can hold companies accountable.\n
            4. Enable injunctive relief to halt ongoing privacy violations.\n
            5. Include provisions for statutory damages to deter non-compliance.\n
            6. Establish an independent privacy agency to monitor and enforce the law.\n
        """
        )

        # Rulemaking Authority Section
        expander_rulemaking = st.expander("Rulemaking Authority")
        expander_rulemaking.write("""\
            1. Grant dedicated rulemaking authority to a privacy agency or the Attorney General.\n
            2. Enable regular updates to privacy standards as technology evolves.\n
            3. Facilitate stakeholder consultation to refine and enforce privacy rules.\n
        """
        )

        # Civil Rights Protections Section
        expander_civil_rights = st.expander("Civil Rights Protections")
        expander_civil_rights.write("""\
            1. Prohibit discrimination based on data profiles or processing practices.\n
            2. Ensure equal access to goods and services regardless of data-driven classifications.\n
            3. Provide robust civil rights remedies for violations of privacy.\n
            4. Include clear language to prevent disparate impacts on marginalized groups.\n
        """
        )

        # Transparency & Assessing High-Risk Data Practices Section
        expander_transparency = st.expander("Transparency & Risk Assessments")
        expander_transparency.write("""\
            1. Mandate regular data protection impact assessments by companies.\n
            2. Require public disclosure of risk assessment summaries.\n
            3. Enforce transparency in data collection, processing, and sharing practices.\n
            4. Allow independent audits of high-risk data practices.\n
        """
        )

        # Meaningful Individual Rights Section
        expander_individual_rights = st.expander("Meaningful Individual Rights")
        expander_individual_rights.write("""\
            1. Guarantee the right to access, correct, and delete personal data.\n
            2. Provide universal opt-out mechanisms for targeted advertising and data sharing.\n
            3. Allow authorized agents to exercise privacy rights on behalf of consumers.\n
            4. Ensure the right to know which third parties receive your data.\n
        """
        )

        # Banning Manipulative Design & Unfair Marketing Section
        expander_unfair_marketing = st.expander(
            "Banning Manipulative Design & Unfair Marketing"
        )
        expander_unfair_marketing.write("""\
            1. Prohibit dark patterns and manipulative design strategies that undermine consent.\n
            2. Ban predatory advertising practices targeting vulnerable populations, including minors.\n
            3. Prevent conditional access to essential services based on consent to data collection.\n
            4. Ensure marketing practices do not coerce or mislead consumers into compromising privacy.\n
        """
        )

        # Importance of Strong Definitions Section
        expander_definitions = st.expander("Strong Definitions")
        expander_definitions.write("""\
            1. Define 'personal data' broadly to include inferred and derived data.\n
            2. Clearly delineate sensitive data categories (e.g., biometric, genetic, geolocation).\n
            3. Avoid exemptions for pseudonymous data to close loopholes.\n
            4. Establish clear definitions for profiling and targeted advertising.\n
            """
        )


if __name__ == "__main__":
    main()
