# 🔍 Python Search Engine

A **Python-based search engine** built from scratch with an **inverted index** for efficient text retrieval. The system indexes a corpus of documents, processes user queries in real-time, and returns relevant results through a clean web interface built with **Flask** and **HTML/CSS**.

---

## ✨ Features

- 🗂️ **Inverted Index** — Efficient keyword-to-document mapping for fast lookups
- 🧹 **Text Normalization & Tokenization** — Regex-based token extraction and cleaning
- 🌐 **Web Interface** — User-friendly search UI built with Flask + HTML/CSS
- ⚡ **Real-Time Search** — Processes queries instantly with indexed lookup
- 💾 **Persistent Index Storage** — Index saved and reloaded using JSON
- 📊 **Performance Metrics** — Reports search processing time and indexing stats
- 📚 **Scalable** — Designed to handle large document collections efficiently

---

## 🏗️ Architecture

The search engine is divided into two main pipelines:

### 🔹 Offline (Indexing Pipeline)
1. **Load & clean** raw text documents
2. **Tokenize & normalize** words (using regex)
3. **Build inverted index** — mapping each term to the list of documents containing it
4. **Save index** to disk (JSON format)

### 🔹 Online (Searching Pipeline)
1. **Load inverted index** into memory
2. **Process user query** — normalize and split into terms
3. **Lookup matching** documents in the index
4. **Return results** as an HTML page
5. **View results** in the browser

---

## 🛠️ Tech Stack

| Category | Tools |
|----------|-------|
| **Language** | Python 3 |
| **Indexing** | `json`, `re`, `os`, `collections` |
| **Searching** | `json`, `re`, `flask`, `time` |
| **Web Framework** | Flask |
| **Frontend** | HTML, CSS |
| **Storage** | JSON (index persistence) |

---

## 📂 Project Structure

```
mini-Search-Engine/
├── indexing.py              # Builds the inverted index from documents
├── searching.py               # Search logic & Flask web server
├── documents/              # Corpus of text documents
├── index.json              # Saved inverted index
├── templates/              # HTML templates
│   └── index.html          # Search page
├── static/                 # CSS stylesheets
│   └── style.css
└── README.md
```

> ⚠️ Adjust file names according to your actual project structure.

---

## 🚀 How to Run

### 1. Clone the repository
```bash
git clone https://github.com/FatemehPaksima/mini-Search-Engine.git
cd Python-Search-Engine
```

### 2. Install dependencies
```bash
pip install flask
```

### 3. Build the inverted index
```bash
python indexer.py
```
This will process all documents in the `documents/` folder and save the index to `index.json`.

### 4. Start the web server
```bash
python search.py
```

### 5. Open in your browser
```
http://127.0.0.1:5000
```

Enter a query and get instant results! 🎉

---

## ⚙️ How It Works

### 🧠 Inverted Index
The core of the search engine. Instead of scanning every document on each query, we precompute a dictionary:

```python
{
  "search": ["doc1.txt", "doc3.txt"],
  "engine": ["doc2.txt", "doc3.txt"],
  "python": ["doc1.txt", "doc4.txt"]
}
```

Each **term** maps to a **list of documents** containing it.

### 🧹 Normalization
- Convert text to **lowercase**
- Remove **punctuation** and **special characters**
- Split into **word tokens** via regex
- (Optional) Remove **stopwords** and apply **stemming**

### ⚡ Search Flow
1. User enters a query in the browser
2. Query is **normalized** and **tokenized**
3. Each term is **looked up** in the inverted index
4. Matching documents are **ranked** and returned
5. Processing time is measured and displayed

---

## 📊 Indexing Statistics

| Metric | Value |
|--------|-------|
| **Corpus Size** | ~50 MB |
| **Indexing Time** | ~4.78 minutes |
| **Index Storage** | JSON format |

---

## 🎨 Web Interface

- **Search bar** for user queries
- **Results page** showing matched documents
- **Processing time** displayed for each search
- **Clean design** with custom CSS

---

## 🧩 Core Modules

| Module | Responsibility |
|--------|----------------|
| `indexer.py` | Load documents, tokenize, build & save inverted index |
| `search.py` | Load index, process queries, serve Flask app |
| `index.json` | Persisted inverted index |
| `templates/index.html` | Search page UI |
| `static/style.css` | Custom styling |

---

## 💡 Future Improvements

- 🏆 **Ranking with TF-IDF / BM25** for better result relevance
- 🔤 **Stemming & Lemmatization** for better matching
- 🧠 **Query Expansion** with synonyms
- 📄 **Support for PDF / DOCX** document formats
- 🎯 **Phrase Search & Boolean Queries**
- 🚀 **Elasticsearch-style REST API**

---

## 📜 License

This project was developed as a university **Information Retrieval** course project.
Free to use for learning and research purposes.

---

## 👨‍💻 Authors

- **Fatemeh Paksima** — [@FatemehPaksima](https://github.com/FatemehPaksima)
- **Atefeh Ghodratifar**

---

## ⭐ Acknowledgments

- Python `re` and `collections` libraries
- Flask web framework
- Course instructor and team collaboration
