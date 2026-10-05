"""
FinSight AI — Page 4: Spending Analysis
Deep-dive category analysis, growth rates, daily patterns, top merchants.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import init_db, get_user_transactions, get_user
from src.spending_analytics import (
    category_breakdown, monthly_trends, category_growth_rates,
    top_merchants, daily_spending_pattern, payment_method_analysis
)
from config.settings import CURRENCY_SYMBOL

st.set_page_config(page_title="Spending Analysis — FinSight AI", page_icon="📈", layout="wide")
init_db()

st.markdown("""
<div style="background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); padding: 2rem; border-radius: 16px; color: white; margin-bottom: 2rem;">
    <h1 style="background: linear-gradient(90deg, #fc5c7d, #6a82fb); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">📈 Spending Analysis</h1>
    <p>Deep dive into your spending patterns, trends, and habits</p>
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

# === Category Deep Dive ===
st.subheader("🔍 Category Deep Dive")

cat_data = category_breakdown(transactions)
selected_category = st.selectbox("Select a category to analyze", cat_data['category'].tolist() if not cat_data.empty else [])

if selected_category:
    cat_txns = transactions[transactions['category'] == selected_category]
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Spent", f"{CURRENCY_SYMBOL}{cat_txns['amount'].sum():,.0f}")
    with col2:
        st.metric("Avg Transaction", f"{CURRENCY_SYMBOL}{cat_txns['amount'].mean():,.0f}")
    with col3:
        st.metric("Max Transaction", f"{CURRENCY_SYMBOL}{cat_txns['amount'].max():,.0f}")
    with col4:
        st.metric("Transactions", len(cat_txns))
    
    # Monthly trend for selected category
    cat_monthly = cat_txns.groupby(cat_txns['date'].dt.to_period('M')).agg(
        total=('amount', 'sum'), count=('amount', 'count')
    ).reset_index()
    cat_monthly['date'] = cat_monthly['date'].astype(str)
    
    fig_cat = go.Figure()
    fig_cat.add_trace(go.Bar(x=cat_monthly['date'], y=cat_monthly['total'], name='Monthly Total', marker_color='#667eea'))
    fig_cat.update_layout(
        title=f"Monthly {selected_category} Spending",
        xaxis_title="Month", yaxis_title=f"Amount ({CURRENCY_SYMBOL})",
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white'
    )
    st.plotly_chart(fig_cat, use_container_width=True)

st.divider()

# === Category Growth Rates ===
st.subheader("📊 Category Growth Rates (Month-over-Month)")

growth_data = category_growth_rates(transactions)
if not growth_data.empty:
    # Pivot for heatmap
    try:
        growth_pivot = growth_data.pivot_table(index='category', columns='month', values='growth_rate', aggfunc='first')
        
        fig_heat = px.imshow(
            growth_pivot.values,
            labels=dict(x="Month", y="Category", color="Growth %"),
            x=[str(c) for c in growth_pivot.columns],
            y=growth_pivot.index.tolist(),
            color_continuous_scale='RdYlGn_r',
            aspect='auto'
        )
        fig_heat.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white',
            margin=dict(t=30)
        )
        st.plotly_chart(fig_heat, use_container_width=True)
    except Exception:
        st.dataframe(growth_data, use_container_width=True)
else:
    st.info("Not enough data for growth rate analysis (need at least 2 months).")

st.divider()

# === Daily Spending Pattern ===
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📅 Daily Spending Pattern")
    daily_data = daily_spending_pattern(transactions)
    
    if not daily_data.empty:
        fig_daily = px.bar(
            daily_data, x='day_name', y='avg_amount',
            color='avg_amount', color_continuous_scale='Turbo'
        )
        fig_daily.update_layout(
            xaxis_title="Day of Week", yaxis_title=f"Avg Spending ({CURRENCY_SYMBOL})",
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white',
            showlegend=False
        )
        st.plotly_chart(fig_daily, use_container_width=True)

with col_right:
    st.subheader("🏪 Top Merchants")
    merchant_data = top_merchants(transactions, n=10)
    
    if not merchant_data.empty:
        fig_merch = px.bar(
            merchant_data.sort_values('total_amount', ascending=True),
            x='total_amount', y='merchant', orientation='h',
            color='total_amount', color_continuous_scale='Plasma'
        )
        fig_merch.update_layout(
            xaxis_title=f"Total Spent ({CURRENCY_SYMBOL})", yaxis_title="",
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white',
            showlegend=False
        )
        st.plotly_chart(fig_merch, use_container_width=True)

# === Monthly Comparison ===
st.divider()
st.subheader("📊 Monthly Category Comparison")

transactions['year_month'] = transactions['date'].dt.to_period('M').astype(str)
monthly_cat = transactions.groupby(['year_month', 'category'])['amount'].sum().reset_index()

fig_stack = px.bar(
    monthly_cat, x='year_month', y='amount', color='category',
    color_discrete_sequence=px.colors.qualitative.Set3,
    barmode='stack'
)
fig_stack.update_layout(
    xaxis_title="Month", yaxis_title=f"Amount ({CURRENCY_SYMBOL})",
    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white',
    legend=dict(font=dict(size=9))
)
st.plotly_chart(fig_stack, use_container_width=True)
