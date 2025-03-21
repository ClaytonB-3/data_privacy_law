"""
Functions for managing FAISS database and chunks
"""

import os
import csv
import re

from dotenv import load_dotenv
import google.generativeai as genai
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from llm_manager.llm_manager import parse_bill_info
from db_manager.pdf_parser import extract_text_from_pdf, chunk_pdf_pages

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def calculate_updated_chunk_ids(chunk_metadatas):
    """
    Update each metadata dict with a unique 'chunk_id' that includes the PDF source, page number,
    and a chunk index that resets for each new page.
    Format: "source:page:chunk_index"

    This is used in various streamlit pages to display the tables
    """
    last_page_id = None
    current_chunk_index = 0

    for meta in chunk_metadatas:
        source = meta.get("Title", "unknown")
        source = source.replace(" ", "_")
        page = meta.get("Page", "1")
        current_page_id = f"{source}_Page_{page}"

        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        meta["Chunk_id"] = f"{current_page_id}_ChunkNo_{current_chunk_index}"
        last_page_id = current_page_id

    return chunk_metadatas


def add_chunk_to_faiss_index(
    chunk_texts,
    chunk_metadatas,
    faiss_folder="./db_manager/faiss_index",
    index_name="index.faiss",
):
    """
    Create or load an existing FAISS index and add new document chunks.
    """
    chunk_metadatas = calculate_updated_chunk_ids(chunk_metadatas)
    # Code for testing what the new chunk_ids are. These are the key to explabaility
    # for items in chunk_metadatas:
    #     print(f"\nThese are the updated chunk ID's\n: {items.get("Chunk_id")}")

    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    index_file = os.path.join(faiss_folder, index_name)
    index_exists = os.path.exists(index_file)

    if index_exists:
        try:
            faiss_store = FAISS.load_local(
                folder_path=faiss_folder,
                embeddings=embeddings,
                allow_dangerous_deserialization=True,
            )
        except (OSError, ValueError) as load_error:
            print(
                "Error loading existing FAISS index; creating new one. Error:",
                load_error,
            )
            faiss_store = None
    else:
        faiss_store = None

    if faiss_store is None:
        if chunk_texts:
            faiss_store = FAISS.from_texts(
                texts=chunk_texts, embedding=embeddings, metadatas=chunk_metadatas
            )
            faiss_store.save_local(faiss_folder)
        return

    # Add only new chunks to the existing index.
    existing_ids = set(getattr(faiss_store.docstore, "_dict").keys())
    # print(f"Existing ID's are {existing_ids}")

    new_doc_dict = {
        "new_texts":[],
        "new_metadatas":[],
        "new_ids":[]
    }

    for text, meta in zip(chunk_texts, chunk_metadatas):
        this_id = meta.get("Chunk_id")
        if this_id and this_id not in existing_ids:
            new_doc_dict["new_texts"].append(text)
            new_doc_dict["new_metadatas"].append(meta)
            new_doc_dict["new_ids"].append(this_id)

    if len(new_doc_dict["new_texts"]) != 0:
        faiss_store.add_texts(texts=new_doc_dict["new_texts"],
                              metadatas=new_doc_dict["new_metadatas"],
                              ids=new_doc_dict["new_ids"])
        faiss_store.save_local(faiss_folder)


def load_faiss_index(faiss_folder="./db_manager/faiss_index"):
    """
    Loads the FAISS index if it exists.
    """
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    faiss_store = FAISS.load_local(
        folder_path=faiss_folder,
        embeddings=embeddings,
        allow_dangerous_deserialization=True,
    )
    return faiss_store

def obtain_text_of_chunk(chunk_id):
    """
    This function takes a chunk id, and then searches the whole FAISS dataset for that chunkid
    When that chunkid is found, the associated text of that chunk is returned.
    """
    faiss_store = load_faiss_index()
    all_docs = list(getattr(faiss_store.docstore, "_dict").values())
    text_to_send_to_llm = None

    for _, content in enumerate(all_docs):
        # print("\nProcessing document index:", idx)

        metadata = content.metadata if hasattr(content, "metadata") else {}

        current_chunk_id = metadata.get("Chunk_id")

        # Only extract page content if the chunk IDs match.
        if current_chunk_id == chunk_id:
            # print("DEBUG: Found matching chunk_id:", chunk_id)
            if isinstance(content, tuple):
                page_text = content[0]
            else:
                page_text = (
                    content.page_content if hasattr(content, "page_content") else ""
                )
            # print("DEBUG: Extracted page text for chunk_id", chunk_id, ":\n", page_text)
            text_to_send_to_llm = page_text
            break

    return text_to_send_to_llm


