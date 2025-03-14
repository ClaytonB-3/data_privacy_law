import os
import json
import sys

import csv
import time
import PyPDF2
import google.generativeai as genai
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts import PromptTemplate
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter


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


# what does text_splitter.create_documents do?
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
    count = 0
    for page_num, page_text in enumerate(texts_per_page, start=1):
        if not page_text.strip():
            continue  # skip empty page
        # Split the page text into smaller chunks:
        splitted_docs = text_splitter.create_documents([page_text])
        # print("page_num in enumerate loop: ", page_num)
        # print("splitted_docs: ", splitted_docs)

        for doc in splitted_docs:
            # print("page_num in doc loop: ", page_num)
            # print("doc: ", doc)
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
        count += 1
        if count == 5:
            break
    return chunk_texts, chunk_metadatas


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
        # source = meta.get("Title", "unknown")
        source = "Texas: Data Privacy and Security Act"
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


def obtain_text_of_chunk(chunk_id):
    """
    This function takes a chunk id, and then searches the whole FAISS dataset for that chunkid
    When that chunkid is found, the associated text of that chunk is returned
    """
    start_time = time.time()
    faiss_store = load_faiss_index()
    print(f"Loading FAISS index took {time.time() - start_time:.2f} seconds")
    all_docs = list(faiss_store.docstore._dict.values())
    text_to_send_to_llm = None

    for idx, content in enumerate(all_docs):
        # print("\nProcessing document index:", idx)

        metadata = content.metadata if hasattr(content, "metadata") else {}

        current_chunk_id = metadata.get("Chunk_id")

        # Only extract page content if the chunk IDs match.
        if current_chunk_id == chunk_id:
            print("DEBUG: Found matching chunk_id:", chunk_id)
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


def main():
    text = extract_text_from_pdf("pdfs/Texas/TDPSA.pdf")
    chunk_texts, chunk_metadatas = chunk_pdf_pages(text, "pdfs/Texas/TDPSA.pdf")
    print("--------------------------------")
    print(chunk_texts)
    print("--------------------------------")
    print(chunk_metadatas)
    print(len(chunk_texts))
    chunk_metadatas = calculate_updated_chunk_ids(chunk_metadatas)
    print("--------------------------------")
    print(chunk_metadatas)
    print("chunk_metadatas[0]['Chunk_id']: ", chunk_metadatas[0]["Chunk_id"])
    for meta in chunk_metadatas:
        print("--------------------------------")
        print("meta['Chunk_id']:", meta["Chunk_id"])
        print("meta['Source']:", meta["Source"])
        print("meta['Page']:", meta["Page"])

        print(
            "obtain_text_of_chunk(meta['Chunk_id']): ",
            obtain_text_of_chunk(meta["Chunk_id"]),
        )


if __name__ == "__main__":
    main()
