# Taller: RAG + IA Moderna + Mini Chatbot

**Asistente ISO 9001** -- Chatbot que busca en la norma ISO 9001 usando RAG (Retrieval-Augmented Generation) con OpenAI GPT-4o-mini.

## Que demuestra este taller

| Concepto | Implementacion |
|---|---|
| **RAG** | PDF -> Chunks -> Embeddings -> ChromaDB -> Busqueda vectorial |
| **IA Moderna** | OpenAI API (GPT-4o-mini), embeddings multilingues, Docker |
| **Mini Chatbot** | Interfaz web con Gradio, historial de conversacion |

## Arquitectura

```
Usuario (Gradio)
      |
      v
  Pregunta
      |
      v
ChromaDB (busqueda vectorial, milisegundos)
      |
      v
Fragmentos relevantes de ISO 9001
      |
      v
OpenAI GPT-4o-mini (genera respuesta con contexto)
      |
      v
Respuesta al usuario con paginas citadas
```

**Flujo simple:** Toda pregunta busca en ChromaDB y pasa los fragmentos a GPT-4o-mini en una sola llamada. Sin pasos intermedios.

## Estructura del proyecto

```
taller-rag-agente/
|-- config.py            # Configuracion centralizada
|-- rag.py               # Base vectorial + busqueda
|-- agent.py             # Chain RAG: buscar + responder
|-- app.py               # Interfaz Gradio (UI)
|-- ingest.py            # Pipeline: PDF -> ChromaDB
|-- Dockerfile           # Imagen Python
|-- docker-compose.yml   # Orquesta el contenedor
|-- requirements.txt     # Dependencias Python
|-- .env                 # API key (NO subir a git)
|-- .env.example         # Ejemplo de .env
|-- .dockerignore        # Exclusiones de build
|-- docs/                # Carpeta para PDFs
|   |-- iso9001.pdf
|-- chroma_db/           # (generado) Base vectorial
```

## Requisitos previos

- Docker y Docker Compose instalados en WSL/Ubuntu
- API key de OpenAI (requiere creditos, minimo $5 USD)

### Obtener API key de OpenAI

1. Ir a https://platform.openai.com
2. Crear cuenta y agregar creditos ($5 minimo)
3. Ir a API Keys y crear una nueva key
4. Copiar la key (empieza con sk-...)

## Instalacion y arranque

### Paso 1: Clonar el repositorio

```bash
git clone https://github.com/CristianJsue17/taller-rag-agente.git
cd taller-rag-agente
```

### Paso 2: Configurar la API key

El archivo .env no esta incluido por seguridad (.gitignore lo excluye). Crear a partir del ejemplo:

```bash
cp .env.example .env
nano .env
```

Tu `.env` debe verse asi:
```
OPENAI_API_KEY=sk-...tu-key-aqui
OPENAI_MODEL=gpt-4o-mini
```

Guardar y cerrar (Ctrl+O, Enter, Ctrl+X en nano).

### Paso 3: Levantar el contenedor (Terminal 1)

```bash
docker compose up --build
```

Espera hasta ver estos mensajes:
```
rag-chatbot  | Cargando base de conocimiento...
rag-chatbot  |    0 fragmentos cargados
rag-chatbot  | Conectando con OpenAI (gpt-4o-mini)...
rag-chatbot  | Listo
```

**No cierres esta terminal.** Deja el contenedor corriendo aqui.

### Paso 4: Ingestar el PDF (Terminal 2)

Abrir una segunda terminal:

```bash
cd taller-rag-agente
docker compose exec app python ingest.py --pdf docs/iso9001.pdf
```

Veras algo como:
```
Cargando base de conocimiento...
Limpiando base anterior...
Cargando PDF: docs/iso9001.pdf
   42 paginas
Dividiendo en fragmentos...
   250+ fragmentos
Generando embeddings...
Guardando en ChromaDB...
Listo! XXX fragmentos indexados

Test: 'gestion de calidad'
   1. (pag 13): ...
```

### Paso 5: Reiniciar para cargar la base

```bash
docker compose restart app
```

Volver a la Terminal 1 y esperar a ver:
```
rag-chatbot  | XXX fragmentos cargados    <-- ya no dice 0
rag-chatbot  | Listo
```

### Paso 6: Usar el chatbot

Abrir en el navegador: **http://localhost:7860**

## Comandos utiles

```bash
# Ver logs en tiempo real
docker compose logs -f app

# Parar todo
docker compose down

# Parar y borrar base vectorial (para re-ingestar desde cero)
docker compose down -v

# Reiniciar sin rebuild (cuando solo cambias .env)
docker compose restart app

# Re-ingestar un PDF nuevo
docker compose exec app python ingest.py --pdf docs/otro-documento.pdf
docker compose restart app
```

## Stack tecnologico

| Componente | Tecnologia | Por que |
|---|---|---|
| LLM | OpenAI GPT-4o-mini | Rapido (5-10 seg), economico (~$0.15/millon tokens) |
| Embeddings | paraphrase-multilingual-MiniLM-L12-v2 | Multilingue, entiende espanol, corre local |
| Vector DB | ChromaDB | En memoria, zero config |
| Framework | LangChain | Loaders, text splitters, integraciones |
| Frontend | Gradio | Chatbot funcional en pocas lineas |
| Contenedor | Docker | Entorno limpio, reproducible |

## Puntos importantes

### Sobre la velocidad
- La busqueda en ChromaDB tarda milisegundos. El tiempo de respuesta depende de la API de OpenAI.
- GPT-4o-mini responde en 5-10 segundos por consulta.
- Con $5 de credito se pueden realizar miles de consultas.

### Sobre la calidad de busqueda
- El modelo de embeddings paraphrase-multilingual-MiniLM-L12-v2 entiende espanol correctamente.
- Si una pregunta no encuentra resultados relevantes, reformular usando terminos de la norma.
- Los chunks de 500 caracteres dan buen balance entre contexto y velocidad.

### Sobre el PDF
- Solo se necesita ingestar una vez. La base persiste en un Docker volume.
- Si se cambia el PDF, re-ingestar y reiniciar.
- Se pueden ingestar multiples PDFs ejecutando ingest.py varias veces con diferentes archivos.

### Sobre Docker
- El primer build tarda ~5-10 minutos (descarga dependencias Python).
- Los siguientes builds son rapidos (cache de Docker).
- Si se cambia requirements.txt, usar --build. Si solo se cambia .env, basta con restart.

## Troubleshooting

| Problema | Solucion |
|---|---|
| Error 401 Unauthorized | API key invalida, verificar en platform.openai.com |
| Error de creditos insuficientes | Agregar creditos en platform.openai.com/billing |
| 0 fragmentos cargados | Ejecutar ingest.py y luego restart |
| Container se cae al iniciar | Revisar docker compose logs app |
| Respuestas no relevantes | Verificar que el PDF se ingesto bien, re-ingestar |
| Build falla por DNS | Configurar DNS en WSL: nameserver 8.8.8.8 en /etc/resolv.conf |
| Build falla por timeout | Reintentar, puede ser internet lento |