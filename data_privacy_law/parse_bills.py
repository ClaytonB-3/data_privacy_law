import os
import sys

from db_manager.faiss_db_manager import add_to_faiss_index, write_db_info_to_csv
from db_manager.pdf_parser import extract_text_from_pdf, chunk_pdf_pages
from llm_manager.llm_manager import parse_bill_info


def main(pdf_paths):
    # Create data directory if it doesn't exist
    if not os.path.exists("./db_manager/data"):
        os.makedirs("./db_manager/data")

    if not os.path.exists("./db_manager/faiss_index"):
        os.makedirs("./db_manager/faiss_index")

    bill_info_list = []
    # Write document into faiss index
    for pdf_path in pdf_paths:
        print(f"\nProcessing: {pdf_path}\n")

        # Step 1: Extract text from the PDF.
        pages_of_pdf = extract_text_from_pdf(pdf_path)

        if not pages_of_pdf:
            print("No text extracted from the PDF.")
            continue

        full_pdf_text = "\n".join(pages_of_pdf)

        # Step 2: Use the LLM to parse the bill details.
        bill_info = parse_bill_info(full_pdf_text)

        # Add PDF path to bill info for CSV
        bill_info["Path"] = "./" + "/".join(pdf_path.split("/")[-3:])
        bill_info["Filename"] = pdf_path.split("/")[-1]
        bill_info_list.append(bill_info)
        # Step 3: Split the document into chunks and get the source and page number for each chunk
        chunk_texts, chunk_metadatas = chunk_pdf_pages(pages_of_pdf, pdf_path)

        # Step 4: Combine the chunk metadata (Source and page number),
        # with the doc metadata (Source, title etc.)
        for metadata_of_chunk in chunk_metadatas:
            metadata_of_chunk.update(bill_info)

        # Step 5: Add the document and metadata to the FAISS index.
        add_to_faiss_index(chunk_texts, chunk_metadatas)

    write_db_info_to_csv(bill_info_list)
    


if __name__ == "__main__":
    # Ask the user for the state name.
    state_input = input(
        "Enter folder name with PDF texts (e.g., Texas/Comprehensive/..): "
    ).strip()

    # Construct the path to the PDFs folder.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # parent_dir = os.path.dirname(current_dir)
    # pdfs_folder = os.path.join(parent_dir, "pdfs", state_input)
    pdfs_folder = os.path.join(current_dir, "pdfs", state_input)

    # print(f"This is the PDF Folder\n:{pdfs_folder}")

    if not os.path.exists(pdfs_folder):
        print(f"Folder not found: {pdfs_folder}")
        sys.exit(1)

    # Gather all PDF file paths in the specified folder.
    pdf_paths = [
        os.path.join(pdfs_folder, filename)
        for filename in os.listdir(pdfs_folder)
        if filename.lower().endswith(".pdf")
    ]

    # print(pdf_paths)
    if not pdf_paths:
        print(f"No PDF files found in folder: {pdfs_folder}")
        sys.exit(1)

    # Process the list of PDF paths.
    main(pdf_paths)
