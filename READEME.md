Here’s a complete and professional **`README.md`** for your project `InsightSort`.

## 🧠 InsightSort

### _AI-Powered Document Classifier & Organizer (Fully Local)_

InsightSort lets you upload `.pdf`, `.txt`, or `.docx` files and automatically:

- Classify them into topics (Tech, Health, Finance, etc.)
- Extract keywords and summaries
- Organize files into folders based on their content
  All using a **local LLM (mistral-7b)** — no cloud, no internet.

---

## 🔧 Features

✅ Drag-and-drop file or folder upload
✅ Topic classification using `mistral-7b` (via `llama-cpp-python`)
✅ Rule-based fallback for classification
✅ Local keyword + summary extraction (TF-IDF or LLM)
✅ Auto-sorting into `/output/organized/<topic>`
✅ CSV reporting and local memory log
✅ Fully offline, privacy-first

---

## 🧱 Tech Stack

- Python 3.9+
- `llama-cpp-python` (mistral-7b model)
- `Tkinter` (GUI)
- `PyMuPDF` (PDF reading)
- `docx2txt`, `scikit-learn`, `pandas`
- `SQLite3` (local memory)

---

## 📁 Folder Structure

```
InsightSort/
├── app.py
├── config.yaml
├── file_handler.py
├── llm_classifier.py
├── rule_based_classifier.py
├── extractor.py
├── memory_store.py
├── utils.py
├── models/
│   └── phi-2.bin
├── output/
│   ├── organized/
│   ├── report.csv
│   └── insight_memory.db
└── logs/
    └── process_log.txt
```

---

## 🚀 Setup & Run

### 1. 🔃 Install Dependencies

```bash
pip install -r requirements.txt
```

> **Make sure** your system supports `llama-cpp-python` and that you have a compatible CPU/GPU.

### 2. 📦 Download `mistral-7b` model (if not present)

Download the **`mistral-7b`** GGUF version (`q4_K_M` recommended) and place it in:

```
models/mistral-7b-instruct-v0.1.Q2_K.gguf
```

### 3. ▶ Run the App

```bash
python app.py
```

---

## ⚙️ Configurable Options (`config.yaml`)

- `use_llm_first: true` – toggle LLM or rule-based classification
- `extractor.llm_mode: true` – use LLM or fallback for keywords/summary
- `topics` – customize or expand topic list

---

## 📌 Example Use Cases

- Organize chaotic download folders
- Sort academic papers, lectures, or journals
- Build a personal knowledge archive
- Run inside private environments (offline-safe)
