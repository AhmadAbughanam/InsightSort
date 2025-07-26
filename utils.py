import os
import re
from datetime import datetime

# ------------------ Text Cleaning ------------------


def clean_text(text: str) -> str:
    """
    Remove excessive whitespace, control characters, and normalize spacing.
    """
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)  # Normalize all whitespace
    text = re.sub(r"[^\x20-\x7E]+", "", text)  # Remove non-printable characters
    return text.strip()


# ------------------ Truncate Long Text ------------------


def truncate_text(text: str, max_words: int = 500) -> str:
    """
    Return only the first `max_words` from the input text.
    """
    words = text.split()
    return " ".join(words[:max_words])


# ------------------ Extension Validator ------------------


def is_supported_file(filename: str) -> bool:
    SUPPORTED_EXTENSIONS = (".pdf", ".txt", ".docx")
    return filename.lower().endswith(SUPPORTED_EXTENSIONS)


# ------------------ Safe Topic Folder Name ------------------


def format_topic_folder_name(topic: str) -> str:
    """
    Clean topic to make a valid folder name.
    """
    topic = topic.strip().lower().replace(" ", "_")
    topic = re.sub(r"[^\w_]", "", topic)  # Remove invalid characters
    return topic


# ------------------ Timestamp Helper ------------------


def current_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
