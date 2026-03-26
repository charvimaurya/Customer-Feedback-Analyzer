import streamlit as st
import requests
import pandas as pd
import os

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Customer Feedback Analyzer",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for premium look
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff;
        color: white;
    }
    .sentiment-card {
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 20px;
    }
    .good { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
    .neutral { background-color: #fff3cd; color: #856404; border: 1px solid #ffeeba; }
    .bad { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Customer Feedback Analyzer")
st.markdown("Analyze customer sentiment in real-time and track feedback history.")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("New Analysis")
    review_text = st.text_area("Enter Customer Review:", height=150, placeholder="Type or paste customer feedback here...")
    
    if st.button("Analyze Sentiment"):
        if review_text.strip():
            try:
                with st.spinner("Analyzing..."):
                    response = requests.post(f"{API_URL}/predict", json={"review": review_text})
                    response.raise_for_status()
                    sentiment = response.json().get("sentiment", "Unknown")
                    
                    # Display result with styling
                    sentiment_class = sentiment.lower()
                    st.markdown(f"""
                        <div class="sentiment-card {sentiment_class}">
                            <h3>Predicted Sentiment: {sentiment}</h3>
                        </div>
                    """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error connecting to API: {e}")
        else:
            st.warning("Please enter some text to analyze.")

with col2:
    st.subheader("Recent History")
    if st.button("Refresh History"):
        try:
            response = requests.get(f"{API_URL}/history")
            response.raise_for_status()
            history_data = response.json()
            
            if history_data:
                # Convert to DataFrame for better display
                df = pd.DataFrame(history_data)
                # Select and rename columns for display
                df_display = df[['raw_content', 'sentiment', 'created_at']].copy()
                df_display.columns = ['Review', 'Sentiment', 'Date']
                st.dataframe(df_display, use_container_width=True)
            else:
                st.info("No history found yet.")
        except Exception as e:
            st.error(f"Error fetching history: {e}")
    else:
        st.info("Click 'Refresh History' to see recent analyzed reviews.")

st.divider()
st.caption("Built with FastAPI, Streamlit, and PostgreSQL")
