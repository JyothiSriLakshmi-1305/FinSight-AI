import sqlite3
import pandas as pd
from datetime import datetime
from config.settings import DB_PATH

def get_connection(db_path=None):
    """Get SQLite connection."""
    path = db_path if db_path else DB_PATH
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path=None) -> None:
    """Create all tables if they don't exist. Use DB_PATH from settings if not provided."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    # users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        income REAL DEFAULT 0,
        budget REAL DEFAULT 0,
        financial_goal TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # transactions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT NOT NULL,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        payment_method TEXT,
        description TEXT,
        merchant TEXT,
        is_anomaly BOOLEAN DEFAULT 0,
        is_recurring BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')
    
    # budgets table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS budgets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        month INTEGER,
        year INTEGER,
        amount REAL NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')
    
    # goals table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        description TEXT NOT NULL,
        target_amount REAL NOT NULL,
        deadline TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')
    
    # forecasts table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS forecasts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        forecast_month INTEGER NOT NULL,
        forecast_year INTEGER NOT NULL,
        predicted_amount REAL NOT NULL,
        model_used TEXT,
        confidence REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')
    
    # recommendations table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS recommendations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        type TEXT NOT NULL,
        priority TEXT,
        message TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')
    
    conn.commit()
    conn.close()

def add_user(username, income=0, budget=0, financial_goal='') -> int:
    """Insert user, return user_id."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO users (username, income, budget, financial_goal)
        VALUES (?, ?, ?, ?)
        ''', (username, income, budget, financial_goal))
        conn.commit()
        user_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        user_id = cursor.fetchone()['id']
    finally:
        conn.close()
    return user_id

def get_user(user_id) -> dict:
    """Get user by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else {}

def get_user_by_username(username) -> dict:
    """Get user by username."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else {}

def add_transactions(user_id, df) -> int:
    """Bulk insert transactions from DataFrame. Return count inserted."""
    if df.empty:
        return 0
        
    conn = get_connection()
    cursor = conn.cursor()
    
    records = []
    for _, row in df.iterrows():
        date_str = str(row['date'].date()) if hasattr(row['date'], 'date') else str(row['date'])
        records.append((
            user_id,
            date_str,
            float(row['amount']),
            str(row['category']),
            str(row.get('payment_method', '')),
            str(row.get('description', '')),
            str(row.get('merchant', ''))
        ))
        
    cursor.executemany('''
    INSERT INTO transactions (user_id, date, amount, category, payment_method, description, merchant)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', records)
    
    count = cursor.rowcount
    conn.commit()
    conn.close()
    
    return count

def get_user_transactions(user_id) -> pd.DataFrame:
    """Get all transactions for a user as DataFrame."""
    conn = get_connection()
    query = 'SELECT * FROM transactions WHERE user_id = ? ORDER BY date ASC'
    df = pd.read_sql_query(query, conn, params=(user_id,))
    conn.close()
    
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
    return df

def update_user_profile(user_id, income=None, budget=None, financial_goal=None) -> None:
    """Update user profile fields."""
    conn = get_connection()
    cursor = conn.cursor()
    
    updates = []
    params = []
    if income is not None:
        updates.append('income = ?')
        params.append(income)
    if budget is not None:
        updates.append('budget = ?')
        params.append(budget)
    if financial_goal is not None:
        updates.append('financial_goal = ?')
        params.append(financial_goal)
        
    if updates:
        params.append(user_id)
        query = f'UPDATE users SET {", ".join(updates)} WHERE id = ?'
        cursor.execute(query, params)
        conn.commit()
        
    conn.close()

def save_forecast(user_id, forecast_month, forecast_year, predicted_amount, model_used, confidence=None) -> None:
    """Save a forecast result."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO forecasts (user_id, forecast_month, forecast_year, predicted_amount, model_used, confidence)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, forecast_month, forecast_year, predicted_amount, model_used, confidence))
    conn.commit()
    conn.close()

def get_forecasts(user_id) -> pd.DataFrame:
    """Get all forecasts for a user."""
    conn = get_connection()
    query = 'SELECT * FROM forecasts WHERE user_id = ? ORDER BY forecast_year, forecast_month'
    df = pd.read_sql_query(query, conn, params=(user_id,))
    conn.close()
    return df

def save_recommendations(user_id, recommendations: list[dict]) -> None:
    """Save recommendation results."""
    if not recommendations:
        return
        
    conn = get_connection()
    cursor = conn.cursor()
    
    records = []
    for rec in recommendations:
        records.append((
            user_id,
            rec.get('type', 'general'),
            rec.get('priority', 'medium'),
            rec.get('message', '')
        ))
        
    cursor.executemany('''
    INSERT INTO recommendations (user_id, type, priority, message)
    VALUES (?, ?, ?, ?)
    ''', records)
    
    conn.commit()
    conn.close()

def clear_user_transactions(user_id) -> None:
    """Delete all transactions for a user (for re-upload)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM transactions WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()
