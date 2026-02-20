<<<<<<< HEAD
import os
from PyPDF2 import PdfReader
from docx import Document

DATA_FOLDER = "knowledge_base"

def extract_text_from_pdf(path):
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(path):
    doc = Document(path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

def extract_text_from_txt(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def load_documents():
    all_chunks = []

    for file in os.listdir(DATA_FOLDER):
        path = os.path.join(DATA_FOLDER, file)

        if file.endswith(".pdf"):
            text = extract_text_from_pdf(path)
        elif file.endswith(".docx"):
            text = extract_text_from_docx(path)
        elif file.endswith(".txt"):
            text = extract_text_from_txt(path)
        else:
            continue

        # Simple chunking
        chunks = text.split("\n\n")
        chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
        all_chunks.extend(chunks)

    return all_chunks
=======
def load_documents():
    with open("nitj_data.txt", "r", encoding="utf-8") as f:
        text = f.read()

    chunks = text.split("\n\n")
    return [chunk.strip() for chunk in chunks if len(chunk.strip()) > 50]
>>>>>>> 3072bd2a7e41953e6e1726351219ad708d87b71f
