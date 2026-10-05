import pandas as pd
from config.settings import CATEGORY_ALIASES

def clean_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """Clean transaction data: handle NaN intelligently, fix types, remove invalid rows."""
    df = df.copy()
    
    # Drop rows without amount or date
    df = df.dropna(subset=['amount', 'date'])
    
    # Convert amount to numeric, drop invalid
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df = df.dropna(subset=['amount'])
    df = df[df['amount'] > 0]
    
    # Fill missing optional text fields
    text_cols = ['payment_method', 'description', 'merchant']
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str)
        else:
            df[col] = ""
            
    # Category fillna
    if 'category' not in df.columns:
        df['category'] = "Miscellaneous"
    else:
        df['category'] = df['category'].fillna("Miscellaneous").astype(str)
        
    return df

def normalize_categories(df: pd.DataFrame) -> pd.DataFrame:
    """Map raw category names to standard categories using CATEGORY_ALIASES."""
    df = df.copy()
    
    def map_category(cat):
        cat_lower = str(cat).lower().strip()
        return CATEGORY_ALIASES.get(cat_lower, cat)
        
    df['category'] = df['category'].apply(map_category)
    return df

def validate_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Parse dates, ensure chronological order, handle various date formats."""
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])
    df = df.sort_values(by='date')
    return df

def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Detect and remove duplicate transactions (same date, amount, category, merchant)."""
    cols_to_check = ['date', 'amount', 'category']
    if 'merchant' in df.columns:
        cols_to_check.append('merchant')
        
    return df.drop_duplicates(subset=cols_to_check, keep='first')

def aggregate_monthly(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate transactions to monthly totals. Return df with columns: year, month, total_expense, transaction_count, avg_transaction."""
    df = df.copy()
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    
    monthly = df.groupby(['year', 'month']).agg(
        total_expense=('amount', 'sum'),
        transaction_count=('amount', 'count'),
        avg_transaction=('amount', 'mean')
    ).reset_index()
    
    return monthly

def aggregate_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate transactions by category per month. Return pivot-style df."""
    df = df.copy()
    df['year_month'] = df['date'].dt.to_period('M')
    
    pivot = df.pivot_table(
        index='year_month',
        columns='category',
        values='amount',
        aggfunc='sum',
        fill_value=0
    ).reset_index()
    
    pivot['year_month'] = pivot['year_month'].astype(str)
    return pivot

def get_date_range(df: pd.DataFrame) -> tuple:
    """Return (min_date, max_date) of the transaction data."""
    if df.empty:
        return None, None
    return df['date'].min(), df['date'].max()

def preprocess_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """Run the full preprocessing pipeline: clean -> normalize -> validate -> deduplicate. Return processed df."""
    df = clean_transactions(df)
    df = validate_dates(df)
    df = normalize_categories(df)
    df = remove_duplicates(df)
    return df
