from sklearn.feature_extraction.text import TfidfVectorizer
from utils import clean_text, truncate_text
from llama_cpp import Llama
import logging

# --------------- Config ------------------

MODEL_PATH = "models/mistral-7b-instruct-v0.1.Q2_K.gguf"
N_CTX = 2048

# --------------- LLM Init ------------------

try:
    llm = Llama(model_path=MODEL_PATH, n_ctx=N_CTX, n_threads=8, verbose=False)
except Exception as e:
    raise RuntimeError(f"Failed to load LLM in extractor.py: {e}")

# --------------- Keyword Extraction (TF-IDF) ------------------


def extract_keywords_tfidf(text: str, top_n: int = 5) -> list:
    try:
        text = clean_text(text)
        vectorizer = TfidfVectorizer(stop_words="english")
        X = vectorizer.fit_transform([text])
        scores = zip(vectorizer.get_feature_names_out(), X.toarray()[0])
        sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
        keywords = [word for word, score in sorted_scores[:top_n]]
        return keywords
    except Exception as e:
        logging.error(f"[TF-IDF] Keyword extraction failed: {e}")
        return []


# --------------- Keyword Extraction (LLM) ------------------

KEYWORD_PROMPT = """
Extract the 5 most important keywords from the following document:

\"\"\"
{text}
\"\"\"

Return them as a comma-separated list only.
"""


def extract_keywords_llm(text: str, top_n: int = 5) -> list:
    try:
        prompt = KEYWORD_PROMPT.format(
            text=truncate_text(clean_text(text), max_words=400)
        )
        output = llm(prompt, stop=["\n"], temperature=0.2, max_tokens=40)
        response = output["choices"][0]["text"].strip()
        keywords = [kw.strip() for kw in response.split(",") if kw.strip()]
        return keywords[:top_n]
    except Exception as e:
        logging.error(f"[LLM] Keyword extraction failed: {e}")
        return []


# --------------- Summary (Rule-based) ------------------


def summarize_rule_based(text: str, max_sentences: int = 3) -> str:
    try:
        sentences = text.split(".")
        summary = ". ".join(
            [s.strip() for s in sentences if len(s.strip()) > 20][:max_sentences]
        )
        return summary.strip() + "." if summary else ""
    except Exception as e:
        logging.error(f"[Rule-Based] Summary failed: {e}")
        return ""


# --------------- Summary (LLM) ------------------

SUMMARY_PROMPT = """
Summarize the following document in 2–3 sentences:

\"\"\"
{text}
\"\"\"
"""


def summarize_llm(text: str) -> str:
    try:
        prompt = SUMMARY_PROMPT.format(
            text=truncate_text(clean_text(text), max_words=500)
        )
        output = llm(prompt, stop=["\n\n"], temperature=0.3, max_tokens=100)
        return output["choices"][0]["text"].strip()
    except Exception as e:
        logging.error(f"[LLM] Summary failed: {e}")
        return ""
