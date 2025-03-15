"""
This module creates and generates the state privacy law app for the streamlit app
"""

import base64
import os
import sys
import time

import PyPDF2
import streamlit as st
import pandas as pd
from langchain.docstore.document import Document

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)  # This gives 'app'
root_dir = os.path.dirname(parent_dir)  # This gives 'data_privacy_law'
# Add to Python path
sys.path.append(root_dir)

from llm_manager.experimental_llm_manager import (
    load_faiss_index,
    get_conversational_chain,
    get_confirmation_result_chain,
    get_document_specific_summary,
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
    [data-testid="stSelectbox"] {
        color: white !important;
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


def convert_date(date_str):
    """
    Convert a date in MMDDYYYY format to DD/MM/YYYY.
    If the input is not an 8-digit number, return it unchanged.
    Args:
        date_str (str): The date string to convert

    Returns:
        str: The converted date string in DD/MM/YYYY format, or the original
        string if it's not an 8-digit number
    """
    if isinstance(date_str, str) and len(date_str) == 8 and date_str.isdigit():
        mm = date_str[0:2]
        dd = date_str[2:4]
        yyyy = date_str[4:]
        return f"{dd}/{mm}/{yyyy}"
    return date_str


def create_state_selector():
    """
    This function creates the state selector.
    """
    selected_state = st.selectbox(
        "Select a state to explore their privacy law", us_states, index=None
    )
    st.session_state["selected_state"] = selected_state
    st.write(f"Selected state: {st.session_state['selected_state']}")
    return st.session_state["selected_state"]


def process_chunk_records(chunk_ids_with_metadata, user_question):
    """
    This function creates a list of dictionies of document, page num, and chunk num to query LLM

    1.
    Args:
        chunk_ids (list): List of chunk identifiers
        user_question (str): The question posed by the user to analyze the Documents

    Returns:
        list: A list of dictionaries containing:
            - Document (str): Name of the document
            - Page Number (int): Page number where chunk appears
            - Chunk Number (int): Sequential number of the chunk
            - Relevant information in chunk (str): LLM-processed text relevant to user question
    """
    # Parse the chunk_id to build a table of Document, Page Number, and Chunk Number.
    records = []
    for cid, (pdf_filename, doc_title, _) in chunk_ids_with_metadata.items():
        if not cid:
            continue
        # Expected format: Texas_Data_Privacy_and_Security_Act_Page_35_ChunkNo_1
        try:
            text_of_chunk = obtain_text_of_chunk(cid)
            # st.write(f"\nText of Chunk is {text_of_chunk}")
            doc_for_processing_chunk = Document(page_content=text_of_chunk, metadata={})
            # st.write(f"\nDoc for processing Chunk is {doc_for_processing_chunk}")
            # st.html(f"""<p style="font-weight:bold; font-size:.5rem;">{cid}</p>""")
            # st.html(
            #     f"""<p style="font-weight:bold; font-size:.5rem;">{text_of_chunk}</p>"""
            # )
            parsed_text_for_llm_input = llm_simplify_chunk_text(text_of_chunk)
            # st.write(f"\nDoc for processing Chunk is {parsed_text_for_llm_input}")
            converted_text = parsed_text_for_llm_input.invoke(
                {
                    "context": [doc_for_processing_chunk],
                    "question": user_question,
                }
            )
            # st.write(f"\nConverted text is {converted_text}")

            parts = cid.split("_Page_")
            if len(parts) != 2:
                continue
            page_part, chunk_part = parts[1].split("_ChunkNo_")
            records.append(
                {
                    "Document": doc_title,
                    "Page": int(page_part),
                    "Chunk Number": int(chunk_part),
                    "Relevant Information": str(converted_text),
                    "File Path": pdf_filename,
                }
            )

        except Exception as e:
            st.write(f"Error parsing chunk_id: {cid}. Error: {e}")
    return records


def generate_page_summary(chunk_ids_with_metadata, user_question):
    """
    This function generates a summary of the page based on the user's question.
    """
    records = []
    unique_pdf_paths = set(pdf_path for pdf_path, _, _ in chunk_ids_with_metadata)
    unique_pdf_paths_list = list(unique_pdf_paths)
    for pdf_path in unique_pdf_paths_list:
        # st.write(f"Processing PDF: {pdf_path}")
        # Get all chunks for this PDF path
        all_pdf_pages = []
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for i, page in enumerate(reader.pages):
                all_pdf_pages.append(page.extract_text() or "")
        for path, title, page_num in chunk_ids_with_metadata:
            for i, page_text in enumerate(all_pdf_pages):
                if (i + 1 == int(page_num)) and (path == pdf_path):
                    chunk_pdf_pages = []
                    chunk_pdf_pages.append(title)
                    chunk_pdf_pages.append(page_text)
                    chunk_pdf_pages.append(page_num)
                    # st.write(f"Chunk PDF Pages: {chunk_pdf_pages}")
                    chain = get_document_specific_summary()
                    doc = Document(page_content=chunk_pdf_pages[1])
                    page_information = chain.invoke(
                        {"context": [doc], "question": user_question}
                    )
                    if page_information:
                        chunk_pdf_pages.append(page_information)
                    else:
                        chunk_pdf_pages.append("")
                    records.append(
                        {
                            "Document": chunk_pdf_pages[0],
                            "Page": chunk_pdf_pages[2],
                            "Relevant Information": chunk_pdf_pages[3],
                            "File Path": pdf_path,
                        }
                    )
    return records


def display_selected_state_bills():
    """
    Retrieve all docs for selected state and return df of title and date.
    Args:
        selected_state (str): The state selected by the user from the dropdown menu.

    Returns:
        pandas.DataFrame: A DataFrame containing bills for the selected state with columns:
            - Title: Name/title of the privacy bill
            - Date (DD/MM/YYYY): Date of the bill in DD/MM/YYYY format
        Returns None if no bills are found for the state.
    """
    # I tried using as_retriever() with a filter, but I wasn't sure the right search type to use.
    # pylint: disable=protected-access
    if st.session_state.selected_state is not None:
        all_docs = list(st.session_state.index.docstore._dict.values())
        # Filter for documents that have metadata "State" matching selected_state.
        state_docs = [
            doc
            for doc in all_docs
            if doc.metadata.get("State") == st.session_state.selected_state
        ]
        if not state_docs:
            st.write("No bills found for this state.")
            return None

        # Deduplicate bills based on Title and convert date format.
        bills = {}
        for doc in state_docs:
            title = doc.metadata.get("Title", "No Title")
            topics = doc.metadata.get("Topics", "No Topics")
            # date = doc.metadata.get("Date", "No Date")

            # Convert date from MMDDYYYY to DD/MM/YYYY.
            # date_converted = convert_date(date)
            if title not in bills:
                bills[title] = {
                    "Title": title,
                    # "Effective Date (DD/MM/YYYY)": date_converted,
                    "Topics": topics,
                }
        df_bills = pd.DataFrame(list(bills.values()))
        # Reset index so it starts from 1.
        # df_bills.index = range(1, len(df_bills) + 1)
        st.session_state.df_bills = df_bills
        # st.subheader("Bills for " + st.session_state.selected_state)
        st.dataframe(st.session_state.df_bills, width=1400, hide_index=True)
        return st.session_state.df_bills

    return None

    # return df_bills


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
                    .agg({"Relevant Information": lambda x: "\n".join(x)})
                    .sort_values("Page", key=lambda x: x.astype(int))
                )

                for _, row in page_data.iterrows():
                    st.write(f"Page {row['Page']}:")
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


def map_chunk_to_metadata(filtered_results):
    """
    This function maps the filtered results to the metadata.

    Args:
        filtered_results (List[Tuple[Document, float]]): A list of tuples of Document and score

    Returns:
        tuple: A tuple of (list of documents, dictionary of chunk_id to (pdf_path, doc_title))
    """
    docs_for_chain = [doc for doc, score in filtered_results]
    chunk_ids = [doc.metadata.get("Chunk_id", "Unknown") for doc in docs_for_chain]
    pdf_paths = [doc.metadata.get("Path", "Unknown") for doc in docs_for_chain]
    doc_titles = [doc.metadata.get("Title", "Unknown") for doc in docs_for_chain]
    doc_pages = [doc.metadata.get("Page", "Unknown") for doc in docs_for_chain]
    chunk_id_page_tuples = list(zip(chunk_ids, doc_titles, pdf_paths, doc_pages))
    unique_pairs = set(
        (pdf_path, doc_title, doc_page)
        for _, doc_title, pdf_path, doc_page in chunk_id_page_tuples
    )
    unique_path_page_tuples = list(unique_pairs)
    return docs_for_chain, unique_path_page_tuples


def initialize_session_state():
    """
    This function initializes the session state variables.
    """
    if "index" not in st.session_state:
        st.session_state.index = load_faiss_index()
    if "df" not in st.session_state:
        st.session_state.df = pd.DataFrame()
    if "selected_pdf" not in st.session_state:
        st.session_state.selected_pdf = None
    if "pdf_title" not in st.session_state:
        st.session_state.pdf_title = None
    if "user_question" not in st.session_state:
        st.session_state.user_question = ""
    if "llm_result" not in st.session_state:
        st.session_state.llm_result = None
    if "new_question" not in st.session_state:
        st.session_state.new_question = True


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

    # col1, col2 = st.columns([0.8, 0.2])

    # with col1:
    st.session_state.selected_state = create_state_selector()
    # st.write(f"You have chosen the state: {selected_state}")
    if st.session_state.selected_state is not None:

        with st.expander(
            f"## Bills for {st.session_state.selected_state}", expanded=True
        ):
            display_selected_state_bills()

    # Get the user's question and store in session state
    user_question = st.text_input(
        "Ask a question about State Privacy Laws:", key="question_input"
    )

    if user_question:  # Only process if a question is asked
        if user_question != st.session_state.user_question:
            st.session_state.user_question = user_question
            st.session_state.new_question = True
            st.session_state.df = pd.DataFrame()  # Reset results when question changes
            st.session_state.llm_result = None  # Reset LLM result when question changes
        else:
            st.session_state.new_question = False

        if st.session_state.new_question:
            filtered_results = (
                st.session_state.index.similarity_search_with_relevance_scores(
                    query=user_question,
                    k=10,
                    filter={"State": st.session_state.selected_state},
                    score_threshold=0.2,
                )
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
                docs_for_chain, chunk_ids_w_metadata = map_chunk_to_metadata(
                    filtered_results
                )
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

                # generate table of contextual info for explainability

                if (
                    "Sorry, the LLM cannot currently generate a good enough response"
                    not in result
                ):
                    records = generate_page_summary(chunk_ids_w_metadata, user_question)
                    st.session_state.df = pd.DataFrame(records)
                    st.session_state.relevant_df = st.session_state.df[
                        ["Document", "Page", "Relevant Information"]
                    ]
                else:
                    records = False  # None

        else:
            st.write(st.session_state.llm_result)
            st.write("---")

    # non text summary components
    # with col2:
    #    display_selected_state_bills()
    display_pdf_section()


def main():
    """
    This function runs the main function and loads the FAISS index.
    """
    initialize_session_state()
    run_state_privacy_page()


if __name__ == "__main__":
    main()
