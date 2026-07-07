FROM python:3.12-slim

WORKDIR /app

# Build context is the repo root (see docker-compose.yml's `context: .` +
# `dockerfile: dataspace_gateway/Dockerfile`) because requirements.txt lives
# there alongside tests/, README.md, etc. - this file just lives inside
# dataspace_gateway/ for symmetry with dataspace-frontend/Dockerfile.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY dataspace_gateway/ ./dataspace_gateway/

EXPOSE 8000

CMD ["uvicorn", "dataspace_gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]
