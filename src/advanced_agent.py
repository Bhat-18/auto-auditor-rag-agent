import os

from typing import TypedDict, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langgraph.graph import StateGraph, END

# --- THE FIX IS HERE: Import directly from Pydantic ---
from pydantic import BaseModel, Field

# --- 1. SETUP ---
# Define the state of our agent
class AgentState(TypedDict):
    question: str
    documents: List[str]
    generation: str
    web_search: str # "Yes" or "No"

# Load Embedding Model
hf_embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Connect to Vector Database
DB_PATH = "./chroma_db_hf"
vectorstore = Chroma(persist_directory=DB_PATH, embedding_function=hf_embedding)
retriever = vectorstore.as_retriever(search_kwargs={"k": 5}) # Fetch top 5 chunks

# --- 2. DEFINE NODES (The Actions) ---

def retrieve(state):
    print("--- 🔍 RETRIEVING DOCUMENTS ---")
    question = state["question"]
    documents = retriever.invoke(question)
    return {"documents": documents, "question": question}

def grade_documents(state):
    print("--- ⚖️ GRADING RELEVANCE ---")
    question = state["question"]
    documents = state["documents"]
    
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    class Grade(BaseModel):
        binary_score: str = Field(description="'yes' or 'no'")

    structured_llm_grader = llm.with_structured_output(Grade)
    
    # Broader grading prompt for R&D + EMDG + ESIC
    system = (
        "You are a strict grader checking for relevance to Australian Business Law. "
        "Check if the document contains rules regarding: "
        "1. R&D Tax Incentive "
        "2. Export Market Development Grants (EMDG) "
        "3. Early Stage Innovation Companies (ESIC). "
        "If the document contains ANY keywords or rules relevant to the user's question, grade it as 'yes'."
    )
    
    grade_prompt = ChatPromptTemplate.from_messages([("system", system), ("human", "Doc: {document} \n Question: {question}")])
    grader = grade_prompt | structured_llm_grader
    
    filtered_docs = []
    
    for d in documents:
        score = grader.invoke({"question": question, "document": d.page_content})
        grade = score.binary_score
        
        if grade == "yes":
            print("   ✅ DOCUMENT KEPT")
            filtered_docs.append(d)
        else:
            print("   ❌ DOCUMENT REJECTED (Irrelevant)")
            
    if not filtered_docs:
        print("⚠️ All docs rejected. Loosening strictness for this turn.")
        filtered_docs = documents 
        rewrite = "Yes" 
    else:
        rewrite = "No"
        
    return {"documents": filtered_docs, "question": question, "web_search": rewrite}

def generate(state):
    print("--- ✍️ GENERATING ANSWER ---")
    question = state["question"]
    documents = state["documents"]
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    # --- PROMPT UPGRADE: STRUCTURED OUTPUT ---
    prompt = ChatPromptTemplate.from_template(
        "You are a strict Auditor for Australian Government Grants (R&D, EMDG, ESIC). \n"
        "Analyze the user's query based *only* on the provided context. \n\n"
        "STRUCTURE YOUR ANSWER EXACTLY LIKE THIS: \n"
        "**1. PRELIMINARY ASSESSMENT:** [Start with: ELIGIBLE / INELIGIBLE / CAUTION / UNCLEAR] \n"
        "**2. ANALYSIS:** [Explain why in 2-3 concise sentences] \n"
        "**3. APPLICABLE RULES:** [Cite specific rules found in context, e.g., 'Feedstock Adjustment' or 'Turnover Limit'] \n"
        "**4. ACTION:** [One specific next step for the user] \n\n"
        "If the context does not contain the answer, say 'I cannot find this in the official guidelines.' \n"
        "Context: {context} \n"
        "Question: {question} \n"
        "Answer:"
    )
    chain = prompt | llm | StrOutputParser()
    generation = chain.invoke({"context": documents, "question": question})
    return {"generation": generation}

# --- 3. BUILD GRAPH ---
workflow = StateGraph(AgentState)

workflow.add_node("retrieve", retrieve)
workflow.add_node("grade_documents", grade_documents)
workflow.add_node("generate", generate)

workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "grade_documents")
workflow.add_edge("grade_documents", "generate")
workflow.add_edge("generate", END)

app = workflow.compile()