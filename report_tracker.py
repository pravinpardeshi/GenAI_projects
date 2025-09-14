import os
import json
import hashlib
import uuid
from datetime import datetime

TRACKER_FILE = "uploaded_reports.json"

def load_tracker():
    if os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE, "r") as f:
            return json.load(f)
    return []

def save_tracker(data):
    with open(TRACKER_FILE, "w") as f:
        json.dump(data, f, indent=2)

def compute_hash(contents: bytes):
    return hashlib.md5(contents).hexdigest()

def generate_report_id():
    return "rpt_" + uuid.uuid4().hex[:8]

def add_report_record(filename: str, contents: bytes, num_chunks: int) -> str:
    reports = load_tracker()
    report_hash = compute_hash(contents)

    for r in reports:
        if r["hash"] == report_hash:
            return r["report_id"]

    report_id = generate_report_id()
    reports.append({
        "report_id": report_id,
        "filename": filename,
        "uploaded_at": datetime.now().isoformat(),
        "hash": report_hash,
        "chunks": num_chunks
    })
    save_tracker(reports)
    return report_id


