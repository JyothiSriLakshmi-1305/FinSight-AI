"""
FinSight AI — Configuration Settings
Central configuration for paths, categories, thresholds, and constants.
"""

import os
from pathlib import Path
# === Paths ===
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
DB_PATH = DATA_DIR / "finsight.db"
SAMPLE_DATA_PATH = DATA_DIR / "sample_transactions.csv"

try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    pass

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)

# === Expense Categories ===
EXPENSE_CATEGORIES = [
    "Food & Dining",
    "Rent",
    "Transport",
    "Utilities",
    "Shopping",
    "Medical & Health",
    "Entertainment",
    "Education",
    "Insurance",
    "Subscriptions",
    "Personal Care",
    "Gifts & Donations",
    "Travel",
    "Miscellaneous"
]

# Category aliases for auto-mapping user input
CATEGORY_ALIASES = {
    "food": "Food & Dining",
    "grocery": "Food & Dining",
    "groceries": "Food & Dining",
    "restaurant": "Food & Dining",
    "dining": "Food & Dining",
    "eating out": "Food & Dining",
    "zomato": "Food & Dining",
    "swiggy": "Food & Dining",
    "rent": "Rent",
    "house rent": "Rent",
    "housing": "Rent",
    "transport": "Transport",
    "transportation": "Transport",
    "fuel": "Transport",
    "petrol": "Transport",
    "diesel": "Transport",
    "uber": "Transport",
    "ola": "Transport",
    "auto": "Transport",
    "bus": "Transport",
    "metro": "Transport",
    "cab": "Transport",
    "utilities": "Utilities",
    "electricity": "Utilities",
    "water": "Utilities",
    "gas": "Utilities",
    "internet": "Utilities",
    "wifi": "Utilities",
    "mobile recharge": "Utilities",
    "phone bill": "Utilities",
    "shopping": "Shopping",
    "clothes": "Shopping",
    "clothing": "Shopping",
    "amazon": "Shopping",
    "flipkart": "Shopping",
    "myntra": "Shopping",
    "shoes": "Shopping",
    "electronics": "Shopping",
    "medical": "Medical & Health",
    "health": "Medical & Health",
    "hospital": "Medical & Health",
    "doctor": "Medical & Health",
    "medicine": "Medical & Health",
    "pharmacy": "Medical & Health",
    "entertainment": "Entertainment",
    "movies": "Entertainment",
    "netflix": "Entertainment",
    "hotstar": "Entertainment",
    "spotify": "Entertainment",
    "games": "Entertainment",
    "education": "Education",
    "books": "Education",
    "course": "Education",
    "tuition": "Education",
    "college": "Education",
    "insurance": "Insurance",
    "lic": "Insurance",
    "health insurance": "Insurance",
    "life insurance": "Insurance",
    "subscription": "Subscriptions",
    "subscriptions": "Subscriptions",
    "gym": "Subscriptions",
    "membership": "Subscriptions",
    "personal care": "Personal Care",
    "salon": "Personal Care",
    "haircut": "Personal Care",
    "skincare": "Personal Care",
    "gifts": "Gifts & Donations",
    "donation": "Gifts & Donations",
    "charity": "Gifts & Donations",
    "travel": "Travel",
    "vacation": "Travel",
    "trip": "Travel",
    "hotel": "Travel",
    "flight": "Travel",
    "train ticket": "Travel",
    "miscellaneous": "Miscellaneous",
    "other": "Miscellaneous",
    "misc": "Miscellaneous",
}

# === Payment Methods ===
PAYMENT_METHODS = ["UPI", "Cash", "Card", "Net Banking", "Wallet", "Other"]

# === ML Configuration ===
ML_CONFIG = {
    "test_months": 3,              # Last N months for test set (temporal split)
    "random_forest_n_estimators": 100,
    "random_forest_random_state": 42,
    "lstm_units_layer1": 64,
    "lstm_units_layer2": 32,
    "lstm_dropout": 0.2,
    "lstm_learning_rate": 0.001,
    "lstm_epochs": 50,
    "lstm_batch_size": 16,
    "lstm_sequence_length": 3,
    "lstm_patience": 10,
}

# === Anomaly Detection Thresholds ===
ANOMALY_CONFIG = {
    "z_score_mild": 2.0,
    "z_score_moderate": 2.5,
    "z_score_severe": 3.5,
    "budget_ratio_threshold": 0.5,   # Flag if single txn > 50% of monthly budget
    "category_multiplier": 3.0,      # Flag if txn > 3x category average
    "min_history_months": 2,         # Minimum months of history needed
}

# === Recurrence Detection ===
RECURRENCE_CONFIG = {
    "amount_tolerance": 0.15,        # ±15% amount tolerance for "same" amount
    "min_occurrences": 2,            # Minimum times to count as recurring
    "lookback_months": 6,            # How far back to look for patterns
}

# === Recommendation Thresholds ===
RECOMMENDATION_CONFIG = {
    "overspend_rate_threshold": 0.5,   # Warn if >50% months are over budget
    "category_growth_threshold": 0.15, # Alert if category grows >15% MoM
    "savings_suggestion_ratio": 0.10,  # Suggest 10% reduction for high categories
}

# === GenAI Configuration (Google Gemini / Cloud API) ===
GENAI_CONFIG = {
    "provider": os.getenv("GENAI_PROVIDER", "gemini"),
    "gemini_api_key": os.getenv("GEMINI_API_KEY", ""),
    "gemini_model": os.getenv("GEMINI_MODEL", "gemini-flash-latest"),
    "host": os.getenv("OLLAMA_HOST", "http://localhost:11434"),
    "model": os.getenv("OLLAMA_MODEL", "llama3.1"),
    "max_tokens": 1000,
    "temperature": 0.3,              # Low temperature for factual, reliable financial responses
}

# === Currency ===
CURRENCY_SYMBOL = "₹"
CURRENCY_NAME = "INR"
