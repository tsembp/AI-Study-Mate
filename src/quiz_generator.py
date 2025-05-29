import os
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

def generate_mcqs(vector_db, num_mcqs=8):
    # Get content from the vector database
    retriever = vector_db.as_retriever(search_kwargs={"k": 5})
    docs = retriever.get_relevant_documents("generate comprehensive multiple choice questions")
    
    content = " ".join([doc.page_content for doc in docs])
    
    # Create a prompt template for flashcard generation
    flashcard_template = """
    Based on the following study content, generate {num_mcqs} multiple choice questions for studying.
    Each question should have a clear question/term and 4 choices, out of which 1 must be correct. You may also include
    options like "All of the above" or "None of the above".
    
    STUDY CONTENT:
    {content}
    
    ANSWER FORMAT:
    Return a list of exactly {num_mcqs} mcqs with consistent formatting.
    Don't include any other messages like "Here's a list...". Just include only the flashcards in the format explained below.
    To point out the correct answer, at the end of the answer that's correct, include the '(<--)' string
    Each mcq should be in the format (in this example B is correct):
    Q: [Question/Term]
    A: [Answer/Definition]
    B: [Answer/Definition] (<--)
    C: [Answer/Definition]
    D: [Answer/Definition]
    
    
    EXAMPLE OUTPUT:
    Q: What is the primary function of mitochondria in a cell?
    A: Generate ATP through cellular respiration (<--)
    B: Protein synthesis
    C: Storage of genetic material
    D: Cell division

    Q: Which programming paradigm emphasizes the use of functions and avoids changing state?
    A: Object-oriented programming
    B: Functional programming (<--)
    C: Procedural programming
    D: Event-driven programming

    Q: In the context of databases, what does ACID stand for?
    A: Atomicity, Consistency, Isolation, Durability (<--)
    B: Adaptive Computing in Databases
    C: Automatic Connection and Information Distribution
    D: Array, Collection, Integration, and Distribution
    """
    
    # Set up the LLM chain
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.5,
    )

    
    prompt = PromptTemplate(
        input_variables=["content", "num_mcqs"],
        template=flashcard_template
    )
    
    chain = prompt | llm
    response = chain.invoke({"content": content, "num_mcqs": num_mcqs})

    print("LLM RAW RESPONSE:\n", response)
    
    # Parse the response into a structured format
    mcqs = []
    raw_mcqs = response.content.strip().split("\n\n")

    for mcq in raw_mcqs:
        if not mcq.strip():
            continue
            
        lines = mcq.strip().split("\n")
        if len(lines) < 5:
            continue

        question = lines[0].replace("Q: ", "").strip()

        correct_option = None
        cleaned_options = {}

        for i, line in enumerate(lines[1:5], 0):
            option_letter = chr(65 + i)
            option_text = line.replace(f"{option_letter}: ", "").strip()
            
            if "(<--)" in option_text:
                correct_option = option_letter
                option_text = option_text.replace("(<--)", "").strip()
                
            cleaned_options[option_letter] = option_text

        mcqs.append({
            "question": question,
            "options": cleaned_options,
            "correct_option": correct_option
        })
    
    return mcqs