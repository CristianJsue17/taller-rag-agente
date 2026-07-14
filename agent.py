"""RAG directo: buscar + responder en una sola llamada a Gemini."""
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from config import GEMINI_MODEL, GOOGLE_API_KEY
from rag import buscar

SYSTEM_PROMPT = """Eres un asistente experto en la norma ISO 9001 y sistemas de gestion de calidad.
Responde basandote en los fragmentos de la norma que se te proporcionan.
Si los fragmentos no contienen la respuesta, dilo honestamente.
Responde siempre en espanol. Cita la pagina cuando sea posible.
Se conciso pero completo."""

print(f"Conectando con Gemini ({GEMINI_MODEL})...")
llm = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL,
    google_api_key=GOOGLE_API_KEY,
    temperature=0,
)
print("Listo")


def run_agent(message: str, history: list) -> str:
    """Busca en ChromaDB + una sola llamada a Gemini."""

    # 1. Buscar en la base vectorial (milisegundos)
    contexto = buscar(message)

    # 2. Construir historial
    lc_messages = [SystemMessage(content=SYSTEM_PROMPT)]
    for msg in history:
        if isinstance(msg, dict):
            if msg["role"] == "user":
                lc_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                lc_messages.append(AIMessage(content=msg["content"]))

    # 3. Armar el prompt con contexto RAG
    if contexto:
        prompt = f"""Fragmentos relevantes de ISO 9001:
{contexto}

Pregunta del usuario: {message}

Responde basandote en los fragmentos anteriores."""
    else:
        prompt = message

    lc_messages.append(HumanMessage(content=prompt))

    # 4. Una sola llamada al LLM
    try:
        response = llm.invoke(lc_messages)
        return response.content
    except Exception as e:
        return f"Error: {str(e)}"