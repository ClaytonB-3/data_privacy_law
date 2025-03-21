# pylint: disable=invalid-name
# the above line is used to disable the invalid-name error for the file name.
# Capital letters needed as Streamlit inherits case for page name from file name
"""
This module creates and generates the state privacy law app for the streamlit app
"""


import base64
import os
import sys
import time

import pandas as pd
import streamlit as st

# Set up root directory for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)  # This gives "app"
root_dir = os.path.dirname(parent_dir)  # This gives "data_privacy_law"
sys.path.append(root_dir)

# Streamlit requires pages be in the page directory so these apps have to be run
# from outside the root directory causing import pylint errors that are suppressed
# pylint: disable=wrong-import-position, import-error
from db_manager.faiss_db_manager import (
    load_faiss_index,
    map_chunk_to_metadata,
)

# Streamlit requires pages be in the page directory so these apps have to be run
# from outside the root directory causing import pylint errors that are suppressed
# pylint: disable=wrong-import-position, import-error
from llm_manager.llm_manager import (
    generate_page_summary,
    get_confirmation_result_chain,
    get_conversational_chain,
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

st.set_page_config(page_title="Explore State Privacy Laws", layout="wide")
STYLING_FOR_STATE_PAGE = """
<style>
    /* Set default text color for all elements */
    * {
        color: #000;
    }

    [data-testid = "stAppViewContainer"]{
    background-color: #fefae0;
    opacity: 1;
    background-image:  radial-gradient(#ccd5ae 1.1000000000000001px, transparent 1.1000000000000001px), 
    radial-gradient(#ccd5ae 1.1000000000000001px, #fefae0 1.1000000000000001px);
    background-size: 56px 56px;
    background-position: 0 0,28px 28px;
    color: #000;
    }

    [data-testid="stSelectbox"] *{
        color: white;
    }
    
    [data-testid="stWidgetLabel"] * {
        color: black !important;
    }

    div[data-baseweb="select"] * {
    background-color: light grey;
    }
   
    [data-testid = "stSelectboxVirtualDropdown"] *{
        color: white !important;
    }

    [data-testid="stSelectbox"] > div[role="button"] {
        color: white !important;
    }

    [data-testid="stSelectbox"] div[role="listbox"] * {
        color: white !important;
    }
    

    [data-testid="stSidebar"] {
        background-color: #dda15e;
        opacity: 1;
    }

    [data-testid="stSidebar"] * {
        color: #000 !important;
        font-weight: bold;
    }

    [data-testid = "stSidebarNav"] * {
        font-size: 18px;
        padding-bottom:5px;
        padding-top:5px;
    }

    [data-testid = "stExpander"] {
        background-color: #eece9f;
    }

    [data-testid = "stExpander"] * {
        color: #000 !important;
        font-weight: bold;
    }

    /* Fix for dataframes and tables */
    [data-testid = "stDataFrame"] * {
        color: #000 !important;
        background-color: transparent !important;
    }

    /* Fix for error messages */
    .stException, .stError {
        color: red !important;
        background-color: transparent !important;
    }

    [data-testid = "stElementContainer"] {
        border-color: black;
    }

    [data-testid = "stTable"] * {
        border-color: black;
    }

    .stButton > button {
        background-color: white !important;
        color: black !important;
        border: 1px solid black !important;
        font-weight: bold !important;
    }

    .stButton > button:hover {
        background-color: #f8f8f8 !important;
        border: 1px solid black !important;
    }
</style>
"""


st.markdown(STYLING_FOR_STATE_PAGE, unsafe_allow_html=True)


def create_state_selector():
    """
    This function creates the state selector.
    """
    selected_state = st.selectbox(
        "Select a state to explore their privacy law", us_states, index=None
    )
    st.write(f"Selected state: {selected_state}")
    return selected_state


def display_selected_state_bills(selected_state):
    """
    Retrieve all docs for selected state and return df of title and topics for that state.

    Args:
        selected_state (str): The selected state to display bills for

    Returns:
        None
    Output:
        st.dataframe of title and topics for the selected state

    """
    # I tried using as_retriever() with a filter, but it didn't work and
    # this is the only way I could get it to work.
    # pylint: disable=protected-access
    if selected_state is not None:
        all_docs = list(st.session_state.index.docstore._dict.values())
        # Filter for documents that have metadata "State" matching selected_state.
        state_docs = [
            doc for doc in all_docs if doc.metadata.get("State") == selected_state
        ]
        if not state_docs:
            st.write("No bills found for this state.")
            return None

        # Deduplicate bills based on Title and convert date format.
        bills = {}
        for doc in state_docs:
            title = doc.metadata.get("Title", "No Title")
            topics = doc.metadata.get("Topics", "No Topics")
            file_path = doc.metadata.get("Path", "No Path")

            if file_path not in bills:

                bills[title] = {
                    "Title": title,
                    "Topics": topics,
                }
        df_bills = pd.DataFrame(list(bills.values()))
        st.session_state.df_bills = df_bills
        st.dataframe(st.session_state.df_bills, width=1400, hide_index=True)
        return st.session_state.df_bills

    return None


def generate_llm_response(user_question):
    """
    This function generates the LLM response to the user's question.

    Args:
        user_question (str): The user's question

    Returns:
        None

    Output:
        if question has already been asked:
            st.write of the LLM response
        if no relevant documents are found:
            st.html of the LLM response
        if new question and relevant documents are found:
            st.session_state.llm_result updated with the new response
            st.dataframe of the summary for each page used to generate response
    """
    if not isinstance(user_question, str):
        raise TypeError("User question must be a string")
    if "selected_state" not in st.session_state:
        raise ValueError("Selected state not found in session state")

    filtered_results = st.session_state.index.similarity_search_with_relevance_scores(
        query=user_question,
        k=10,
        filter={"State": st.session_state.selected_state},
        score_threshold=0.2,
    )

    if not filtered_results:
        st.html(
            """<p style = "font-weight:bold; font-size:1.3rem;">
            "No relevant documents found for the selected state based on your query."
            </p>
        """
        )

    else:
        # Prepare documents for the conversational chain.
        docs_for_chain, chunk_ids_w_metadata = map_chunk_to_metadata(filtered_results)
        # Gen summary from llm of relevant context
        chain = get_conversational_chain()
        firstresult = chain.invoke(
            {"context": docs_for_chain, "question": user_question}
        )
        # Verify if the first LLM response was coherent or not.
        chain = get_confirmation_result_chain()
        result = chain.invoke(
            {
                "context": docs_for_chain,
                "question": user_question,
                "answer": firstresult,
            }
        )
        if result != st.session_state.llm_result:
            st.write_stream(stream_data(result))
            st.write("---")
        else:
            st.write(result)
        st.session_state.llm_result = result

        if (
            "Sorry, the LLM cannot currently generate a good enough response"
            not in result
        ) and (
            "Sorry, the database does not have specific information about your question"
            not in result
        ):
            records = generate_page_summary(chunk_ids_w_metadata, user_question)
            st.session_state.df = pd.DataFrame(records)
            st.session_state.relevant_df = st.session_state.df[
                ["Document", "Page", "Relevant Information"]
            ]
        else:
            records = False


def stream_data(result_of_llm):
    """
    This function streams the LLM result to the screen.

    Args:
        result_of_llm (str): The result of the LLM

    Returns:
        None
    """
    for word in result_of_llm.split(" "):
        yield word + " "
        time.sleep(0.02)


def show_pdf(file_path):
    """
    This function displays the PDF in a new tab.

    Args:
        file_path (str): The path to the PDF file to display

    Returns:
        None

    Output:
        iframe of the pdf viewer
    """
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
    pdf_display = f"""<div style="text-align: center">
                    <iframe src="data:application/pdf;base64,{base64_pdf}"
                    width="1100" height="800" type="application/pdf"></iframe>
                    </div>"""
    st.markdown(pdf_display, unsafe_allow_html=True)


def display_pdf_section():
    """
    Displays the PDF section of the app, including:
    - Creating a DataFrame without duplicate documents
    - Showing document titles with "View PDF" buttons
    - Displaying the selected PDF when a button is clicked

    The function uses session state variables:
    - df: The main DataFrame containing document info
    - df_no_duplicates: DataFrame with duplicate documents removed
    - selected_pdf: Path to currently selected PDF
    - pdf_title: Title of currently selected PDF
    """
    st.session_state.df_no_duplicates = pd.DataFrame()
    # Remove duplicate rows based on Document column if DataFrame exists and has rows
    if len(st.session_state.df) > 0:
        # Group by Document first to organize data per document
        documents_grouped = st.session_state.df.groupby("Document")
        # Add section header for sources and relevant information
        st.markdown("### Sources and Relevant Information")
        # Create collapsers for each document
        for doc_name, doc_group in documents_grouped:
            with st.expander(f"## 📄 {doc_name}"):
                # Group the document's data by page and create a table
                page_data = (
                    doc_group.groupby(["Page", "File Path"], as_index=False)
                    .agg({"Relevant Information": "\n".join})
                    .sort_values("Page", key=lambda x: x.astype(int))
                )

                for _, row in page_data.iterrows():
                    st.write(f"Page {row["Page"]}:")
                    st.write(row["Relevant Information"])
                # Add View PDF button for this document
                if st.button("View PDF", key=f"pdf_btn_{doc_name}"):
                    st.session_state.selected_pdf = page_data["File Path"].iloc[0]
                    st.session_state.pdf_title = doc_name
        # Display selected PDF
        if st.session_state.selected_pdf:
            st.markdown(f"### Document: {st.session_state.pdf_title}")
            pdf_path = os.path.normpath(st.session_state.selected_pdf)
            show_pdf(pdf_path)


def initialize_session_state():
    """
    This function initializes the session state variables.
    """
    if "index" not in st.session_state or st.session_state.reset_state_page is True:
        st.session_state.index = load_faiss_index()
    if "df" not in st.session_state or st.session_state.reset_state_page is True:
        st.session_state.df = pd.DataFrame()
    if (
        "selected_pdf" not in st.session_state
        or st.session_state.reset_state_page is True
    ):
        st.session_state.selected_pdf = None
    if "pdf_title" not in st.session_state or st.session_state.reset_state_page is True:
        st.session_state.pdf_title = None
    if (
        "user_question" not in st.session_state
        or st.session_state.reset_state_page is True
    ):
        st.session_state.user_question = ""
    if (
        "llm_result" not in st.session_state
        or st.session_state.reset_state_page is True
    ):
        st.session_state.llm_result = None
    if (
        "new_question" not in st.session_state
        or st.session_state.reset_state_page is True
    ):
        st.session_state.new_question = True
    if (
        "question_input_key" not in st.session_state
        or st.session_state.reset_state_page is True
    ):
        st.session_state.question_input_key = 0


def run_state_privacy_page():
    """
    This function runs the state privacy law page.
    """
    _, logo_column, title_column = st.columns(
        [0.01, 0.05, 0.94], gap="small", vertical_alignment="bottom"
    )
    with logo_column:
        st.image("./app/images/map.png", width=75)
    with title_column:
        st.header("Explore State Privacy Laws")

    selected_state = create_state_selector()

    if selected_state:
        with st.expander(f"## Bills for {selected_state}", expanded=True):
            _, center_col, _ = st.columns([0.05, 0.9, 0.05])
            with center_col:
                display_selected_state_bills(selected_state)
    if ("selected_state" not in st.session_state) or (
        st.session_state.selected_state != selected_state
    ):
        st.session_state.question_input_key += 1
    # Get the user's question and store in session state
    user_question = st.text_input(
        "Ask a question about State Privacy Laws:",
        key=f"question_input_{st.session_state.question_input_key}",
    )
    if ("selected_state" not in st.session_state) or (
        st.session_state.selected_state != selected_state
    ):
        st.session_state.user_question = ""
        st.session_state.new_question = True
        st.session_state.df = pd.DataFrame()  # Reset results when state changes
        st.session_state.llm_result = None  # Reset LLM result when state changes
        st.session_state.selected_state = selected_state
        st.session_state.pdf_title = None
        st.session_state.selected_pdf = None

    else:
        if user_question:  # Only process if a question is asked
            if user_question != st.session_state.user_question:
                st.session_state.user_question = user_question
                st.session_state.new_question = True
                st.session_state.df = (
                    pd.DataFrame()
                )  # Reset results when question changes
                st.session_state.llm_result = (
                    None  # Reset LLM result when question changes
                )
            else:
                st.session_state.new_question = False

            if st.session_state.new_question:
                generate_llm_response(user_question)

            else:
                st.write(st.session_state.llm_result)
                st.write("---")
    display_pdf_section()


def main():
    """
    This function runs the main function and loads the FAISS index.
    """
    initialize_session_state()
    run_state_privacy_page()
    st.session_state.reset_state_page = False


if __name__ == "__main__":
    main()
