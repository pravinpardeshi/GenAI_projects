from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import os
import faiss

from llm_client import OllamaClient
from embedding_model import EmbeddingModel
from awr_parser import parse_awr_html
from report_tracker import add_report_record, load_tracker

app = FastAPI()

# Allow frontend requests (adjust origins for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage paths
VECTOR_DIR = "vectorstore"
os.makedirs(VECTOR_DIR, exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def index():
    with open("templates/index.html", "r") as f:
        return f.read()


@app.post("/upload")
async def upload_awr(file: UploadFile = File(...)):
    contents = await file.read()

    try:
        html = contents.decode('utf-8', errors='ignore')
    except Exception as e:
        return {"status": "error", "message": "Unable to decode HTML file."}

    # Parse and chunk
    chunks = parse_awr_html(html)
    if not chunks:
        return {"status": "error", "message": "No usable content found in the AWR report."}

    # Generate vectors
    embedder = EmbeddingModel()
    vectors = embedder.embed_chunks(chunks)

    # Track report & get report_id
    report_id = add_report_record(file.filename, contents, len(chunks))

    # Save FAISS index
    index_path = os.path.join(VECTOR_DIR, f"index_{report_id}.faiss")
    index = faiss.IndexFlatL2(len(vectors[0]))
    index.add(vectors)
    faiss.write_index(index, index_path)

    return {
        "status": "ok",
        "message": f"AWR report uploaded and indexed as '{report_id}'.",
        "report_id": report_id
    }


@app.post("/chat")
async def chat_with_report(query: str = Form(...), report_id: str = Form(...)):
    index_path = os.path.join(VECTOR_DIR, f"index_{report_id}.faiss")

    if not os.path.exists(index_path):
        return {"answer": f"❌ Report ID '{report_id}' not found."}

    # Load index
    index = faiss.read_index(index_path)

    # Embed the query
    embedder = EmbeddingModel()
    query_vec = embedder.embed_chunks([query])[0]

    # Search top chunks
    D, I = index.search(query_vec.reshape(1, -1), k=5)
    retrieved_chunks = [f"Chunk #{i}" for i in I[0]]  # TODO: Replace with real text chunks

    # Build prompt
    context = "\n\n".join(retrieved_chunks)
    prompt = f"""You are an expert in Oracle AWR performance analysis.
            Given the following report data:\n{context}\n
            Answer this question:\n{query}
            """

    ollama = OllamaClient("llama3")
    answer = ollama.generate(prompt)

    return {"answer": answer}


@app.get("/reports")
def list_reports():
    return load_tracker()


