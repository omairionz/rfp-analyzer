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

def main():
    generate_database()

def generate_database(rfp_folder: str, force_rebuild=False):
    data_path = os.path.join("data", rfp_folder)
    chroma_path = os.path.join("chroma-database", rfp_folder)
    # checks if CHROMA_PATH exists before running --> saves embedding money
    if os.path.exists(chroma_path) and not force_rebuild:
        print("Database already exists, loading documents only...")
        return load_documents(data_path) 
    
    if os.path.exists(chroma_path):
        shutil.rmtree(chroma_path)
    documents = load_documents(data_path)
    chunks = split_text(documents)
    save_to_chroma(chunks, rfp_folder)
    return documents

def load_documents(data_path: str):
    documents = []
    for pdf_path in glob_module.glob(os.path.join(data_path, "*.pdf")):
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
    # regular text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        add_start_index=True
    )
    chunks = text_splitter.split_documents(documents)
    return chunks

def save_to_chroma(chunks: list[Document], rfp_folder: str):
    # regular embeddings creation and saving
    chroma_path = os.path.join("chroma-database", rfp_folder)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    db = Chroma.from_documents(
        chunks,
        embeddings,
        persist_directory=chroma_path
    )

# extract_tier1
def get_first_pages_text(documents: list[Document], max_chars: int = 18000) -> str:
    # gets the first 18000 chars from documents --> i.e. first pages
    sorted_docs = sorted(documents, key=lambda d: d.metadata.get("page", 0))
    combined = "\n\n".join(d.page_content for d in sorted_docs)
    return combined[:max_chars]

# extract_tier2
def get_relevant_text(rfp_folder: str) -> str:
    chroma_path = os.path.join("chroma-database", rfp_folder)
    query_text = "Step 1 Step 2 offerors shall submit proposal response instructions"
    db = Chroma(persist_directory=chroma_path, embedding_function=OpenAIEmbeddings(model="text-embedding-3-small"))

    print(f"Collection count: {db._collection.count()}")  # add this

    relevant_chunks = db.similarity_search_with_relevance_scores(query_text, k=10)

    for doc, score in relevant_chunks:  # add this
        print(f"Score: {score:.3f} | {doc.page_content[:100]}")

    if len(relevant_chunks) == 0 or relevant_chunks[0][1] < 0.3:
        print(f"Unable to find matching results.")
        return 
    
    results = "\n\n---\n\n".join([doc.page_content for doc, _score in relevant_chunks])
    return results
