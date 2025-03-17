"""
Functions for parsing texts from pdf.
"""

import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter

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
            for _, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                text.append(page_text)

    except FileNotFoundError as e:
        print("Error reading PDF:", e)

    return text
