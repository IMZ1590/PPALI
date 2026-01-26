from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import List
import os
import re
import numpy as np
import sys

# Add current directory to sys.path to ensure analyzer import works
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from analyzer import run_residue_pca

app = FastAPI(title="PPALI")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Relative path to frontend
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_PATH = os.path.join(BASE_DIR, "frontend", "index.html")

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
        
        # If the frontend sends everything as ONE large string in a list, split it
        all_lines = []
        for item in intensities:
            all_lines.extend(item.replace('\r', '').split('\n'))
            
        # Parse lines
        valid_lines = [l.strip() for l in all_lines if l.strip()]
        if not valid_lines:
             raise HTTPException(status_code=400, detail="No data provided")
             
        first_line = valid_lines[0]
        parts = re.split(r'[,\s]+', first_line)
        
        # Check if first line is header (if 2nd col onwards are NOT floats)
        is_header = False
        if len(parts) >= 2:
            try:
                [float(v) for v in parts[1:]]
            except ValueError:
                is_header = True
                feature_names = parts[1:]
                
        # Parse data
        for s in valid_lines:
            if is_header and s == first_line:
                continue
                
            parts = re.split(r'[,\s]+', s)
            if len(parts) < 2: continue
            
            res_id_str_raw = parts[0]
            # Strip non-numeric characters to get pure residue number (e.g. "A10" -> "10")
            res_id_numeric = re.sub(r'\D', '', res_id_str_raw)
            
            if not res_id_numeric: 
                # If no number found, skip or keep raw? Let's skip to avoid NaN issues
                continue
                
            try:
                values = [float(v) for v in parts[1:]]
                # Use the processed numeric string as the ID
                residue_data.append([res_id_numeric] + values)
                
                # Fallback naming if no header
                if feature_names is None:
                     feature_names = [f"Feature_{i+1}" for i in range(len(values))]
            except ValueError:
                continue
        
        if not residue_data:
            raise HTTPException(status_code=400, detail="No valid residue data found")
        
        # Run PCA
        result = run_residue_pca(residue_data, feature_names=feature_names)
        return result
        
    except Exception as e:
        # import traceback
        # traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
