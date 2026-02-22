import os
import re
from PyPDF2 import PdfReader
from docx import Document
from typing import List, Dict

DATA_FOLDER = "knowledge_base"

def extract_text_from_pdf(path: str) -> List[Dict]:
    """
    Extract text from PDF with better formatting and metadata
    Returns: List of dicts with text, source, page
    """
    reader = PdfReader(path)
    documents = []
    
    for page_num, page in enumerate(reader.pages):
        text = page.extract_text()
        
        # Clean up extracted text
        text = clean_text(text)
        
        if text.strip():  # Only add non-empty pages
            documents.append({
                'text': text,
                'source': path,
                'page': page_num + 1,
                'file_type': 'pdf'
            })
    
    return documents


def extract_text_from_docx(path: str) -> List[Dict]:
    """
    Extract text from DOCX with proper structure
    """
    doc = Document(path)
    documents = []
    
    # Extract paragraphs
    full_text = "\n".join([para.text for para in doc.paragraphs])
    full_text = clean_text(full_text)
    
    if full_text.strip():
        documents.append({
            'text': full_text,
            'source': path,
            'page': 1,
            'file_type': 'docx'
        })
    
    return documents


def extract_text_from_txt(path: str) -> List[Dict]:
    """
    Extract text from TXT files
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        
        text = clean_text(text)
        
        if text.strip():
            return [{
                'text': text,
                'source': path,
                'page': 1,
                'file_type': 'txt'
            }]
    except Exception as e:
        print(f"Error reading {path}: {e}")
    
    return []


def clean_text(text: str) -> str:
    """
    Clean and normalize extracted text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep structure
    text = re.sub(r'[^\w\s\.\,\:\;\-\(\)\/]', '', text)
    
    # Fix hyphenated words
    text = re.sub(r'(\w)-\s+(\w)', r'\1-\2', text)
    
    return text.strip()


def semantic_chunking(text: str, chunk_size: int = 300, overlap: int = 50) -> List[str]:
    """
    Split text into chunks with overlap for better context preservation
    Uses sentences as boundaries instead of arbitrary splits
    
    Args:
        text: Text to chunk
        chunk_size: Target size in characters (roughly 60 words)
        overlap: Number of characters to overlap between chunks
    
    Returns:
        List of chunk strings
    """
    # Split by sentence boundaries (. ! ?)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < chunk_size:
            current_chunk += " " + sentence
        else:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            current_chunk = sentence
    
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    # Add overlap (last part of previous chunk + current chunk)
    chunked_with_overlap = []
    for i, chunk in enumerate(chunks):
        if i > 0 and overlap > 0:
            # Add last N chars from previous chunk
            prev_overlap = chunks[i-1][-overlap:] if len(chunks[i-1]) > overlap else chunks[i-1]
            overlap_chunk = prev_overlap + " " + chunk
            chunked_with_overlap.append(overlap_chunk)
        else:
            chunked_with_overlap.append(chunk)
    
    return [c.strip() for c in chunked_with_overlap if c.strip()]


def load_documents() -> List[Dict]:
    """
    Load all documents from knowledge base folder
    Returns: List of document chunks with metadata
    """
    all_docs = []
    
    if not os.path.exists(DATA_FOLDER):
        print(f"Warning: {DATA_FOLDER} folder not found")
        return all_docs
    
    for file in os.listdir(DATA_FOLDER):
        path = os.path.join(DATA_FOLDER, file)
        
        if not os.path.isfile(path):
            continue
        
        print(f"Processing: {file}")
        
        documents = []
        
        try:
            if file.endswith(".pdf"):
                documents = extract_text_from_pdf(path)
            elif file.endswith(".docx"):
                documents = extract_text_from_docx(path)
            elif file.endswith(".txt"):
                documents = extract_text_from_txt(path)
            else:
                continue
        except Exception as e:
            print(f"Error processing {file}: {e}")
            continue
        
        # Chunk each document
        for doc in documents:
            chunks = semantic_chunking(doc['text'], chunk_size=300, overlap=50)
            
            for idx, chunk in enumerate(chunks):
                all_docs.append({
                    'text': chunk,
                    'source': doc['source'],
                    'page': doc['page'],
                    'file_type': doc['file_type'],
                    'chunk_id': f"{file}_page{doc['page']}_chunk{idx}"
                })
        
        print(f"  ✓ Extracted {len(all_docs)} total chunks so far")
    
    print(f"\nTotal chunks loaded: {len(all_docs)}")
    return all_docs


if __name__ == "__main__":
    docs = load_documents()
    for i, doc in enumerate(docs[:3]):  # Print first 3
        print(f"\n--- Chunk {i+1} ---")
        print(f"Source: {doc['source']}, Page: {doc['page']}")
        print(f"Text: {doc['text'][:200]}...")