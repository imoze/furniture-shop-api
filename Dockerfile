FROM python:3.14.6-slim

WORKDIR /app

COPY requirments.txt .
RUN pip install --no-cache-dir -r requirments.txt

COPY app/ .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0","--port", "8000"]