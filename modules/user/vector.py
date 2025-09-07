import os
import fitz 
import re
from dotenv import load_dotenv

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load API Key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("❌ Missing GOOGLE_API_KEY in .env file")

#  CONFIGURATION 
pdf_files = [
    r"E:\Project\constitution\laws\Administrative_and_Public_Law.pdf",
    r"E:\Project\constitution\laws\Consumer_and_Commercial_Law.pdf",
    r"E:\Project\constitution\laws\Cyber_and_ICT_Laws.pdf",
    r"E:\Project\constitution\laws\Employment_and_Labour_Laws.pdf",
    r"E:\Project\constitution\laws\Environmental_and_Wildlife_Laws.pdf",
    r"E:\Project\constitution\laws\Family_and_Personal_Laws.pdf",
    r"E:\Project\constitution\laws\Fundamental_Rights_and_Constitutional_Laws.pdf",
    r"E:\Project\constitution\laws\General_Civil_and_Criminal_Laws.pdf",
    r"E:\Project\constitution\laws\Human_Rights_and_Gender_Laws.pdf",
    r"E:\Project\constitution\laws\Motor_Traffic_law.pdf",
    r"E:\Project\constitution\laws\Property_and_Land_Laws.pdf",
    r"E:\Project\constitution\laws\Rent_Laws.pdf"
]

db_location = "./chroma_legal_db"
collection_name = "Sri_Lanka_Legal_Docs"
chunk_size = 1000
chunk_overlap = 150

#  Initialize Embeddings
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=api_key
)

# PDF LOADER 
def load_pdf(file_path: str) -> str:
    text = ""
    with fitz.open(file_path) as pdf_document:
        for page in pdf_document:
            text += page.get_text()
    return text

# TEXT CLEANER 
def clean_text(text: str) -> str:
    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r"Page\s*\d+", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()

# TEXT SPLITTER 
def split_text(raw_text: str, source_name: str) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )
    chunks = splitter.split_text(raw_text)
    return [
        Document(page_content=chunk, metadata={"source": source_name, "chunk": i})
        for i, chunk in enumerate(chunks)
    ]

# VECTOR STORE SETUP
add_documents = not os.path.exists(db_location)

vector_store = Chroma(
    collection_name=collection_name,
    persist_directory=db_location,
    embedding_function=embeddings
)

if add_documents:
    all_documents = []
    for pdf_path in pdf_files:
        if not os.path.exists(pdf_path):
            print(f"⚠️ Skipped missing file: {pdf_path}")
            continue
        raw_text = load_pdf(pdf_path)
        cleaned_text = clean_text(raw_text)
        source_name = os.path.basename(pdf_path)
        split_docs = split_text(cleaned_text, source_name)
        print(f"📄 {source_name} → {len(split_docs)} chunks")
        all_documents.extend(split_docs)

    vector_store.add_documents(all_documents)
    vector_store.persist()

# RETRIEVER INSTANCE 
retriever = vector_store.as_retriever(
    search_type="mmr",  # Maximal Marginal Relevance
    search_kwargs={
        "k": 10,
        "fetch_k": 20,
        "lambda_mult": 0.8
    }
)
