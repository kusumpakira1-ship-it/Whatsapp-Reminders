FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for reportlab, pandas, and general building
RUN apt-get update && apt-get install -y \
    gcc \
    libmariadb-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Create media directory for downloads
RUN mkdir -p /app/media

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
