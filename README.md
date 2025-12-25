# Customer Feedback Analyzer

A production-ready sentiment analysis system for customer reviews with PostgreSQL database integration and an intelligent chatbot interface powered by OpenAI.

## Overview

This application analyzes customer feedback sentiment (Positive, Neutral, or Negative) using machine learning. It provides:
- **REST API**: FastAPI-based backend for sentiment prediction
- **Sentiment Analysis**: Pre-trained Logistic Regression model with TF-IDF vectorization
- **Database Storage**: PostgreSQL with four-table architecture for raw data, cleaned data, positive reviews, and negative reviews
- **Interactive Chatbot**: CLI-based chatbot that combines sentiment analysis with conversational AI
- **Docker Support**: Fully containerized application with Docker Compose orchestration

---

## Prerequisites

Before you begin, ensure you have the following installed on your system:

### Required Software

1. **Docker Desktop** (includes Docker and Docker Compose)
   - **Windows/Mac**: Download from [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
   - **Linux**: Install Docker Engine and Docker Compose separately:
     ```bash
     # Install Docker
     curl -fsSL https://get.docker.com -o get-docker.sh
     sudo sh get-docker.sh
     
     # Install Docker Compose
     sudo apt-get update
     sudo apt-get install docker-compose-plugin
     ```
   - Verify installation:
     ```bash
     docker --version
     docker-compose --version
     ```

2. **OpenAI API Key** (Required for chatbot functionality)
   - Create an account at [platform.openai.com](https://platform.openai.com)
   - Navigate to API Keys section: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
   - Click "Create new secret key"
   - Copy and save the key securely (you won't be able to see it again)
   - **Important**: Add a payment method at [platform.openai.com/account/billing](https://platform.openai.com/account/billing) to avoid quota errors

### Optional Software

- **Python 3.10+**: Only needed if running locally without Docker
- **PostgreSQL 15+**: Only needed if running locally without Docker
- **Text Editor**: Any editor (VS Code, Sublime Text, Notepad++, nano, vim)

---

## Quick Start Guide

### Step 1: Download the Project

If you received this as a ZIP file, extract it to your desired location. If using Git:

```bash
git clone <repository-url>
cd Customer-Feedback-Analyzer
```

### Step 2: Configure Environment Variables

1. **Create the environment file**:
   ```bash
   cp .env.example .env
   ```

2. **Edit the `.env` file**:
   
   Open the `.env` file with any text editor:
   ```bash
   # Using nano (Linux/Mac)
   nano .env
   
   # Using notepad (Windows)
   notepad .env
   
   # Or use any text editor of your choice
   ```

3. **Add your OpenAI API key**:
   
   Replace `your_openai_api_key_here` with your actual API key:
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/customer_feedback
   PORT=8000
   OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
   
   Save and close the file (in nano: press `Ctrl+X`, then `Y`, then `Enter`).

### Step 3: Start the Application

Run the following command in your terminal:

```bash
docker-compose up --build
```

**What this does**:
- Downloads required Docker images (PostgreSQL, Python)
- Builds the application container
- Creates a PostgreSQL database
- Starts both the database and API server
- Initializes all required database tables

**Expected output**: You should see logs indicating the services are starting. Wait for the message:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Note**: The first run may take 5-10 minutes to download images and install dependencies.

### Step 4: Verify the Installation

Open your web browser and navigate to:

- **API Health Check**: [http://localhost:8000](http://localhost:8000)
  - Should display: `{"status": "healthy", "message": "Customer Feedback Analyzer API is running with 4-table storage"}`

- **Interactive API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
  - Provides a web interface to test all API endpoints

### Step 5: Test the API

#### Using the Web Interface

1. Go to [http://localhost:8000/docs](http://localhost:8000/docs)
2. Click on `POST /predict`
3. Click "Try it out"
4. Enter a sample review in the request body:
   ```json
   {
     "review": "This product is amazing! Best purchase ever."
   }
   ```
5. Click "Execute"
6. View the sentiment result in the response

#### Using Command Line (curl)

```bash
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{"review": "This product is amazing! Best purchase ever."}'
```

**Expected response**:
```json
{"sentiment": "Good"}
```

### Step 6: Run the Interactive Chatbot (Optional)

The chatbot provides a conversational interface for analyzing customer feedback.

1. **Open a new terminal window** (keep the Docker containers running in the first terminal)

2. **Install Python dependencies** (if not already installed):
   ```bash
   pip install openai requests python-dotenv
   ```

3. **Run the chatbot**:
   ```bash
   python chatbot/chatbot.py
   ```

4. **Interact with the chatbot**:
   ```
   Welcome to Customer Feedback Chatbot!
   
   Enter a review (or 'exit' to quit): This product exceeded my expectations!
   
   AI: That's wonderful to hear! It sounds like you had a very positive experience...
   ```

5. **Exit**: Type `exit` when done

---

## API Reference

### Endpoints

#### `GET /`
**Description**: Health check endpoint  
**Response**:
```json
{
  "status": "healthy",
  "message": "Customer Feedback Analyzer API is running with 4-table storage"
}
```

#### `POST /predict`
**Description**: Analyze sentiment of a customer review  
**Request Body**:
```json
{
  "review": "Your customer review text here"
}
```
**Response**:
```json
{
  "sentiment": "Good" | "Neutral" | "Bad"
}
```
**Status Codes**:
- `200`: Success
- `400`: Invalid request (empty review)
- `500`: Server error

#### `GET /history`
**Description**: Retrieve the last 10 analyzed reviews  
**Response**:
```json
[
  {
    "id": 1,
    "review": "Great product!",
    "sentiment": "Good",
    "created_at": "2025-12-25T10:30:00"
  },
  ...
]
```

---

## Database Architecture

The application uses a four-table PostgreSQL database structure:

1. **`raw_feedback`**: Stores original, unprocessed customer reviews
2. **`cleaned_feedback`**: Stores preprocessed text (lowercased, lemmatized, stop words removed)
3. **`positive_feedback`**: Stores reviews classified as positive
4. **`negative_feedback`**: Stores reviews classified as negative
5. **`feedbacks`**: Legacy table maintaining all reviews with sentiment labels

---

## Stopping the Application

To stop the Docker containers:

1. **Graceful shutdown**: Press `Ctrl+C` in the terminal running Docker
2. **Complete cleanup**:
   ```bash
   docker-compose down
   ```
3. **Remove all data** (including database):
   ```bash
   docker-compose down -v
   ```

---

## Troubleshooting

### Issue: "Port 8000 already in use"

**Solution**: Another application is using port 8000. Either:
- Stop the other application, or
- Change the port in `docker-compose.yml`:
  ```yaml
  ports:
    - "8001:8000"  # Use port 8001 instead
  ```

### Issue: "OpenAI quota exceeded" or "Insufficient credits"

**Cause**: Your OpenAI account has no credits or hasn't been set up for billing.

**Solution**:
1. Visit [platform.openai.com/account/billing](https://platform.openai.com/account/billing)
2. Add a payment method
3. Set usage limits to control costs
4. The chatbot now uses `gpt-3.5-turbo` (affordable model) instead of `gpt-4o`

### Issue: Docker containers fail to start

**Solution**:
1. Ensure Docker Desktop is running
2. Check Docker has sufficient resources (Settings → Resources)
3. Try rebuilding:
   ```bash
   docker-compose down
   docker-compose up --build
   ```

### Issue: "Cannot connect to database"

**Solution**:
1. Ensure the database container is running:
   ```bash
   docker ps
   ```
2. Check logs:
   ```bash
   docker-compose logs db
   ```
3. Restart containers:
   ```bash
   docker-compose restart
   ```

### Issue: Models not found

**Cause**: Missing model files in the `models/` directory.

**Solution**: Ensure these files exist:
- `models/tfidf_vectorizer.pkl` (or `tfidf_vectorizer_updated.pkl`)
- `models/logistic_regression.pkl` (or `logistic_regression_updated.pkl`)

---

## Advanced: Running Without Docker

If you prefer to run the application locally without Docker:

### Prerequisites
- Python 3.10 or higher
- PostgreSQL 15 or higher installed and running

### Setup Steps

1. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up PostgreSQL database**:
   ```sql
   CREATE DATABASE customer_feedback;
   CREATE USER user WITH PASSWORD 'password';
   GRANT ALL PRIVILEGES ON DATABASE customer_feedback TO user;
   ```

4. **Configure environment**:
   
   Edit `.env` and update the `DATABASE_URL`:
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/customer_feedback
   PORT=8000
   OPENAI_API_KEY=your_actual_api_key
   ```

5. **Run the application**:
   ```bash
   python main.py
   ```

6. **Run the chatbot** (in a separate terminal):
   ```bash
   python chatbot/chatbot.py
   ```

---

## Project Structure

```
Customer-Feedback-Analyzer/
├── api/
│   ├── __init__.py
│   └── main.py              # FastAPI application and endpoints
├── chatbot/
│   ├── __init__.py
│   └── chatbot.py           # Interactive chatbot client
├── models/
│   ├── tfidf_vectorizer.pkl # TF-IDF vectorizer
│   └── logistic_regression.pkl # Trained sentiment model
├── notebooks/               # Jupyter notebooks for model training
├── database.py              # Database models and connection
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker container configuration
├── docker-compose.yml       # Multi-container orchestration
├── .env.example             # Environment variables template
└── README.md                # This file
```

---

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review Docker logs: `docker-compose logs`
3. Verify your `.env` configuration
4. Ensure all prerequisites are properly installed

---

## License

This project is provided as-is for educational and commercial use.