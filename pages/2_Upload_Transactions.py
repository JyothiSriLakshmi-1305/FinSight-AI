"""
FinSight AI — Page 2: Upload Transactions
CSV/Excel upload and manual transaction entry.
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import init_db, add_transactions, get_user_transactions, clear_user_transactions, get_user
from src.data_input import parse_csv, parse_excel, validate_dataframe, create_manual_transaction
from src.preprocessing import preprocess_pipeline
from config.settings import EXPENSE_CATEGORIES, PAYMENT_METHODS, CURRENCY_SYMBOL, SAMPLE_DATA_PATH

st.set_page_config(page_title="Upload Transactions — FinSight AI", page_icon="📤", layout="wide")
init_db()

st.markdown("""
<div style="background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); padding: 2rem; border-radius: 16px; color: white; margin-bottom: 2rem;">
    <h1 style="background: linear-gradient(90deg, #11998e, #38ef7d); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">📤 Upload Transactions</h1>
    <p>Upload your expense data via CSV/Excel or enter transactions manually</p>
</div>
""", unsafe_allow_html=True)

# === Check User ===
if not st.session_state.get('user_id'):
    st.warning("⚠️ Please set up your profile first! Go to **User Profile** page.")
    st.stop()

user = get_user(st.session_state.user_id)
st.info(f"📌 Uploading for user: **{st.session_state.username}** (ID: {st.session_state.user_id})")

# === Tabs ===
tab_upload, tab_manual, tab_sample = st.tabs(["📁 File Upload", "✍️ Manual Entry", "📦 Load Sample Data"])

with tab_upload:
    st.subheader("Upload CSV or Excel File")
    
    st.markdown("""
    **Required columns:** `date`, `amount`, `category`  
    **Optional columns:** `payment_method`, `description`, `merchant`
    """)
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['csv', 'xlsx', 'xls'],
        help="Upload a CSV or Excel file with your transaction data"
    )
    
    if uploaded_file:
        try:
            # Parse file
            if uploaded_file.name.endswith('.csv'):
                df = parse_csv(uploaded_file)
            else:
                df = parse_excel(uploaded_file)
            
            st.success(f"✅ File parsed: **{len(df)} transactions** found")
            
            # Validate
            is_valid, errors = validate_dataframe(df)
            
            if errors:
                with st.expander("⚠️ Validation Warnings", expanded=True):
                    for error in errors:
                        st.warning(error)
            
            # Preview
            st.subheader("📋 Data Preview")
            st.dataframe(df.head(20), use_container_width=True)
            
            # Summary
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Transactions", len(df))
            with col2:
                st.metric("Total Amount", f"{CURRENCY_SYMBOL}{df['amount'].sum():,.0f}")
            with col3:
                st.metric("Categories", df['category'].nunique())
            
            # Preprocess and save
            if st.button("✅ Process & Save Transactions", use_container_width=True, type="primary"):
                with st.spinner("Processing transactions..."):
                    processed_df = preprocess_pipeline(df)
                    
                    # Clear existing and add new
                    clear_user_transactions(st.session_state.user_id)
                    count = add_transactions(st.session_state.user_id, processed_df)
                    
                    st.session_state.transactions_loaded = True
                    st.success(f"✅ **{count} transactions** saved successfully!")
                    st.balloons()
                    
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")

with tab_manual:
    st.subheader("Enter Transaction Manually")
    
    with st.form("manual_entry", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            txn_date = st.date_input("📅 Date")
            txn_amount = st.number_input(f"💰 Amount ({CURRENCY_SYMBOL})", min_value=1, value=500, step=50)
            txn_category = st.selectbox("📂 Category", EXPENSE_CATEGORIES)
        
        with col2:
            txn_payment = st.selectbox("💳 Payment Method", PAYMENT_METHODS)
            txn_description = st.text_input("📝 Description", placeholder="e.g., Lunch at office")
            txn_merchant = st.text_input("🏪 Merchant", placeholder="e.g., Swiggy")
        
        submitted = st.form_submit_button("➕ Add Transaction", use_container_width=True, type="primary")
        
        if submitted:
            txn = create_manual_transaction(
                date=txn_date,
                amount=txn_amount,
                category=txn_category,
                payment_method=txn_payment,
                description=txn_description,
                merchant=txn_merchant
            )
            txn_df = pd.DataFrame([txn])
            count = add_transactions(st.session_state.user_id, txn_df)
            st.session_state.transactions_loaded = True
            st.success(f"✅ Transaction added: {CURRENCY_SYMBOL}{txn_amount:,} in {txn_category}")

with tab_sample:
    st.subheader("Load Sample Transaction Data")
    st.markdown("Load the built-in sample dataset for demonstration purposes.")
    
    if SAMPLE_DATA_PATH.exists():
        st.info(f"📦 Sample data found at: `{SAMPLE_DATA_PATH.name}`")
        
        # Preview sample
        sample_df = pd.read_csv(SAMPLE_DATA_PATH)
        st.dataframe(sample_df.head(10), use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Transactions", len(sample_df))
        with col2:
            st.metric("Total", f"{CURRENCY_SYMBOL}{sample_df['amount'].sum():,.0f}")
        with col3:
            st.metric("Months", sample_df['date'].apply(lambda x: x[:7]).nunique())
        
        if st.button("📦 Load Sample Data", use_container_width=True, type="primary"):
            with st.spinner("Loading sample transactions..."):
                processed_df = preprocess_pipeline(sample_df)
                clear_user_transactions(st.session_state.user_id)
                count = add_transactions(st.session_state.user_id, processed_df)
                st.session_state.transactions_loaded = True
                st.success(f"✅ **{count} sample transactions** loaded!")
                st.balloons()
    else:
        st.warning("⚠️ Sample data file not found. It will be generated during setup.")

# === Current Data Summary ===
st.divider()
st.subheader("📊 Current Transaction Data")

transactions = get_user_transactions(st.session_state.user_id)

if not transactions.empty:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Transactions", len(transactions))
    with col2:
        st.metric("Total Spending", f"{CURRENCY_SYMBOL}{transactions['amount'].sum():,.0f}")
    with col3:
        st.metric("Categories", transactions['category'].nunique())
    with col4:
        date_range = f"{transactions['date'].min()} to {transactions['date'].max()}"
        st.metric("Date Range", date_range[:21])
    
    with st.expander("📋 View All Transactions", expanded=False):
        st.dataframe(
            transactions.sort_values('date', ascending=False),
            use_container_width=True,
            height=400
        )
    
    # Clear data option
    if st.button("🗑️ Clear All Transactions", type="secondary"):
        clear_user_transactions(st.session_state.user_id)
        st.session_state.transactions_loaded = False
        st.warning("All transactions cleared!")
        st.rerun()
else:
    st.info("No transactions loaded yet. Use the tabs above to add data.")
