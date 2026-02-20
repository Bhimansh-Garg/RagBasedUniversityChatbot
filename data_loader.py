def load_documents():
    with open("nitj_data.txt", "r", encoding="utf-8") as f:
        text = f.read()

    chunks = text.split("\n\n")
    return [chunk.strip() for chunk in chunks if len(chunk.strip()) > 50]
