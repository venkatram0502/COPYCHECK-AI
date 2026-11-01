import pymupdf

def extract_text(filename, file_bytes):
    extension = filename.rsplit(".", 1)[-1].lower()
    if extension == "pdf":
        document = pymupdf.open(stream=file_bytes, filetype="pdf")
        try:
            return "\n".join(page.get_text("text") for page in document)
        finally:
            document.close()
    if extension == "txt":
        return file_bytes.decode("utf-8", errors="ignore")
    raise ValueError("Only PDF and TXT files are supported.")
