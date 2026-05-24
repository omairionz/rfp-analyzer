# parse_rfp.py
# extracts text from a PDF - similar to create_database.py from other repos

from langchain_core.documents import Document
import pdfplumber
import glob as glob_module
from langchain_text_splitters import RecursiveCharacterTextSplitter 
from langchain_chroma import Chroma 
from langchain_openai import OpenAIEmbeddings
import os 
import shutil
from dotenv import load_dotenv

load_dotenv()

DATA_PATH = "data/RFP-1"
CHROMA_PATH = "chroma-database"

def main():
    generate_database()

def generate_database(force_rebuild=False):
    if os.path.exists(CHROMA_PATH) and not force_rebuild:
        print("Database already exists, loading documents only...")
        return load_documents() 
    
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
    documents = load_documents()
    chunks = split_text(documents)
    save_to_chroma(chunks)
    return documents

def load_documents():
    documents = []
    for pdf_path in glob_module.glob(os.path.join(DATA_PATH, "*.pdf")):
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                if text.strip():  # skip blank pages
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "source": pdf_path,
                            "page": page_num + 1  # 1-indexed
                        }
                    ))
    return documents

def split_text(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        add_start_index=True
    )
    chunks = text_splitter.split_documents(documents)
    return chunks

def get_first_pages_text(documents: list[Document], max_chars: int = 18000) -> str:
    sorted_docs = sorted(documents, key=lambda d: d.metadata.get("page", 0))
    combined = "\n\n".join(d.page_content for d in sorted_docs)
    return combined[:max_chars]

def save_to_chroma(chunks: list[Document]):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    db = Chroma.from_documents(
        chunks,
        embeddings,
        persist_directory=CHROMA_PATH
    )
