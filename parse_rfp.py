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

def generate_database(rfp_folder: str, force_rebuild=True): # False by default. True - rebuilds DB on every run
    # joins data_path and chroma-path locations together automatically instaed of typing data/ + RFP-1. 
    chroma_path = os.path.join("chroma-database", rfp_folder)
    data_path = os.path.join("data", rfp_folder) 
    # checks if CHROMA_PATH exists before running --> saves embedding money
    if os.path.exists(chroma_path) and not force_rebuild: # if DB exists and False, just load documents; not need to rebuild DB
        print("Database already exists, loading documents only...")
        return load_documents(data_path) 
    
    if os.path.exists(chroma_path): # if DB exists and True; chroma-database is deleted and rebuilt with following few lines
        shutil.rmtree(chroma_path)
    documents = load_documents(data_path)
    chunks = split_text(documents)
    save_to_chroma(chunks, rfp_folder)
    return documents

def load_documents(data_path: str): # this extracts PDF text from ONE FOLDER only i.e data/RFP-1
    documents = [] # creates a list where PDF pages will go
    for pdf_path in glob_module.glob(os.path.join(data_path, "*.pdf")): # loops through list of files of data_path/*pdf one at a time; glob_modul... find every file on laptop with data_path/*pdf specification
        with pdfplumber.open(pdf_path) as pdf: # opens PDF file using pdfplumber; each pdf object represents one document
            for page_num, page in enumerate(pdf.pages): # pdf.pages is list of each PDF's page. enumerate also stores page_num alongside the page object 
                text = page.extract_text() or "" # extracts the text off of each page object
                if text.strip():  # skip blank pages
                    documents.append(Document(  # add this Document to list of documents contaiing text and metadata
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
    sorted_docs = sorted(documents, key=lambda d: d.metadata.get("page", 0)) # sorts all documents by page number (smallest to largest). "page" is page #, not page object
    combined = "\n\n".join(d.page_content for d in sorted_docs) # joins text from each page in sorted docs, sperated by new lines
    return combined[:max_chars] # gets chars from index 0 to max_chars

# extract_tier2
def get_relevant_text(rfp_folder: str) -> str:
    chroma_path = os.path.join("chroma-database", rfp_folder)
    query_text = """
    proposal instructions to offerors.
    submission requirements.
    proposal preparation instructions.
    section l instructions.
    offerors shall submit.
    page limitations.
    volume structure.
    formatting requirements.
    font size margins spacing.
    required forms and certifications.
    proposal due date.
    submission email or portal.
    pre-proposal conference.
    questions due.
    late proposal instructions.
    electronic copies hard copies.
    step 1 step 2 proposal submission.
    """    
    db = Chroma(persist_directory=chroma_path, embedding_function=OpenAIEmbeddings(model="text-embedding-3-small"))
    print(f"Collection count: {db._collection.count()}") 
    relevant_chunks = db.similarity_search_with_relevance_scores(query_text, k=10)
    # for doc, score in relevant_chunks:  
       # print(f"Score: {score:.3f} | {doc.page_content[:100]}")
    if len(relevant_chunks) == 0 or relevant_chunks[0][1] < 0.3:
        print(f"Unable to find matching results.")
        return 
    results = "\n\n---\n\n".join([doc.page_content for doc, _score in relevant_chunks])
    return results

# extract_tier3
def find_section_m_pages(documents: list[Document], rfp_folder: str):      
    page_numbers = []
    chroma_path = os.path.join("chroma-database", rfp_folder)
    query_text = """
    Section M evaluation factors for award.
    Evaluation criteria.
    Basis for award.
    Government will evaluate proposals.
    Award will be made to the offeror.
    Best value tradeoff.
    Lowest price technically acceptable.
    Evaluation factors and subfactors.
    Technical factor.
    Past performance factor.
    Price evaluation.
    Relative importance of factors.
    Technical is more important than price.
    Key personnel evaluation.
    Corporate experience.
    Offerors will be evaluated.
    """
    db = Chroma(persist_directory=chroma_path, embedding_function=OpenAIEmbeddings(model="text-embedding-3-small"))
    relevant_chunks = db.similarity_search_with_relevance_scores(query_text, k=10)
    if len(relevant_chunks) == 0 or relevant_chunks[0][1] < 0.3:
        print(f"Unable to find matching results.")
        return []
    sorted_docs = sorted(documents, key=lambda d: d.metadata.get("page", 0))
    for d in sorted_docs:
        for doc, _score in relevant_chunks:
            if(doc.metadata.get("page") == d.metadata.get("page")):
                page_numbers.append(d.metadata.get("page"))
    return list(set(page_numbers))

# extract_tier3
def tier3_page_content(documents: list[Document], page_numbers: list[int]):
    result = ""
    sorted_docs = sorted(documents, key=lambda d: d.metadata.get("page", 0))
    for d in sorted_docs:
        if(d.metadata.get("page") in page_numbers):
            result += (f"\n\n{d.page_content}")
    return result