"""
FinSight AI — Page 6: Forecast
ML prediction, model comparison, feature importance, prediction explanation.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import init_db, get_user_transactions, get_user, save_forecast
from src.feature_engineering import create_monthly_features, add_temporal_features, add_trend_features, prepare_train_test, prepare_lstm_sequences
from src.ml_forecasting import train_and_evaluate_all, predict_next_month, save_model
from src.anomaly_detection import detect_anomalies
from src.explainability import get_feature_importance, explain_prediction, format_explanation, get_model_summary
from config.settings import CURRENCY_SYMBOL, ML_CONFIG

st.set_page_config(page_title="Forecast — FinSight AI", page_icon="🔮", layout="wide")
init_db()

st.markdown("""
<div style="background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); padding: 2rem; border-radius: 16px; color: white; margin-bottom: 2rem;">
    <h1 style="background: linear-gradient(90deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">🔮 Expense Forecast</h1>
    <p>ML-powered expense prediction using Random Forest, Linear Regression, and LSTM</p>
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

# Check minimum data
n_months = transactions.groupby(transactions['date'].dt.to_period('M')).ngroups
if n_months < 4:
    st.warning(f"⚠️ Only {n_months} months of data found. Need at least 4 months for meaningful forecasts.")
    st.stop()

# === Train & Predict ===
if st.button("🚀 Train Models & Generate Forecast", use_container_width=True, type="primary"):
    
    progress_bar = st.progress(0)
    status = st.empty()
    
    try:
        # Step 1: Feature Engineering
        status.text("📊 Creating features from transaction data...")
        progress_bar.progress(10)
        
        monthly_features = create_monthly_features(transactions, budget=budget)
        monthly_features = add_temporal_features(monthly_features)
        monthly_features = add_trend_features(monthly_features)
        
        progress_bar.progress(25)
        
        # Step 2: Prepare train/test split
        status.text("✂️ Splitting data (temporal split — no data leakage)...")
        
        test_months = min(ML_CONFIG['test_months'], len(monthly_features) - 3)
        X_train, X_test, y_train, y_test, feature_names = prepare_train_test(monthly_features, test_months=test_months)
        
        progress_bar.progress(35)
        
        # Step 3: Prepare LSTM data
        status.text("🧠 Preparing LSTM sequences...")
        
        X_lstm_train, X_lstm_test, y_lstm_train, y_lstm_test = None, None, None, None
        try:
            X_sequences, y_targets = prepare_lstm_sequences(monthly_features)
            if X_sequences is not None and len(X_sequences) >= 4:
                split_idx = max(1, len(X_sequences) - test_months)
                X_lstm_train = X_sequences[:split_idx]
                X_lstm_test = X_sequences[split_idx:]
                y_lstm_train = y_targets[:split_idx]
                y_lstm_test = y_targets[split_idx:]
        except Exception as e:
            st.info(f"ℹ️ LSTM skipped: {str(e)}")
        
        progress_bar.progress(45)
        
        # Step 4: Train all models
        status.text("🏋️ Training Random Forest, Linear Regression, and LSTM...")
        
        results = train_and_evaluate_all(
            X_train, X_test, y_train, y_test,
            X_lstm_train, X_lstm_test, y_lstm_train, y_lstm_test
        )
        
        progress_bar.progress(80)
        
        # Step 5: Generate prediction
        status.text("🔮 Generating next-month prediction...")
        
        best_result = results.get('best_model', {})
        best_model = best_result.get('model')
        best_scaler = best_result.get('scaler')
        best_name = best_result.get('model_name', 'Unknown')
        
        # Get latest features for prediction
        latest_features = X_test.iloc[-1:] if len(X_test) > 0 else X_train.iloc[-1:]
        prediction = predict_next_month(best_model, best_scaler, latest_features)
        
        progress_bar.progress(90)
        
        # Save results to session state
        st.session_state.forecast_results = {
            'prediction': prediction,
            'best_model_name': best_name,
            'all_results': results,
            'feature_names': feature_names,
            'best_model': best_model,
            'X_test': X_test,
            'y_test': y_test
        }
        
        # Save to database
        from datetime import datetime
        now = datetime.now()
        next_month = now.month + 1 if now.month < 12 else 1
        next_year = now.year if now.month < 12 else now.year + 1
        
        try:
            save_forecast(
                st.session_state.user_id,
                next_month, next_year,
                prediction, best_name
            )
        except Exception:
            pass
        
        progress_bar.progress(100)
        status.text("✅ Forecast complete!")
        
    except Exception as e:
        st.error(f"❌ Error during forecasting: {str(e)}")
        import traceback
        with st.expander("Error Details"):
            st.code(traceback.format_exc())

