import pandas as pd
from config.settings import RECOMMENDATION_CONFIG, CURRENCY_SYMBOL

def generate_recommendations(prediction: float, profile: dict, anomalies: dict = None, recurring: dict = None, category_trends: pd.DataFrame = None) -> list[dict]:
    """Generate 8 rules-based financial recommendations."""
    recommendations = []
    budget = profile.get("monthly_budget", 0)
    
    # 1. Budget overspend warning
    if budget > 0 and prediction > budget:
        overspend = prediction - budget
        recommendations.append({
            "type": "budget_warning",
            "priority": "high",
            "title": "Budget Exceeded Warning",
            "message": f"You are projected to overspend your budget by {CURRENCY_SYMBOL}{overspend:,.2f} next month.",
            "savings_potential": overspend,
            "icon": "⚠️"
        })
        
    # 2. Category trend alerts
    if category_trends is not None and not category_trends.empty:
        growth_threshold = RECOMMENDATION_CONFIG.get("category_growth_threshold", 0.15)
        for _, row in category_trends.iterrows():
            if row.get('growth_rate', 0) > growth_threshold:
                cat = row.get('category', 'Unknown')
                growth = row['growth_rate'] * 100
                recommendations.append({
                    "type": "trend_alert",
                    "priority": "medium",
                    "title": f"Rising Expense: {cat}",
                    "message": f"Your {cat} expenses grew by {growth:.1f}% recently. Consider setting a specific limit.",
                    "savings_potential": row.get('amount', 0) * RECOMMENDATION_CONFIG.get("savings_suggestion_ratio", 0.1),
                    "icon": "📈"
                })

    # 3. Anomaly context
    if anomalies and anomalies.get("count", 0) > 0:
        recommendations.append({
            "type": "anomaly_alert",
            "priority": "medium",
            "title": "Unusual Spending Detected",
            "message": f"You had {anomalies['count']} unusual transactions recently totaling {CURRENCY_SYMBOL}{anomalies.get('amount', 0):,.2f}. Review these to ensure they were necessary.",
            "savings_potential": anomalies.get('amount', 0) * 0.5, # Assume 50% could have been saved
            "icon": "🔍"
        })
        
    # 4. Savings opportunities based on high ratios
    # (assuming profile contains recent category ratios)
    cat_ratios = profile.get("category_ratios", {})
    for cat, ratio in cat_ratios.items():
        if ratio > 0.25:  # If a category is > 25% of total
            recommendations.append({
                "type": "optimization",
                "priority": "low",
                "title": f"Optimize {cat} Spending",
                "message": f"{cat} makes up {ratio*100:.1f}% of your expenses. Small optimizations here yield large savings.",
                "savings_potential": (budget * ratio) * 0.1,
                "icon": "💡"
            })
            
    # 5. Goal progress tracking
    goal = profile.get("financial_goal")
    if goal:
        recommendations.append({
            "type": "goal_tracking",
            "priority": "medium",
            "title": "Goal Check-in",
            "message": f"Keep your goal '{goal}' in mind before making impulse purchases.",
            "savings_potential": 0,
            "icon": "🎯"
        })
        
    # 6. Recurring expense review
    if recurring and recurring.get("total", 0) > budget * 0.4: # > 40% of budget is fixed
        recommendations.append({
            "type": "recurring_review",
            "priority": "high",
            "title": "High Fixed Costs",
            "message": f"Recurring subscriptions and bills make up a large portion of your budget. Review and cancel unused ones.",
            "savings_potential": recurring.get("total", 0) * 0.1,
            "icon": "🔄"
        })
        
    # 7. Budget utilization optimization
    if budget > 0 and prediction < budget * 0.8:
        recommendations.append({
            "type": "budget_optimization",
            "priority": "low",
            "title": "Great Budget Discipline",
            "message": f"You're projected to have 20%+ of your budget left. Consider investing the surplus {CURRENCY_SYMBOL}{budget - prediction:,.2f}.",
            "savings_potential": 0,
            "icon": "🌟"
        })
        
    # 8. Seasonal spending awareness
    if profile.get("is_holiday_season"):
        recommendations.append({
            "type": "seasonal_awareness",
            "priority": "medium",
            "title": "Holiday Spending Approaching",
            "message": "It's the holiday season. Historical data shows spending increases by 20%. Plan ahead!",
            "savings_potential": budget * 0.2,
            "icon": "🎄"
        })
        
    return prioritize_recommendations(recommendations)

def prioritize_recommendations(recommendations: list[dict]) -> list[dict]:
    priority_map = {'high': 0, 'medium': 1, 'low': 2}
    return sorted(recommendations, key=lambda x: (priority_map.get(x['priority'], 3), -x.get('savings_potential', 0)))

def format_for_display(recommendations: list[dict]) -> list[dict]:
    formatted = []
    for r in recommendations:
        f = r.copy()
        if f.get('savings_potential', 0) > 0:
            f['display_savings'] = f"{CURRENCY_SYMBOL}{f['savings_potential']:,.2f}"
        else:
            f['display_savings'] = ""
        f['display_title'] = f"{f.get('icon', '')} {f.get('title', '')}"
        formatted.append(f)
    return formatted

def get_savings_summary(recommendations: list[dict]) -> dict:
    total_monthly = sum(r.get('savings_potential', 0) for r in recommendations)
    counts = {'high': 0, 'medium': 0, 'low': 0}
    for r in recommendations:
        counts[r['priority']] = counts.get(r['priority'], 0) + 1
        
    return {
        "total_monthly_savings_potential": total_monthly,
        "total_annual_savings_potential": total_monthly * 12,
        "action_count_by_priority": counts
    }
