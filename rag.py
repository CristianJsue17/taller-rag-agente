"""Base vectorial y herramienta de busqueda."""
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from config import CHROMA_DIR, COLLECTION_NAME, EMBEDDING_MODEL, TOP_K, MAX_CONTEXT_CHARS

print("Cargando base de conocimiento...")
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL, model_kwargs={"device": "cpu"})
vectorstore = Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings, collection_name=COLLECTION_NAME)
fragment_count = vectorstore._collection.count()
print(f"   {fragment_count} fragmentos cargados")


def buscar(consulta: str) -> str:
    """Busca en ChromaDB y retorna fragmentos recortados."""
    docs = vectorstore.similarity_search(consulta, k=TOP_K)
    if not docs:
        return ""
    resultados = []
    total = 0
    for doc in docs:
        page = doc.metadata.get("page", "?")
        texto = doc.page_content[:400]
        total += len(texto)
        if total > MAX_CONTEXT_CHARS:
            break
        resultados.append(f"[Pagina {page}] {texto}")
    return "\n---\n".join(resultados)