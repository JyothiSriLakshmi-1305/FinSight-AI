import pandas as pd
from datetime import datetime
from config.settings import CATEGORY_ALIASES

def parse_csv(file) -> pd.DataFrame:
    """Parse uploaded CSV file. Validate columns exist. Return cleaned DataFrame."""
    try:
        df = pd.read_csv(file)
    except Exception as e:
        raise ValueError(f"Error reading CSV file: {e}")
    
    return _process_parsed_df(df)

def parse_excel(file) -> pd.DataFrame:
    """Parse uploaded Excel file. Return cleaned DataFrame."""
    try:
        df = pd.read_excel(file)
    except Exception as e:
        raise ValueError(f"Error reading Excel file: {e}")
    
    return _process_parsed_df(df)

def _process_parsed_df(df: pd.DataFrame) -> pd.DataFrame:
    """Helper to process DataFrame after parsing."""
    df.columns = [col.strip().lower() for col in df.columns]
    mapping = get_column_mapping(df.columns.tolist())
    
    df = df.rename(columns=mapping)
    
    required_cols = {'date', 'amount', 'category'}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    
    return df

def validate_transaction(row: dict) -> tuple[bool, str]:
    """Validate a single transaction row. Return (is_valid, error_message)."""
    if 'date' not in row or 'amount' not in row or 'category' not in row:
        return False, "Missing required fields (date, amount, category)"
    
    try:
        amount = float(row['amount'])
        if amount <= 0:
            return False, "Amount must be a positive number"
    except (ValueError, TypeError):
        return False, "Invalid amount format"
        
    try:
        if isinstance(row['date'], str):
            pd.to_datetime(row['date'])
    except Exception:
        return False, "Invalid date format"
        
    return True, ""

def validate_dataframe(df: pd.DataFrame) -> tuple[bool, list[str]]:
    """Validate entire DataFrame. Return (is_valid, list_of_errors)."""
    errors = []
    required_cols = {'date', 'amount', 'category'}
    missing = required_cols - set(df.columns)
    if missing:
        errors.append(f"Missing required columns: {missing}")
        return False, errors
        
    for index, row in df.iterrows():
        is_valid, error = validate_transaction(row.to_dict())
        if not is_valid:
            errors.append(f"Row {index}: {error}")
            
    return len(errors) == 0, errors

def get_column_mapping(columns: list[str]) -> dict:
    """Auto-detect column mapping from user's column names to standard names."""
    mapping = {}
    standard_cols = ['date', 'amount', 'category', 'payment_method', 'description', 'merchant']
    
    for col in columns:
        col_lower = col.lower().strip()
        if col_lower in standard_cols:
            mapping[col] = col_lower
        elif 'date' in col_lower or 'time' in col_lower:
            if 'date' not in mapping.values(): mapping[col] = 'date'
        elif 'amt' in col_lower or 'price' in col_lower or 'cost' in col_lower:
            if 'amount' not in mapping.values(): mapping[col] = 'amount'
        elif 'cat' in col_lower or 'type' in col_lower:
            if 'category' not in mapping.values(): mapping[col] = 'category'
        elif 'desc' in col_lower or 'note' in col_lower:
            if 'description' not in mapping.values(): mapping[col] = 'description'
        elif 'merch' in col_lower or 'store' in col_lower:
            if 'merchant' not in mapping.values(): mapping[col] = 'merchant'
            
    return mapping

def create_manual_transaction(date, amount, category, payment_method, description, merchant) -> dict:
    """Create a single transaction dict from manual entry form fields."""
    return {
        'date': str(date),
        'amount': float(amount),
        'category': str(category),
        'payment_method': str(payment_method) if payment_method else '',
        'description': str(description) if description else '',
        'merchant': str(merchant) if merchant else ''
    }
