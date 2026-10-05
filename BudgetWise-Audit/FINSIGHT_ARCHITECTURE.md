# FINSIGHT AI — Architecture Design

> FinSight AI: An AI-Powered Personal Finance Intelligence and Expense Forecasting System

---

## 1. System Overview

```
USER
 ↓
Manual Entry / CSV / Excel Upload
 ↓
┌──────────────────────────────────────────────┐
│           DATA LAYER                         │
│  Data Validation → Preprocessing → Storage   │
│  (SQLite)                                    │
└──────────────────────────────────────────────┘
 ↓
┌──────────────────────────────────────────────┐
│        ANALYTICS LAYER                       │
│  Financial Profile → Spending Analytics      │
│  Category Analysis → Budget Analysis         │
└──────────────────────────────────────────────┘
 ↓
┌──────────────────────────────────────────────┐
│       INTELLIGENCE LAYER                     │
│  Anomaly Detection → Recurrence Analysis     │
│  Feature Engineering → ML Forecasting        │
│  Model Comparison → Best Model Selection     │
└──────────────────────────────────────────────┘
 ↓
┌──────────────────────────────────────────────┐
│          AI LAYER                            │
│  Recommendation Engine → Model Explainability│
│  Llama 3.1 via Ollama → Natural Language     │
└──────────────────────────────────────────────┘
 ↓
┌──────────────────────────────────────────────┐
│       PRESENTATION LAYER                     │
│  Streamlit Multi-Page Dashboard              │
│  Interactive Charts (Plotly)                 │
│  AI Financial Assistant Chat                 │
└──────────────────────────────────────────────┘
```

---

## 2. Detailed Module Architecture

### 2.1 Data Input Module

**Source**: New FinSight functionality

| Feature | Details |
|---------|---------|
| Manual Entry | Streamlit form for individual transactions |
| CSV Upload | Parse CSV with date, amount, category, payment_method, description |
| Excel Upload | Parse .xlsx with same structure |
| Validation | Date format, amount range, category mapping, duplicate detection |
| Sample Data | Built-in sample dataset for demo |

**Transaction Schema**:
```
date            DATE         (required)
amount          FLOAT        (required)
category        VARCHAR(50)  (required)
payment_method  VARCHAR(30)  (optional, default: 'Cash')
description     VARCHAR(200) (optional)
user_id         INTEGER      (foreign key)
merchant        VARCHAR(100) (optional)
recurring_flag  BOOLEAN      (optional, system-detected)
```

### 2.2 Data Preprocessing Module

**Source**: Adapted from BudgetWise `load_and_preprocess_data()` + new logic

| Step | Description |
|------|-------------|
| Cleaning | Handle missing values intelligently (not blanket fill-0) |
| Normalization | Standardize category names, date formats |
| Aggregation | Transaction-level → daily/weekly/monthly summaries |
| Encoding | Month numbers, quarter, seasonal flags |
| Validation | Amount range checks, date ordering, category validation |

### 2.3 Financial Profile Module

**Source**: New FinSight functionality (inspired by base paper personalization concept)

Builds a user-specific financial baseline:

```python
FinancialProfile:
    user_id
    income                    # User-provided
    budget                    # User-provided
    financial_goal            # User-provided
    avg_monthly_expense       # Computed from history
    expense_volatility        # Std deviation of monthly expenses
    category_distribution     # % breakdown by category
    recurring_expense_total   # Sum of identified recurring expenses
    budget_utilization_rate   # avg_expense / budget
    spending_trend            # Increasing / Decreasing / Stable
    anomaly_frequency         # How often unusual expenses occur
```

### 2.4 Spending Analytics Module

**Source**: Adapted from BudgetWise `_create_features()` + new analytics

| Analysis | Output |
|----------|--------|
| Category breakdown | % spending per category (pie chart) |
| Monthly trends | Spending over time (line chart) |
| Budget utilization | Current vs. budget (gauge chart) |
| Day-of-week patterns | Spending intensity by weekday |
| Payment method analysis | UPI vs. Card vs. Cash distribution |
| Category growth rates | Which categories are increasing/decreasing |

### 2.5 Anomaly Detection Module

