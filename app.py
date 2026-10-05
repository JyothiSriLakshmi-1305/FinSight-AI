"""
FinSight AI — Main Streamlit Application
An AI-Powered Personal Finance Intelligence and Expense Forecasting System
"""

import streamlit as st
from pathlib import Path
import sys

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.database import init_db

# === Page Configuration ===
st.set_page_config(
    page_title="FinSight AI — Personal Finance Intelligence",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# === Initialize Database ===
init_db()

# === Custom CSS ===
st.markdown("""
<style>
    /* Main theme */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Gradient header */
    .hero-header {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        padding: 2.5rem 2rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    .hero-header h1 {
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        background: linear-gradient(90deg, #f5af19, #f12711);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .hero-header p {
        font-size: 1.1rem;
        opacity: 0.85;
        margin-bottom: 0;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #f5af19;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.7;
        margin-top: 0.3rem;
    }
    
    /* Feature cards */
    .feature-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        background: rgba(255, 255, 255, 0.06);
        border-color: rgba(245, 175, 25, 0.3);
    }
    
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0c29 0%, #1a1a2e 100%);
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .status-active {
        background: rgba(46, 213, 115, 0.15);
        color: #2ed573;
        border: 1px solid rgba(46, 213, 115, 0.3);
    }
    
    .status-warning {
        background: rgba(255, 165, 2, 0.15);
        color: #ffa502;
        border: 1px solid rgba(255, 165, 2, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# === Session State Initialization ===
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'transactions_loaded' not in st.session_state:
    st.session_state.transactions_loaded = False
if 'profile' not in st.session_state:
    st.session_state.profile = None
if 'forecast_results' not in st.session_state:
    st.session_state.forecast_results = None

# === Hero Header ===
st.markdown("""
<div class="hero-header">
    <h1>💰 FinSight AI</h1>
    <p>AI-Powered Personal Finance Intelligence & Expense Forecasting System</p>
</div>
""", unsafe_allow_html=True)

# === Welcome Section ===
if st.session_state.user_id is None:
    st.info("👋 **Welcome to FinSight AI!** Navigate to **User Profile** in the sidebar to get started.")

# === Feature Overview ===
st.subheader("🚀 What FinSight AI Can Do")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📊</div>
        <strong>Expense Analytics</strong>
        <p style="font-size: 0.85rem; opacity: 0.7;">Category breakdown, trends, and spending patterns</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🔮</div>
        <strong>ML Forecasting</strong>
        <p style="font-size: 0.85rem; opacity: 0.7;">3-model comparison: Random Forest, Linear Regression, LSTM</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">⚠️</div>
        <strong>Anomaly Detection</strong>
        <p style="font-size: 0.85rem; opacity: 0.7;">Statistical z-score analysis against your personal baseline</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🤖</div>
        <strong>AI Assistant</strong>
        <p style="font-size: 0.85rem; opacity: 0.7;">Llama 3.1 powered financial explanations via Ollama</p>
    </div>
    """, unsafe_allow_html=True)

# === How It Works ===
st.divider()
st.subheader("📋 How It Works")

steps = [
    ("1️⃣", "Set Up Profile", "Enter your income, monthly budget, and financial goals"),
    ("2️⃣", "Upload Transactions", "Upload a CSV/Excel file or enter transactions manually"),
    ("3️⃣", "Explore Analytics", "View category breakdowns, spending trends, and patterns"),
    ("4️⃣", "Detect Anomalies", "Automatically flag unusual expenses relative to your baseline"),
    ("5️⃣", "Get Forecasts", "ML models predict your next month's expenditure"),
    ("6️⃣", "Read Recommendations", "Personalized, data-driven savings suggestions"),
    ("7️⃣", "Chat with AI", "Ask questions about your finances in natural language"),
]

for i in range(0, len(steps), 3):
    cols = st.columns(3)
    for j, col in enumerate(cols):
        if i + j < len(steps):
            icon, title, desc = steps[i + j]
            with col:
                st.markdown(f"**{icon} {title}**")
                st.caption(desc)

# === Quick Status ===
st.divider()
col_status1, col_status2, col_status3 = st.columns(3)

with col_status1:
    if st.session_state.user_id:
        st.markdown(f'<span class="status-badge status-active">✅ Profile: {st.session_state.username}</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-badge status-warning">⏳ No profile set up</span>', unsafe_allow_html=True)

with col_status2:
    if st.session_state.transactions_loaded:
        st.markdown('<span class="status-badge status-active">✅ Transactions loaded</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-badge status-warning">⏳ No transactions uploaded</span>', unsafe_allow_html=True)

with col_status3:
    # Check Ollama status
    try:
        from src.genai_assistant import check_ollama_connection
        if check_ollama_connection():
            st.markdown('<span class="status-badge status-active">✅ Ollama connected</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-badge status-warning">⏳ Ollama offline</span>', unsafe_allow_html=True)
    except Exception:
        st.markdown('<span class="status-badge status-warning">⏳ Ollama offline</span>', unsafe_allow_html=True)

# === Footer ===
st.divider()
st.caption("FinSight AI — Final Year Academic Project | Powered by Scikit-learn, TensorFlow, Plotly, Streamlit & Llama 3.1")
