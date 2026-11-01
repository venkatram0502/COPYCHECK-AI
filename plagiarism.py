import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def calculate_similarity(text1, text2):
    a, b = preprocess_text(text1), preprocess_text(text2)
    if not a or not b:
        return 0.0
    try:
        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        matrix = vectorizer.fit_transform([a, b])
        return float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0] * 100)
    except ValueError:
        return 0.0

def split_sentences(text):
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [p.strip() for p in parts if len(p.strip().split()) >= 5]

def find_matching_sentences(text1, text2):
    right = {preprocess_text(s): s for s in split_sentences(text2)}
    found, seen = [], set()
    for sentence in split_sentences(text1):
        key = preprocess_text(sentence)
        if key in right and key not in seen:
            found.append(sentence)
            seen.add(key)
    return found

def compare_documents(name1, text1, name2, text2, kind):
    return {
        "source": name1, "target": name2, "kind": kind,
        "score": round(calculate_similarity(text1, text2), 2),
        "matches": find_matching_sentences(text1, text2)
    }
