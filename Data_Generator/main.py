from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import requests
import os

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount frontend as static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve index.html at root
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    return FileResponse("frontend/index.html")

# Model for incoming schema request
class SchemaRequest(BaseModel):
    schema: str

@app.post("/generate-data-script")
async def generate_data_script(request: SchemaRequest):
    prompt = f"""
You are a Python expert. Given the following database schema, generate a Python script that creates synthetic data (1000+ rows per table). Ensure:
- Foreign keys are respected.
- Unique constraints are maintained.
- Data is realistic and consistent.

Use libraries like faker, random, and uuid as needed.
Output only the Python code, no extra text.

Schema:
{request.schema}
"""
    llama_response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "llama3", "prompt": prompt, "stream": False}
    )

    if llama_response.status_code == 200:
        result = llama_response.json()
        return {"code": result.get("response", "").strip()}
    else:
        return {"code": f"Error from Ollama: {llama_response.status_code}"}
