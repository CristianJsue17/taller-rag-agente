"""RAG directo: buscar + responder con OpenAI."""
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from config import OPENAI_MODEL, OPENAI_API_KEY
from rag import buscar

SYSTEM_PROMPT = """Eres un asistente experto en la norma ISO 9001 y sistemas de gestion de calidad.
Responde basandote en los fragmentos de la norma que se te proporcionan.
Si los fragmentos no contienen la respuesta, dilo honestamente.
Responde siempre en espanol. Cita la pagina cuando sea posible.
Se conciso pero completo."""

print(f"Conectando con OpenAI ({OPENAI_MODEL})...")
llm = ChatOpenAI(
    model=OPENAI_MODEL,
    api_key=OPENAI_API_KEY,
    temperature=0,
)
print("Listo")


def run_agent(message: str, history: list) -> str:
    contexto = buscar(message)

    lc_messages = [SystemMessage(content=SYSTEM_PROMPT)]
    for msg in history:
        if isinstance(msg, dict):
            if msg["role"] == "user":
                lc_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                lc_messages.append(AIMessage(content=msg["content"]))

    if contexto:
        prompt = f"""Fragmentos relevantes de ISO 9001:
{contexto}

Pregunta del usuario: {message}

Responde basandote en los fragmentos anteriores."""
    else:
        prompt = message

    lc_messages.append(HumanMessage(content=prompt))

    try:
        response = llm.invoke(lc_messages)
        return response.content
    except Exception as e:
        return f"Error: {str(e)}"