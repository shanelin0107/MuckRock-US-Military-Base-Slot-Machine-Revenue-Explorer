FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY military_slots.db metadata.yaml ./
COPY . .

EXPOSE 8001

CMD ["datasette", "military_slots.db", "-h", "0.0.0.0", "-p", "${PORT:-8001}", "-m", "metadata.yaml", "--cors", "--setting", "sql_time_limit_ms", "1000", "--setting", "default_page_size", "100"]
