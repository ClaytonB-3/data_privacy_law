import os

from dotenv import load_dotenv
import google.generativeai as genai
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from llm_manager.llm_manager import llm_simplify_chunk_text

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

def process_chunk_records(chunk_ids_with_filenames, user_question):
    """
    This function creates a list of dictionaries of document, page num, and chunk num to query LLM

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
            doc_for_processing_chunk = Document(page_content=text_of_chunk, metadata={})
            parsed_text_for_llm_input = llm_simplify_chunk_text()
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
            print(f"Error parsing chunk_id: {cid}. Error: {e}")
    return records

def add_to_faiss_index(chunk_texts, chunk_metadatas, faiss_folder="./db_manager/faiss_index", index_name= "index.faiss"):
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
    existing_ids = set(faiss_store.docstore._dict.keys())
    # print(f"Existing ID's are {existing_ids}")

    new_texts = []
    new_metadatas = []
    new_ids = []
    for text, meta in zip(chunk_texts, chunk_metadatas):
        this_id = meta.get("Chunk_id")
        if this_id and this_id not in existing_ids:
            new_texts.append(text)
            new_metadatas.append(meta)
            new_ids.append(this_id)

    if new_texts:
        faiss_store.add_texts(texts=new_texts, metadatas=new_metadatas, ids=new_ids)
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
    When that chunkid is found, the associated text of that chunk is returned
    """
    faiss_store = load_faiss_index()
    all_docs = list(faiss_store.docstore._dict.values())
    text_to_send_to_llm = None

    for idx, content in enumerate(all_docs):
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
        else:
            continue
            # print("DEBUG: Chunk id does not match, continuing...")

    return text_to_send_to_llm


def map_chunk_to_metadata(filtered_results):
    """
    This function maps the filtered results to the metadata.

    Args:
        filtered_results (List[Tuple[Document, float]]): A list of tuples of Document and score

    Returns:
        tuple: A tuple of (list of documents, dictionary of chunk_id to (pdf_path, doc_title))
    """
    docs_for_chain = [doc for doc, _ in filtered_results]
    chunk_ids = [doc.metadata.get("Chunk_id") for doc in docs_for_chain]
    pdf_paths = [doc.metadata.get("Path") for doc in docs_for_chain]
    doc_titles = [doc.metadata.get("Title") for doc in docs_for_chain]
    chunk_ids_w_filepaths_titles = {
        chunk_id: (pdf_path, doc_title)
        for chunk_id, pdf_path, doc_title in zip(chunk_ids, pdf_paths, doc_titles)
    }
    return docs_for_chain, chunk_ids_w_filepaths_titles

def write_db_info_to_csv(bill_info_list, file_name="bill_info.csv"):

    # Create or open CSV file for writing
    csv_path = f"./db_manager/data/{file_name}"
    csv_exists = os.path.exists(csv_path)

    # First read existing CSV data if it exists
    existing_data = {}
    if csv_exists:
        with open(csv_path, "r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                existing_data[row["Title"]] = row
    try:
        with open(csv_path, "w", newline="") as csvfile:
            fieldnames = [
                "Title",
                "Date",
                "Type",
                "Sector",
                "State",
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
                title = bill_info["Title"]
                if title in existing_data:
                    existing_row = existing_data[title]
                    if all(bill_info[k] == existing_row[k] for k in fieldnames):
                        continue  # Skip if all values are the same
                    del existing_data[title]  # Remove old entry to be replaced
                # Write new/updated entry to CSV
                writer.writerow(bill_info)
    except:
        print(f'Failed to write {title} into csv.')
    return None