import sqlite3
import os
import logging
from datetime import datetime

DB_PATH = "output/insight_memory.db"

# ------------------ Initialize ------------------


def init_db():
    os.makedirs("output", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS file_memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        topic TEXT,
        keywords TEXT,
        summary TEXT,
        processed_at TEXT
    )
    """
    )

    conn.commit()
    conn.close()


# ------------------ Insert Record ------------------


def store_file_metadata(filename, topic, keywords, summary):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
        INSERT INTO file_memory (filename, topic, keywords, summary, processed_at)
        VALUES (?, ?, ?, ?, ?)
        """,
            (filename, topic, ", ".join(keywords), summary, datetime.now().isoformat()),
        )
        conn.commit()
        conn.close()
        logging.info(f"[Memory] Stored metadata for: {filename}")
    except Exception as e:
        logging.error(f"[Memory] Failed to store: {filename} → {e}")


# ------------------ Fetch by Topic ------------------


def get_files_by_topic(topic):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
    SELECT filename, keywords, summary, processed_at
    FROM file_memory
    WHERE topic = ?
    ORDER BY processed_at DESC
    """,
        (topic,),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


# ------------------ Topic Delete   ------------------


def delete_file_metadata(filename):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM file_memory WHERE filename = ?", (filename,))
        conn.commit()
        conn.close()
        logging.info(f"[Memory] Deleted metadata for: {filename}")
    except Exception as e:
        logging.error(f"[Memory] Failed to delete metadata for {filename}: {e}")


def delete_files_by_folder(folder_path):
    """
    Deletes all DB entries for files found in a given folder.
    """
    try:
        filenames = [
            f
            for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f))
        ]

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        for filename in filenames:
            cursor.execute("DELETE FROM file_memory WHERE filename = ?", (filename,))
            logging.info(f"[Memory] Deleted metadata for: {filename}")
        conn.commit()
        conn.close()

    except Exception as e:
        logging.error(
            f"[Memory] Failed to delete metadata from folder {folder_path}: {e}"
        )


# ------------------ Topic Frequency ------------------


def get_topic_counts():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
    SELECT topic, COUNT(*) as count
    FROM file_memory
    GROUP BY topic
    ORDER BY count DESC
    """
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


# ------------------ On Import ------------------

init_db()
