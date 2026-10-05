import pandas as pd
import numpy as np
from config.settings import EXPENSE_CATEGORIES

def create_monthly_features(transactions: pd.DataFrame, budget: float = 0) -> pd.DataFrame:
    """Aggregate transactions to monthly feature vectors."""
    if transactions.empty:
        return pd.DataFrame()
        
    transactions = transactions.copy()
    transactions['date'] = pd.to_datetime(transactions['date'])
    transactions['year'] = transactions['date'].dt.year
    transactions['month'] = transactions['date'].dt.month
    
    # Base aggregation
    monthly = transactions.groupby(['year', 'month']).agg(
        total_expense=('amount', 'sum'),
        transaction_count=('amount', 'count'),
        avg_transaction_amount=('amount', 'mean')
    ).reset_index()
    
    # Category aggregation
    cat_pivot = transactions.pivot_table(
        index=['year', 'month'], 
        columns='category', 
        values='amount', 
        aggfunc='sum', 
        fill_value=0
    ).reset_index()
    
    # Rename category columns
    for col in cat_pivot.columns:
        if col not in ['year', 'month']:
            cat_pivot.rename(columns={col: f"category_{col}"}, inplace=True)
            
    monthly = pd.merge(monthly, cat_pivot, on=['year', 'month'], how='left')
    
    # Fill missing categories
    for cat in EXPENSE_CATEGORIES:
        col_name = f"category_{cat}"
        if col_name not in monthly.columns:
            monthly[col_name] = 0.0
            
    # Budget features
    monthly['budget_utilization'] = np.where(budget > 0, monthly['total_expense'] / budget, 0)
    monthly['budget_remaining'] = budget - monthly['total_expense']
    monthly['overspend_amount'] = np.maximum(0, monthly['total_expense'] - budget)
    
    return monthly.sort_values(['year', 'month']).reset_index(drop=True)

def add_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add temporal features based on month."""
    if df.empty:
        return df
    df = df.copy()
    df['month_num'] = df['month']
    df['quarter'] = np.ceil(df['month_num'] / 3)
    df['is_holiday_season'] = df['month_num'].isin([11, 12, 1]).astype(int)
    df['is_summer'] = df['month_num'].isin([6, 7, 8]).astype(int)
    return df

def add_trend_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add rolling metrics using past data only."""
    if df.empty:
        return df
    df = df.copy()
    
    # 3-month rolling averages (shift 1 to avoid data leakage from current month)
    df['rolling_mean_3m'] = df['total_expense'].shift(1).rolling(window=3, min_periods=1).mean().fillna(0)
    df['rolling_std_3m'] = df['total_expense'].shift(1).rolling(window=3, min_periods=1).std().fillna(0)
    
    # Simple slope between last month and the month before
    df['expense_trend_slope'] = (df['total_expense'].shift(1) - df['total_expense'].shift(2)).fillna(0)
    
    return df

def add_anomaly_features(df: pd.DataFrame, anomaly_counts: dict = None) -> pd.DataFrame:
    """Add anomaly counts and amounts."""
    df = df.copy()
    if not anomaly_counts:
        df['anomaly_count'] = 0
        df['anomaly_amount'] = 0.0
    else:
        # Assuming anomaly_counts maps (year, month) -> {'count': x, 'amount': y}
        def get_count(r):
            return anomaly_counts.get((r['year'], r['month']), {}).get('count', 0)
        def get_amount(r):
            return anomaly_counts.get((r['year'], r['month']), {}).get('amount', 0.0)
            
        df['anomaly_count'] = df.apply(get_count, axis=1)
        df['anomaly_amount'] = df.apply(get_amount, axis=1)
    return df

def add_recurrence_features(df: pd.DataFrame, recurring_total: dict = None) -> pd.DataFrame:
    """Add recurring expense totals."""
    df = df.copy()
    if not recurring_total:
        df['recurring_expense_total'] = 0.0
    else:
        # Assuming recurring_total maps (year, month) -> amount
        def get_recurring(r):
            return recurring_total.get((r['year'], r['month']), 0.0)
        df['recurring_expense_total'] = df.apply(get_recurring, axis=1)
    return df

def get_feature_names() -> list[str]:
    """Return feature column names used for ML."""
    base_features = [
        'transaction_count', 'avg_transaction_amount', 
        'budget_utilization', 'budget_remaining', 'overspend_amount',
        'month_num', 'quarter', 'is_holiday_season', 'is_summer',
        'rolling_mean_3m', 'rolling_std_3m', 'expense_trend_slope',
        'anomaly_count', 'anomaly_amount', 'recurring_expense_total'
    ]
    cat_features = [f"category_{cat}" for cat in EXPENSE_CATEGORIES]
    return base_features + cat_features

def prepare_train_test(df: pd.DataFrame, test_months: int = 3) -> tuple:
    """Temporal split - no data leakage!"""
    features = get_feature_names()
    
    # Ensure columns exist, fill with 0 if missing
    for col in features:
        if col not in df.columns:
            df[col] = 0.0
            
    target = 'total_expense'
    
    if len(df) <= test_months:
        # Fallback if very little data
        split_idx = max(1, len(df) - 1)
    else:
        split_idx = len(df) - test_months
        
    train_df = df.iloc[:split_idx]
    test_df = df.iloc[split_idx:]
    
    X_train = train_df[features]
    X_test = test_df[features]
    y_train = train_df[target]
    y_test = test_df[target]
    
    return X_train, X_test, y_train, y_test, features

def prepare_lstm_sequences(df: pd.DataFrame, sequence_length: int = 3) -> tuple:
    """Create sequences preserving temporal order."""
    features = get_feature_names()
    
    for col in features:
        if col not in df.columns:
            df[col] = 0.0
            
    X_data = df[features].values
    y_data = df['total_expense'].values
    
    X_sequences, y_targets = [], []
    
    if len(df) > sequence_length:
        for i in range(len(df) - sequence_length):
            X_sequences.append(X_data[i : i + sequence_length])
            y_targets.append(y_data[i + sequence_length])
            
    return np.array(X_sequences), np.array(y_targets)
