FROM python:3.9-slim

WORKDIR /app

# 1. Install system tools needed for some python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 2. Copy requirements
COPY requirements.txt .

# 3. THE FIX: Install CPU-only PyTorch explicitly FIRST
# This prevents downloading the massive GPU version
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# 4. Install the rest of the requirements (Chroma, LangChain)
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]