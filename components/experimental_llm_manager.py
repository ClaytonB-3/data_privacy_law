"""

This script is used to vectorize PDF files and add it to a FAISS index with metadata.

The final metadata for each chunk is:

    "Source": pdf_path,
    "Page": str(page_num),
    "Filename": pdf_path.split('/')[-1],
    "Path": "./" + "/".join(pdf_path.split("/")[-3:]),
    "Title": "",
    "Date": "",
    "Type": "",
    "Sector": "",
    "State": "",
    "Chunk_id": f"{current_page_id}_ChunkNo_{current_chunk_index}"
}
"""

import os
import json
import sys

import csv

import PyPDF2
import google.generativeai as genai
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts import PromptTemplate
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter


load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def extract_text_from_pdf(pdf_path):
    """
    Return text of a PDF file in a list of strings.

    Args:
        pdf_path (str): The path to the PDF file.

    Returns:
        list: A list of strings, each representing a page of the PDF file.
    """

    text = []
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                text.append(page_text)

    except FileNotFoundError as e:
        print("Error reading PDF:", e)

    return text


def parse_bill_info(pdf_text):
    """
    Feeds the extracted PDF text into the LLM to obtain bill details.
    The LLM is expected to return a JSON object with:
    { "Title": "", "Date": "", "Type": "", "Sector": "", "State": "" }
    """
    prompt_template = """
        You are given the text of a legal document from a PDF file.
        Extract the following details:
        1. Type of the bill (choose from: "State level sectoral", "Federal level", "Comprehensive State level", "GDPR").
        Choose Comprehensive State Level if it is a state legislation related to more than one sector. 
        2. If the bill is "State level sectoral", specify the sector (choose from: "Health", "Education", "Finance", 
        "Telecommunications & Technology", "Government & Public Sector", "Retail & E-Commerce", "Employment & HR", 
        "Media & Advertising", "Critical Infrastructure (Energy, Transportation, etc.)", 
        "Children’s Data Protection"). Otherwise, set it to null.
        3. The latest date mentioned in the bill in MMDDYYYY format.
        4. For state-level laws ("State level sectoral" or "Comprehensive State level"), which state is it 
        associated with (e.g., "Texas", "California").
        5. The title of the bill in 15 words or less. Use format (State name as the first word if it is a 
        State level sectoral bill or Comprehensive State level bill. If it is not in these categories, write Federal as
        the first word. Then put a colon ":" and write the title of the bill after that)

        Return the information as a JSON object EXACTLY in the following format:
        {{"Title": "", "Date": "", "Type": "", "Sector": "", "State": ""}}

        Bill text:
        {context}
    """
    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash-8b", temperature=0.2)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context"])
    chain = create_stuff_documents_chain(llm=model, prompt=prompt)

    doc = Document(page_content=pdf_text)

    result = chain.invoke({"context": [doc]})
    try:

        if result.startswith("```json"):
            result = result[len("```json") :].strip()

        if result.endswith("```"):
            result = result[:-3].strip()

        bill_info = json.loads(result)

    except json.JSONDecodeError as json_err:
        print("Error parsing LLM response:", json_err)
        bill_info = {}

    # print(f"bill_info is {bill_info}")
    return bill_info


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

def add_to_faiss_index(chunk_texts, chunk_metadatas, faiss_folder="./faiss_index", index_name= "index.faiss"):
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


def load_faiss_index(faiss_folder="./faiss_index"):
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


def get_conversational_chain():
    """
    Sets up a QA chain using ChatGoogleGenerativeAI and a custom prompt template.
    """
    prompt_template = """
        If the context has documents related to the question, start your answer with 
        "According to my database of information, ".
        If the context does not have documents related to the question, start your answer with 
        "Sorry, the database does not have specific information about your question". After this, 
        say on the next line "According to my training data, the answer to your question is...", and then write 
        the answer on the next line from your training data. 

        Context:
        {context}

        Question:
        {question}

        Answer:
    """
    model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-001",
        temperature=0.2,
        system_prompt=(
            """You are a helpful assistant that MUST write an introduction,
            bullet points for the main body of the response, and a conclusion"""
        ),
    )
    prompt = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )
    return create_stuff_documents_chain(llm=model, prompt=prompt)


