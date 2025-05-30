from langchain_openai import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
import tempfile
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def summarize_document(vector_db, doc_title="Summary"):
    retriever = vector_db.as_retriever(search_kwargs={"k": 5})

    try:
        docs = retriever.invoke("generate comprehensive document summary")
    except (AttributeError, TypeError):
        docs = retriever.get_relevant_documents("generate comprehensive document summary")
    
    context = " ".join([doc.page_content for doc in docs])

    system_template = """
    You are an expert academic summarizer. Your task is: given text (context) from a document, 
    create a comprehensive, well-structured summary that captures all of the key points, 
    main concepts, and important details to help a student learn about what was included in the document
    without having to read the whole document. 
    
    Make sure to cover all topics, concepts and details of the document.
    Make the summary educational and useful for a student reviewing this material.
    Include section headings where appropriate (with #, ## etc).
    Organize the content in a logical flow.
    Don't include any extra text (e.g. "Here's your summary...") other than the summary its self.
    """

    human_template = """
    CONTEXT:
    {context}
    """

    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.3,
    )

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_template),
        HumanMessagePromptTemplate.from_template(human_template)
    ])

    chain = prompt | llm
    response = chain.invoke({"context": context})

    if hasattr(response, 'content'):
        summary_text = response.content
    else:
        summary_text = str(response)
    
    pdf_path = generate_summary_pdf(summary_text, doc_title)

    return summary_text, pdf_path

    

def generate_summary_pdf(summary_text, doc_title):
    # temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf_path = temp_file.name
    temp_file.close()
    
    # PDF document
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Define custom styles presets for document
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=1,
        spaceAfter=20
    )
    
    lines = summary_text.split('\n')
    story = []
    
    # Doc title
    story.append(Paragraph(f"{doc_title}", title_style))
    
    # Process summary content with heading formatting
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        if line.startswith('#'):
            # title
            heading = line.lstrip('#').strip()
            story.append(Paragraph(heading, styles['Heading2']))
        elif line.isupper() and len(line) > 3:
            # subtitle
            story.append(Paragraph(line, styles['Heading3']))
        else:
            # paragraph
            story.append(Paragraph(line, styles['Normal']))
            story.append(Spacer(1, 10))
    
    # Build the PDF
    doc.build(story)
    
    return pdf_path