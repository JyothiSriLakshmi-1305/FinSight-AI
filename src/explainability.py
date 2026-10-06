import pandas as pd
import numpy as np

def get_feature_importance(model, feature_names: list[str], model_type: str = 'rf') -> pd.DataFrame:
    """Get feature importance for tree-based or linear models."""
    importances = []
    
    if model_type.lower() == 'rf' or hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
    elif model_type.lower() == 'lr' or hasattr(model, 'coef_'):
        importances = np.abs(model.coef_)
    else:
        return None
        
    df = pd.DataFrame({
        'feature': feature_names,
        'importance': importances
    })
    
    # Normalize importance
    if df['importance'].sum() > 0:
        df['importance'] = df['importance'] / df['importance'].sum()
        
    return df.sort_values('importance', ascending=False).reset_index(drop=True)

def explain_prediction(model, features: pd.DataFrame, feature_names: list[str], model_type: str = 'rf') -> dict:
    """Explain a prediction by combining feature values with their global importance."""
    importance_df = get_feature_importance(model, feature_names, model_type)
    
    top_factors = []
    if importance_df is not None and not features.empty:
        # Get latest row
        latest = features.iloc[-1]
        
        # We attribute contribution by multiplying value by importance
        # (This is an approximation for explainability)
        for _, row in importance_df.head(5).iterrows():
            feat = row['feature']
            imp = row['importance']
            val = latest.get(feat, 0)
            
            if abs(imp) > 0.01:
                top_factors.append({
                    'feature': feat,
                    'importance': float(imp),
                    'value': float(val)
                })
                
    # Predict value
    try:
        pred = float(model.predict(features)[0])
    except:
        pred = 0.0
        
    return {
        'predicted_value': pred,
        'top_factors': top_factors,
        'model_type': model_type
    }

def format_explanation(explanation: dict) -> str:
    """Format the explanation as a human-readable string."""
    from config.settings import CURRENCY_SYMBOL
    
    pred = explanation.get('predicted_value', 0)
    factors = explanation.get('top_factors', [])
    
    text = f"Prediction: {CURRENCY_SYMBOL}{pred:,.2f}\n\nTop contributing factors:\n"
    
    for i, factor in enumerate(factors, 1):
        feat = factor['feature'].replace('_', ' ').title()
        val = factor['value']
        imp = factor['importance'] * 100
        text += f"  {i}. {feat} ({val:.2f}) — {imp:.1f}% importance\n"
        
    if not factors:
        text += "  (Model does not provide direct feature importances)"
        
    return text

from config.settings import CURRENCY_SYMBOL

def get_model_summary(results: dict) -> str:
    """Format model comparison results safely across all column naming conventions."""
    comp_df = results.get('comparison_df', pd.DataFrame())
    if comp_df is None or comp_df.empty:
        return "No model comparison available."
        
    summary = "Model Performance Comparison Leaderboard:\n"
    for _, row in comp_df.iterrows():
        # Handle both uppercase and lowercase column names
        name = row.get('Model') or row.get('model_name') or 'Model'
        mae = row.get('MAE') if row.get('MAE') is not None else row.get('mae', 0.0)
        rmse = row.get('RMSE') if row.get('RMSE') is not None else row.get('rmse', 0.0)
        acc = row.get('Accuracy (%)') if row.get('Accuracy (%)') is not None else row.get('accuracy')
        mape = row.get('MAPE (%)') if row.get('MAPE (%)') is not None else row.get('mape')
        
        acc_text = f" | Accuracy: {acc:.1f}%" if acc is not None else ""
        mape_text = f" | MAPE: {mape:.1f}%" if mape is not None else ""
        summary += f"- {name}: MAE = {CURRENCY_SYMBOL}{mae:,.0f}, RMSE = {CURRENCY_SYMBOL}{rmse:,.0f}{acc_text}{mape_text}\n"
        
    best_info = results.get('best_model', {})
    best_name = best_info.get('model_name') or best_info.get('Model', 'Unknown')
    summary += f"\n🏆 Top Model Selected: {best_name}"
    
    return summary
