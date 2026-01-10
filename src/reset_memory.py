import os
import shutil
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# --- CONFIGURATION ---
DATA_PATH = "./data/rules"  # Where your PDFs are
DB_PATH = "./chroma_db_hf"  # Where the database lives
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2" # FORCE 384 DIMENSIONS

def reset_memory():
    # 1. DELETE OLD DATABASE (The Fix)
    if os.path.exists(DB_PATH):
        print(f"🗑️  Deleting mismatched database at {DB_PATH}...")
        shutil.rmtree(DB_PATH)
        print("✅  Old memory wiped.")
    else:
        print("ℹ️  No existing database found. Creating new one.")

    # 2. LOAD PDFS
    print("📂  Loading PDFs from data/rules...")
    loader = DirectoryLoader(DATA_PATH, glob="*.pdf", loader_cls=PyPDFLoader)
    documents = loader.load()
    print(f"📄  Found {len(documents)} pages of legislation.")

    # 3. SPLIT TEXT
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(documents)
    print(f"🧩  Split into {len(chunks)} knowledge chunks.")

    # 4. CREATE NEW DATABASE
    print("🧠  Embedding data with 384-dimension model...")
    embedding_model = HuggingFaceEmbeddings(model_name=MODEL_NAME)
    
    vectorstore = Chroma.from_documents(
        documents=chunks, 
        embedding=embedding_model, 
        persist_directory=DB_PATH
    )
    print("✅  SUCCESS: New compatible database created!")

if __name__ == "__main__":
    reset_memory()