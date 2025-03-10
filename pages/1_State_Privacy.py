"""
This module creates and generates the state privacy law app for the streamlit app
"""

import os
import time
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

st.set_page_config(page_title="Explore State Privacy Laws", layout="wide")

styling_for_state_page = """
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

[data-testid = "stElementContainer"] {
    color: #000;
    border-color: black;
}

[data-testid = "stTable"] * {
    border-color: black;
    color: #000;
}

[data-testid = "stMarkdownContainer"] {
    color: #111;
}

</style>
"""


st.markdown(styling_for_state_page, unsafe_allow_html=True)


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
    return st.session_state["selected_state"]


def process_chunk_records(chunk_ids_with_filenames, user_question):
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
    for cid, (pdf_filename, doc_title) in chunk_ids_with_filenames.items():
        if not cid:
            continue
        # Expected format: Texas_Data_Privacy_and_Security_Act_Page_35_ChunkNo_1
        try:

            text_of_chunk = obtain_text_of_chunk(cid)
            # st.write(f"\nText of Chunk is {text_of_chunk}")

            doc_for_processing_chunk = Document(page_content=text_of_chunk, metadata={})
            # st.write(f"\nDoc for processing Chunk is {doc_for_processing_chunk}")

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

            rest = parts[1]  # e.g. 35_ChunkNo_1
            page_part, chunk_part = rest.split("_ChunkNo_")
            page_number = int(page_part)
            chunk_number = int(chunk_part)

            records.append(
                {
                    "Document": doc_title,
                    "Page": page_number,
                    "Chunk Number": chunk_number,
                    "Relevant information": str(converted_text),
                    "File Path": pdf_filename,
                }
            )
        except Exception as e:
            st.write(f"Error parsing chunk_id: {cid}. Error: {e}")
    return records


def display_state_bills(selected_state):
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
    # Load the FAISS index. (Reuse if already loaded; here we load again for clarity.)
    faiss_store = load_faiss_index()
    # I tried using as_retriever() with a filter, but I wasn't sure the right search type to use.
    # pylint: disable=protected-access
    all_docs = list(faiss_store.docstore._dict.values())
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
        date = doc.metadata.get("Date", "No Date")

        # Convert date from MMDDYYYY to DD/MM/YYYY.
        date_converted = convert_date(date)
        if title not in bills:
            bills[title] = {
                "Title": title,
                "Effective Date (DD/MM/YYYY)": date_converted,
            }
    df_bills = pd.DataFrame(list(bills.values()))
    # Reset index so it starts from 1.
    df_bills.index = range(1, len(df_bills) + 1)
    return df_bills


def stream_data(result_of_llm):
    for word in result_of_llm.split(" "):
        yield word + " "
        time.sleep(0.02)


def run_state_privacy_page():
    """
    This function runs the state privacy law page.
    """
    empty_column, logo_column, title_column = st.columns(
        [0.01, 0.05, 0.94], gap="small", vertical_alignment="bottom"
    )
    with logo_column:
        st.image("images/map.png", width=75)
    with title_column:
        st.header("Explore State Privacy Laws")

    col1, col2 = st.columns([0.7, 0.3])
    pdf_path = False

    with col1:

        selected_state = create_state_selector()
        st.write(f"You have chosen the state: {selected_state}")

        # Get the user's question.
        user_question = st.text_input("Ask a question about State Privacy Laws:")

        if user_question:
            # Load the FAISS index.
            faiss_store = load_faiss_index()
            # Use the similarity_search_with_relevance_scores function with a filter
            # to ensure that only documents with metadata "State" equal to the
            # selected state are returned.

            close_results = True

            filtered_results = faiss_store.similarity_search_with_relevance_scores(
                query=user_question,
                k=10,
                filter={"State": selected_state},
                score_threshold=0.2,
            )

            if not filtered_results:
                st.html(
                    """<p style = "font-weight:bold; font-size:1.3rem;">
                    "No relevant documents found for the selected state based on your query."
                    </p>
                """
                )
                close_results = False

            if close_results:

                # Prepare documents for the conversational chain.
                # From various documents we retrieve their chunk id's, path, and title
                # A dictionary of these values is then created

                docs_for_chain = [doc for doc, score in filtered_results]
                chunk_ids = [doc.metadata.get("Chunk_id") for doc in docs_for_chain]
                pdf_paths = [doc.metadata.get("Path") for doc in docs_for_chain]
                doc_titles = [doc.metadata.get("Title") for doc in docs_for_chain]
                chunk_ids_w_filepaths_titles = {
                    chunk_id: (pdf_path, doc_title)
                    for chunk_id, pdf_path, doc_title in zip(
                        chunk_ids, pdf_paths, doc_titles
                    )
                }

                # Now we call the LLM in the first instance and pass it the user question as well as the documents
                # that the similiarity search function returned above

                chain = get_conversational_chain()
                firstresult = chain.invoke(
                    {"context": docs_for_chain, "question": user_question}
                )

                # Now we pass the LLM response, along with the user query and the same documents to verify if the first
                # LLM response was coherent or not. Only upon a verification being done by this second LLM call will we
                # print things to screen.

                # The get_confirmation_result_chain function below can return a structured response (with introduction,
                # body, and conclusion) if the first LLM call gave a good quality response. However, if the response of
                # the first LLM call was not good, then a custom error message will be returned, which is then shown
                # on the screen.

                chain = get_confirmation_result_chain()
                result = chain.invoke(
                    {
                        "context": docs_for_chain,
                        "question": user_question,
                        "answer": firstresult,
                    }
                )

                st.write_stream(
                    stream_data(result)
                )  # Print outcome of the second LLM, word-by-word for stylistic effect
                st.write("---")

                # On verifying that a structured LLM response (from the second LLM call) was obtained, we print a table
                # of information below the response. This is for AI explanability, and it shows which text segments that
                # were used to construct the LLM response

                if (
                    "Sorry, the LLM cannot currently generate a good enough response"
                    not in result
                ):
                    records = process_chunk_records(
                        chunk_ids_w_filepaths_titles, user_question
                    )
                else:
                    records = None

                if records:
                    df = pd.DataFrame(records)
                    df.index = range(1, len(df) + 1)
                    st.table(df[["Document", "Page", "Relevant information"]])
                    pdf_path = df["File Path"].iloc[0]
                    pdf_title = df["Document"].iloc[0]
                else:
                    st.write(
                        "No relevant information found for the selected state based on your query."
                    )

    with col2:
        if selected_state:
            st.subheader("Bills for " + selected_state)
            st.table(display_state_bills(selected_state))
        container_pdf = st.container()
        with container_pdf:
            if pdf_path:
                st.markdown(f"### Document: {pdf_title}")
                pdf_path = os.path.normpath(pdf_path)
                pdf_viewer(pdf_path, height=600)

    return None


def main():
    """
    This function runs the main function.
    """
    run_state_privacy_page()


if __name__ == "__main__":
    main()