**Source**: New FinSight functionality

**Method**: Statistical + user-baseline comparison

```
For each transaction:
    1. Compute user's historical baseline for that category
       (mean, std of past transactions in same category)

    2. Calculate z-score = (transaction_amount - category_mean) / category_std

    3. Flag as anomaly if:
       - z-score > 2.5 (or configurable threshold)
       - OR amount > 3× user's average monthly spend in that category
       - OR amount > 50% of user's monthly budget in a single transaction

    4. Classify severity:
       - Mild:     z-score 2.0–2.5
       - Moderate: z-score 2.5–3.5
       - Severe:   z-score > 3.5

    5. Provide context:
       - "₹2,00,000 in Medical — your average Medical spending is ₹3,500/month"
```

### 2.6 Recurrence Analysis Module

**Source**: New FinSight functionality

**Method**: Pattern matching on transaction history

```
For each category:
    1. Look for repeated similar amounts (within ±15% tolerance)
    2. Check temporal regularity (monthly, quarterly, annual)
    3. Classify:
       - NORMAL:     Within expected range, regular pattern
       - UNUSUAL:    Outside expected range, no pattern match
       - ONE_TIME:   Anomalous + occurred only once
       - RECURRING:  Regular amount at regular intervals
       - PERSISTENT: Previously anomalous, but now repeating

    4. Impact on forecasting:
       - ONE_TIME:   Exclude from baseline forecast
       - RECURRING:  Include as persistent commitment
       - PERSISTENT: Flag for user attention, include with adjustment
```

### 2.7 Feature Engineering Module

**Source**: Adapted from BudgetWise `_create_features()` + new features

**Features for ML forecasting** (transaction-level → monthly aggregation):

| Feature | Formula | Source |
|---------|---------|--------|
| total_monthly_expense | Sum of all transactions in month | New |
| category_expenses (×N) | Sum per category per month | New |
| budget_utilization | total_expense / budget | BudgetWise ✓ |
| budget_remaining | budget - total_expense | BudgetWise ✓ |
| overspend_amount | max(0, total_expense - budget) | BudgetWise ✓ |
| month_num, quarter | Temporal encoding | BudgetWise ✓ |
| is_holiday_season | Nov/Dec/Jan flag | BudgetWise ✓ |
| is_summer | Jun/Jul/Aug flag | BudgetWise ✓ |
| avg_monthly_expense | User's rolling average | BudgetWise ✓ (fix leakage) |
| expense_volatility | User's rolling std | BudgetWise ✓ (fix leakage) |
| category_ratios | Each category / total | BudgetWise ✓ |
| transaction_count | Number of transactions in month | New |
| avg_transaction_amount | Monthly average per transaction | New |
| recurring_expense_total | Sum of detected recurring expenses | New |
| anomaly_count | Number of anomalies in month | New |
| expense_trend | Slope of recent 3-month spending | New |
| income_expense_ratio | income / total_expense | New |

> [!IMPORTANT]
> **Data leakage fix**: All user-level aggregate features (avg, std, trend) must be computed using ONLY training data (expanding window or leave-future-out), never on the full dataset.

### 2.8 ML Forecasting Module

**Source**: Adapted from BudgetWise `train_models()` + fixes

**Target**: Next-month total expenditure

**Candidate Models**:
1. **Linear Regression** — baseline model (from BudgetWise ✓)
2. **Random Forest Regressor** — ensemble model (from BudgetWise ✓)
3. **LSTM** — sequential model (from BudgetWise ✓, fix temporal split)

**Pipeline**:
```
Historical Monthly Features
    ↓
Train/Test Split (temporal — last N months as test, NOT random)
    ↓
Scale features (MinMaxScaler, fit on train only)
    ↓
Train all 3 models
    ↓
Evaluate on test set: MAE, RMSE, R²
    ↓
Select best model (lowest MAE)
    ↓
Save best model (joblib)
    ↓
Predict next month's expense
```

### 2.9 Model Explainability Module

**Source**: New FinSight functionality

| Model Type | Explainability Method |
|-----------|----------------------|
| Random Forest | Feature importance (built-in `.feature_importances_`) |
| Linear Regression | Coefficients (`.coef_`) |
| LSTM | Input feature contribution (approximated via feature ablation or attention weights) |

