"""
FinSight AI — Page 8: AI Financial Assistant
Chat interface powered by Llama 3.1 via Ollama with template fallbacks.
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import init_db, get_user_transactions, get_user, get_connection
from src.financial_profile import build_profile
from src.anomaly_detection import detect_anomalies, get_anomaly_summary
from src.recurrence_analysis import get_recurrence_report, detect_recurring
from src.genai_assistant import (
    get_ai_status, build_financial_context,
    explain_prediction as ai_explain_prediction,
    explain_recommendations as ai_explain_recs,
    financial_chat
)
from src.recommendations import generate_recommendations, prioritize_recommendations
from config.settings import CURRENCY_SYMBOL, GENAI_CONFIG

st.set_page_config(page_title="AI Assistant — FinSight AI", page_icon="🤖", layout="wide")
init_db()

# Initialize session state keys
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []

st.markdown("""
<div style="background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); padding: 2rem; border-radius: 16px; color: white; margin-bottom: 2rem;">
    <h1 style="background: linear-gradient(90deg, #a18cd1, #fbc2eb); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">🤖 AI Financial Assistant</h1>
    <p>Ask questions about your finances — powered by Google Gemini AI with grounded financial analytics</p>
</div>
""", unsafe_allow_html=True)

# Auto-detect or select profile if not currently in session
if not st.session_state.get('user_id'):
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT id, username FROM users")
        existing_users = c.fetchall()
        conn.close()
    except Exception:
        existing_users = []
        
    if existing_users:
        st.info("💡 **Select a profile to activate FinSight AI analysis:**")
        col_sel, col_btn = st.columns([3, 1])
        with col_sel:
            user_dict = {u['username']: u['id'] for u in existing_users}
            chosen_username = st.selectbox("Active Profile:", list(user_dict.keys()), index=0)
        with col_btn:
            st.write("") # vertical spacing
            if st.button("Activate Profile", type="primary", use_container_width=True):
                st.session_state.user_id = user_dict[chosen_username]
                st.session_state.username = chosen_username
                st.rerun()
        st.stop()
    else:
        st.warning("⚠️ No profiles found. Please create one on the **User Profile** page first.")
        st.stop()

# === Check AI Status (Gemini / Ollama) ===
ai_status = get_ai_status()

if ai_status["available"]:
    st.success(f"✅ **{ai_status['message']}**")
else:
    st.info(
        "💡 **Offline Rule-Based Mode Active.** The assistant is using local deterministic financial logic.\n\n"
        "**To unlock real-time Gemini AI:** Open `.env` in the project folder and paste your free key:\n"
        "`GEMINI_API_KEY=AIzaSy...` (from [Google AI Studio](https://aistudio.google.com/app/apikey))"
    )

# === Build Financial Context ===
transactions = get_user_transactions(st.session_state.user_id)
user = get_user(st.session_state.user_id)
budget = user.get('budget', 0) if user else 0
income = user.get('income', 0) if user else 0

context = ""
profile = None

if not transactions.empty:
    transactions['date'] = pd.to_datetime(transactions['date'])
    
    profile = build_profile(transactions, income=income, budget=budget,
                           financial_goal=user.get('financial_goal', ''))
    
    analyzed = detect_anomalies(transactions, budget=budget)
    anomaly_summary = get_anomaly_summary(analyzed)
    
    recurring_txns = detect_recurring(transactions)
    recurrence_report = get_recurrence_report(recurring_txns)
    
    prediction = None
    if st.session_state.get('forecast_results'):
        prediction = st.session_state.forecast_results.get('prediction')
    
    recs = generate_recommendations(
        prediction=prediction or profile.get('avg_monthly_expense', 0),
        profile=profile,
        anomalies=anomaly_summary,
        recurring=recurrence_report
    )
    recs = prioritize_recommendations(recs)
    
    context = build_financial_context(
        profile=profile,
        prediction=prediction,
        anomalies=anomaly_summary,
        recommendations=recs
    )

# === Quick Action Buttons ===
st.subheader("⚡ Quick Actions")

col1, col2, col3, col4 = st.columns(4)

with col1:
    explain_pred = st.button("🔮 Explain My Forecast", use_container_width=True)
with col2:
    explain_recs = st.button("💡 Explain Recommendations", use_container_width=True)
with col3:
    spending_summary = st.button("📊 Spending Summary", use_container_width=True)
with col4:
    financial_health = st.button("🏥 Financial Health", use_container_width=True)

# Handle quick actions
if explain_pred:
    if context:
        with st.spinner("🤔 Thinking..."):
            response = ai_explain_prediction(context)
        st.markdown("### 🔮 Forecast Explanation")
        st.markdown(response)
    else:
        st.info("Upload transactions and run a forecast first.")

if explain_recs:
    if context and recs:
        with st.spinner("🤔 Thinking..."):
            response = ai_explain_recs(recs, context)
        st.markdown("### 💡 Recommendation Explanation")
        st.markdown(response)
    else:
        st.info("Upload transactions to generate recommendations.")

if spending_summary:
    if profile:
        st.markdown("### 📊 Spending Summary")
        st.markdown(f"""
