import streamlit as st
import os
from src.document_loader import load_document
from src.chunk_and_embed import chunk_documents, embed_and_store
from dotenv import load_dotenv
import torch
from src.quiz_generator import generate_mcq
from src.flashcard_generator import generate_flashcards

torch._C._jit_set_profiling_mode(False)

load_dotenv()

if 'document_processed' not in st.session_state:
    st.session_state.document_processed = False
if 'vector_db' not in st.session_state:
    st.session_state.vector_db = None
if 'selected_mode' not in st.session_state:
    st.session_state.selected_mode = None
if 'flashcards' not in st.session_state:
    st.session_state.flashcards = []
if 'current_card_index' not in st.session_state:
    st.session_state.current_card_index = 0
if 'show_answer' not in st.session_state:
    st.session_state.show_answer = False

st.set_page_config(page_title="AI StudyMate", layout="wide")

st.image("assets/app-banner.png", width=1500)
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


# Study features buttons
st.write('')
st.subheader("Choose Your Study Method", divider="gray")
col1, col2, col3, col4 = st.columns(4)

with col1:
    flashcard_card = st.container(border=True)
    with flashcard_card:
        st.markdown("### 🃏 Flashcards")
        st.markdown("Study with interactive flashcards generated from your notes.")
        if st.button("Start Flashcards", key="flashcards"):
            if st.session_state.document_processed and st.session_state.vector_db is not None:
                st.session_state.selected_mode = "flashcards"
            else:
                st.toast("Please upload and process a document first.", icon="⚠️")


with col2:
    quiz_card = st.container(border=True)
    with quiz_card:
        st.markdown("### 🧠 Quiz")
        st.markdown("Test your knowledge with multiple-choice questions.")
        if st.button("Start Quiz", key="quiz"):
            if st.session_state.document_processed and st.session_state.vector_db is not None:
                st.session_state.selected_mode = "quiz"
            else:
                st.toast("Please upload and process a document first.", icon="⚠️")


with col3:
    qa_card = st.container(border=True)
    with qa_card:
        st.markdown("### 🤔 Ask Me")
        st.markdown("Ask questions and I'll reply based on your notes.")
        if st.button("Start Asking", key="ask"):
            if st.session_state.document_processed and st.session_state.vector_db is not None:
                st.session_state.selected_mode = "ask"
            else:
                st.toast("Please upload and process a document first.", icon="⚠️")


with col4:
    qa_card = st.container(border=True)
    with qa_card:
        st.markdown("### 📋 Summarize")
        st.markdown("Generate document with summary of notes.")
        if st.button("Start Summarizing", key="summarize"):
            if st.session_state.document_processed and st.session_state.vector_db is not None:
                st.session_state.selected_mode = "summarize"
            else:
                st.toast("Please upload and process a document first.", icon="⚠️")

# Handle study feature click only if document is processed 
if st.session_state.selected_mode == "flashcards":
    st.subheader("🃏 Flashcards", divider="green")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        num_cards = st.slider("Number of flashcards to generate:", 5, 20, 10)
    
    with col2:
        if st.button("Generate Flashcards"):
            with st.spinner("Generating flashcards from your notes..."):
                # Generate flashcards
                st.session_state.flashcards = generate_flashcards(
                    st.session_state.vector_db, 
                    num_cards=num_cards
                )
                st.session_state.current_card_index = 0
                st.session_state.show_answer = False
            st.toast("Flashcards generated!", icon="✨")
    
    # Display flashcards if they exist
    if st.session_state.flashcards and len(st.session_state.flashcards) > 0:
        st.write("")
        
        if st.session_state.current_card_index >= len(st.session_state.flashcards):
            st.session_state.current_card_index = 0
        
        # Card container with fixed height
        card_container = st.container(border=True)
        with card_container:
            current_card = st.session_state.flashcards[st.session_state.current_card_index]
            
            # Progress indicator
            st.caption(f"Card {st.session_state.current_card_index + 1} of {len(st.session_state.flashcards)}")
            
            # Display front of card
            st.markdown(f"### {current_card['front']}")
            
            # Display back of card if show_answer is True
            if st.session_state.show_answer:
                st.divider()
                st.markdown(f"**Answer:** {current_card['back']}")
        
        # Navigation row
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button("Previous", disabled=st.session_state.current_card_index == 0):
                st.session_state.current_card_index -= 1
                st.session_state.show_answer = False
                st.experimental_rerun()
        
        with col2:
            if st.session_state.show_answer:
                if st.button("Hide Answer"):
                    st.session_state.show_answer = False
                    st.experimental_rerun()
            else:
                if st.button("Show Answer"):
                    st.session_state.show_answer = True
                    st.experimental_rerun()
        
        with col3:
            if st.button("Next", disabled=st.session_state.current_card_index == len(st.session_state.flashcards) - 1):
                st.session_state.current_card_index += 1
                st.session_state.show_answer = False
                st.experimental_rerun()
    else:
        st.info("Click 'Generate Flashcards' to create flashcards from your notes!")

elif st.session_state.selected_mode == "quiz":
    st.subheader("🧠 Quiz Mode", divider="green")
    st.info("Quiz MCQs are coming soon!")

elif st.session_state.selected_mode == "ask":
    st.subheader("🤔 Ask Me Anything", divider="green")
    user_question = st.text_input("Ask a question about your notes:", placeholder = 'e.g. What is the formula of the Pythagorean Theorem?')

elif st.session_state.selected_mode == "summarize":
    st.subheader("📋 Summarize Document Generator", divider="green")
    st.info("Summarize feature is coming soon!")