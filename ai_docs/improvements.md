# Codebase Improvements

This file documents potential technical debt, architectural improvements, and optimizations for the Customer Feedback Analyzer.

## Security & Configuration
- **Hardcoded Credentials**: `chatbot/chatbot.py` contains a placeholder `"your-api-key-here"`. While it uses `os.getenv`, default fallbacks for secrets can lead to accidental leaks or unexpected behavior. Similar issues exist in `database.py` with the default PostgreSQL URI containing `user:password`.
- **Environment Management**: Rely more strictly on a configuration management library like `pydantic-settings` to handle all environment variables, type casting, and validation centrally, rather than calling `os.getenv` in multiple files.

## Application Lifecycle & Performance
- **Model Loading**: In `api/main.py`, the ML models are loaded in the global scope synchronously. This delays the initial worker startup. It is best practice in FastAPI to load models using the `lifespan` context manager so they are loaded precisely when the app starts, preventing startup blocks and aiding in testing.
- **NLTK Downloads**: `api/main.py` tries to download NLTK data globally on import. This should ideally be moved to a Docker build step or a separate pre-start script to ensure the API worker doesn't fail or stall due to network issues at runtime.
- **Synchronous Database Calls**: The current setup uses synchronous SQLAlchemy (`SessionLocal`, `create_engine`). Migrating to `async` SQLAlchemy (with `asyncpg`) and making the FastAPI endpoints `async def` would greatly improve the concurrency and throughput of the API.

## Code Quality & Maintainability
- **Magic Strings/Numbers**: Sentiment mapping (`pred == 2` -> "Good") is hardcoded in the `/predict` route. These should be defined as Enum classes (e.g., `SentimentLabel.GOOD`).
- **Error Handling & Transactions**: In `api/main.py`, `db.rollback()` is used within a broad `except Exception` block. It is often cleaner to handle sessions using context managers or Dependency Injection that automatically handles rollbacks on exceptions, reducing boilerplate code.
- **Database Migrations**: Currently, `database.py` uses `Base.metadata.create_all(bind=engine)`. For a production system, this should be replaced with `Alembic` to manage schema versions and migrations properly over time.

## Frontend (Streamlit)
- **State Management**: The Streamlit app refetches history only when the "Refresh History" button is clicked. It could utilize `st.session_state` and Streamlit's fragment caching or autorefresh capabilities to provide a more real-time dashboard feel without manual refreshes.
- **Hardcoded Styling**: The UI uses injected CSS via `st.markdown(unsafe_allow_html=True)`. This can become difficult to maintain. Using native Streamlit theming (via `.streamlit/config.toml`) is preferred where possible.

## Chatbot
- **Model Selection**: `chatbot.py` hardcodes `gpt-3.5-turbo`. Upgrading to `gpt-4o-mini` would provide better performance and intelligence at a similar or lower cost.
- **Error Handling**: The exception blocks simply print or return the stringified error. Implementing structured logging and retries (e.g., using `tenacity`) would make the CLI tool more robust against temporary API failures.
