# Taller: RAG + IA Moderna + Mini Chatbot

**Asistente ISO 9001** -- Chatbot que busca en la norma ISO 9001 usando RAG (Retrieval-Augmented Generation) con Google Gemini.

## Que demuestra este taller

| Concepto | Implementacion |
|---|---|
| **RAG** | PDF -> Chunks -> Embeddings -> ChromaDB -> Busqueda vectorial |
| **IA Moderna** | Google Gemini API, embeddings multilingues, Docker |
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
Google Gemini (genera respuesta con contexto)
      |
      v
Respuesta al usuario con paginas citadas
```

**Flujo simple:** Toda pregunta busca en ChromaDB y pasa los fragmentos a Gemini en una sola llamada. Sin pasos intermedios.

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
- API key de Google Gemini (gratis o pago)

### Obtener API key de Gemini

1. Ir a https://aistudio.google.com/apikey
2. Crear API key (no requiere tarjeta en free tier)
3. Copiar la key

## Instalacion y arranque

### Paso 1: Preparar el proyecto

```bash
cd ~/taller-rag-agente

# Crear carpeta docs y copiar tu PDF
mkdir -p docs
cp /ruta/a/tu/iso9001.pdf docs/

# Configurar API key
cp .env.example .env
nano .env
# Pegar tu GOOGLE_API_KEY y guardar
```

Tu `.env` debe verse asi:
```
GOOGLE_API_KEY=AIzaSy...tu-key-aqui
GEMINI_MODEL=gemini-3.5-flash
```

### Paso 2: Levantar el contenedor (Terminal 1)

```bash
docker compose up --build
```

Espera hasta ver estos mensajes:
```
rag-chatbot  | Cargando base de conocimiento...
rag-chatbot  |    0 fragmentos cargados
rag-chatbot  | Conectando con Gemini (gemini-3.5-flash)...
rag-chatbot  | Listo
```

**No cierres esta terminal.** Deja el contenedor corriendo aqui.

### Paso 3: Ingestar el PDF (Terminal 2)

Abre una segunda terminal:

```bash
cd ~/taller-rag-agente
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

### Paso 4: Reiniciar para cargar la base

```bash
docker compose restart app
```

Vuelve a la Terminal 1 y espera a ver:
```
rag-chatbot  | XXX fragmentos cargados    <-- ya no dice 0
rag-chatbot  | Listo
```

### Paso 5: Usar el chatbot

Abre en tu navegador: **http://localhost:7860**

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
| LLM | Google Gemini 3.5 Flash | Rapido, API simple, free tier disponible |
| Embeddings | paraphrase-multilingual-MiniLM-L12-v2 | Multilingue, entiende espanol |
| Vector DB | ChromaDB | En memoria, zero config |
| Framework | LangChain | Loaders, text splitters, integraciones |
| Frontend | Gradio | Chatbot funcional en pocas lineas |
| Contenedor | Docker | Entorno limpio, reproducible |

## Puntos importantes

### Sobre la velocidad
- La busqueda en ChromaDB tarda milisegundos. El 95% del tiempo es la llamada a Gemini.
- Free tier: ~30-40 segundos por respuesta. Con plan pago: ~10-15 segundos.
- Si ves error 503 (UNAVAILABLE), es demanda alta temporal en Gemini. Espera unos minutos.
- Si ves error 429 (RESOURCE_EXHAUSTED), llegaste al limite de requests. Espera o cambia de modelo.

### Sobre la calidad de busqueda
- El modelo de embeddings `paraphrase-multilingual-MiniLM-L12-v2` entiende espanol.
- Si una pregunta no encuentra resultados relevantes, prueba reformularla con terminos de la norma.
- Los chunks de 500 caracteres dan buen balance entre contexto y velocidad.

### Sobre el PDF
- Solo necesitas ingestar una vez. La base persiste en un Docker volume.
- Si cambias el PDF, re-ingesta y reinicia.
- Puedes ingestar multiples PDFs ejecutando ingest.py varias veces con diferentes archivos.

### Sobre Docker
- El primer build tarda ~5-10 minutos (descarga dependencias Python).
- Los siguientes builds son rapidos (cache de Docker).
- Si cambias requirements.txt, necesitas `--build`. Si solo cambias .env, basta con `restart`.

## Troubleshooting

| Problema | Solucion |
|---|---|
| Error 503 UNAVAILABLE | Gemini saturado, espera 1-2 minutos y reintenta |
| Error 429 RESOURCE_EXHAUSTED | Limite de requests alcanzado, espera o cambia modelo |
| 0 fragmentos cargados | Ejecuta ingest.py y luego restart |
| Container se cae al iniciar | Revisa `docker compose logs app` |
| Respuestas no relevantes | Revisa que el PDF se ingesto bien, prueba re-ingestar |
| Build falla por DNS | Configura DNS en WSL: nameserver 8.8.8.8 en /etc/resolv.conf |

## Modelos alternativos de Gemini

Si `gemini-3.5-flash` da problemas, cambia en tu `.env`:

```bash
# Opciones (de mas nuevo a mas estable):
GEMINI_MODEL=gemini-3.5-flash
GEMINI_MODEL=gemini-3-flash
GEMINI_MODEL=gemini-2.5-flash-preview-05-20
GEMINI_MODEL=gemini-2.5-flash-lite-preview-06-17
```