def get_confirmation_result_chain():
    """
    Sets up a QA chain using ChatGoogleGenerativeAI and a custom prompt template.
    """
    prompt_template = """
        I will provide you the answer to a question I asked an LLM model based on a given context. 
        Look at the question and the answer, and make sure that the answer is correct and coherent. 
        DO NOT MENTION THAT I HAVE ASKED YOU THIS QUESTION BEFORE.

        If the answer does not make sense, state "Sorry, the LLM cannot currently generate a good enough response for 
        this question. Please refer to the side table and see if there is anything from those topics that you would like
        to know about."   

        If the answer does make sense, state "The document database has an answer to your question. Here is the 
        structured response based on TPLC's database", and then write the answer with an introduction, body 
        and conclusion for the response. , based on the question and answer and context you were provided. 
        DO NOT USE THE WORDS INTRODUCTION, BODY, CONCLUSION, in your response. 
        THERE MUST BE AN INTRODUCTION AND CONCLUSION part to your response no matter what. 

        Context:
        {context}

        Question:
        {question}

        Previous Answer:
        {answer}

        Answer:
    """
    model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-001",
        temperature=0.2,
        system_prompt=(
            """You are a helpful assistant that MUST write an introduction,
            bullet points, and a conclusion"""
        ),
    )
    prompt = PromptTemplate(
        template=prompt_template, input_variables=["context", "question", "answer"]
    )
    return create_stuff_documents_chain(llm=model, prompt=prompt)


def chunk_pdf_pages(texts_per_page, pdf_path, chunk_size=800, chunk_overlap=200):
    """
    Takes a list of page texts, splits each page into smaller
    chunks using RecursiveCharacterTextSplitter, and keeps track
    of the page number + source in metadata.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )

    chunk_texts = []
    chunk_metadatas = []

    for page_num, page_text in enumerate(texts_per_page, start=1):
        if not page_text.strip():
            continue  # skip empty page
        # Split the page text into smaller chunks:
        splitted_docs = text_splitter.create_documents([page_text])
        for doc in splitted_docs:
            chunk_texts.append(doc.page_content)
            # We'll store the PDF path and page in metadata;
            # the final chunk_id gets built by calculate_pdf_chunk_ids()
            chunk_metadatas.append(
                {
                    "Source": pdf_path,
                    "Page": str(page_num),
                    "Filename": pdf_path.split("/")[-1],
                    "Path": "./" + "/".join(pdf_path.split("/")[-3:]),
                }
            )
    return chunk_texts, chunk_metadatas


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


def llm_simplify_chunk_text(text_for_llm):
    prompt_template = """
        Give me a more readable version of the given text (a quotable summary). Be brief. Answer in points. Dont give any introductions and get straight to the point. Summarize in the context of the question

        Context:
        {context}

        Question:
        {question}

        Answer:
    """
    model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-001",
        temperature=0.5,
    )
    prompt = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )
    return create_stuff_documents_chain(llm=model, prompt=prompt)


def main(pdf_paths):
    # Create data directory if it doesn't exist
    if not os.path.exists("./data"):
        os.makedirs("./data")

    if not os.path.exists("./faiss_index"):
        os.makedirs("./faiss_index")

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

    # Create or open CSV file for writing
    csv_path = "./data/bill_info.csv"
    csv_exists = os.path.exists(csv_path)

    # First read existing CSV data if it exists
    existing_data = {}
    if csv_exists:
        with open(csv_path, "r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                existing_data[row["Title"]] = row

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


if __name__ == "__main__":
    # Ask the user for the state name.
    state_input = input(
        "Enter folder name with PDF texts (e.g., Texas/Comprehensive/..): "
    ).strip()

    # Construct the path to the PDFs folder.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    pdfs_folder = os.path.join(parent_dir, "pdfs", state_input)

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
