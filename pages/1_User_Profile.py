"""
FinSight AI — Page 1: User Profile
Set up income, budget, financial goals, and view financial baseline.
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import init_db, add_user, get_user, get_user_by_username, update_user_profile, get_user_transactions
from src.financial_profile import build_profile, compare_to_budget
from config.settings import CURRENCY_SYMBOL

st.set_page_config(page_title="User Profile — FinSight AI", page_icon="👤", layout="wide")
init_db()

st.markdown("""
<style>
    .profile-header {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        padding: 2rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2rem;
    }
    .profile-header h1 {
        background: linear-gradient(90deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .profile-stat {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
    }
    .profile-stat .value { font-size: 1.6rem; font-weight: 700; color: #f5af19; }
    .profile-stat .label { font-size: 0.85rem; opacity: 0.7; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="profile-header">
    <h1>👤 User Profile</h1>
    <p>Set up your financial identity and view your spending baseline</p>
</div>
""", unsafe_allow_html=True)

# === Profile Setup / Login ===
tab_new, tab_existing = st.tabs(["🆕 New Profile", "🔑 Load Existing"])

with tab_new:
    st.subheader("Create Your Financial Profile")
    
    with st.form("profile_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input("👤 Username", placeholder="e.g., jyothi_sri")
            income = st.number_input(f"💰 Monthly Income ({CURRENCY_SYMBOL})", min_value=0, value=30000, step=1000)
        
        with col2:
            budget = st.number_input(f"📊 Monthly Budget ({CURRENCY_SYMBOL})", min_value=0, value=22000, step=1000)
            financial_goal = st.text_input("🎯 Financial Goal", placeholder="e.g., Save ₹50,000 for emergency fund")
        
        submitted = st.form_submit_button("✅ Create Profile", use_container_width=True, type="primary")
        
        if submitted:
            if not username:
                st.error("Please enter a username!")
            else:
                # Check if user exists
                existing = get_user_by_username(username)
                if existing:
                    st.warning(f"Username '{username}' already exists. Loading profile...")
                    st.session_state.user_id = existing['id']
                    st.session_state.username = existing['username']
                    # Update profile with new values
                    update_user_profile(existing['id'], income=income, budget=budget, financial_goal=financial_goal)
                    st.success("Profile updated!")
                else:
                    user_id = add_user(username, income=income, budget=budget, financial_goal=financial_goal)
                    st.session_state.user_id = user_id
                    st.session_state.username = username
                    st.success(f"✅ Profile created for **{username}**! (User ID: {user_id})")
                    st.balloons()
                st.rerun()

with tab_existing:
    st.subheader("Load Existing Profile")
    
    load_username = st.text_input("Enter your username", key="load_user")
    
    if st.button("🔑 Load Profile", use_container_width=True):
        if load_username:
            user = get_user_by_username(load_username)
            if user:
                st.session_state.user_id = user['id']
                st.session_state.username = user['username']
                st.success(f"✅ Welcome back, **{user['username']}**!")
                st.rerun()
            else:
                st.error(f"No user found with username '{load_username}'")
        else:
            st.error("Please enter a username")

# === Profile Display ===
st.divider()

if st.session_state.user_id:
    user = get_user(st.session_state.user_id)
    
    if user:
        st.subheader(f"📋 Profile: {user['username']}")
        
        # Profile info cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="profile-stat">
                <div class="value">{CURRENCY_SYMBOL}{user.get('income', 0):,.0f}</div>
                <div class="label">Monthly Income</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="profile-stat">
                <div class="value">{CURRENCY_SYMBOL}{user.get('budget', 0):,.0f}</div>
                <div class="label">Monthly Budget</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            goal = user.get('financial_goal', 'Not set')
            st.markdown(f"""
            <div class="profile-stat">
                <div class="value">🎯</div>
                <div class="label">{goal if goal else 'Not set'}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="profile-stat">
                <div class="value">#{user['id']}</div>
                <div class="label">User ID</div>
            </div>
            """, unsafe_allow_html=True)
        
        # === Financial Baseline (if transactions exist) ===
        transactions = get_user_transactions(st.session_state.user_id)
        
        if not transactions.empty:
            st.divider()
            st.subheader("📈 Financial Baseline")
            
            profile = build_profile(
                transactions,
                income=user.get('income', 0),
                budget=user.get('budget', 0),
                financial_goal=user.get('financial_goal', '')
            )
            st.session_state.profile = profile
            
            # Baseline metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Avg Monthly Expense",
                    f"{CURRENCY_SYMBOL}{profile['avg_monthly_expense']:,.0f}",
                    delta=f"{profile['spending_trend']}"
                )
            
            with col2:
                utilization = profile.get('budget_utilization_rate', 0)
                st.metric(
                    "Budget Utilization",
                    f"{utilization:.1%}",
                    delta="Over budget" if utilization > 1 else "Under budget",
                    delta_color="inverse"
                )
            
            with col3:
                st.metric(
                    "Expense Volatility",
                    f"{CURRENCY_SYMBOL}{profile['expense_volatility']:,.0f}",
                    help="Standard deviation of monthly expenses"
                )
            
            with col4:
                st.metric(
                    "Total Transactions",
                    f"{profile['total_transactions']:,}",
                    delta=f"{profile['total_months']} months of data"
                )
            
            # Category distribution
            st.divider()
            st.subheader("📊 Spending Distribution")
            
            import plotly.express as px
            
            cat_dist = profile.get('category_distribution', {})
            if cat_dist:
                cat_df_data = [{"Category": k, "Percentage": v} for k, v in cat_dist.items()]
                import pandas as pd
                cat_df = pd.DataFrame(cat_df_data)
                
                fig = px.pie(
                    cat_df, names='Category', values='Percentage',
                    title='Spending Distribution by Category',
                    color_discrete_sequence=px.colors.qualitative.Set3,
                    hole=0.4
                )
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Budget comparison
            budget_comp = compare_to_budget(profile)
            if budget_comp:
                st.divider()
                st.subheader("💰 Budget Health")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Budget Status", budget_comp.get('budget_status', 'N/A'))
                with col2:
                    st.metric("Months Over Budget", budget_comp.get('overspend_months', 0))
                with col3:
                    st.metric("Months Under Budget", budget_comp.get('underspend_months', 0))
        else:
            st.info("📤 No transactions found. Go to **Upload Transactions** to add your data!")
else:
    st.info("👆 Create or load a profile above to get started.")
