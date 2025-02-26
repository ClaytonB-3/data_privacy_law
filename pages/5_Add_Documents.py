import streamlit as st
import tempfile
from components.pdf_utils import get_pdf_paths_for_state, parse_and_chunk_pdfs
from components.interface_with_FAISS import add_to_faiss_index

# List of US states for the dropdown
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

def run_add_documents_page():
    st.title("Add PDF Documents")
    
    # Basic input for subfolder
    subfolder_name = st.text_input("Enter the subfolder name inside './pdfs/' where new PDFs reside:", "")
    
    # File uploader for individual PDFs
    uploaded_pdf = st.file_uploader("Or, upload a PDF Document:", type=["pdf"], accept_multiple_files=False)
    
    # Jurisdiction options: Federal, State, or GDPR law
    jurisdiction = st.selectbox("Select the jurisdiction of the law:", ["Federal", "State", "GDPR"])
    additional_metadata = {"jurisdiction": jurisdiction}
    
    # For state-level laws, collect additional information
    if jurisdiction == "State":
        # Dropdown for state selection using the provided list
        state_name = st.selectbox("Select the state the file belongs to:", us_states)
        additional_metadata["state"] = state_name
        
        # Option to select if the file is comprehensive or topic specific
        state_file_type = st.selectbox("Select the state-level file type:", ["Comprehensive", "Topic Specific"])
        additional_metadata["state_file_type"] = state_file_type
        
        # If topic specific, choose one of the permitted sectors
        if state_file_type == "Topic Specific":
            topic_sector = st.selectbox("Select the topic sector:", [
                "Financial Privacy", 
                "Health Data Privacy",
                "Digital Privacy",
                "Workplace Privacy", 
                "Consumer Privacy", 
                "Biometric Privacy",
                "Government Surveillance"
            ])
            additional_metadata["topic_sector"] = topic_sector

    if st.button("Process PDFs"):
        pdf_paths = []

        # Process PDFs from subfolder if provided
        if subfolder_name.strip():
            folder_pdf_paths = get_pdf_paths_for_state(subfolder_name)
            if not folder_pdf_paths:
                st.warning(f"No PDF files found in subfolder: {subfolder_name}")
            else:
                pdf_paths.extend(folder_pdf_paths)
        
        # Process uploaded PDF files if any
        if uploaded_pdf:
            for uploaded_file in uploaded_pdf:
                # Save the uploaded file to a temporary file on disk
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    pdf_paths.append(tmp_file.name)
        
        # Ensure that there is at least one PDF to process
        if not pdf_paths:
            st.error("Please provide a subfolder name with PDFs or upload at least one PDF file.")
            return
        
        with st.spinner("Parsing and chunking PDFs..."):
            chunk_texts, chunk_metadatas = parse_and_chunk_pdfs(pdf_paths)
        
        # Merge the additional metadata into each chunk's metadata
        for metadata in chunk_metadatas:
            metadata.update(additional_metadata)
        
        with st.spinner("Adding to FAISS index..."):
            add_to_faiss_index(chunk_texts, chunk_metadatas)
        
        st.success("PDFs have been processed and added to the FAISS index.")

def main():
    run_add_documents_page()

if __name__ == "__main__":
    main()