# === Display Results ===
if st.session_state.get('forecast_results'):
    results = st.session_state.forecast_results
    prediction = results['prediction']
    best_name = results['best_model_name']
    all_results = results['all_results']
    
    st.divider()
    
    # === Prediction Display ===
    st.subheader("🎯 Next Month Prediction")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Predicted Expense",
            f"{CURRENCY_SYMBOL}{prediction:,.0f}",
            delta=f"Budget: {CURRENCY_SYMBOL}{budget:,.0f}" if budget > 0 else None
        )
    with col2:
        st.metric("Best Model", best_name.upper())
    with col3:
        if budget > 0:
            diff = prediction - budget
            status = "Over Budget" if diff > 0 else "Under Budget"
            st.metric("Budget Status", status, delta=f"{CURRENCY_SYMBOL}{abs(diff):,.0f}")
    
    # Budget warning
    if budget > 0 and prediction > budget:
        st.error(f"⚠️ **Budget Alert:** Predicted expense ({CURRENCY_SYMBOL}{prediction:,.0f}) exceeds your budget ({CURRENCY_SYMBOL}{budget:,.0f}) by {CURRENCY_SYMBOL}{prediction - budget:,.0f}")
    elif budget > 0:
        st.success(f"✅ Predicted expense is within budget. Expected savings: {CURRENCY_SYMBOL}{budget - prediction:,.0f}")
    
    st.divider()
    
    # === Model Comparison ===
    st.subheader("📊 Model Comparison")
    
    comparison_df = all_results.get('comparison_df')
    if comparison_df is not None and not comparison_df.empty:
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown("##### 🏆 Model Leaderboard")
            available_subsets_min = [c for c in ['MAE', 'RMSE', 'MAPE (%)'] if c in comparison_df.columns]
            available_subsets_max = [c for c in ['Accuracy (%)'] if c in comparison_df.columns]

            styler = comparison_df.style
            if available_subsets_min:
                styler = styler.highlight_min(subset=available_subsets_min, color='rgba(46, 213, 115, 0.3)')
            if available_subsets_max:
                styler = styler.highlight_max(subset=available_subsets_max, color='rgba(46, 213, 115, 0.4)')

            st.dataframe(styler, use_container_width=True)
        
        with col_right:
            st.markdown("##### 📊 Accuracy Comparison")
            if 'Accuracy (%)' in comparison_df.columns:
                fig_comp = px.bar(
                    comparison_df,
                    x='Model', y='Accuracy (%)',
                    color='Accuracy (%)',
                    color_continuous_scale=['#f5576c', '#f093fb', '#2ed573'],
                    text='Accuracy (%)'
                )
                fig_comp.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                fig_comp.update_layout(
                    yaxis=dict(range=[0, 110], title="Accuracy (%)"),
                    xaxis_title="",
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    showlegend=False,
                    margin=dict(t=20, b=20)
                )
                st.plotly_chart(fig_comp, use_container_width=True)
            else:
                fig_comp = go.Figure()
                fig_comp.add_trace(go.Bar(x=comparison_df['Model'], y=comparison_df['MAE'], name='MAE', marker_color='#667eea'))
                fig_comp.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
                st.plotly_chart(fig_comp, use_container_width=True)
        
        # Model summary
        summary_str = get_model_summary(all_results)
        if summary_str:
            with st.expander("📝 Model Summary"):
                st.text(summary_str)
    
    st.divider()
    
    # === Feature Importance ===
    st.subheader("🔑 Feature Importance")
    
    best_model = results.get('best_model')
    feature_names = results.get('feature_names', [])
    
    if best_model and feature_names:
        is_tree = any(k in best_name.lower() for k in ['random', 'rf', 'gradient', 'boosting'])
        model_type = 'rf' if is_tree else 'lr'
        importance_df = get_feature_importance(best_model, feature_names, model_type)
        
        if importance_df is not None and not importance_df.empty:
            fig_imp = px.bar(
                importance_df.head(10).sort_values('importance'),
                x='importance', y='feature', orientation='h',
                color='importance', color_continuous_scale='Viridis'
            )
            fig_imp.update_layout(
                title=f"Top 10 Features ({best_name.upper()})",
                xaxis_title="Importance", yaxis_title="",
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font_color='white', showlegend=False
            )
            st.plotly_chart(fig_imp, use_container_width=True)
    
    # === Actual vs Predicted ===
    st.divider()
    st.subheader("📈 Actual vs Predicted (Test Set)")
    
    for model_result in all_results.get('model_results', []):
        model_name = model_result.get('model_name', '')
        y_test_vals = model_result.get('y_test')
        y_pred_vals = model_result.get('predictions')
        
        if y_test_vals is not None and y_pred_vals is not None:
            try:
                y_test_arr = np.array(y_test_vals).flatten()
                y_pred_arr = np.array(y_pred_vals).flatten()
                min_len = min(len(y_test_arr), len(y_pred_arr))
                
                if min_len > 0:
                    scatter_df = pd.DataFrame({
                        'Actual': y_test_arr[:min_len],
                        'Predicted': y_pred_arr[:min_len]
                    })
                    
                    fig_scatter = px.scatter(
                        scatter_df, x='Actual', y='Predicted',
                        title=f"{model_name} — Actual vs Predicted",
                        color_discrete_sequence=['#f5af19']
                    )
                    
                    min_val = min(scatter_df['Actual'].min(), scatter_df['Predicted'].min())
                    max_val = max(scatter_df['Actual'].max(), scatter_df['Predicted'].max())
                    fig_scatter.add_shape(
                        type="line", x0=min_val, y0=min_val, x1=max_val, y1=max_val,
                        line=dict(color="red", dash="dash")
                    )
                    fig_scatter.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                        font_color='white'
                    )
                    st.plotly_chart(fig_scatter, use_container_width=True)
            except Exception:
                pass
    
    # === Prediction Explanation ===
    st.divider()
    st.subheader("💡 Prediction Explanation")
    
    if best_model and feature_names:
        X_test = results.get('X_test')
        if X_test is not None and len(X_test) > 0:
            model_type = 'rf' if 'random' in best_name.lower() or 'rf' in best_name.lower() else 'lr'
            explanation = explain_prediction(best_model, X_test.iloc[-1:], feature_names, model_type)
            if explanation:
                formatted = format_explanation(explanation)
                st.code(formatted, language=None)

else:
    st.info("👆 Click the button above to train models and generate your forecast.")