**Monthly Overview:**
- Average monthly expense: **{CURRENCY_SYMBOL}{profile.get('avg_monthly_expense', 0):,.0f}**
- Budget: **{CURRENCY_SYMBOL}{budget:,.0f}**
- Budget utilization: **{profile.get('budget_utilization_rate', 0):.1%}**
- Spending trend: **{profile.get('spending_trend', 'N/A')}**

**Top Categories:**
""")
        cat_dist = profile.get('category_distribution', {})
        for cat, pct in list(cat_dist.items())[:5]:
            st.markdown(f"- {cat}: **{pct:.1f}%**")
    else:
        st.info("Upload transactions first.")

if financial_health:
    if profile:
        utilization = profile.get('budget_utilization_rate', 0)
        trend = profile.get('spending_trend', 'Stable')
        volatility = profile.get('expense_volatility', 0)
        
        health_score = 100
        if utilization > 1.0:
            health_score -= 30
        elif utilization > 0.9:
            health_score -= 15
        if trend == 'Increasing':
            health_score -= 10
        if volatility > profile.get('avg_monthly_expense', 1) * 0.3:
            health_score -= 10
        
        health_score = max(0, health_score)
        
        st.markdown("### 🏥 Financial Health Check")
        
        if health_score >= 80:
            st.success(f"**Score: {health_score}/100** — Excellent! Your finances are well-managed.")
        elif health_score >= 60:
            st.warning(f"**Score: {health_score}/100** — Good, but there's room for improvement.")
        else:
            st.error(f"**Score: {health_score}/100** — Needs attention. Review your recommendations.")
        
        st.markdown(f"""
- Budget utilization: **{utilization:.1%}** {'✅' if utilization < 0.9 else '⚠️'}
- Spending trend: **{trend}** {'✅' if trend != 'Increasing' else '⚠️'}
- Expense stability: **{CURRENCY_SYMBOL}{volatility:,.0f}** std {'✅' if volatility < profile.get('avg_monthly_expense', 1) * 0.3 else '⚠️'}
""")
    else:
        st.info("Upload transactions first.")

st.divider()

# === Chat Interface ===
st.subheader("💬 Ask Me Anything About Your Finances")

# Initialize chat history
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []

# Display chat history
for message in st.session_state.chat_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
user_input = st.chat_input("Ask about your expenses, budget, savings, or forecasts...")

if user_input:
    # Add user message
    st.session_state.chat_messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            if context:
                response = financial_chat(user_input, context)
            else:
                response = (
                    "I don't have any transaction data to analyze yet. "
                    "Please upload your transactions on the **Upload Transactions** page first, "
                    "then come back here for personalized financial insights!"
                )
        
        st.markdown(response)
    
    # Add assistant response
    st.session_state.chat_messages.append({"role": "assistant", "content": response})

# Clear chat button
if st.session_state.chat_messages:
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_messages = []
        st.rerun()

# === Context Info ===
with st.expander("ℹ️ How the AI Assistant Works"):
    st.markdown("""
    **Data-Grounded Responses:** The AI assistant uses ONLY your actual financial data to respond. 
    It never invents numbers or makes up statistics.
    
    **Context provided to the AI includes:**
    - Your financial profile (income, budget, average spending)
    - Spending patterns and category distribution
    - Detected anomalies and their explanations
    - Recurring expenses and their impact
    - ML forecast predictions (if generated)
    - Personalized recommendations
    
    **Two operating modes:**
    - 🟢 **Google Gemini Connected:** Real-time financial intelligence powered by Google Gemini
    - 🟡 **Offline Mode:** Rule-based deterministic financial reasoning using your local SQLite data
    """)
