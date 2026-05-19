# Customer Feedback Analyzer - Codebase Overview

This document provides a comprehensive overview of the Customer Feedback Analyzer codebase, intended for AI agents and developers to quickly understand the architecture, components, and data flow.

## Architecture & Components

The application is a distributed system consisting of the following main components:

1.  **FastAPI Backend (`api/`)**: Serves as the core API, processing text, running machine learning inferences, and interacting with the database.
2.  **Streamlit Frontend (`ui/`)**: Provides a web-based user interface for real-time sentiment analysis and historical data viewing.
3.  **CLI Chatbot (`chatbot/`)**: A terminal-based chatbot that integrates with the backend for sentiment analysis and uses OpenAI's GPT models to generate contextual responses.
4.  **PostgreSQL Database (`database.py`)**: Stores all feedback data (raw, processed, and sentiment labels).
5.  **Machine Learning Models (`models/` & `notebooks/`)**: Pre-trained TF-IDF vectorizers and Logistic Regression models for sentiment classification, along with the Jupyter notebooks used to create them.

---

## Detailed Component Breakdown

### 1. Database Layer (`database.py`)
-   **ORM**: Uses SQLAlchemy.
-   **Connection**: Expects a PostgreSQL connection string via the `DATABASE_URL` environment variable (defaults to `postgresql://user:password@db:5432/customer_feedback`).
-   **Schema**:
    -   Table: `feedbacks`
    -   Columns: `id` (Integer), `raw_content` (Text), `processed_content` (Text, nullable), `sentiment` (String), `created_at` (DateTime).
-   **Initialization**: Contains an `init_db()` function that retries connecting to the database 5 times. It creates tables using `Base.metadata.create_all(bind=engine)`.

### 2. Backend API (`api/main.py`)
-   **Framework**: FastAPI.
-   **Dependencies**: NLTK (for NLP preprocessing), Scikit-Learn/Joblib (for ML model loading), SQLAlchemy (for DB operations).
-   **Initialization**:
    -   Downloads NLTK resources (`stopwords`, `punkt`, `wordnet`) on startup.
    -   Loads the ML models from the `../models` directory. It tries to load `_updated.pkl` files first, falling back to older versions if they fail.
    -   Calls `init_db()` to ensure tables exist.
-   **Endpoints**:
    -   `GET /`: Health check.
    -   `POST /predict`: 
        1. Accepts a JSON payload `{"review": "text"}`.
        2. Cleans text: lowers casing, removes URLs/HTML/punctuation/digits, removes stopwords, and lemmatizes.
        3. Predicts sentiment (0=Bad, 1=Neutral, 2=Good) using the loaded TF-IDF vectorizer and Logistic Regression model.
        4. Saves the `raw_content`, `processed_content`, and `sentiment` to the database.
        5. Returns the predicted sentiment.
    -   `GET /history`: Retrieves the 10 most recent feedback entries from the database, ordered by `created_at` descending.

### 3. Frontend UI (`ui/app.py`)
-   **Framework**: Streamlit.
-   **Configuration**: Connects to the backend via the `API_URL` environment variable (defaults to `http://localhost:8000`).
-   **Features**:
    -   **New Analysis**: A text area to input reviews. Clicking "Analyze Sentiment" sends a POST request to the API and displays the result with color-coded styling (Green/Yellow/Red).
    -   **Recent History**: A button to fetch and display the last 10 analyzed reviews in a Pandas DataFrame table.

### 4. Chatbot (`chatbot/chatbot.py`)
-   **Framework**: Standard Python CLI + OpenAI SDK.
-   **Dependencies**: Requires an `OPENAI_API_KEY` and the `API_URL` of the backend.
-   **Workflow**:
    1. Prompts user for a review string.
    2. Calls the local backend (`/predict`) to classify the sentiment.
    3. Constructs a prompt for OpenAI: `"The user said: '{user_input}'. The sentiment is {sentiment}. Respond helpfully."`
    4. Streams/prints the GPT-3.5-turbo response to the terminal.

### 5. Entrypoint (`main.py`)
-   A simple script that reads the `PORT` environment variable and runs the FastAPI application (`api.main:app`) using Uvicorn on `0.0.0.0`.

### 6. Machine Learning (`notebooks/` & `models/`)
-   `customer_analyzer_preprocessing.ipynb`: Data cleaning, tokenization, lemmatization.
-   `customer_analyzer_training.ipynb`: TF-IDF vectorization, training Logistic Regression, exporting `.pkl` files.
-   `customer_analyzer_evaluate.ipynb`: Evaluating model accuracy and metrics.
-   The `.pkl` files in `models/` are the serialized artifacts of these notebooks.

---

## Data Flow for a Review
1. User enters text in Streamlit UI or CLI Chatbot.
2. HTTP POST request is sent to `FastAPI (api/main.py) /predict`.
3. FastAPI cleans the text using NLTK.
4. Cleaned text is transformed by the TF-IDF vectorizer.
5. Logistic Regression model predicts the sentiment integer, which is mapped to a string.
6. The raw text, cleaned text, and sentiment are committed to PostgreSQL via SQLAlchemy.
7. The string sentiment is returned in the HTTP response.
8. UI/Chatbot displays or utilizes the sentiment.
