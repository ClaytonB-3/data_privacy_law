import streamlit as st
from components.interface_with_FAISS import load_faiss_index, get_conversational_chain

def run_eu_gdpr_page():
    st.title("EU GDPR Explorer")

    user_question = st.text_input("Ask a question about EU GDPR:")

    if user_question:
        faiss_store = load_faiss_index()
        chain = get_conversational_chain()

        docs_with_scores = faiss_store.similarity_search_with_score(user_question, k=10)
        docs_for_chain = [item[0] for item in docs_with_scores]
        chunk_ids = [doc.metadata.get("chunk_id") for doc in docs_for_chain]

        result = chain.invoke({"context": docs_for_chain, "question": user_question})
        st.markdown("**Answer:**\n" + result)
        st.write("---")
        st.subheader("Retrieved Chunks")
        st.table({"Chunk ID": chunk_ids})

def main():
    run_eu_gdpr_page()

if __name__ == "__main__":
    main()
