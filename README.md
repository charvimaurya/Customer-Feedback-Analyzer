# Customer Feedback Analyzer

A production-ready sentiment analysis system for customer reviews, integrated with PostgreSQL and Docker.

## Features
- **FastAPI Backend**: Provides a robust API for sentiment prediction.
- **Sentiment Analysis**: Uses a pre-trained Logistic Regression model with TF-IDF.
- **PostgreSQL Integration**: Automatically logs every prediction into a database.
- **Dockerized**: Easy setup with Docker and Docker Compose.
- **Chatbot Client**: Interactive CLI chatbot to analyze reviews via OpenAI.

## Getting Started

### Prerequisites
- Docker and Docker Compose
- (Optional) Python 3.10+ for local development

### Configuration
1. Copy `.env.example` to `.env`.
2. Update the `OPENAI_API_KEY` in `.env` if you want to use the chatbot.

### Running with Docker
The easiest way to run the entire stack (API + Database) is using Docker Compose:

```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`. You can access the automatic documentation at `http://localhost:8000/docs`.

### Running Locally
If you prefer to run locally:

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the API:
   ```bash
   python main.py
   ```
3. (Optional) Run the chatbot:
   ```bash
   python chatbot/chatbot.py
   ```

## API Endpoints
- `GET /`: Health check.
- `POST /predict`: Submit a review for sentiment analysis.
- `GET /history`: View the last 10 analyzed reviews.
