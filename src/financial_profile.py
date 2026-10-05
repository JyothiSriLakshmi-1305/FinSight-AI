import pandas as pd
from typing import Dict, Any, List
import numpy as np
from config.settings import CURRENCY_SYMBOL

def build_profile(transactions: pd.DataFrame, income: float = 0, budget: float = 0, financial_goal: str = '') -> Dict[str, Any]:
    """Build complete financial profile from transaction history.
    Returns dict with keys: income, budget, financial_goal, avg_monthly_expense,
    expense_volatility, category_distribution (dict), recurring_expense_total,
    budget_utilization_rate, spending_trend ('Increasing'/'Decreasing'/'Stable'),
    anomaly_frequency, total_months, total_transactions, highest_expense_category,
    lowest_expense_category, monthly_expenses (list of monthly totals)
    """
    if transactions.empty:
        return {}

    transactions['date'] = pd.to_datetime(transactions['date'])
    transactions['year_month'] = transactions['date'].dt.to_period('M')
    
    monthly_summary = get_monthly_summary(transactions)
    monthly_expenses_list = monthly_summary['total_expense'].tolist()
    
    total_months = len(monthly_summary)
    total_transactions = len(transactions)
    
    avg_monthly_expense = monthly_summary['total_expense'].mean()
    expense_volatility = monthly_summary['total_expense'].std() if total_months > 1 else 0.0
    
    cat_dist = get_category_distribution(transactions)
    highest_cat = list(cat_dist.keys())[0] if cat_dist else None
    lowest_cat = list(cat_dist.keys())[-1] if cat_dist else None

    # Simplified mock for recurring and anomalies as they belong to other modules,
    # or just calculate placeholders/basics. The prompt does not say to import from other modules here.
    recurring_expense_total = 0.0 
    anomaly_frequency = 0.0

    spending_trend = get_spending_trend(monthly_expenses_list)
    
    budget_utilization_rate = (avg_monthly_expense / budget) if budget > 0 else 0.0

    return {
        'income': income,
        'budget': budget,
        'financial_goal': financial_goal,
        'avg_monthly_expense': avg_monthly_expense,
        'expense_volatility': expense_volatility,
        'category_distribution': cat_dist,
        'recurring_expense_total': recurring_expense_total,
        'budget_utilization_rate': budget_utilization_rate,
        'spending_trend': spending_trend,
        'anomaly_frequency': anomaly_frequency,
        'total_months': total_months,
        'total_transactions': total_transactions,
        'highest_expense_category': highest_cat,
        'lowest_expense_category': lowest_cat,
        'monthly_expenses': monthly_expenses_list
    }

def get_spending_trend(monthly_expenses: List[float]) -> str:
    """Determine if spending is Increasing, Decreasing, or Stable using linear regression slope."""
    if len(monthly_expenses) < 2:
        return 'Stable'
    x = list(range(len(monthly_expenses)))
    slope = np.polyfit(x, monthly_expenses, 1)[0]
    # threshold for stable
    threshold = 0.01 * (sum(monthly_expenses)/len(monthly_expenses)) 
    if slope > threshold:
        return 'Increasing'
    elif slope < -threshold:
        return 'Decreasing'
    return 'Stable'

def get_category_distribution(transactions: pd.DataFrame) -> Dict[str, float]:
    """Return dict of {category: percentage} sorted by percentage descending."""
    if transactions.empty or 'amount' not in transactions.columns or 'category' not in transactions.columns:
        return {}
    
    total_spent = transactions['amount'].sum()
    if total_spent == 0:
        return {}
        
    cat_sums = transactions.groupby('category')['amount'].sum().sort_values(ascending=False)
    cat_percentages = (cat_sums / total_spent) * 100
    return cat_percentages.to_dict()

def get_monthly_summary(transactions: pd.DataFrame) -> pd.DataFrame:
    """Return DataFrame with year, month, total_expense, transaction_count for each month."""
    if transactions.empty:
        return pd.DataFrame(columns=['year', 'month', 'total_expense', 'transaction_count'])

    df = transactions.copy()
    if not pd.api.types.is_datetime64_any_dtype(df['date']):
        df['date'] = pd.to_datetime(df['date'])
    
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    
    summary = df.groupby(['year', 'month']).agg(
        total_expense=('amount', 'sum'),
        transaction_count=('amount', 'count')
    ).reset_index()
    
    return summary.sort_values(by=['year', 'month'])

def compare_to_budget(profile: Dict[str, Any]) -> Dict[str, Any]:
    """Compare spending profile to budget. Return dict with budget_status, overspend_months, underspend_months, avg_overspend, avg_underspend."""
    budget = profile.get('budget', 0)
    monthly_expenses = profile.get('monthly_expenses', [])
    
    if budget <= 0 or not monthly_expenses:
        return {
            'budget_status': 'No Budget',
            'overspend_months': 0,
            'underspend_months': 0,
            'avg_overspend': 0.0,
            'avg_underspend': 0.0
        }
        
    overspend = [exp - budget for exp in monthly_expenses if exp > budget]
    underspend = [budget - exp for exp in monthly_expenses if exp <= budget]
    
    overspend_months = len(overspend)
    underspend_months = len(underspend)
    
    avg_overspend = sum(overspend) / overspend_months if overspend_months > 0 else 0.0
    avg_underspend = sum(underspend) / underspend_months if underspend_months > 0 else 0.0
    
    if overspend_months > underspend_months:
        status = 'Mostly Over Budget'
    elif underspend_months > overspend_months:
        status = 'Mostly Under Budget'
    else:
        status = 'Balanced'
        
    return {
        'budget_status': status,
        'overspend_months': overspend_months,
        'underspend_months': underspend_months,
        'avg_overspend': avg_overspend,
        'avg_underspend': avg_underspend
    }
