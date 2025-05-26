import streamlit as st
import os
from src.document_loader import load_document
from src.chunk_and_embed import chunk_documents, embed_and_store
from dotenv import load_dotenv
import torch

torch._C._jit_set_profiling_mode(False)

load_dotenv()

st.title('AI StudyMate')

uploaded_file = st.file_uploader("Upload a study file (.pdf or .docx)", type = ["pdf", "docx"])

if uploaded_file:
    if not os.path.exists("data"):
        os.makedirs("data")

    save_path = os.path.join("data", uploaded_file.name)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.toast(f"Uploaded file: {uploaded_file.name}", icon="✅")

    try:
        docs = load_document(save_path)
        
        if st.button("🔍 Process & Embed Text"):
            with st.spinner("Chunking and embedding..."):
                chunks = chunk_documents(docs)
                vector_db = embed_and_store(chunks)
                st.success("Processing complete! Your document is ready.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")