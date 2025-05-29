import os
import json
from langchain.prompts.chat import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI

def generate_mcqs(vector_db, num_mcqs=8):
    # Get content from the vector database
    retriever = vector_db.as_retriever(search_kwargs={"k": 5})
    docs = retriever.get_relevant_documents("generate comprehensive multiple choice questions")
    
    content = " ".join([doc.page_content for doc in docs])
    
    # Create a prompt template for flashcard generation
    system_template = """
    You are an assistant generating study material. Follow these formatting rules strictly:
    - Generate {num_mcqs} multiple choice questions.
    - Each should have 4 options (A, B, C, D).
    - EXACTLY one option must be correct and you need to point it out in the JSON output
    - Do NOT add explanations.
    - Format the output **exactly** as shown:

    Return output as a JSON list of objects in the following format:

    [
        {{
            "question": "What is the capital of France?",
            "options": {{
            "A": "Paris",
            "B": "Madrid",
            "C": "Berlin",
            "D": "Rome"
            }},
            "correct_option": "A"
        }},
        ...
    ]
    """

    human_template = """
    STUDY CONTENT:
    {content}
    """
    
    # Set up the LLM chain
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.5,
    )

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_template),
        HumanMessagePromptTemplate.from_template(human_template)
    ])

    chain = prompt | llm
    response = chain.invoke({"content": content, "num_mcqs": num_mcqs})

    print("LLM RAW RESPONSE:\n", response)
    
    mcqs = []
    response_text = response.content.strip()
    mcqs = json.loads(response_text)

    return mcqs