"""
FinSight AI — Page 5: Anomaly Detection
Flag unusual transactions with z-score analysis against user baseline.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import init_db, get_user_transactions, get_user
from src.anomaly_detection import detect_anomalies, get_anomaly_summary, get_anomaly_timeline
from config.settings import CURRENCY_SYMBOL, ANOMALY_CONFIG

st.set_page_config(page_title="Anomaly Detection — FinSight AI", page_icon="⚠️", layout="wide")
init_db()

st.markdown("""
<div style="background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); padding: 2rem; border-radius: 16px; color: white; margin-bottom: 2rem;">
    <h1 style="background: linear-gradient(90deg, #f12711, #f5af19); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">⚠️ Anomaly Detection</h1>
    <p>Identify unusual expenses using statistical z-score analysis against your personal spending baseline</p>
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

# === Run Anomaly Detection ===
with st.spinner("🔍 Analyzing transactions for anomalies..."):
    analyzed = detect_anomalies(transactions, budget=budget)
    summary = get_anomaly_summary(analyzed)

# === Summary Metrics ===
total_anomalies = summary.get('total_anomalies', 0)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Anomalies", total_anomalies)
with col2:
    st.metric("Anomaly Amount", f"{CURRENCY_SYMBOL}{summary.get('total_anomaly_amount', 0):,.0f}")
with col3:
    severe = summary.get('by_severity', {}).get('Severe', 0)
    st.metric("Severe Anomalies", severe)
with col4:
    pct = (total_anomalies / len(transactions) * 100) if len(transactions) > 0 else 0
    st.metric("Anomaly Rate", f"{pct:.1f}%")

st.divider()

if total_anomalies == 0:
    st.success("✅ No anomalies detected! Your spending patterns look consistent.")
    st.stop()

# === Severity Distribution ===
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🔴 Severity Distribution")
    severity_data = summary.get('by_severity', {})
    if severity_data:
        sev_df = pd.DataFrame([
            {"Severity": k, "Count": v} for k, v in severity_data.items()
        ])
        colors = {'Mild': '#ffa502', 'Moderate': '#ff6348', 'Severe': '#ff4757'}
        fig_sev = px.bar(
            sev_df, x='Severity', y='Count',
            color='Severity',
            color_discrete_map=colors
        )
        fig_sev.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font_color='white', showlegend=False
        )
        st.plotly_chart(fig_sev, use_container_width=True)

with col_right:
    st.subheader("📂 Anomalies by Category")
    cat_data = summary.get('by_category', {})
    if cat_data:
        cat_df = pd.DataFrame([
            {"Category": k, "Count": v} for k, v in cat_data.items()
        ])
        fig_cat = px.pie(
            cat_df, names='Category', values='Count',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_cat.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        st.plotly_chart(fig_cat, use_container_width=True)

# === Anomaly Timeline ===
st.divider()
st.subheader("📅 Anomaly Timeline")

timeline = get_anomaly_timeline(analyzed)
if not timeline.empty:
    fig_timeline = go.Figure()
    
    severity_colors = {'Mild': '#ffa502', 'Moderate': '#ff6348', 'Severe': '#ff4757'}
    
    for severity in ['Mild', 'Moderate', 'Severe']:
        sev_data = timeline[timeline['anomaly_severity'] == severity]
        if not sev_data.empty:
            fig_timeline.add_trace(go.Scatter(
                x=sev_data['date'],
                y=sev_data['amount'],
                mode='markers',
                name=severity,
                marker=dict(
                    size=sev_data['amount'].apply(lambda x: min(max(x/5000, 8), 40)),
                    color=severity_colors.get(severity, '#ffffff'),
                    opacity=0.8
                ),
                text=sev_data.apply(
                    lambda r: f"{r['category']}: {CURRENCY_SYMBOL}{r['amount']:,.0f}<br>{r.get('anomaly_reason', '')}",
                    axis=1
                ),
                hovertemplate='%{text}<extra></extra>'
            ))
    
    fig_timeline.update_layout(
        title="Anomalous Transactions Over Time",
        xaxis_title="Date", yaxis_title=f"Amount ({CURRENCY_SYMBOL})",
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )
    st.plotly_chart(fig_timeline, use_container_width=True)

# === Detailed Anomaly Cards ===
st.divider()
st.subheader("🔎 Anomaly Details")

anomalies_list = summary.get('anomalies_list', [])
if anomalies_list:
    for i, anomaly in enumerate(anomalies_list[:20]):  # Show top 20
        severity = anomaly.get('anomaly_severity', 'Unknown')
        color = {'Mild': '🟡', 'Moderate': '🟠', 'Severe': '🔴'}.get(severity, '⚪')
        
        with st.expander(
            f"{color} {anomaly.get('category', 'N/A')} — {CURRENCY_SYMBOL}{anomaly.get('amount', 0):,.0f} "
            f"on {anomaly.get('date', 'N/A')} [{severity}]",
            expanded=(severity == 'Severe')
        ):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Amount:** {CURRENCY_SYMBOL}{anomaly.get('amount', 0):,.0f}")
                st.write(f"**Category:** {anomaly.get('category', 'N/A')}")
                st.write(f"**Date:** {anomaly.get('date', 'N/A')}")
                st.write(f"**Merchant:** {anomaly.get('merchant', 'N/A')}")
            with col2:
                st.write(f"**Z-Score:** {anomaly.get('z_score', 0):.2f}")
                st.write(f"**Severity:** {severity}")
                st.write(f"**Reason:** {anomaly.get('anomaly_reason', 'N/A')}")
                st.write(f"**Description:** {anomaly.get('description', 'N/A')}")

# === Configuration Info ===
with st.expander("⚙️ Detection Configuration"):
    st.json(ANOMALY_CONFIG)
