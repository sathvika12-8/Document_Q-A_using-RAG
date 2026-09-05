from pathlib import Path

# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DOCUMENTS_DIR = BASE_DIR / "documents"
DATA_DIR = BASE_DIR / "data"
VECTORSTORE_DIR = BASE_DIR / "vectorstore"

EMPLOYEE_FILE = DATA_DIR / "employee.csv"


# ============================================================
# OLLAMA
# ============================================================

OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2:3b"


# ============================================================
# EMBEDDINGS
# ============================================================

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


# ============================================================
# RAG SETTINGS
# ============================================================

CHUNK_SIZE = 900
CHUNK_OVERLAP = 120
TOP_K = 3