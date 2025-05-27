from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.llms import HuggingFaceHub


def get_quiz_prompt():
    template = """
    Based on the following study text, create a multiple choice question to test the knowledge of a student.
    
    Text:
    {context}
    
    Privide your response as:
    Question: <your question>
    A. <option A>
    B. <option B>
    C. <option C>
    D. <option D>
    Answer: <correct letter>
    """

    return PromptTemplate(
        input_variables = ["context"],
        template=template,
    )

def generate_mcq(context: str):
    prompt = get_quiz_prompt()
    llm = HuggingFaceHub(
        repo_id="google/flan-t5-base",
        model_kwargs={"temperature": 0.5},
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    return chain.run(context=context)
