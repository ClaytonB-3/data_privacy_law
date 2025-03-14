import base64
import os
import time
import streamlit as st
import pandas as pd
from langchain.docstore.document import Document
from experimental_llm_manager import (
    load_faiss_index,
    get_conversational_chain,
    get_confirmation_result_chain,
    get_document_specific_summary,
    # obtain_text_of_chunk,
    llm_simplify_chunk_text,
)


def obtain_text_of_chunk(chunk_id):
    """
    This function takes a chunk id, and then searches the whole FAISS dataset for that chunkid
    When that chunkid is found, the associated text of that chunk is returned
    """
    faiss_store = load_faiss_index()
    all_docs = list(faiss_store.docstore._dict.values())
    # print(f"all_docs is {all_docs}")
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


def check_for_duplicate_chunk_content():
    faiss_store = load_faiss_index()
    all_docs = list(faiss_store.docstore._dict.values())
    tracking_dict = {}
    for doc in all_docs:
        if doc.page_content not in tracking_dict:
            tracking_dict[doc.page_content] = [doc.metadata.get("Chunk_id")]
        else:
            tracking_dict[doc.page_content].append(doc.metadata.get("Chunk_id"))

        # Sort dictionary by length of values list in descending order
        tracking_dict = dict(
            sorted(tracking_dict.items(), key=lambda x: len(x[1]), reverse=True)
        )
    # Get first 5 items from the sorted dictionary
    first_five = list(tracking_dict.values())[:20]
    return first_five


print(check_for_duplicate_chunk_content())
# print(
#     obtain_text_of_chunk(
#         "Texas:_Act_relating_to_smart_device_data_collection_transparency_Page_1_ChunkNo_5"
#     )
# )


# print(
#     obtain_text_of_chunk(
#         "Texas:_Act_relating_to_smart_device_data_collection_transparency_Page_3_ChunkNo_0"
#     )
# )