**Output format**:
```
Prediction: ₹23,400

Top contributing factors:
  1. Previous month spending (₹22,100)     — 35% importance
  2. Recurring expenses (₹12,000)          — 25% importance
  3. Grocery spending trend (↑12%)         — 15% importance
  4. Holiday season effect                 — 10% importance
  5. Transport spending                    — 8% importance
```

### 2.10 Recommendation Engine

**Source**: Extended from BudgetWise `generate_budget_recommendations()` + new logic

**Inputs**: predicted expense, historical spending, budget, financial goals, anomalies, recurring expenses, category trends

**Recommendation categories**:

| Category | Example |
|----------|---------|
| Budget Warning | "You are likely to exceed your ₹22,000 budget. Predicted expense: ₹23,400." |
| Category Alert | "Your transport spending has increased 18% compared to your 3-month average." |
| Anomaly Context | "Your recent ₹2,00,000 medical expense is unusual. It should not be treated as recurring." |
| Savings Opportunity | "Reducing grocery spending by 10% could save ~₹800/month." |
| Goal Progress | "At current spending rate, your ₹50,000 savings goal will take 8 months." |
| Recurrence Notice | "3 recurring subscriptions detected totaling ₹2,500/month." |

### 2.11 Generative AI Layer

**Source**: Base paper concept (Llama 3.1 + Ollama) — new FinSight implementation

**Architecture**:
```
ML Predictions + Analytics Results (VERIFIED DATA)
    ↓
Structured prompt with financial context
    ↓
Llama 3.1 via Ollama (local inference)
    ↓
Natural language explanation
```

**LLM Role** (strictly bounded):
- ✅ Explain ML predictions in plain language
- ✅ Explain spending trends and patterns
- ✅ Explain anomalies in context
- ✅ Explain recommendations with reasoning
- ✅ Answer questions about user's financial data
- ❌ Must NOT invent numerical facts
- ❌ Must NOT replace the ML model's predictions
- ❌ Must NOT provide regulated financial advice

**Prompt template pattern**:
```
You are a personal finance assistant for an academic prototype.

USER FINANCIAL CONTEXT:
- Monthly income: ₹{income}
- Monthly budget: ₹{budget}
- Predicted next-month expense: ₹{prediction}
- Budget utilization: {utilization}%
- Top spending categories: {categories}
- Detected anomalies: {anomalies}
- Recurring expenses: {recurring}

Based on the above verified data, explain the user's financial situation
and the prediction in simple, clear language. Do not invent any numbers.
```

### 2.12 Streamlit Dashboard

**Pages**:

| Page | Content |
|------|---------|
| 🏠 Home | Welcome, system overview, quick stats |
| 👤 User Profile | Income, budget, goals, financial baseline summary |
| 📤 Upload Transactions | CSV/Excel upload + manual entry form |
| 📊 Expense Dashboard | Total spending, category breakdown, monthly trends (Plotly) |
| 📈 Spending Analysis | Detailed category analysis, trends, comparisons |
| ⚠️ Anomaly Detection | Flagged unusual transactions with explanations |
| 🔮 Forecast | ML prediction, model comparison, feature importance |
| 💡 Recommendations | Personalized suggestions with rationale |
| 🤖 AI Financial Assistant | Chat interface powered by Llama 3.1 |

---

## 3. Database Schema (SQLite)

