import streamlit as st
import os
from src.document_loader import load_document
from src.chunk_and_embed import chunk_documents, embed_and_store
from dotenv import load_dotenv
import torch
from src.quiz_generator import generate_mcq

torch._C._jit_set_profiling_mode(False)

load_dotenv()

if 'document_processed' not in st.session_state:
    st.session_state.document_processed = False
if 'vector_db' not in st.session_state:
    st.session_state.vector_db = None
if 'selected_mode' not in st.session_state:
    st.session_state.selected_mode = None

st.set_page_config(page_title="AI StudyMate", layout="wide")

st.header('📖 AI StudyMate')
st.subheader(
    'Import your notes in PDF or DOCX format and choose your way of preferred studying!', 
    divider = "green"
)

st.write('')

uploaded_file = st.file_uploader("Upload a study file (.pdf or .docx)", type = ["pdf", "docx"])

if uploaded_file:
    if not os.path.exists("data"):
        os.makedirs("data")

    save_path = os.path.join("data", uploaded_file.name)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.toast(f"Uploaded file: {uploaded_file.name}", icon="ℹ️")

    # Load & parse document
    try:
        docs = load_document(save_path)
        
        if st.button("🔍 Process & Embed Text"):
            with st.spinner("Chunking and embedding..."):
                chunks = chunk_documents(docs)
                vector_db = embed_and_store(chunks)
                st.session_state.vector_db = vector_db
                st.session_state.document_processed = True
                st.toast("Processing complete! Your document is ready.", icon="✅")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.session_state.document_processed = False
    
if st.session_state.document_processed and st.session_state.vector_db is not None:
    st.write('')
    st.subheader("Choose Your Study Method", divider="gray")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        flashcard_card = st.container(border=True)
        with flashcard_card:
            st.markdown("### 🃏 Flashcards")
            st.markdown("Study with interactive flashcards generated from your notes.")
            if st.button("Start Flashcards", key="flashcards"):
                st.session_state.selected_mode = "flashcards"
    
    with col2:
        quiz_card = st.container(border=True)
        with quiz_card:
            st.markdown("### 🧠 Quiz")
            st.markdown("Test your knowledge with multiple-choice questions.")
            if st.button("Start Quiz", key="quiz"):
                st.session_state.selected_mode = "quiz"
    
    with col3:
        qa_card = st.container(border=True)
        with qa_card:
            st.markdown("### 🤔 Ask Me")
            st.markdown("Ask questions and I'll reply based on your notes.")
            if st.button("Start Asking", key="ask"):
                st.session_state.selected_mode = "ask"
    
    with col4:
        qa_card = st.container(border=True)
        with qa_card:
            st.markdown("### 📋 Summarize")
            st.markdown("Generate document with summary of notes.")
            if st.button("Start Summarizing", key="summarize"):
                st.session_state.selected_mode = "summarize"
    
    if st.session_state.selected_mode == "flashcards":
        st.subheader("🃏 Flashcards", divider="green")
        st.info("Flashcard feature is coming soon!")

    elif st.session_state.selected_mode == "quiz":
        st.subheader("🧠 Quiz Mode", divider="green")
        st.info("Quiz MCQs are coming soon!")
    
    elif st.session_state.selected_mode == "ask":
        st.subheader("🤔 Ask Me Anything", divider="green")
        user_question = st.text_input("Ask a question about your notes:", placeholder = 'e.g. What is the formula of the Pythagorean Theorem?')

    elif st.session_state.selected_mode == "summarize":
        st.subheader("📋 Summarize Document Generator", divider="green")
        st.info("Summarize feature is coming soon!")