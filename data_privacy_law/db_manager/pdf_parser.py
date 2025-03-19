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

def chunk_text_while_adding_docs(
    pdf_pages: list[str],
    chunk_size: int = 800,
    chunk_overlap: int = 200
):
    """
    Takes a list of PDF pages (as strings) from extract_uploaded_pdf_pages,
    splits each page into smaller chunks using RecursiveCharacterTextSplitter,
    and sets metadata for each chunk, including:
        - Path: "Submitted-Online"
        - Page: The page number (as a string)
    
    No Filename or Source are included here because that is handled elsewhere.

    Args:
        pdf_pages (list[str]): A list of strings, each representing one PDF page’s text.
        chunk_size (int): Maximum characters per chunk. Default = 800.
        chunk_overlap (int): Overlap of characters between chunks. Default = 200.

    Returns:
        (chunk_texts, chunk_metadatas):
            chunk_texts (List[str]): The textual chunks.
            chunk_metadatas (List[dict]): Each chunk’s metadata dict with
                                          "Path" and "Page".
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    chunk_texts = []
    chunk_metadatas = []

    # Iterate through each page in the pdf_pages list
    for page_num, page_text in enumerate(pdf_pages, start=1):
        # Skip empty pages
        if not page_text.strip():
            continue

        # Split the page text into smaller chunks
        splitted_docs = text_splitter.create_documents([page_text])
        for doc in splitted_docs:
            chunk_texts.append(doc.page_content)

            # Minimal metadata: path + page number
            chunk_metadatas.append({
                "Path": "Submitted-Online",
                "Page": str(page_num)
            })

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

    except Exception as e:
        raise FileNotFoundError('Error reading PDF:', e) from e

    return text

def extract_uploaded_pdf_pages(uploaded_file):
    """
    Takes an uploaded file (Streamlit's UploadedFile) and returns a list of 
    page texts, exactly like 'extract_text_from_pdf' does for a local PDF path.
    """

    all_pages = []
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        for page in reader.pages:
            page_text = page.extract_text() or ""
            all_pages.append(page_text)
    except FileNotFoundError as e:
        print(f"Error reading PDF: {e}")
    return all_pages
