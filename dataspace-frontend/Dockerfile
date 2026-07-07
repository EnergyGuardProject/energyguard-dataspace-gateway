FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY manage.py .
COPY dataspace_frontend/ ./dataspace_frontend/
COPY dataspace/ ./dataspace/

EXPOSE 8095

CMD ["python", "manage.py", "runserver", "0.0.0.0:8095"]
