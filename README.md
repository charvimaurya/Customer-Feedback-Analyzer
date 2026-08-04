
Project description · MD
# Customer Feedback Analyzer
 
> An AI-powered system that transforms unstructured customer reviews into a prioritized, defensible action plan — in seconds, not hours.
 
---
 
## The Problem
 
Product managers and business analysts are drowning in customer feedback. A mid-sized e-commerce brand can receive hundreds of reviews per week across Amazon, Trustpilot, Google Play, and their own platform. The bottleneck is never *collecting* the feedback — it's making sense of it.
 
The current reality for most teams looks like this:
 
- A PM manually reads through hundreds of reviews before a quarterly planning session
- They highlight recurring complaints in a spreadsheet
- They present a prioritized list to stakeholders based on gut feel and recency bias
- Someone asks "why is sizing ahead of delivery on the roadmap?" and there's no data-backed answer
- Two weeks later, a new wave of reviews arrives and the process starts again
This is slow, subjective, and impossible to defend in a roadmap review. It also misses critical signals — a product issue that is getting *worse* over time looks identical to one that has been stable for months, and a review that says "I'm switching to a competitor" carries more business weight than one that says "not great" — but both get treated as the same negative data point.
 
**The core problem: teams lack a system that converts qualitative, high-volume feedback into a ranked, auditable action list with built-in business context.**
 
---
 
## The Solution
 
The Customer Feedback Analyzer is a full-stack AI system that ingests customer reviews from multiple sources, enriches each one with machine learning and large language model analysis, and surfaces a prioritized list of issues ranked by a compound scoring formula called the **Problem Impact Score (PIS)**.
 
Instead of reading reviews, a PM pastes a product URL or uploads a CSV and gets back:
 
- A ranked list of issue categories ordered by business impact
- A severity score for each category that accounts for frequency, recency, and emotional intensity
- Revenue risk flags on reviews that signal churn, returns, or brand switching
- An AI chatbot to query the data in plain English
The system does not just report what customers are saying. It tells you **what to fix first and why**, with a number anyone can audit.
 
---
 
## How It Works
 
### Data ingestion
Reviews enter the system through two paths:
 
- **CSV / Excel / JSON upload** — for internal data exports, CRM dumps, NPS responses, or historical review archives
- **URL scraper** — paste a Trustpilot, G2, or Google Play Store URL and the system fetches reviews directly, with no manual export step
### Two-stage analysis pipeline
 
**Stage 1 — Sentiment classification (ML model)**
Each review is cleaned with NLTK, vectorized with TF-IDF, and classified as Good, Neutral, or Bad using a Logistic Regression model trained on customer review data. This runs locally with no API cost.
 
**Stage 2 — LLM enrichment (GPT-4o-mini)**
Each review is passed to GPT-4o-mini which extracts three additional signals that the sentiment classifier cannot provide:
 
| Signal | What it captures |
|---|---|
| `insight_category` | The business area the review is about (e.g. Sizing & fit, Delivery, Return process) |
| `intensity_score` | How strongly negative or positive, on a 1–10 scale — "awful" scores differently to "not great" |
| `revenue_risk_flag` | Whether the review contains language that signals lost revenue — returns, refunds, brand switching, "never buying again" |
 
### Problem Impact Score (PIS)
 
Every insight category is scored on a single compound number:
 
```
PIS = frequency × recency_weight × avg_intensity × revenue_risk_multiplier
```
 
| Factor | Logic |
|---|---|
| `frequency` | How many reviews mention this issue out of the total |
| `recency_weight` | Reviews from the last 30 days are weighted 3×, decaying linearly to 1× at 180 days |
| `avg_intensity` | The mean intensity score across all reviews in this category |
| `revenue_risk_multiplier` | 1.5× applied to any category where revenue-risk reviews are present |
 
Nobody sees the formula. The PM sees a number from 0–100 next to each issue, colour-coded by severity, and knows that #1 needs fixing before #2. A problem that is getting *worse* over time surfaces faster than one that has been stable for a year. A category full of churn-language reviews scores higher than one of equal frequency with milder complaints.
 
### Dashboard and export
Results are displayed in a Streamlit dashboard with:
- Four headline metrics (total reviews, negative rate, revenue risk count, average intensity)
- A ranked PIS leaderboard with severity colour coding (🔥 critical, ⚠️ moderate, ✅ low)
- Full review table with filters by sentiment, category, and source
- An AI chatbot tab for plain-English queries against the review data
- One-click export to PDF (stakeholder report), Excel (ranked data table), or JSON (developer use)
---
 
## Why This Is Different From Standard Sentiment Analysis
 
Most sentiment analysis tools answer: *"Are customers happy?"*
 
This system answers: *"What is the #1 thing costing us revenue, and how urgently do we need to fix it?"*
 
The distinction matters because:
 
