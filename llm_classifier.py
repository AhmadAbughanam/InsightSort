from llama_cpp import Llama
import logging
from utils import clean_text, truncate_text

# --------------- Config ------------------
MODEL_PATH = "models/mistral-7b-instruct-v0.1.Q2_K.gguf"
N_CTX = 2048  # Adjust to available VRAM
TOPIC_LIST = [
    "Tech",
    "Health",
    "Finance",
    "Education",
    "Legal",
    "Personal",
    "Notes",
    "Misc",
]

# --------------- Load LLM ------------------
try:
    llm = Llama(model_path=MODEL_PATH, n_ctx=N_CTX, n_threads=8, verbose=False)
except Exception as e:
    raise RuntimeError(f"Failed to load LLM: {e}")

# --------------- Prompt Template ------------------

CLASSIFY_PROMPT_TEMPLATE = """
You are a smart document classifier. Classify the following document into one of the following categories:
{categories}

Document:
\"\"\"
{text}
\"\"\"

Respond only with the topic name, nothing else.
"""

# --------------- Main Classifier ------------------


def classify_with_llm(document_text: str) -> str:
    try:
        # Step 1: Clean & truncate long content
        text = truncate_text(clean_text(document_text), max_words=500)

        # Step 2: Format prompt
        prompt = CLASSIFY_PROMPT_TEMPLATE.format(
            categories=", ".join(TOPIC_LIST), text=text
        )

        # Step 3: Run LLM
        output = llm(prompt, stop=["\n", "\n\n"], temperature=0.2, max_tokens=10)
        raw_response = output["choices"][0]["text"].strip()

        # Step 4: Post-process result
        topic = normalize_topic(raw_response)

        if topic:
            logging.info(f"[LLM] Classified as: {topic}")
            return topic
        else:
            logging.warning(f"[LLM] Invalid response: '{raw_response}'")
            return "Misc"

    except Exception as e:
        logging.error(f"[LLM] Classification failed: {e}")
        return "Misc"


# --------------- Utilities ------------------


def normalize_topic(response: str) -> str:
    response_clean = response.strip().lower()
    for topic in TOPIC_LIST:
        if response_clean == topic.lower():
            return topic
    return None
