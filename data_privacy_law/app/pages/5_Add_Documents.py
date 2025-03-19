# pylint: disable=invalid-name
# pylint: disable=duplicate-code
# pylint: disable=wrong-import-position
# the above line is used to disable the invalid-name error for the file name.
# Capital letters needed as Streamlit inherits case for page name from file name
"""
This module creates and generates the Add Documents page for the streamlit app
"""

import os
import sys
import streamlit as st
from PyPDF2 import PdfReader

# Set up root directory for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)    # This gives "app"
root_dir = os.path.dirname(parent_dir)    # This gives "data_privacy_law"
sys.path.append(root_dir)

from db_manager.faiss_db_manager import (
    add_chunk_to_faiss_index,
    create_folder_for_added_files
)
from db_manager.pdf_parser import (
    extract_uploaded_pdf_pages,
    chunk_text_while_adding_docs
)
from llm_manager.llm_manager import (
    parse_bill_variant_for_adding_docs,
)




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

st.set_page_config(
    page_title="Privacy Laws Explorer",
    layout="wide"
)

STYLING_FOR_ADD_DOC_PAGE = """
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

st.markdown(STYLING_FOR_ADD_DOC_PAGE, unsafe_allow_html=True)


def main(): # pylint: disable=too-many-locals, too-many-statements, unused-variable
    """
    This function runs the Add Document page.
    Pylint suppression being done as many variables used to create empty space
    """
    st.session_state.reset_state_page = True
    _, logo_column, title_column = st.columns(
        [0.01, 0.05, 0.94], gap="small", vertical_alignment="bottom"
    )
    with logo_column:
        st.image("./app/images/add.png", width=75)
    with title_column:
        st.title("Add a Document to our Database of Laws")

    st.write("")
    st.write("")
    st.write("")

    _,input_1,_, input_2, _ = st.columns(
        [0.12,0.3,0.12,0.3,0.12]
    )

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
        st.subheader("Enter relevant US state / NA", divider = True)

        selected_state = st.selectbox(
            "Select a state to explore their privacy law", us_states, index=None
        )
        st.write("")
        st.write("State selection:", selected_state)

    st.write("")
    st.write("")

    _, file_upload_column, _ = st.columns([0.33,0.33,0.33])
    with file_upload_column:
        uploaded_file = st.file_uploader("Choose a PDF file", type = "pdf")
        if uploaded_file is not None:
            reader = PdfReader(uploaded_file)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text

    st.write("")
    st.write("")
    st.write("")

    _, button_col, _ = st.columns([0.25, 0.5, 0.25])
    with button_col:
        if button_col.button(
            "Validate and Submit Inputs", 
            type = "primary",
            use_container_width = True,
            icon = ":material/place_item:"
            ):
            if None not in (level_of_law, selected_state, uploaded_file):
                st.html("""<p style = "font-weight:bold;">
                        Values obtained. Metadata being listed below...
                        </p>""")

                # Process the given text and other parameters to create a
                # JSON object containing the metadata
                parsed_metadata_of_doc = parse_bill_variant_for_adding_docs(
                    text,
                    selected_state,
                    level_of_law
                )
                st.write(parsed_metadata_of_doc)

                # Gather all the pages of the pdf in the form of a list with indexes
                list_of_pages = []
                list_of_pages = extract_uploaded_pdf_pages(uploaded_file)

                st.html("""<p style = "font-weight:bold;">Adding to database now...</p>""")

                # Create new metadata for each chunk of text
                # chunk_text is a list of strings
                # chunk_metadatas is a JSON object containing the metadata for each chunk_text
                chunk_texts, chunk_metadatas = chunk_text_while_adding_docs(list_of_pages)

                # Combine the metadatas obtained by both function -->
                # parse_bill_variant_for_adding_docs(), and chunk_text_while_adding_docs()
                for metadata_of_chunk in chunk_metadatas:
                    metadata_of_chunk.update(parsed_metadata_of_doc)

                # Save the PDF file
                # Check to see if the correct directory exists.
                # If not then create it. Add results into it then.
                # The following function will also update the chunk_metadatas
                # and give them a new "Path" value
                chunk_metadatas = create_folder_for_added_files(chunk_metadatas, uploaded_file)
                st.html("""<p style = "font-weight:bold;
                        text-align:center;
                        font-size:1.3rem;
                        ">
                        Your files have been saved to our database.
                        </p>""")

                # Add the document to FAISS database
                add_chunk_to_faiss_index(chunk_texts, chunk_metadatas)
                st.html("""<p style = "font-weight:bold;
                        text-align:center;
                        font-size:1.3rem;
                        ">
                        Your files have been added to the FAISS database.
                        </p>""")

            else:
                st.write("All inputs have not been filled!")

if __name__ == "__main__":
    main()
