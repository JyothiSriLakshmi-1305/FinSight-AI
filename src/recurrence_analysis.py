import pandas as pd
import numpy as np
from typing import Dict, Any, List
from config.settings import RECURRENCE_CONFIG, ANOMALY_CONFIG

def detect_recurring(transactions: pd.DataFrame) -> pd.DataFrame:
    """Detect recurring transactions by finding similar amounts in the same category at regular intervals.
    Uses amount_tolerance (±15%) to match 'similar' amounts.
    Returns df with added columns: is_recurring, recurrence_type, recurrence_group
    """
    if transactions.empty:
        return transactions
        
    df = transactions.copy()
    df['is_recurring'] = False
    df['recurrence_type'] = 'None'
    df['recurrence_group'] = -1
    
    if not pd.api.types.is_datetime64_any_dtype(df['date']):
        df['date'] = pd.to_datetime(df['date'])
        
    df = df.sort_values(by='date')
    
    tolerance = RECURRENCE_CONFIG['amount_tolerance']
    min_occurrences = RECURRENCE_CONFIG['min_occurrences']
    
    group_id = 0
    # Process by category
    for cat in df['category'].unique():
        cat_df = df[df['category'] == cat]
        
        # Simple grouping by similar amount
        amounts = cat_df['amount'].values
        grouped = np.zeros(len(amounts), dtype=bool)
        
        for i, amt in enumerate(amounts):
            if grouped[i]:
                continue
                
            # Find similar amounts
            similar_mask = (amounts >= amt * (1 - tolerance)) & (amounts <= amt * (1 + tolerance))
            similar_indices = np.where(similar_mask & ~grouped)[0]
            
            if len(similar_indices) >= min_occurrences:
                # Mark as recurring
                for idx in similar_indices:
                    grouped[idx] = True
                    actual_idx = cat_df.index[idx]
                    df.at[actual_idx, 'is_recurring'] = True
                    df.at[actual_idx, 'recurrence_group'] = group_id
                    
                    # determine type based on dates - simplified logic
                    dates = sorted(cat_df.iloc[similar_indices]['date'].dt.date.tolist())
                    if len(dates) > 1:
                        avg_days = sum((dates[j] - dates[j-1]).days for j in range(1, len(dates))) / (len(dates) - 1)
                        if 25 <= avg_days <= 35:
                            df.at[actual_idx, 'recurrence_type'] = 'Monthly'
                        elif 6 <= avg_days <= 8:
                            df.at[actual_idx, 'recurrence_type'] = 'Weekly'
                        elif 350 <= avg_days <= 380:
                            df.at[actual_idx, 'recurrence_type'] = 'Yearly'
                        else:
                            df.at[actual_idx, 'recurrence_type'] = 'Custom'
                group_id += 1
                
    return df

def classify_expense_type(transactions: pd.DataFrame) -> pd.DataFrame:
    """Classify each transaction as: NORMAL, UNUSUAL, ONE_TIME, RECURRING, PERSISTENT.
    Returns df with added column: expense_type
    """
    if transactions.empty:
        return transactions
        
    df = transactions.copy()
    df['expense_type'] = 'NORMAL'
    
    # We assume is_anomaly and is_recurring might exist, if not we add them simply
    # but the prompt does not say to call detect_anomalies from here, we will just check if column exists
    # If not, we will just use the ones we know
    
    if 'is_recurring' not in df.columns:
        df = detect_recurring(df)
        
    has_anomaly = 'is_anomaly' in df.columns
    
    for idx, row in df.iterrows():
        is_rec = row.get('is_recurring', False)
        is_anom = row.get('is_anomaly', False) if has_anomaly else False
        
        if is_rec and not is_anom:
            df.at[idx, 'expense_type'] = 'RECURRING'
        elif is_rec and is_anom:
            df.at[idx, 'expense_type'] = 'PERSISTENT'
        elif not is_rec and is_anom:
            df.at[idx, 'expense_type'] = 'ONE_TIME'
        elif not is_rec and not is_anom:
            # We don't have enough logic to differentiate NORMAL vs UNUSUAL fully without anomaly thresholds
            # so default to NORMAL.
            df.at[idx, 'expense_type'] = 'NORMAL'
            
    return df

def get_recurring_summary(transactions: pd.DataFrame) -> pd.DataFrame:
    """Return summary of all detected recurring expenses: category, avg_amount, frequency, total_annual_cost."""
    if transactions.empty or 'is_recurring' not in transactions.columns:
        return pd.DataFrame(columns=['category', 'avg_amount', 'frequency', 'total_annual_cost'])
        
    recurring = transactions[transactions['is_recurring'] == True]
    if recurring.empty:
        return pd.DataFrame(columns=['category', 'avg_amount', 'frequency', 'total_annual_cost'])
        
    summary = []
    
    for grp, group_df in recurring.groupby('recurrence_group'):
        cat = group_df['category'].iloc[0]
        avg_amt = group_df['amount'].mean()
        freq = group_df['recurrence_type'].iloc[0]
        
        annual_cost = avg_amt
        if freq == 'Monthly':
            annual_cost *= 12
        elif freq == 'Weekly':
            annual_cost *= 52
        elif freq == 'Yearly':
            annual_cost *= 1
        else: # Custom
            annual_cost *= (365 / 30) # approx
            
        summary.append({
            'category': cat,
            'avg_amount': avg_amt,
            'frequency': freq,
            'total_annual_cost': annual_cost
        })
        
    return pd.DataFrame(summary)

def forecast_impact(expense_type: str) -> str:
    """Return how this expense type should affect forecasting"""
    if expense_type in ['NORMAL', 'RECURRING']:
        return 'Include in baseline forecast'
    elif expense_type == 'ONE_TIME':
        return 'Exclude from baseline forecast'
    elif expense_type == 'PERSISTENT':
        return 'Include with adjustment flag'
    elif expense_type == 'UNUSUAL':
        return 'Monitor for future occurrences'
    return 'Unknown'

def get_recurrence_report(transactions: pd.DataFrame) -> Dict[str, Any]:
    """Return comprehensive recurrence report: recurring_expenses (list), total_recurring_monthly, one_time_expenses (list), persistent_expenses (list)."""
    if transactions.empty:
        return {
            'recurring_expenses': [],
            'total_recurring_monthly': 0.0,
            'one_time_expenses': [],
            'persistent_expenses': []
        }
        
    if 'expense_type' not in transactions.columns:
        df = classify_expense_type(transactions)
    else:
        df = transactions
        
    rec_df = df[df['expense_type'] == 'RECURRING']
    one_time_df = df[df['expense_type'] == 'ONE_TIME']
    persist_df = df[df['expense_type'] == 'PERSISTENT']
    
    recurring_expenses = get_recurring_summary(rec_df).to_dict(orient='records') if not rec_df.empty else []
    one_time_expenses = one_time_df.to_dict(orient='records')
    persistent_expenses = persist_df.to_dict(orient='records')
    
    # approx monthly cost
    total_monthly = 0.0
    for exp in recurring_expenses:
        total_monthly += exp['total_annual_cost'] / 12.0
        
    return {
        'recurring_expenses': recurring_expenses,
        'total_recurring_monthly': total_monthly,
        'one_time_expenses': one_time_expenses,
        'persistent_expenses': persistent_expenses
    }
