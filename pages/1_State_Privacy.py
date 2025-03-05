"""
This module creates and generates the state privacy law app for the streamlit app
"""

import streamlit as st
import pandas as pd
from langchain.docstore.document import Document
from components.experimental_llm_manager import (
    load_faiss_index,
    get_conversational_chain,
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


def process_chunk_records(chunk_ids, user_question):
    """
    This function creates a list of dictionies of document, page num, and chunk num to query LLM
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
    for cid in chunk_ids:
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
            document_name = parts[0]  # e.g. Texas_Data_Privacy_and_Security_Act
            rest = parts[1]  # e.g. 35_ChunkNo_1
            page_part, chunk_part = rest.split("_ChunkNo_")
            page_number = int(page_part)
            chunk_number = int(chunk_part)

            records.append(
                {
                    "Document": document_name,
                    "Page Number": page_number,
                    "Chunk Number": chunk_number,
                    "Relevant information in chunk": str(converted_text),
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
                "Date (DD/MM/YYYY)": date_converted,
            }
    df_bills = pd.DataFrame(list(bills.values()))
    # Reset index so it starts from 1.
    df_bills.index = range(1, len(df_bills) + 1)
    return df_bills


def run_state_privacy_page():
    """
    This function runs the state privacy law page.
    """
    st.title("State Privacy Law Explorer")

    col1, col2 = st.columns([9, 3])

    with col1:

        selected_state = create_state_selector()
        st.write(f"You have chosen the state: {selected_state}")

        # Get the user's question.
        user_question = st.text_input("Ask a question about State Privacy Laws:")

        if user_question:
            # Load the FAISS index.
            faiss_store = load_faiss_index()

            # Use the similarity_search function with a filter to ensure that only documents
            # with metadata "State" equal to the selected state are returned.
            filtered_results = faiss_store.similarity_search(
                query=user_question, k=10, filter={"State": selected_state}
            )

            # print(filtered_results)

            if not filtered_results:
                st.write(
                    "No relevant documents found for the selected state based on your query."
                )
                return None

            # Prepare documents for the conversational chain.
            docs_for_chain = filtered_results
            chunk_ids = [doc.metadata.get("chunk_id") for doc in docs_for_chain]

            # Get the conversational chain and invoke it.
            chain = get_conversational_chain()
            result = chain.invoke(
                {"context": docs_for_chain, "question": user_question}
            )
            st.markdown("**Answer:**\n" + result, unsafe_allow_html=True)
            st.write("---")
            if (
                "Sorry! The document database does not contain documents related to the query."
                not in result
            ):
                records = process_chunk_records(chunk_ids, user_question)
            else:
                records = None

            if records:
                df = pd.DataFrame(records)
                df.index = range(1, len(df) + 1)
                st.table(df)
            else:
                st.write("No chunk details to display.")

    with col2:
        if selected_state:
            st.subheader("Bills for " + selected_state)
            # df_bills = display_state_bills(selected_state)
            st.table(display_state_bills(selected_state))
    return None


def main():
    """
    This function runs the main function.
    """
    run_state_privacy_page()


if __name__ == "__main__":
    main()
