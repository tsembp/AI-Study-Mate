import streamlit as st
import os
from src.document_loader import load_document
from src.chunk_and_embed import chunk_documents, embed_and_store
from dotenv import load_dotenv
import torch
from src.quiz_generator import generate_mcqs
from src.flashcard_generator import generate_flashcards

torch._C._jit_set_profiling_mode(False)
load_dotenv()

# Sesstion states
if 'document_processed' not in st.session_state:
    st.session_state.document_processed = False
if 'vector_db' not in st.session_state:
    st.session_state.vector_db = None
if 'selected_mode' not in st.session_state:
    st.session_state.selected_mode = None
if 'study_mode_selected' not in st.session_state:
    st.session_state.study_mode_selected = False
if 'flashcards' not in st.session_state:
    st.session_state.flashcards = []
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'current_card_index' not in st.session_state:
    st.session_state.current_card_index = 0
if 'show_answer' not in st.session_state:
    st.session_state.show_answer = False
if 'file_already_uploaded' not in st.session_state:
    st.session_state.file_already_uploaded = False
if 'current_filename' not in st.session_state:
    st.session_state.current_filename = None

st.set_page_config(page_title="AI StudyMate", layout="wide")

# File upload handler
def handle_file_upload(uploaded_file):
    if not uploaded_file:
        return
    
    # Check file uploaded is new
    new_file_uploaded = False
    if st.session_state.current_filename != uploaded_file.name:
        st.session_state.current_filename = uploaded_file.name
        new_file_uploaded = True
    
    if not os.path.exists("data"):
        os.makedirs("data")

    save_path = os.path.join("data", uploaded_file.name)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    if new_file_uploaded:
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

# HEADER SECTION CONTAINER
with st.container():
    st.image("assets/app-banner.png", width=1500)
    st.subheader(
        'Import your notes in PDF or DOCX format and choose your preferred way of studying!', 
        divider = "green"
    )

    st.write('')

    uploaded_file = st.file_uploader("Upload a study file (.pdf or .docx)", type = ["pdf", "docx"])
    handle_file_upload(uploaded_file)


# STUDY FEATURES CONTAINER
with st.container():
    st.write('')
    st.subheader("Choose a study method", divider="gray")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        flashcard_card = st.container(border=True)
        with flashcard_card:
            st.markdown("### 🃏 Flashcards")
            st.markdown("Study with interactive flashcards generated from your notes.")
            if st.button("Start Flashcards", key="flashcards_btn"):
                if st.session_state.document_processed and st.session_state.vector_db is not None:
                    st.session_state.selected_mode = "flashcards"
                    st.session_state.study_mode_selected = True
                else:
                    st.toast("Please upload and process a document first.", icon="⚠️")

    with col2:
        quiz_card = st.container(border=True)
        with quiz_card:
            st.markdown("### 🧠 Quiz")
            st.markdown("Test your knowledge with multiple-choice questions.")
            if st.button("Start Quiz", key="quiz_btn"):
                if st.session_state.document_processed and st.session_state.vector_db is not None:
                    st.session_state.selected_mode = "quiz"
                    st.session_state.study_mode_selected = True
                else:
                    st.toast("Please upload and process a document first.", icon="⚠️")

    with col3:
        qa_card = st.container(border=True)
        with qa_card:
            st.markdown("### 🤔 Ask Me")
            st.markdown("Ask questions and I'll reply based on your notes.")
            if st.button("Start Asking", key="ask_btn"):
                if st.session_state.document_processed and st.session_state.vector_db is not None:
                    st.session_state.selected_mode = "ask"
                    st.session_state.study_mode_selected = True
                else:
                    st.toast("Please upload and process a document first.", icon="⚠️")

    with col4:
        qa_card = st.container(border=True)
        with qa_card:
            st.markdown("### 📋 Summarize")
            st.markdown("Generate document with summary of notes.")
            if st.button("Start Summarizing", key="summarize"):
                if st.session_state.document_processed and st.session_state.vector_db is not None:
                    st.session_state.selected_mode = "summarize_btn "
                    st.session_state.study_mode_selected = True
                else:
                    st.toast("Please upload and process a document first.", icon="⚠️")


