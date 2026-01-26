# Base Image
FROM python:3.9-slim

# Working Directory
WORKDIR /app

# Install system dependencies (if needed later, e.g. for numpy compilation)
# RUN apt-get update && apt-get install -y gcc

# Copy Requirements
COPY requirements.txt .

# Install Python Dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy Application Code
# Copy backend code
COPY backend/ ./backend/
# Copy frontend code (Must include this so main.py can serve index.html)
COPY frontend/ ./frontend/

# Expose Port
EXPOSE 8000

# Run Command
# Note: We run from /app, so module path is backend.main
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
