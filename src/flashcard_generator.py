import os
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.llms import HuggingFaceHub

def generate_flashcards(vector_db, num_cards=10):
    # Get content from the vector database
    retriever = vector_db.as_retriever(search_kwargs={"k": 5})
    docs = retriever.get_relevant_documents("generate comprehensive flashcards")
    
    content = " ".join([doc.page_content for doc in docs])
    
    # Create a prompt template for flashcard generation
    flashcard_template = """
    Based on the following study content, generate {num_cards} flashcards for studying.
    Each flashcard should have a clear question/term on the front and a concise answer/definition on the back.
    
    STUDY CONTENT:
    {content}
    
    ANSWER FORMAT:
    Return a list of exactly {num_cards} flashcards with consistent formatting.
    Each flashcard should be in the format:
    Q: [Question/Term] (front side)
    A: [Answer/Definition] (back side)
    
    EXAMPLE OUTPUT:
    FLASHCARDS:

    Q: What is photosynthesis?
    A: The process by which green plants and some other organisms convert light energy into chemical energy. Plants use sunlight, water, and carbon dioxide to produce oxygen and glucose.
    
    Q: Define the term "mitosis"
    A: A type of cell division in which a single cell divides into two identical daughter cells, each containing the same number of chromosomes as the parent cell.
    
    Q: What is the law of conservation of energy?
    A: Energy cannot be created or destroyed, only transformed from one form to another. The total amount of energy in an isolated system remains constant.
    """
    
    # Set up the LLM chain
    llm = HuggingFaceHub(
        repo_id = "tiiuae/falcon-7b-instruct",
        model_kwargs={"temperature": 0.5, "max_new_tokens": 256},
    )

    
    prompt = PromptTemplate(
        input_variables=["content", "num_cards"],
        template=flashcard_template
    )
    
    chain = LLMChain(llm=llm, prompt=prompt)
    
    # Generate flashcards
    response = chain.run(content=content, num_cards=num_cards)
    
    # Parse the response into a structured format
    flashcards = []
    raw_cards = response.strip().split("\n\n")
    
    for card in raw_cards:
        if not card.strip():
            continue
            
        parts = card.strip().split("\nA: ")
        if len(parts) != 2:
            continue
            
        question = parts[0].replace("Q: ", "").strip()
        answer = parts[1].strip()
        
        flashcards.append({
            "front": question,
            "back": answer
        })
    
    return flashcards