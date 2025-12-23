# UPGRADE: Python 3.11 (Fixes compatibility issues)
FROM python:3.11-slim

WORKDIR /app

# 1. System tools
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 2. THE HEAVY LAYER (Cached)
COPY requirements-heavy.txt .
RUN pip install --no-cache-dir -r requirements-heavy.txt --extra-index-url https://download.pytorch.org/whl/cpu

# 3. THE LIGHT LAYER (New Tools)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy Code
COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]