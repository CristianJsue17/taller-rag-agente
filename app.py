"""
Asistente ISO 9001 | RAG + Agente
python app.py → http://localhost:7860
"""
import gradio as gr
from config import GOOGLE_API_KEY, SERVER_HOST, SERVER_PORT, GEMINI_MODEL
from rag import fragment_count
from agent import run_agent

if not GOOGLE_API_KEY:
    print("Error: Falta GOOGLE_API_KEY")
    exit(1)

def chat(message, history):
    return run_agent(message, history)

# 1. CSS Personalizado enfocado solo en el botón y limpieza general
custom_css = """
.gradio-container {
    font-family: 'Inter', system-ui, sans-serif !important;
}

/* Ocultar footer de Gradio */
footer {
    display: none !important;
}

/* ESTILOS DEL BOTÓN DE ENVIAR */
/* Estado Deshabilitado (Sin texto): Gris */
button[aria-label="Submit"]:disabled {
    background-color: #f3f4f6 !important;
    color: #9ca3af !important;
    cursor: not-allowed !important;
    border: 1px solid #e5e7eb !important;
    opacity: 0.7;
}

/* Estado Habilitado (Con texto): Azul */
button[aria-label="Submit"]:not(:disabled) {
    background-color: #2563eb !important;
    color: white !important;
    cursor: pointer !important;
    border: none !important;
    opacity: 1;
}
"""

# 2. Tema suave y profesional
theme = gr.themes.Soft(
    primary_hue="blue",
    neutral_hue="slate",
    font=[gr.themes.GoogleFont('Inter'), 'ui-sans-serif', 'system-ui', 'sans-serif']
)

# 3. Contenedor Principal (fill_height=True para expandir verticalmente)
with gr.Blocks(theme=theme, css=custom_css, fill_height=True) as demo:
    gr.ChatInterface(
        fn=chat,
        title="Asistente ISO 9001",
        description="Sistema experto en gestión de calidad. Ingrese su consulta sobre la norma ISO 9001.",
        examples=[
            "Hola, ¿quién eres?",
            "¿Qué es un SGC?",
            "Requisitos de liderazgo",
            "Auditorías internas",
            "Mejora continua",
        ],
        fill_height=True # Hace que el área del chat se expanda al máximo disponible
    )

if __name__ == "__main__":
    print(f"\nIniciando servidor en http://localhost:{SERVER_PORT}")
    print(f"Modelo: {GEMINI_MODEL} | Fragmentos: {fragment_count}\n")
    demo.launch(server_name=SERVER_HOST, server_port=SERVER_PORT, share=False)