def map_chunk_to_metadata(filtered_results):
    """
    This function maps the filtered results to the metadata.

    Args:
        filtered_results (List[Tuple[Document, float]]): A list of tuples of Document and score

    Returns:
        tuple: A tuple of (list of documents,
                           dictionary of chunk_id: (pdf_path, doc_title, doc_page))
    """
    if not isinstance(filtered_results, list):
        raise TypeError("filtered_results must be a list")
    docs_for_chain = [doc for doc, score in filtered_results]
    # print(docs_for_chain[0].metadata.get("Chunk_id"))
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


def add_bills_to_faiss_index(pdf_paths):
    """
    Add all of the bills in the `pdf_paths` into faiss DB.
    Args:
        pdf_paths: List[pdf_path:str]

    Return:
        bill_info_list: List[Dict[str, str]], The summary of the bills 
    that were added to the FAISS DB.

    """

    bill_info_list = []
    # Write document into faiss index
    for pdf_path in pdf_paths:
        print(f"\nProcessing: {pdf_path}\n")

        # Step 1: Extract text from the PDF. Returns a list
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
        add_chunk_to_faiss_index(chunk_texts, chunk_metadatas)

    return bill_info_list


def write_bill_info_to_csv(bill_info_list, file_name="bill_info.csv"):
    """
    Write bill info into .csv file with following columns:
    - Title
    - Date
    - Type
    - Sector
    - State
    - Topic
    - Path
    - Filename,
    see llm_model.parse_bill_info for more details.
    
    Args:
        bill_info_list: List[Dict[str, str]]
    
    """
    # Create or open CSV file for writing
    csv_path = f"./db_manager/data/{file_name}"
    csv_exists = os.path.exists(csv_path)

    # First read existing CSV data if it exists
    existing_data = {}
    if csv_exists:
        with open(csv_path, "r", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # print(row["Title"])
                existing_data[row["Path"]] = row
    try:
        with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "Title",
                "Date",
                "Type",
                "Sector",
                "State",
                "Topics",
                "Path",
                "Filename",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            # Write existing data first
            for row in existing_data.values():
                writer.writerow(row)

            for bill_info in bill_info_list:
                # Check if this title already exists and if the data is different
                ## Fix bugs: Path should be the unique key for bills, not Title
                path = bill_info["Path"]

                if path in existing_data:
                    existing_row = existing_data[path]
                    if all(bill_info[k] == existing_row[k] for k in fieldnames):
                        del existing_data[path]  # Remove old entry to be replaced
                        continue  # Skip if all values are the same
                # Write new/updated entry to CSV
                writer.writerow(bill_info)

    except ValueError as e:
        print(e)
        print(f"Failed to write {path} into csv.")

def sanitize_filename(filename):
    """
    Remove characters that are illegal in Windows file names.
    """
    # Remove: \ / * ? : " < > |
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def create_folder_for_added_files(chunk_metadatas, uploaded_file):
    """
    Creates a folder to save the uploaded file, if there isn’t one already.
    If the folder exists, the file is added to it.

    For metadata with "Type" equal to "State-level sectoral":
      - Uses individual_metadatas["State"] as the folder name.
    Otherwise:
      - Uses individual_metadatas["Type"] as the folder name.
    
    The folders are located inside the 'pdfs' directory, which is 2 levels above this file.
    
    Inputs: 
        chunk_metadatas: List of dictionaries with metadata.
        uploaded_file: PDF file from Streamlit.
    Returns:
        None
    """
    # If no metadata is provided, exit early.
    if not chunk_metadatas:
        return chunk_metadatas

    # Use only the first metadata dictionary.
    individual_metadatas = chunk_metadatas[0]

    # Determine the path to the 'pdfs' folder (2 levels above this file)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    pdfs_dir = os.path.abspath(os.path.join(current_dir, "..", "pdfs"))

    # Choose folder and file names based on metadata.
    if individual_metadatas["Type"] == "State-level sectoral":
        folder_name = individual_metadatas["State"]
    else:
        folder_name = individual_metadatas["Type"]

    # Sanitize folder name.
    folder_name = sanitize_filename(folder_name)

    file_name = sanitize_filename(individual_metadatas["Title"])
    # Append .pdf extension if not present.
    if not file_name.lower().endswith(".pdf"):
        file_name += ".pdf"

    # Define the full destination directory path.
    dest_dir = os.path.join(pdfs_dir, folder_name)

    # Create the folder if it doesn't exist.
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    # Build the full file path.
    file_path = os.path.join(dest_dir, file_name)

    # Write the uploaded file's content to disk.
    uploaded_file.seek(0) # Sets the pointer to the start of the file
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    for individual_metadatas in chunk_metadatas:
        individual_metadatas["Path"] = file_path

    return chunk_metadatas
