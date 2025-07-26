import os
import shutil
import pandas as pd
import logging
import fitz  # PyMuPDF
import docx2txt

from datetime import datetime
from utils import clean_text

# ------------------ Configuration ------------------

SUPPORTED_EXTENSIONS = (".pdf", ".txt", ".docx")
REPORT_PATH = os.path.join("output", "report.csv")
LOG_PATH = os.path.join("logs", "process_log.txt")
ORGANIZED_DIR = os.path.join("output", "organized")

# ------------------ Setup Logging ------------------

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# ------------------ File Parsing ------------------


def extract_text_from_file(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()

    try:
        if ext == ".pdf":
            return extract_pdf(file_path)
        elif ext == ".txt":
            return extract_txt(file_path)
        elif ext == ".docx":
            return extract_docx(file_path)
        else:
            logging.warning(f"Unsupported file type: {file_path}")
            return ""
    except Exception as e:
        logging.error(f"Failed to extract from {file_path}: {e}")
        return ""


def extract_pdf(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return clean_text(text)


def extract_txt(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return clean_text(f.read())


def extract_docx(file_path):
    text = docx2txt.process(file_path)
    return clean_text(text)


# ------------------ Folder Operations ------------------


def create_topic_folder(topic: str) -> str:
    topic_folder_name = topic.strip().replace(" ", "_").lower()
    folder_path = os.path.join(ORGANIZED_DIR, topic_folder_name)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path


def move_file_to_topic_folder(file_path: str, topic: str):
    destination_folder = create_topic_folder(topic)
    filename = os.path.basename(file_path)
    destination_path = os.path.join(destination_folder, filename)

    try:
        shutil.move(file_path, destination_path)
        logging.info(f"Moved: {filename} → {destination_folder}")
    except Exception as e:
        logging.error(f"Failed to move file: {file_path} → {e}")


# ------------------ Report Generation ------------------


def log_to_report(file_path: str, topic: str, keywords: list, summary: str):
    os.makedirs("output", exist_ok=True)

    report_data = {
        "filename": os.path.basename(file_path),
        "topic": topic,
        "keywords": ", ".join(keywords),
        "summary": summary,
        "processed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    df = pd.DataFrame([report_data])
    if not os.path.exists(REPORT_PATH):
        df.to_csv(REPORT_PATH, index=False)
    else:
        df.to_csv(REPORT_PATH, mode="a", index=False, header=False)


# ------------------ Report Deletion   ------------------


def remove_from_report_csv(filename, csv_path="output/report.csv"):
    """
    Remove a specific file entry from the report.csv file.
    """
    if not os.path.exists(csv_path):
        return  # Nothing to update

    try:
        df = pd.read_csv(csv_path)
        df = df[df["Filename"] != filename]  # Remove row where filename matches
        df.to_csv(csv_path, index=False)
        print(f"[CSV] Removed {filename} from report.")
    except Exception as e:
        print(f"[CSV] Error removing {filename} from report: {e}")


# ------------------ Bulk Scanning ------------------


def scan_directory_for_files(directory_path: str) -> list:
    valid_files = []
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.lower().endswith(SUPPORTED_EXTENSIONS):
                valid_files.append(os.path.join(root, file))
    return valid_files
