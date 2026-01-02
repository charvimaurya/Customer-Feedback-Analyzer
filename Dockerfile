
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

# 4️⃣ Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5️⃣ Copy rest of the app
COPY . .

# 6️⃣ Expose FastAPI port
EXPOSE 8000

# 7️⃣ Start the FastAPI server
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]