- **Sentiment is a commodity.** Every major cloud provider offers it. The value is not in labelling reviews Good or Bad — it is in ranking the *categories* of problems by business impact.
- **Recency decay is built in.** A wave of sizing complaints from last week outranks an equally frequent delivery issue from six months ago, automatically.
- **Revenue language is separated from general negativity.** "The colour was a bit off" and "I'm never buying from this brand again" are both negative — but only one of them is a churn signal. The system treats them differently.
- **The output is a prioritized action list, not a report.** The intended workflow is: reviews come in → PIS recalculates → highest-scoring issue is assigned to a team member → they action it → mark resolved → next issue surfaces. The system is built for doing, not just reading.
---
 
## Tech Stack
 
| Layer | Technology |
|---|---|
| Backend API | FastAPI (Python) |
| Frontend | Streamlit |
| Database | PostgreSQL via SQLAlchemy |
| Sentiment model | TF-IDF + Logistic Regression (scikit-learn) |
| LLM enrichment | OpenAI `gpt-4o-mini` |
| Web scraper | Requests + BeautifulSoup · Playwright (for JS-rendered pages) |
| Containerisation | Docker Compose |
 
---

## Architecture

![Architecture Diagram](architecture-diagram.svg)

## Project Structure 
```
Customer-Feedback-Analyzer
│
├── api/                    # FastAPI application
│   └── main.py
│
├── services/               # Core business logic
│   ├── sentiment_service.py
│   ├── review_analysis.py
│   ├── chatbot.py           # Interactive CLI chatbot
│   ├── preprocessing.py
│   └── chat_history.py
│
├── database/               # Database setup
│   ├── db.py
│   ├── models.py
│   └── init_db.py
│
├── models/                 # ML models & vectorizers
│   ├── logistic_regression.pkl
│   └── tfidf_vectorizer.pkl
│
├── notebooks/              # Training & evaluation notebooks
│
├── utils/                  # Text utilities
│
├── frontend/               # Web frontend
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── Dockerfile
├── requirements.txt
└── README.md

```

## Who This Is Built For
 
The primary user is a **product manager or business analyst** at a consumer-facing company who regularly reads customer reviews to inform their roadmap. They are comfortable with data but not necessarily technical. They need to walk into a planning meeting with a defensible, ranked list of issues — not a CSV of labelled sentiment.
 
Secondary users include:
- **Customer experience teams** triaging support issues
- **E-commerce operators** monitoring competitor product pages on Trustpilot or G2
- **Founders** who want a fast read on product-market fit signals from public reviews
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
### Step 6: Run the Web Frontend

Open frontend/index.html in a browser.

Optional: Serve locally with Python:
```bash
cd frontend
python -m http.server 5500
```

Open: http://localhost:5500/index.html

Upload CSV/TXT with a review column for bulk analysis.

Or enter a single review for sentiment & AI explanation.

CSV Example:
```csv
review
"This product is amazing!"
"Battery stopped working after a week."
"The design feels premium."
```

### Step 7: Run the Interactive Chatbot (Optional)

The chatbot provides a conversational interface for analyzing customer feedback.

1. **Open a new terminal window** (keep the Docker containers running in the first terminal)

2. **Install Python dependencies** (if not already installed):
   ```bash
   pip install openai requests python-dotenv
   ```

3. **Run the chatbot**:
   ```bash
   python services/chatbot.py
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
  "reply": "Good | Neutral | Bad"
}
```
#### `POST /chat`
**Description**: Explains why a sentiment was assigned using an LLM  
**Request Body**:
```json
{
  "review": "The quality of the product was okay but could be better"
}
```
**Response**:
```json
{
  "reply": "The sentiment was assigned as neutral because the review expresses a mixed opinion. The phrase "the product quality is okay" indicates a moderate level of satisfaction, while "could be better" suggests dissatisfaction or room for improvement. This balance of positive and negative elements results in a neutral overall sentiment."
}
```
#### `POST /analyze-file`
**Description**: Upload a .csv or .txt file containing multiple reviews. 
**Request Body**:
```
upload file
```
**Response**:
```json
{
"statistics": {
"total_reviews": 120,
"good": 70,
"neutral": 30,
"bad": 20
},
"best_reviews": ["Excellent design", "Great battery life"],
"worst_reviews": ["Screen cracked easily"],
"insights": "Overall customers value design but durability is a concern..."
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

| Table              | Purpose                 |
| ------------------ | ----------------------- |
| raw_feedbacks      | Stores original reviews |
| cleaned_feedbacks  | Preprocessed text       |
| positive_feedbacks | Positive reviews        |
| negative_feedbacks | Negative reviews        |
| feedbacks          | Legacy combined table   |


---
## Running with Docker
1️⃣ Build the image
docker build -t feedback-analyzer .

2️⃣ Run the container
docker run -p 8000:8000 --env-file .env feedback-analyzer

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
