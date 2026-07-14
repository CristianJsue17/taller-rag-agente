"""
Carga un PDF en ChromaDB.
Uso: python ingest.py --pdf docs/iso9001.pdf
"""
import argparse, os, shutil
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from config import CHROMA_DIR, COLLECTION_NAME, EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP


def ingest(pdf_path: str):
    if not os.path.exists(pdf_path):
        print(f"❌ No se encontró: {pdf_path}"); return

    if os.path.exists(CHROMA_DIR):
        print("🗑️  Limpiando base anterior...")
        for item in os.listdir(CHROMA_DIR):
            p = os.path.join(CHROMA_DIR, item)
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)

    print(f"\n📄 Cargando PDF: {pdf_path}")
    pages = PyPDFLoader(pdf_path).load()
    print(f"   → {len(pages)} páginas")

    print(f"✂️  Dividiendo en fragmentos...")
    chunks = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", ", ", " "],
    ).split_documents(pages)
    print(f"   → {len(chunks)} fragmentos")

    print(f"🧠 Generando embeddings...")
    emb = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL, model_kwargs={"device": "cpu"})

    print(f"💾 Guardando en ChromaDB...")
    vs = Chroma.from_documents(documents=chunks, embedding=emb, persist_directory=CHROMA_DIR, collection_name=COLLECTION_NAME)

    print(f"\n✅ ¡Listo! {vs._collection.count()} fragmentos indexados")

    print(f"\n🔍 Test: 'gestión de calidad'")
    for i, doc in enumerate(vs.similarity_search("gestión de calidad", k=2), 1):
        print(f"   {i}. (pág {doc.metadata.get('page','?')}): {doc.page_content[:100]}...")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", required=True)
    ingest(parser.parse_args().pdf)