```sql
-- Users table
CREATE TABLE users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT UNIQUE NOT NULL,
    income        REAL DEFAULT 0,
    budget        REAL DEFAULT 0,
    financial_goal TEXT,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transactions table
CREATE TABLE transactions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    date            DATE NOT NULL,
    amount          REAL NOT NULL,
    category        TEXT NOT NULL,
    payment_method  TEXT DEFAULT 'Cash',
    description     TEXT,
    merchant        TEXT,
    is_anomaly      BOOLEAN DEFAULT 0,
    is_recurring    BOOLEAN DEFAULT 0,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Budgets table
CREATE TABLE budgets (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    month       INTEGER NOT NULL,
    year        INTEGER NOT NULL,
    amount      REAL NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Goals table
CREATE TABLE goals (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    description TEXT NOT NULL,
    target_amount REAL,
    deadline    DATE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Forecasts table
CREATE TABLE forecasts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    forecast_month  INTEGER NOT NULL,
    forecast_year   INTEGER NOT NULL,
    predicted_amount REAL NOT NULL,
    model_used      TEXT NOT NULL,
    confidence      REAL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Recommendations table
CREATE TABLE recommendations (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    type        TEXT NOT NULL,
    priority    TEXT NOT NULL,
    message     TEXT NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## 4. Technology Stack

| Layer | Technology | Justification |
|-------|-----------|---------------|
| Language | Python 3.10+ | Standard for ML/DS |
| Data Processing | Pandas, NumPy | Industry standard |
| ML Models | Scikit-learn | RF, LR, evaluation metrics |
| Deep Learning | TensorFlow/Keras | LSTM model |
| Visualization | Plotly | Interactive charts for Streamlit |
| Dashboard | Streamlit | Rapid prototyping, academic-friendly |
| Database | SQLite | Zero-config, file-based, sufficient for prototype |
| LLM | Llama 3.1 via Ollama | Local inference, no API costs |
| Model Persistence | Joblib | Save/load trained models |
| Config | python-dotenv | Environment variables |

---

## 5. Proposed Directory Structure

```
FinSight/
├── app.py                      # Streamlit entry point
├── requirements.txt
├── .env.example
├── README.md
├── config/
│   └── settings.py             # Configuration constants
├── data/
│   ├── sample_transactions.csv # Demo dataset
│   └── finsight.db             # SQLite database
├── src/
│   ├── __init__.py
│   ├── data_input.py           # CSV/Excel parsing, validation
│   ├── preprocessing.py        # Cleaning, normalization
│   ├── database.py             # SQLite operations
│   ├── financial_profile.py    # User profile builder
│   ├── spending_analytics.py   # Category/trend analysis
│   ├── anomaly_detection.py    # Anomaly detection
│   ├── recurrence_analysis.py  # Recurrence classification
│   ├── feature_engineering.py  # Feature creation for ML
│   ├── ml_forecasting.py       # Model training, evaluation, selection
│   ├── explainability.py       # Feature importance, explanations
│   ├── recommendations.py      # Recommendation engine
│   └── genai_assistant.py      # Llama 3.1 integration via Ollama
├── models/
│   └── (saved .joblib models)
├── pages/
│   ├── 1_User_Profile.py
│   ├── 2_Upload_Transactions.py
│   ├── 3_Expense_Dashboard.py
│   ├── 4_Spending_Analysis.py
│   ├── 5_Anomaly_Detection.py
│   ├── 6_Forecast.py
│   ├── 7_Recommendations.py
│   └── 8_AI_Assistant.py
├── tests/
│   └── (unit tests)
└── docs/
    ├── PROJECT_AUDIT.md
    ├── FINSIGHT_ARCHITECTURE.md
    └── (diagrams)
```

---

## 6. Provenance Map

This table clearly distinguishes what comes from where:

| Component | Base Paper | BudgetWise | FinSight (New) |
|-----------|:---------:|:----------:|:--------------:|
| ML + GenAI concept | ✅ | — | — |
| Feature engineering | — | ✅ (adapted) | Extended |
| RF / LR / LSTM models | — | ✅ (adapted) | Fixed bugs |
| Model comparison framework | — | ✅ (reused) | — |
| Evaluation metrics (MAE, RMSE, R²) | — | ✅ (reused) | — |
| Recommendation engine structure | — | ✅ (extended) | Extended |
| Llama 3.1 + Ollama concept | ✅ | — | Implemented |
| Streamlit concept | ✅ | — | Implemented |
| Transaction-level data input | — | — | ✅ |
| Anomaly detection | — | — | ✅ |
| Recurrence analysis | — | — | ✅ |
| Financial profile builder | — | — | ✅ |
| Model explainability | — | — | ✅ |
| SQLite database | — | — | ✅ |
| AI chat assistant | — | — | ✅ |
| Interactive Plotly dashboard | — | — | ✅ |
