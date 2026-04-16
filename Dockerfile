FROM python:3.10-slim

WORKDIR /app

# Install only necessary system deps
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data (cached layer)
RUN python - <<EOF
import nltk
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
EOF

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]