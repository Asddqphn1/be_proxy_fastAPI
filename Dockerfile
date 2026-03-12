# 1. Pake Python versi ringan
FROM python:3.9-slim

# 2. Bikin folder kerja di dalam container
WORKDIR /app

# 3. Copy file requirements dulu (biar cache Docker jalan optimal)
COPY requirements.txt .

# 4. Install library Python
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy sisa codingan
COPY . .

# 6. Command default (nanti ditimpa docker-compose, tapi ini buat jaga2)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]