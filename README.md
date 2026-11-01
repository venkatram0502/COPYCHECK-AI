# CopyCheck AI – Enhanced Streamlit NLP Project

## Features
- Compare multiple uploaded PDF/TXT documents pairwise.
- Compare uploaded documents against local reference files in `dataset/`.
- TF-IDF with unigram/bigram features and cosine similarity.
- Exact matching sentence display with highlighted text.
- Dashboard metrics and comparison chart.
- Downloadable PDF analysis report.

## Run on Windows PowerShell
```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe -m streamlit run app.py
```
If PowerShell blocks activation, use the commands above; activation is not required.

## Render
Build command: `pip install -r requirements.txt`
Start command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`

## Reference collection
Add `.txt` or selectable-text `.pdf` files to `dataset/`.

## Limitations
This is an educational similarity-screening prototype, not a certified plagiarism detector. It compares uploaded documents with each other and with the local reference collection only. It does not search the public internet or commercial databases. Similarity is not proof of plagiarism. Scanned PDFs need OCR.
