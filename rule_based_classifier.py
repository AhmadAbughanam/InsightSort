from utils import clean_text
import logging

# ------------------ Rule Definitions ------------------

TOPIC_KEYWORDS = {
    "Tech": [
        "ai",
        "software",
        "machine learning",
        "programming",
        "cloud",
        "neural",
        "python",
        "server",
        "network",
    ],
    "Health": [
        "health",
        "medicine",
        "doctor",
        "exercise",
        "diet",
        "mental",
        "therapy",
        "disease",
    ],
    "Finance": [
        "stock",
        "investment",
        "money",
        "interest rate",
        "bank",
        "loan",
        "inflation",
        "trading",
    ],
    "Education": [
        "student",
        "exam",
        "university",
        "teacher",
        "school",
        "lecture",
        "curriculum",
    ],
    "Legal": [
        "law",
        "contract",
        "court",
        "legal",
        "evidence",
        "attorney",
        "rights",
        "jurisdiction",
    ],
    "Personal": ["journal", "diary", "my life", "experience", "feelings", "goals"],
    "Notes": ["notes", "summary", "lecture notes", "meeting", "to-do", "checklist"],
}

DEFAULT_TOPIC = "Misc"

# ------------------ Classification Logic ------------------


def classify_rule_based(text: str) -> str:
    """
    Uses keyword-matching to classify a document into a topic.
    """
    try:
        text = clean_text(text).lower()
        scores = {}

        for topic, keywords in TOPIC_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                scores[topic] = score

        if scores:
            best_topic = max(scores, key=scores.get)
            logging.info(f"[Rule-Based] Classified as: {best_topic}")
            return best_topic
        else:
            logging.info("[Rule-Based] No match found. Using fallback.")
            return DEFAULT_TOPIC

    except Exception as e:
        logging.error(f"[Rule-Based] Failed: {e}")
        return DEFAULT_TOPIC
