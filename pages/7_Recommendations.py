"""
FinSight AI — Page 7: Recommendations
Personalized, data-driven financial recommendations with savings potential.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import init_db, get_user_transactions, get_user
from src.financial_profile import build_profile
from src.anomaly_detection import detect_anomalies, get_anomaly_summary
from src.recurrence_analysis import detect_recurring, get_recurrence_report
from src.spending_analytics import category_growth_rates
from src.recommendations import generate_recommendations, prioritize_recommendations, format_for_display, get_savings_summary
from config.settings import CURRENCY_SYMBOL

st.set_page_config(page_title="Recommendations — FinSight AI", page_icon="💡", layout="wide")
init_db()

st.markdown("""
<div style="background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); padding: 2rem; border-radius: 16px; color: white; margin-bottom: 2rem;">
    <h1 style="background: linear-gradient(90deg, #11998e, #38ef7d); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">💡 Recommendations</h1>
    <p>Personalized, data-driven financial advice based on your spending patterns</p>
</div>
""", unsafe_allow_html=True)

if not st.session_state.get('user_id'):
    st.warning("⚠️ Please set up your profile first!")
    st.stop()

transactions = get_user_transactions(st.session_state.user_id)
if transactions.empty:
    st.info("📤 No transactions found. Upload data first.")
    st.stop()

transactions['date'] = pd.to_datetime(transactions['date'])
user = get_user(st.session_state.user_id)
budget = user.get('budget', 0) if user else 0
income = user.get('income', 0) if user else 0

# === Build all required inputs ===
with st.spinner("🔍 Analyzing your financial data..."):
    # Profile
    profile = build_profile(transactions, income=income, budget=budget,
                           financial_goal=user.get('financial_goal', ''))
    
    # Anomalies
    analyzed_txns = detect_anomalies(transactions, budget=budget)
    anomaly_summary = get_anomaly_summary(analyzed_txns)
    
    # Recurrence
    recurring_txns = detect_recurring(transactions)
    recurrence_report = get_recurrence_report(recurring_txns)
    
    # Category trends
    cat_trends = category_growth_rates(transactions)
    
    # Prediction (use session state if available)
    prediction = None
    if st.session_state.get('forecast_results'):
        prediction = st.session_state.forecast_results.get('prediction', None)
    
    if prediction is None:
        prediction = profile.get('avg_monthly_expense', 0)

# === Generate Recommendations ===
recommendations = generate_recommendations(
    prediction=prediction,
    profile=profile,
    anomalies=anomaly_summary,
    recurring=recurrence_report,
    category_trends=cat_trends
)

recommendations = prioritize_recommendations(recommendations)
display_recs = format_for_display(recommendations)
savings = get_savings_summary(recommendations)

# === Summary Metrics ===
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Recommendations", len(recommendations))
with col2:
    st.metric("Monthly Savings Potential",
              f"{CURRENCY_SYMBOL}{savings.get('total_monthly_savings_potential', 0):,.0f}")
with col3:
    st.metric("Annual Savings Potential",
              f"{CURRENCY_SYMBOL}{savings.get('total_annual_savings_potential', 0):,.0f}")
with col4:
    high_count = savings.get('action_count_by_priority', {}).get('high', 0)
    st.metric("High Priority Actions", high_count)

st.divider()

# === Priority Distribution ===
if recommendations:
    priority_counts = savings.get('action_count_by_priority', {})
    if priority_counts:
        col_left, col_right = st.columns([1, 2])
        
        with col_left:
            st.subheader("📊 Priority Breakdown")
            priority_df = pd.DataFrame([
                {"Priority": k.capitalize(), "Count": v}
                for k, v in priority_counts.items() if v > 0
            ])
            colors = {'High': '#ff4757', 'Medium': '#ffa502', 'Low': '#2ed573'}
            if not priority_df.empty:
                fig = px.pie(priority_df, names='Priority', values='Count',
                           color='Priority', color_discrete_map=colors)
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white', margin=dict(t=20, b=20)
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col_right:
            st.subheader("💰 Savings Opportunities")
            savings_recs = [r for r in display_recs if r.get('savings_potential', 0) > 0]
            if savings_recs:
                savings_df = pd.DataFrame([{
                    'Recommendation': r.get('title', 'N/A'),
                    'Monthly Savings': r.get('savings_potential', 0),
                    'Annual Savings': r.get('savings_potential', 0) * 12
                } for r in savings_recs])
                
                fig_bar = px.bar(
                    savings_df, x='Monthly Savings', y='Recommendation',
                    orientation='h', color='Monthly Savings',
                    color_continuous_scale='Greens'
                )
                fig_bar.update_layout(
                    xaxis_title=f"Monthly Savings ({CURRENCY_SYMBOL})",
                    yaxis_title="",
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white', showlegend=False
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("No specific savings amounts identified — see recommendations below.")

    st.divider()

# === Recommendation Cards ===
st.subheader("📋 Your Personalized Recommendations")

if not display_recs:
    st.success("✅ Your spending patterns look healthy! No major recommendations at this time.")
else:
    for i, rec in enumerate(display_recs):
        priority = rec.get('priority', 'low')
        icon = rec.get('icon', '💡')
        color_map = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}
        priority_icon = color_map.get(priority, '⚪')
        
        title = rec.get('title', 'Recommendation')
        message = rec.get('message', '')
        savings_pot = rec.get('savings_potential', 0)
        rec_type = rec.get('type', 'general')
        
        with st.expander(f"{priority_icon} {icon} {title}", expanded=(priority == 'high')):
            st.markdown(f"**{message}**")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.caption(f"Priority: **{priority.upper()}**")
            with col2:
                st.caption(f"Type: {rec_type.replace('_', ' ').title()}")
            with col3:
                if savings_pot > 0:
                    st.caption(f"💰 Potential savings: {CURRENCY_SYMBOL}{savings_pot:,.0f}/month")

# === Recurring Expenses Section ===
st.divider()
st.subheader("🔄 Recurring Expenses Summary")

if recurrence_report:
    recurring_list = recurrence_report.get('recurring_expenses', [])
    total_recurring = recurrence_report.get('total_recurring_monthly', 0)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Recurring Monthly", f"{CURRENCY_SYMBOL}{total_recurring:,.0f}")
    with col2:
        if budget > 0:
            pct = (total_recurring / budget) * 100
            st.metric("% of Budget (Recurring)", f"{pct:.1f}%")
    
    if recurring_list:
        rec_df = pd.DataFrame(recurring_list)
        st.dataframe(rec_df, use_container_width=True)
    else:
        st.info("No recurring expenses detected.")

# === Financial Health Score ===
st.divider()
st.subheader("🏥 Financial Health Snapshot")

col1, col2, col3 = st.columns(3)
with col1:
    trend = profile.get('spending_trend', 'Stable')
    trend_icon = {'Increasing': '📈', 'Decreasing': '📉', 'Stable': '➡️'}.get(trend, '➡️')
    st.metric("Spending Trend", f"{trend_icon} {trend}")

with col2:
    utilization = profile.get('budget_utilization_rate', 0)
    if utilization > 0:
        health = "Healthy" if utilization < 0.85 else "Caution" if utilization < 1.0 else "Over Budget"
        st.metric("Budget Health", health)
    else:
        st.metric("Budget Health", "Set a budget")

with col3:
    anomaly_count = anomaly_summary.get('total_anomalies', 0)
    st.metric("Unusual Expenses", anomaly_count)
