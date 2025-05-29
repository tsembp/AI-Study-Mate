import os
import json
from langchain.prompts.chat import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.prompts.chat import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

from langchain_openai import ChatOpenAI

def generate_flashcards(vector_db, num_cards=8):
    # Get content from the vector database
    retriever = vector_db.as_retriever(search_kwargs={"k": 5})
    docs = retriever.get_relevant_documents("generate comprehensive flashcards")
    
    content = " ".join([doc.page_content for doc in docs])
    
    # Create a prompt template for flashcard generation
    system_template = """
    You are an assistant generating study material. Follow these formatting rules strictly:
    - Generate {num_cards} flashcards.
    - Each should have a front and back side.
    - Do NOT add explanations.
    - Format the output **exactly** as shown:

    Return output as a JSON list of objects in the following format:

    [
        {{
            "front": "What is...",
            "back": "It is..."
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
    response = chain.invoke({"content": content, "num_cards": num_cards})

    print("LLM RAW RESPONSE:\n", response)
    
    flashcards = []
    raw_cards = response.content.strip()
    flashcards = json.loads(raw_cards)

    return flashcards