# Handle study feature click only if document is processed 
if st.session_state.study_mode_selected == True:

    # flashcards selected
    if st.session_state.selected_mode == "flashcards":
        st.subheader("🃏 Flashcards", divider="green")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            num_cards = st.slider("Number of flashcards to generate:", 5, 15, 8)
        
        with col2:
            if st.button("Generate Flashcards", key="gen_flashcards_btn"):
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
        if isinstance(st.session_state.flashcards, list) and len(st.session_state.flashcards) > 0:
            st.write("Flashcards below...")
            
            if st.session_state.current_card_index >= len(st.session_state.flashcards):
                st.session_state.current_card_index = 0
            
            # Define callback functions for buttons
            def show_answer():
                st.session_state.show_answer = True
                
            def hide_answer():
                st.session_state.show_answer = False
                
            def next_card():
                if st.session_state.current_card_index < len(st.session_state.flashcards) - 1:
                    st.session_state.current_card_index += 1
                    st.session_state.show_answer = False
                
            def prev_card():
                if st.session_state.current_card_index > 0:
                    st.session_state.current_card_index -= 1
                    st.session_state.show_answer = False
            
            card_container = st.container(border=True)
            with card_container:
                current_card = st.session_state.flashcards[st.session_state.current_card_index]
                
                st.caption(f"Card {st.session_state.current_card_index + 1} of {len(st.session_state.flashcards)}")
                
                st.markdown(f"### {current_card['front']}")
                
                if st.session_state.show_answer:
                    st.divider()
                    st.markdown(f"**Answer:** {current_card['back']}")
            
            # Navigation row
            col1, col2, col3 = st.columns([1, 2, 1], gap="large")
            
            with col1:
                st.button("⬅️ Previous", key="prev_btn", 
                         on_click=prev_card,
                         disabled=st.session_state.current_card_index == 0, 
                         use_container_width=True)
            
            with col2:
                if st.session_state.show_answer:
                    st.button("🙈 Hide Answer", key="hide_btn", 
                             on_click=hide_answer,
                             use_container_width=True)
                else:
                    st.button("👀 Show Answer", key="show_btn", 
                             on_click=show_answer,
                             use_container_width=True)
            
            with col3:
                st.button("Next ➡️", key="next_btn", 
                         on_click=next_card,
                         disabled=st.session_state.current_card_index == len(st.session_state.flashcards) - 1, 
                         use_container_width=True)
        else:
            st.info("Click 'Generate Flashcards' to create flashcards from your notes!")


    # quiz selected
    elif st.session_state.selected_mode == "quiz":
        st.subheader("🧠 Quiz Mode", divider="green")
        col1, col2 = st.columns([1, 1])
        
        with col1:
            num_mcqs = st.slider("Number of questions to generate:", 5, 15, 8)
        
        with col2:
            if 'mcqs_generated' not in st.session_state:
                st.session_state.mcqs_generated = False
                
            generate_mcqs_btn = st.button("Generate Questions", key="generate_mcqs_btn")
            if generate_mcqs_btn:
                with st.spinner("Generating flashcards from your notes..."):
                    # Generate mcqs
                    st.session_state.questions = generate_mcqs(
                        st.session_state.vector_db,
                        num_mcqs = num_mcqs
                    )  
                       
                st.session_state.mcqs_generated = True
                st.toast("MCQs generated!", icon="✨")

        if 'questions' in st.session_state and isinstance(st.session_state.questions, list) and len(st.session_state.questions) > 0:
            st.write("Quiz questions below...")
            
            # Initialize session state for quiz features
            if 'user_answers' not in st.session_state:
                st.session_state.user_answers = {}
            if 'show_quiz_answers' not in st.session_state:
                st.session_state.show_quiz_answers = {}
            if 'submitted_answers' not in st.session_state:
                st.session_state.submitted_answers = {}
            
            # Display each question
            for i, question in enumerate(st.session_state.questions):
                question_key = f"q_{i}"
                
                # question container
                question_container = st.container(border=True)
                with question_container:
                    st.caption(f"Question {i+1} of {len(st.session_state.questions)}")
                    st.markdown(f"### {question['question']}")
                    
                    # options
                    options = question['options']
                    selected_option = st.radio(
                        "Select your answer:",
                        options.keys(),
                        key=f"radio_{question_key}",
                        format_func=lambda x: f"{x}: {options[x]}",
                        index=None,
                        horizontal=False
                    )
                    
                    # Store user selection in session state
                    if selected_option:
                        st.session_state.user_answers[question_key] = selected_option
                    
                    col1, col2 = st.columns(2)
                    
                    # Show/Hide answer button
                    with col1:
                        if st.session_state.show_quiz_answers.get(question_key, False):
                            if st.button("🙈 Hide Answer", key=f"hide_ans_{question_key}", use_container_width=True):
                                st.session_state.show_quiz_answers[question_key] = False
                        else:
                            if st.button("👀 Show Answer", key=f"show_ans_{question_key}", use_container_width=True):
                                st.session_state.show_quiz_answers[question_key] = True
                    
                    # Submit button
                    with col2:
                        submit_disabled = question_key not in st.session_state.user_answers
                        if st.button("Submit Answer ✓", key=f"submit_{question_key}", disabled=submit_disabled, use_container_width=True):
                            st.session_state.submitted_answers[question_key] = st.session_state.user_answers.get(question_key)
                    
                    # Show the answer if requested
                    if st.session_state.show_quiz_answers.get(question_key, False):
                        st.divider()
                        st.markdown("**Answer:**")
                        correct_option = question['correct_option']
                        st.markdown(f"The correct answer is **{correct_option}: {options[correct_option]}**")
                    
                    # Show feedback if submitted
                    if question_key in st.session_state.submitted_answers:
                        st.divider()
                        user_choice = st.session_state.submitted_answers[question_key]
                        correct_option = question['correct_option']
                        
                        if user_choice == correct_option:
                            st.success(f"Correct! You selected {user_choice}: {options[user_choice]}")
                        else:
                            st.error(f"Incorrect. The correct answer was {correct_option}: {options[correct_option]}")
                
                st.write("")
        else:
            st.info("Click 'Generate Questions' to create a quiz from your notes!")


    # ask selected
    elif st.session_state.selected_mode == "ask":
        st.subheader("🤔 Ask Me Anything", divider="green")
        user_question = st.text_input("Ask a question about your notes:", placeholder = 'e.g. What is the formula of the Pythagorean Theorem?')


    # summarize selected
    elif st.session_state.selected_mode == "summarize":
        st.subheader("📋 Summarize Document Generator", divider="green")
        st.info("Summarize feature is coming soon!")