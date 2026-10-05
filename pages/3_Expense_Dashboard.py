"""
FinSight AI — Page 3: Expense Dashboard
Total spending, category breakdown, monthly trends, interactive Plotly charts.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import init_db, get_user_transactions, get_user
from src.spending_analytics import category_breakdown, monthly_trends, budget_analysis, payment_method_analysis, get_spending_summary
from src.report_generator import compute_monthly_health_report, generate_monthly_pdf
from config.settings import CURRENCY_SYMBOL

st.set_page_config(page_title="Expense Dashboard — FinSight AI", page_icon="📊", layout="wide")
init_db()

st.markdown("""
<div style="background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); padding: 2rem; border-radius: 16px; color: white; margin-bottom: 2rem;">
    <h1 style="background: linear-gradient(90deg, #f093fb, #f5576c); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">📊 Expense Dashboard</h1>
    <p>Comprehensive overview of your spending patterns</p>
</div>
""", unsafe_allow_html=True)

if not st.session_state.get('user_id'):
    st.warning("⚠️ Please set up your profile first!")
    st.stop()

transactions = get_user_transactions(st.session_state.user_id)

if transactions.empty:
    st.info("📤 No transactions found. Upload data on the **Upload Transactions** page.")
    st.stop()

user = get_user(st.session_state.user_id)
budget = user.get('budget', 0) if user else 0

# Ensure date column is datetime
transactions['date'] = pd.to_datetime(transactions['date'])

# === Quick Stats ===
summary = get_spending_summary(transactions, budget)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Spending", f"{CURRENCY_SYMBOL}{transactions['amount'].sum():,.0f}")
with col2:
    avg_monthly = transactions.groupby(transactions['date'].dt.to_period('M'))['amount'].sum().mean()
    st.metric("Avg Monthly", f"{CURRENCY_SYMBOL}{avg_monthly:,.0f}")
with col3:
    st.metric("Transactions", f"{len(transactions):,}")
with col4:
    if budget > 0:
        utilization = (avg_monthly / budget) * 100
        st.metric("Budget Utilization", f"{utilization:.1f}%")
    else:
        st.metric("Categories", transactions['category'].nunique())

# === Monthly Financial Statement & PDF Export ===
st.divider()
st.subheader("📅 Monthly Financial Health Statement & PDF Export")

available_months = sorted(transactions['date'].dt.to_period('M').astype(str).unique(), reverse=True)

if available_months:
    m_col1, m_col2 = st.columns([2, 1])
    with m_col1:
        selected_month = st.selectbox("Select Statement Month to Audit & Download:", available_months, index=0)
    
    report = compute_monthly_health_report(transactions, user, selected_month)
    
    if report:
        with m_col2:
            st.write("") # vertical alignment spacing
            pdf_bytes = generate_monthly_pdf(report, user)
            st.download_button(
                label=f"📥 Download {selected_month} Statement (PDF)",
                data=pdf_bytes,
                file_name=f"FinSight_Statement_{selected_month}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
        
        # Display monthly scorecard
        sc1, sc2, sc3, sc4 = st.columns(4)
        with sc1:
            st.metric("Month Expenditure", f"{CURRENCY_SYMBOL}{report['total_spent']:,.0f}")
        with sc2:
            st.metric("Monthly Budget", f"{CURRENCY_SYMBOL}{report['budget']:,.0f}")
        with sc3:
            net_bal = report['net_savings']
            delta_label = "Surplus" if net_bal >= 0 else "Deficit"
            st.metric("Net Balance", f"{CURRENCY_SYMBOL}{abs(net_bal):,.0f}", delta=f"{delta_label} ({report['utilization_pct']:.1f}% used)")
        with sc4:
            st.metric("Health Score", f"{report['health_score']}/100", delta=report['grade'])
            
        if report.get('anomalies'):
            st.warning(f"⚠️ **{len(report['anomalies'])} Unusual Anomaly Detected in {selected_month}:** " + 
                       ", ".join([f"{a['category']}: {CURRENCY_SYMBOL}{a['amount']:,.0f}" for a in report['anomalies']]))

st.divider()

# === Row 1: Category Breakdown + Monthly Trends ===
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🍕 Category Breakdown")
    cat_data = category_breakdown(transactions)
    
    if not cat_data.empty:
        fig_pie = px.pie(
            cat_data, names='category', values='total_amount',
            color_discrete_sequence=px.colors.qualitative.Set3,
            hole=0.45
        )
        fig_pie.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            margin=dict(t=30, b=30, l=30, r=30),
            legend=dict(font=dict(size=10))
        )
        st.plotly_chart(fig_pie, use_container_width=True)

with col_right:
    st.subheader("📈 Monthly Spending Trends")
    trends = monthly_trends(transactions)
    
    if not trends.empty:
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=trends['year_month'].astype(str),
            y=trends['total_expense'],
            mode='lines+markers',
            name='Total Expense',
            line=dict(color='#f5af19', width=3),
            marker=dict(size=8)
        ))
        
        if budget > 0:
            fig_trend.add_hline(
                y=budget, line_dash="dash",
                line_color="red",
                annotation_text=f"Budget: {CURRENCY_SYMBOL}{budget:,.0f}"
            )
        
        fig_trend.update_layout(
            xaxis_title="Month",
            yaxis_title=f"Amount ({CURRENCY_SYMBOL})",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            margin=dict(t=30, b=30)
        )
        st.plotly_chart(fig_trend, use_container_width=True)

st.divider()

# === Row 2: Category Bar Chart + Payment Methods ===
col_left2, col_right2 = st.columns(2)

with col_left2:
    st.subheader("📊 Spending by Category")
    if not cat_data.empty:
        fig_bar = px.bar(
            cat_data.sort_values('total_amount', ascending=True),
            x='total_amount', y='category',
            orientation='h',
            color='total_amount',
            color_continuous_scale='Viridis'
        )
        fig_bar.update_layout(
            xaxis_title=f"Total Amount ({CURRENCY_SYMBOL})",
            yaxis_title="",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            showlegend=False,
            margin=dict(t=30, b=30)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

with col_right2:
    st.subheader("💳 Payment Methods")
    pay_data = payment_method_analysis(transactions)
    
    if not pay_data.empty:
        # function returns column 'method' (not 'payment_method')
        name_col = 'method' if 'method' in pay_data.columns else 'payment_method'
        fig_pay = px.pie(
            pay_data, names=name_col, values='total_amount',
            color_discrete_sequence=['#667eea', '#764ba2', '#f5af19', '#f12711'],
            hole=0.5
        )
        fig_pay.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            margin=dict(t=30, b=30, l=30, r=30)
        )
        st.plotly_chart(fig_pay, use_container_width=True)

# === Budget Analysis ===
if budget > 0:
    st.divider()
    st.subheader("💰 Budget Analysis")
    
    budget_data = budget_analysis(transactions, budget)
    
    if budget_data:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            rate = budget_data.get('utilization_rate', 0)
            # budget_analysis returns % value (e.g. 85.2), display directly
            st.metric("Utilization Rate", f"{rate:.1f}%")
        with col2:
            st.metric("Months Over Budget", budget_data.get('months_over_budget', 0))
        with col3:
            st.metric("Months Under Budget", budget_data.get('months_under_budget', 0))
        with col4:
            savings = budget_data.get('avg_savings', 0)
            st.metric("Avg Monthly Savings", f"{CURRENCY_SYMBOL}{savings:,.0f}")

# === Recent Transactions ===
st.divider()
st.subheader("📋 Recent Transactions")
recent = transactions.sort_values('date', ascending=False).head(15)
st.dataframe(
    recent[['date', 'amount', 'category', 'payment_method', 'description', 'merchant']],
    use_container_width=True,
    column_config={
        "amount": st.column_config.NumberColumn(f"Amount ({CURRENCY_SYMBOL})", format="%,.0f"),
        "date": st.column_config.DateColumn("Date"),
    }
)
