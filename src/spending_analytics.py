import pandas as pd
from typing import Dict, Any
from config.settings import CURRENCY_SYMBOL

def category_breakdown(transactions: pd.DataFrame) -> pd.DataFrame:
    """Return category-level summary: category, total_amount, percentage, transaction_count, avg_amount."""
    if transactions.empty:
        return pd.DataFrame(columns=['category', 'total_amount', 'percentage', 'transaction_count', 'avg_amount'])
        
    summary = transactions.groupby('category').agg(
        total_amount=('amount', 'sum'),
        transaction_count=('amount', 'count')
    ).reset_index()
    
    total_spend = summary['total_amount'].sum()
    summary['percentage'] = (summary['total_amount'] / total_spend) * 100 if total_spend > 0 else 0
    summary['avg_amount'] = summary['total_amount'] / summary['transaction_count']
    
    return summary.sort_values(by='total_amount', ascending=False)

def monthly_trends(transactions: pd.DataFrame) -> pd.DataFrame:
    """Return monthly spending trends: year_month, total_expense, transaction_count. Sorted chronologically."""
    if transactions.empty:
        return pd.DataFrame(columns=['year_month', 'total_expense', 'transaction_count'])
        
    df = transactions.copy()
    if not pd.api.types.is_datetime64_any_dtype(df['date']):
        df['date'] = pd.to_datetime(df['date'])
        
    df['year_month'] = df['date'].dt.to_period('M')
    
    summary = df.groupby('year_month').agg(
        total_expense=('amount', 'sum'),
        transaction_count=('amount', 'count')
    ).reset_index()
    
    summary['year_month'] = summary['year_month'].astype(str)
    return summary.sort_values(by='year_month')

def budget_analysis(transactions: pd.DataFrame, budget: float) -> Dict[str, Any]:
    """Return budget analysis: utilization_rate, months_over_budget, months_under_budget, avg_savings, total_overspend."""
    trends = monthly_trends(transactions)
    if trends.empty or budget <= 0:
        return {
            'utilization_rate': 0.0,
            'months_over_budget': 0,
            'months_under_budget': 0,
            'avg_savings': 0.0,
            'total_overspend': 0.0
        }
        
    total_expense = trends['total_expense'].sum()
    total_budget = budget * len(trends)
    utilization_rate = (total_expense / total_budget) * 100
    
    over = trends[trends['total_expense'] > budget]
    under = trends[trends['total_expense'] <= budget]
    
    months_over_budget = len(over)
    months_under_budget = len(under)
    
    total_overspend = (over['total_expense'] - budget).sum() if not over.empty else 0.0
    total_savings = (budget - under['total_expense']).sum() if not under.empty else 0.0
    
    avg_savings = total_savings / months_under_budget if months_under_budget > 0 else 0.0
    
    return {
        'utilization_rate': utilization_rate,
        'months_over_budget': months_over_budget,
        'months_under_budget': months_under_budget,
        'avg_savings': avg_savings,
        'total_overspend': total_overspend
    }

def payment_method_analysis(transactions: pd.DataFrame) -> pd.DataFrame:
    """Return payment method distribution: method, total_amount, percentage, transaction_count."""
    if transactions.empty or 'payment_method' not in transactions.columns:
        return pd.DataFrame(columns=['method', 'total_amount', 'percentage', 'transaction_count'])
        
    summary = transactions.groupby('payment_method').agg(
        total_amount=('amount', 'sum'),
        transaction_count=('amount', 'count')
    ).reset_index()
    summary.rename(columns={'payment_method': 'method'}, inplace=True)
    
    total_spend = summary['total_amount'].sum()
    summary['percentage'] = (summary['total_amount'] / total_spend) * 100 if total_spend > 0 else 0
    
    return summary.sort_values(by='total_amount', ascending=False)

def category_growth_rates(transactions: pd.DataFrame) -> pd.DataFrame:
    """Return month-over-month growth rate per category. Columns: category, month, growth_rate."""
    if transactions.empty:
        return pd.DataFrame(columns=['category', 'month', 'growth_rate'])
        
    df = transactions.copy()
    if not pd.api.types.is_datetime64_any_dtype(df['date']):
        df['date'] = pd.to_datetime(df['date'])
        
    df['month'] = df['date'].dt.to_period('M').astype(str)
    
    monthly_cat = df.groupby(['category', 'month'])['amount'].sum().reset_index()
    monthly_cat.sort_values(by=['category', 'month'], inplace=True)
    
    monthly_cat['prev_amount'] = monthly_cat.groupby('category')['amount'].shift(1)
    
    # Calculate growth rate
    def calc_growth(row):
        if pd.isna(row['prev_amount']) or row['prev_amount'] == 0:
            return 0.0
        return ((row['amount'] - row['prev_amount']) / row['prev_amount']) * 100
        
    monthly_cat['growth_rate'] = monthly_cat.apply(calc_growth, axis=1)
    return monthly_cat[['category', 'month', 'growth_rate']]

def top_merchants(transactions: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Return top N merchants by total spend: merchant, total_amount, transaction_count."""
    if transactions.empty or 'merchant' not in transactions.columns:
        return pd.DataFrame(columns=['merchant', 'total_amount', 'transaction_count'])
        
    summary = transactions.groupby('merchant').agg(
        total_amount=('amount', 'sum'),
        transaction_count=('amount', 'count')
    ).reset_index()
    
    return summary.sort_values(by='total_amount', ascending=False).head(n)

def daily_spending_pattern(transactions: pd.DataFrame) -> pd.DataFrame:
    """Return spending by day of week: day_name, avg_amount, total_amount, transaction_count."""
    if transactions.empty:
        return pd.DataFrame(columns=['day_name', 'avg_amount', 'total_amount', 'transaction_count'])
        
    df = transactions.copy()
    if not pd.api.types.is_datetime64_any_dtype(df['date']):
        df['date'] = pd.to_datetime(df['date'])
        
    df['day_name'] = df['date'].dt.day_name()
    
    summary = df.groupby('day_name').agg(
        total_amount=('amount', 'sum'),
        transaction_count=('amount', 'count')
    ).reset_index()
    
    summary['avg_amount'] = summary['total_amount'] / summary['transaction_count']
    
    # Order by day of week
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    summary['day_name'] = pd.Categorical(summary['day_name'], categories=days, ordered=True)
    summary.sort_values('day_name', inplace=True)
    
    return summary

def get_spending_summary(transactions: pd.DataFrame, budget: float = 0) -> Dict[str, Any]:
    """Return comprehensive summary dict for dashboard display."""
    if transactions.empty:
        return {}
        
    total_spent = transactions['amount'].sum()
    transaction_count = len(transactions)
    cat_breakdown = category_breakdown(transactions)
    top_cat = cat_breakdown.iloc[0]['category'] if not cat_breakdown.empty else None
    
    budget_stats = budget_analysis(transactions, budget)
    
    return {
        'total_spent': total_spent,
        'transaction_count': transaction_count,
        'top_category': top_cat,
        'budget_utilization': budget_stats.get('utilization_rate', 0.0),
        'months_over_budget': budget_stats.get('months_over_budget', 0),
        'category_summary': cat_breakdown.to_dict(orient='records'),
        'monthly_trends': monthly_trends(transactions).to_dict(orient='records')
    }
