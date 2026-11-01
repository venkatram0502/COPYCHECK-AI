import os
from pdf_reader import extract_text

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "dataset")

def load_reference_documents():
    documents = []
    if not os.path.isdir(DATASET_DIR):
        return documents
    for filename in sorted(os.listdir(DATASET_DIR)):
        path = os.path.join(DATASET_DIR, filename)
        if not os.path.isfile(path) or not filename.lower().endswith((".txt", ".pdf")):
            continue
        try:
            with open(path, "rb") as file:
                content = extract_text(filename, file.read())
            if content.strip():
                documents.append({"filename": filename, "text": content})
        except Exception as exc:
            print(f"Skipping {filename}: {exc}")
    return documents
