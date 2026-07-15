"""Configuracion centralizada."""
import os

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
CHROMA_DIR = os.getenv("CHROMA_DIR", "./chroma_db")
COLLECTION_NAME = "iso9001"
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
TOP_K = 3
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100
MAX_CONTEXT_CHARS = 1500
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 7860