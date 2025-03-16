import os
import json

from dotenv import load_dotenv

import google.generativeai as genai
from langchain.docstore.document import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts import PromptTemplate

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def parse_bill_info(pdf_text):
    """
    Feeds the extracted PDF text into the LLM to obtain bill details.
    The LLM is expected to return a JSON object with:
    { "Title": "", "Date": "", "Type": "", "Sector": "", "State": "", "Topics": "" }
    """
    prompt_template = """
        You are given the text of a legal document from a PDF file.
        Extract the following details:
        1. Type of the bill (choose from: "State level sectoral", "Federal level", "Comprehensive State level", "GDPR").
        Choose Comprehensive State Level if it is a state legislation related to more than one sector. 
        2. If the bill is "State level sectoral", specify the sector (choose from: "Health", "Education", "Finance", 
        "Telecommunications & Technology", "Government & Public Sector", "Retail & E-Commerce", "Employment & HR", 
        "Media & Advertising", "Critical Infrastructure (Energy, Transportation, etc.)", 
        "Children’s Data Protection"). Otherwise, set it to null.
        3. The latest date mentioned in the bill in MMDDYYYY format.
        4. For state-level laws ("State level sectoral" or "Comprehensive State level"), which state is it 
        associated with (e.g., "Texas", "California").
        5. The title of the bill in 15 words or less. Use format (State name as the first word if it is a 
        State level sectoral bill or Comprehensive State level bill. If it is not in these categories, write Federal as
        the first word. Then put a colon ":" and write the title of the bill after that)
        6. A list of no more than six topics that the bill is related to

        Return the information as a JSON object EXACTLY in the following format:
        {{"Title": "", "Date": "", "Type": "", "Sector": "", "State": "", "Topics": []}}

        Bill text:
        {context}
    """
    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash-8b", temperature=0.2)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context"])
    chain = create_stuff_documents_chain(llm=model, prompt=prompt)

    doc = Document(page_content=pdf_text)

    result = chain.invoke({"context": [doc]})
    try:

        if result.startswith("```json"):
            result = result[len("```json") :].strip()

        if result.endswith("```"):
            result = result[:-3].strip()

        bill_info = json.loads(result)

    except json.JSONDecodeError as json_err:
        print("Error parsing LLM response:", json_err)
        bill_info = {}

    # print(f"bill_info is {bill_info}")
    return bill_info


def get_conversational_chain():
    """
    Sets up a QA chain using ChatGoogleGenerativeAI and a custom prompt template.
    """
    prompt_template = """
        If the context has documents related to the question, start your answer with 
        "According to my database of information, ".
        If the context does not have documents related to the question, start your answer with 
        "Sorry, the database does not have specific information about your question". After this, 
        say on the next line "According to my training data, the answer to your question is...", and then write 
        the answer on the next line from your training data. 

        Context:
        {context}

        Question:
        {question}

        Answer:
    """
    model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-001",
        temperature=0.2,
        system_prompt=(
            """You are a helpful assistant that MUST write an introduction,
            bullet points for the main body of the response, and a conclusion"""
        ),
    )
    prompt = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )
    return create_stuff_documents_chain(llm=model, prompt=prompt)


def get_confirmation_result_chain():
    """
    Sets up a QA chain using ChatGoogleGenerativeAI and a custom prompt template.
    """
    prompt_template = """
        I will provide you the answer to a question I asked an LLM model based on a given context.  
        Look at the question and the answer, and make sure that the answer is correct and coherent. 
        DO NOT MENTION THAT I HAVE ASKED YOU THIS QUESTION BEFORE.

        If the answer contains "Sorry, the database does not have specific information about your question" or a similar
        phrase, state "Sorry, the database does not have specific information about your question”.

        If the answer does not make sense, state "Sorry, the LLM cannot currently generate a good enough
        response for this question. Please refer to the side table and see if there is anything from
        those topics that you would like to know about."   

        If the answer does make sense, state "The document database has an answer to your question. Here is the 
        structured response based on TPLC's database", and then write the answer with an introduction, body 
        and conclusion for the response. , based on the question and answer and context you were provided. 
        DO NOT USE THE WORDS INTRODUCTION, BODY, CONCLUSION, in your response. 
        THERE MUST BE AN INTRODUCTION AND CONCLUSION part to your response no matter what. 

        Context:
        {context}

        Question:
        {question}

        Previous Answer:
        {answer}

        Answer:
    """
    model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-001",
        temperature=0.2,
        system_prompt=(
            """You are a helpful assistant that MUST write an introduction,
            bullet points, and a conclusion"""
        ),
    )
    prompt = PromptTemplate(
        template=prompt_template, input_variables=["context", "question", "answer"]
    )
    return create_stuff_documents_chain(llm=model, prompt=prompt)


def get_document_specific_summary():
    """
    Sets up a QA chain using ChatGoogleGenerativeAI and a custom prompt template.
    """
    prompt_template = """
    I will provide text that is concatinated responses from an LLM model in response
    to a question about data privacy bills. I need you summarize the text in a way
    that is easy to read and understand without adding any additional information. 
    The summary should be in short paragraphs or bullet points.

    Text:
    {text}

    Summary:
    """
    model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-001",
        temperature=0.2,
        system_prompt=(
            """You are a helpful assistant that summarizes text without adding any additional information. """
        ),
    )
    prompt = PromptTemplate(template=prompt_template, input_variables=["text"])
    return create_stuff_documents_chain(llm=model, prompt=prompt)



def llm_simplify_chunk_text():
    prompt_template = """
        Provide any information from the provided context that is relevant to the question.
        Only use the information from the context to answer the question.
        Be brief, answer in points. Dont give any introductions and get straight to the point. 

        Context:
        {context}

        Question:
        {question}

        Answer:
    """
    model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-001",
        temperature=0.1,
        system_prompt=(
            """
            Your knowledge is only limited to the information in the provided context.
            Be brief and answer in points without introduction or context."""
        ),
    )
    prompt = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )
    return create_stuff_documents_chain(llm=model, prompt=prompt)