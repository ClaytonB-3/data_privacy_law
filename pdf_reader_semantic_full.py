import streamlit as st
from langchain_community.document_loaders import TextLoader
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


def main():
    st.title("Search Washington Privacy Laws...")

    load_dotenv()

    # 1. Load all PDFs from a folder
    loader = PyPDFDirectoryLoader("WashingtonPDFS/")
    text_documents = loader.load()

    # 2. Split each document into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    documents = text_splitter.split_documents(text_documents)

    # 3. Create a vectorstore from the documents
    llm = Ollama(model="llama2")
    embeddings = OllamaEmbeddings(model="llama2")
    db = Chroma.from_documents(documents, embeddings)

    # 4. Create the prompt and chain
    prompt = ChatPromptTemplate.from_template(
        """
        Answer the following question based ONLY on the context provided.
        Think step by step before answering.
        Be factual.  
        <context>
        {context}
        </context>
        Question: {input}
        """
    )
    document_chain = create_stuff_documents_chain(llm, prompt)
    retriever = db.as_retriever()
    retrieval_chain = create_retrieval_chain(retriever, document_chain)

    # 5. Streamlit UI: text input for the user's question
    user_query = st.text_input("Ask a question about the PDFs...")

    # 6. When the user clicks search, run the chain
    if st.button("Search"):
        if user_query.strip():
            response = retrieval_chain.invoke({"input": user_query})
            st.markdown("**Answer:**")
            st.write(response['answer'])
        else:
            st.warning("Please enter a query before searching.")

if __name__ == "__main__":
    main()