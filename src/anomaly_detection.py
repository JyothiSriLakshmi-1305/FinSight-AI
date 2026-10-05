import pandas as pd
import numpy as np
from typing import Dict, Any, List
from config.settings import ANOMALY_CONFIG, CURRENCY_SYMBOL

def detect_anomalies(transactions: pd.DataFrame, budget: float = 0) -> pd.DataFrame:
    """Detect anomalous transactions using z-score method.
    For each transaction:
    1. Compute user's historical mean and std for that category
    2. Calculate z-score
    3. Flag as anomaly if z-score > threshold OR amount > budget_ratio_threshold * budget
    Returns original df with added columns: is_anomaly, z_score, anomaly_severity, anomaly_reason
    """
    if transactions.empty:
        return transactions

    df = transactions.copy()
    df['is_anomaly'] = False
    df['z_score'] = 0.0
    df['anomaly_severity'] = 'Normal'
    df['anomaly_reason'] = ''

    # Calculate category stats
    cat_stats = df.groupby('category')['amount'].agg(['mean', 'std']).reset_index()
    
    # Fill NaN std with 0
    cat_stats['std'] = cat_stats['std'].fillna(0)

    for idx, row in df.iterrows():
        cat = row['category']
        amount = row['amount']
        
        stats = cat_stats[cat_stats['category'] == cat]
        if stats.empty:
            continue
            
        c_mean = stats['mean'].values[0]
        c_std = stats['std'].values[0]
        
        z_score = (amount - c_mean) / c_std if c_std > 0 else 0.0
        df.at[idx, 'z_score'] = z_score
        
        severity = classify_severity(z_score)
        
        is_anom = False
        reason = []
        
        if severity != 'Normal':
            is_anom = True
            reason.append(f"Z-score {z_score:.2f} indicates {severity} anomaly.")
            
        if budget > 0 and amount > (ANOMALY_CONFIG['budget_ratio_threshold'] * budget):
            is_anom = True
            reason.append(f"Amount exceeds {ANOMALY_CONFIG['budget_ratio_threshold']*100}% of monthly budget.")
            severity = 'Severe' if severity in ['Normal', 'Mild'] else severity
            
        if amount > (ANOMALY_CONFIG['category_multiplier'] * c_mean):
            is_anom = True
            reason.append(f"Amount is more than {ANOMALY_CONFIG['category_multiplier']}x category average.")
            severity = 'Severe' if severity in ['Normal', 'Mild'] else severity

        df.at[idx, 'is_anomaly'] = is_anom
        if is_anom:
            df.at[idx, 'anomaly_severity'] = severity if severity != 'Normal' else 'Mild'
            exp = explain_anomaly(row, c_mean, c_std)
            df.at[idx, 'anomaly_reason'] = exp + " " + " ".join(reason)

    return df

def classify_severity(z_score: float) -> str:
    """Classify anomaly severity: 'Normal', 'Mild', 'Moderate', 'Severe' based on ANOMALY_CONFIG thresholds."""
    abs_z = abs(z_score)
    if abs_z >= ANOMALY_CONFIG['z_score_severe']:
        return 'Severe'
    elif abs_z >= ANOMALY_CONFIG['z_score_moderate']:
        return 'Moderate'
    elif abs_z >= ANOMALY_CONFIG['z_score_mild']:
        return 'Mild'
    return 'Normal'

def explain_anomaly(transaction: pd.Series, category_mean: float, category_std: float) -> str:
    """Generate a human-readable explanation for why this transaction is anomalous."""
    amt = transaction['amount']
    cat = transaction['category']
    return f"{CURRENCY_SYMBOL}{amt:,.2f} in {cat} — your average {cat} spending is {CURRENCY_SYMBOL}{category_mean:,.2f}/transaction."

def get_anomaly_summary(transactions: pd.DataFrame) -> Dict[str, Any]:
    """Return summary: total_anomalies, by_severity (dict), by_category (dict), total_anomaly_amount, anomalies_list (list of dicts)."""
    if transactions.empty or 'is_anomaly' not in transactions.columns:
        return {
            'total_anomalies': 0,
            'by_severity': {},
            'by_category': {},
            'total_anomaly_amount': 0.0,
            'anomalies_list': []
        }
        
    anomalies = transactions[transactions['is_anomaly'] == True]
    
    by_sev = anomalies['anomaly_severity'].value_counts().to_dict()
    by_cat = anomalies['category'].value_counts().to_dict()
    total_amt = anomalies['amount'].sum()
    
    return {
        'total_anomalies': len(anomalies),
        'by_severity': by_sev,
        'by_category': by_cat,
        'total_anomaly_amount': total_amt,
        'anomalies_list': anomalies.to_dict(orient='records')
    }

def get_anomaly_timeline(transactions: pd.DataFrame) -> pd.DataFrame:
    """Return anomalies sorted by date for timeline display."""
    if transactions.empty or 'is_anomaly' not in transactions.columns:
        return pd.DataFrame()
        
    anomalies = transactions[transactions['is_anomaly'] == True].copy()
    if not pd.api.types.is_datetime64_any_dtype(anomalies['date']):
        anomalies['date'] = pd.to_datetime(anomalies['date'])
        
    return anomalies.sort_values(by='date')
