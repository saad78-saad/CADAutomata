FROM python:3.10-slim

WORKDIR /app

# Install system dependencies required by trimesh / numerical packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Install package and web dependencies
RUN pip install --no-cache-dir . fastapi uvicorn

# Expose port and run FastAPI via Uvicorn using Railway's dynamic PORT
EXPOSE 8000
CMD uvicorn cad_automata.api:app --host 0.0.0.0 --port ${PORT:-8000}