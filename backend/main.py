from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import List
import os
import re
import numpy as np
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from analyzer import run_residue_pca
app = FastAPI(title="PPALI")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_PATH = os.path.join(BASE_DIR, "frontend", "index.html")
@app.get("/logo")
async def get_logo():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(script_dir, "KBSI_Logo.png")
    if os.path.exists(logo_path):
        return FileResponse(logo_path)
    return FileResponse("KBSI_Logo.png") # Fallback
@app.get("/")
async def read_index():
    if not os.path.exists(FRONTEND_PATH):
        raise HTTPException(status_code=404, detail="Frontend file not found")
    return FileResponse(FRONTEND_PATH)
@app.post("/analyze_picked")
async def analyze_picked(
    intensities: List[str] = Form(...)
):
    try:
        residue_data = []
        feature_names = None
        all_lines = []
        for item in intensities:
            all_lines.extend(item.replace('\r', '').split('\n'))
        valid_lines = [l.strip() for l in all_lines if l.strip()]
        if not valid_lines:
             raise HTTPException(status_code=400, detail="No data provided")
        first_line = valid_lines[0]
        parts = re.split(r'[,\s]+', first_line)
        is_header = False
        if len(parts) >= 2:
            try:
                [float(v) for v in parts[1:]]
            except ValueError:
                is_header = True
                feature_names = parts[1:]
        for s in valid_lines:
            if is_header and s == first_line:
                continue
            parts = re.split(r'[,\s]+', s)
            if len(parts) < 2: continue
            res_id_str_raw = parts[0]
            res_id_numeric = re.sub(r'\D', '', res_id_str_raw)
            if not res_id_numeric: 
                continue
            try:
                values = [float(v) for v in parts[1:]]
                residue_data.append([res_id_numeric] + values)
                if feature_names is None:
                     feature_names = [f"Feature_{i+1}" for i in range(len(values))]
            except ValueError:
                continue
        if not residue_data:
            raise HTTPException(status_code=400, detail="No valid residue data found")
        result = run_residue_pca(residue_data, feature_names=feature_names)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)