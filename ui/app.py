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
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
    /* Global Typography */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
        color: white;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 123, 255, 0.2);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 123, 255, 0.3);
    }
    
    /* Sentiment Cards */
    .sentiment-card {
        padding: 25px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        transition: transform 0.2s ease;
    }
    .sentiment-card:hover {
        transform: scale(1.02);
    }
    .sentiment-card h3 { margin: 0; font-weight: 700; }
    .good { background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%); color: #155724; border: 1px solid #b1dfbb; }
    .neutral { background: linear-gradient(135deg, #fff3cd 0%, #ffeeba 100%); color: #856404; border: 1px solid #ffdf7e; }
    .bad { background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%); color: #721c24; border: 1px solid #f1b0b7; }
    
    /* PIS Insight Cards */
    .insight-card {
        background: white;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border-left: 6px solid #e5e7eb;
        position: relative;
        overflow: hidden;
    }
    .insight-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    }
    .insight-card.high-risk { border-left-color: #ef4444; }
    .insight-card.med-risk { border-left-color: #f59e0b; }
    .insight-card.low-risk { border-left-color: #10b981; }
    
    .insight-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #f3f4f6;
        padding-bottom: 16px;
        margin-bottom: 16px;
    }
    .insight-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #111827;
        margin: 0;
    }
    .pis-badge {
        color: white;
        padding: 6px 16px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 1.1rem;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .pis-badge.high { background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); box-shadow: 0 4px 10px rgba(239, 68, 68, 0.3); }
    .pis-badge.medium { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); box-shadow: 0 4px 10px rgba(245, 158, 11, 0.3); }
    .pis-badge.low { background: linear-gradient(135deg, #10b981 0%, #059669 100%); box-shadow: 0 4px 10px rgba(16, 185, 129, 0.3); }
    
    .insight-stats {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 16px;
    }
    .stat-item {
        display: flex;
        flex-direction: column;
    }
    .stat-label {
        font-size: 0.85rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .stat-value {
        font-size: 1.1rem;
        font-weight: 700;
        color: #374151;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Customer Feedback Analyzer")
st.markdown("Analyze customer sentiment in real-time and dynamically rank insights by Problem Impact Score (PIS).")

tab1, tab2 = st.tabs(["Real-time Analyzer", "Batch Upload & PIS Dashboard"])

with tab1:
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
                    df = pd.DataFrame(history_data)
                    df_display = df[['raw_content', 'sentiment', 'created_at']].copy()
                    df_display.columns = ['Review', 'Sentiment', 'Date']
                    st.dataframe(df_display, use_container_width=True)
                else:
                    st.info("No history found yet.")
            except Exception as e:
                st.error(f"Error fetching history: {e}")
        else:
            st.info("Click 'Refresh History' to see recent analyzed reviews.")

with tab2:
    col_upload, col_dash = st.columns([1, 2])
    
    with col_upload:
        st.subheader("Upload CSV Data")
        st.markdown("Ensure your CSV has these columns: `review_text`, `review_date` (optional).")
        uploaded_file = st.file_uploader("Upload Reviews", type=["csv"], label_visibility="collapsed")
        
        if uploaded_file is not None:
            if st.button("Process & Generate PIS"):
                with st.spinner("Analyzing with LLM..."):
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
                    try:
                        response = requests.post(f"{API_URL}/upload-csv", files=files)
                        response.raise_for_status()
                        st.success("Analysis started! Refresh dashboard shortly.")
                    except Exception as e:
                        st.error(f"Upload failed: {e}")
    
    with col_dash:
        st.subheader("Problem Impact Score (PIS) Rankings")
        
        if st.button("🔄 Refresh Rankings"):
            try:
                response = requests.get(f"{API_URL}/insights/ranked")
                response.raise_for_status()
                insights = response.json()
                
                if insights:
                    html_content = ""
                    for row in insights:
                        pis = round(row.get('pis_score', 0), 2)
                        
                        # Determine styling based on score
                        if pis > 15:
                            badge_class, border_class, icon = "high", "high-risk", "🔥"
                        elif pis > 5:
                            badge_class, border_class, icon = "medium", "med-risk", "⚠️"
                        else:
                            badge_class, border_class, icon = "low", "low-risk", "✅"
                            
                        date_str = row.get('last_calculated_at', '')[:10]
                        
                        html_content += f"""
                        <div class="insight-card {border_class}">
                            <div class="insight-header">
                                <h4 class="insight-title">{row.get('category', 'Unknown')}</h4>
                                <div class="pis-badge {badge_class}">{icon} PIS: {pis}</div>
                            </div>
                            <div class="insight-stats">
                                <div class="stat-item">
                                    <span class="stat-label">Total Impacted Reviews</span>
                                    <span class="stat-value">{row.get('total_reviews', 0)}</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-label">Last Calculated</span>
                                    <span class="stat-value">{date_str}</span>
                                </div>
                            </div>
                        </div>
                        """
                    
                    st.markdown(html_content, unsafe_allow_html=True)
                else:
                    st.info("No insights found. Upload some data to generate PIS rankings.")
            except Exception as e:
                st.error(f"Error fetching insights: {e}")
        else:
            st.info("Click 'Refresh Rankings' to load the dashboard.")

st.divider()
st.caption("Built with FastAPI, Streamlit, PostgreSQL, and OpenAI GPT-4o-mini")
