# PROJECT AUDIT: BudgetWise → FinSight AI

> **Audit Date**: 2026-09-08
> **Repository**: [BudgetWise-AI-Based-Expense-Forecasting-Tool](https://github.com/JyothiSriLakshmi-1305/BudgetWise-AI-Based-Expense-Forecasting-Tool)
> **Commits**: 22 | **License**: MIT | **Branch**: main

---

## A. Complete Repository Structure

```
BudgetWise-AI-Based-Expense-Forecasting-Tool/
├── .gitignore                          (4.9 KB)
├── DatasetFinalCSV.csv                 (23.7 KB, 240 data rows)
├── Final_PPT_Team 1.pptx              (2.2 MB)
├── LICENSE                             (MIT)
├── README.md                           (4.7 KB)
├── requirements.txt                    (690 B — Flask-only deps)
│
├── Model/
│   ├── model.py                        (25.2 KB — main ML pipeline)
│   └── temp                            (2 B — empty placeholder)
│
├── LandingPage/
│   ├── app.py                          (4.5 KB — Flask web app)
│   ├── static/
│   │   ├── script.js                   (29.6 KB)
│   │   └── style.css                   (34.7 KB)
│   └── templates/
│       ├── home.html                   (16.6 KB)
│       ├── index.html                  (8 KB)
│       ├── login.html                  (3.8 KB)
│       └── signup.html                 (4.5 KB)
│
└── ModelPredCode+PklFile/
    ├── InfosysModelFullCode.ipynb      (53.8 KB — training notebook)
    ├── ModelPredictionCode.ipynb        (6 KB — prediction notebook)
    └── rf_pipeline.pkl                 (940 KB — saved Random Forest)
```

---

## B. File-by-File Explanation

### Root Files

| File | Purpose | Notes |
|------|---------|-------|
| `DatasetFinalCSV.csv` | Training dataset | 240 rows, ~20 users × 12 months. Budget-level (NOT transaction-level). Columns: User, Month, Monthly_Budget, Grocery_Ini1, Rent_Ini2, Transport_Ini3, InitialExpense, Have_Balance, OtherExpense_name, AmountOfProduct, Remaining_Balance, Purchase_Allowed |
| `requirements.txt` | Python dependencies | **Flask-only** — contains Flask, SQLAlchemy, PyMySQL, Flask-Login, etc. Does NOT include any ML libraries (pandas, sklearn, tensorflow). Incomplete. |
| `README.md` | Project description | Describes features, workflow, achievement (Infosys Springboard). Claims Random Forest as the algorithm. |
| `Final_PPT_Team 1.pptx` | Presentation | Academic presentation from original project. |
| `.gitignore` | Git ignores | Standard Python gitignore. |

### Model/model.py (25.2 KB) — Core ML Pipeline

This is a **single-file, class-based** ML pipeline (`BudgetWiseForecaster`):

| Method | Purpose | Assessment |
|--------|---------|------------|
| `__init__()` | Initializes data containers, scalers, models, predictions | ✅ Clean |
| `load_and_preprocess_data(filepath)` | Loads CSV, fills NaN with 0, creates month ordering | ⚠️ NaN handling too aggressive (fills all with 0) |
| `_create_features()` | Feature engineering: Total_Expenses, Budget_Utilization, Budget_Remaining, Overspend_Amount, Month_Num, Quarter, user aggregates (Avg_Expenses, Expense_Volatility, Avg_Budget), category ratios, seasonal indicators | ⚠️ **Data leakage**: user-level aggregate features (Avg_Expenses, Avg_Budget) are computed on the FULL dataset before train/test split |
| `prepare_lstm_data(sequence_length=3)` | Creates sequential data for LSTM with MinMaxScaler | ⚠️ Very limited sequences (~9 per user with 12 months and seq_len=3) |
| `build_lstm_model(input_shape)` | 2-layer LSTM (64→32 units), Dropout 0.2, Adam optimizer | ✅ Standard architecture |
| `train_models()` | Trains RF (100 trees), LR, LSTM; 80/20 split | ⚠️ LSTM train/test uses random split on sequential data (should be temporal) |
| `evaluate_models()` | Compares MAE, RMSE, R² across models; selects best by MAE | ✅ Good comparison framework |
| `forecast_future_expenses(user, months_ahead)` | Forecasts using RF model (hardcoded default) | ⚠️ Always uses RF regardless of evaluation results |
| `generate_budget_recommendations(user)` | Rule-based recommendations (overspend rate, category %, seasonal) | ⚠️ Fully rule-based, not ML-driven. Limited rules. |
| `create_dashboard_visualizations()` | 9-panel matplotlib dashboard | ⚠️ Static matplotlib, not interactive |
| `generate_user_report(user)` | Text-based console report | ✅ Good structure, needs UI adaptation |

**Libraries imported**: pandas, numpy, matplotlib, seaborn, sklearn (MinMaxScaler, LabelEncoder, train_test_split, MAE, MSE, R², RandomForest, LinearRegression), tensorflow.keras (Sequential, LSTM, Dense, Dropout, Adam, EarlyStopping, ReduceLROnPlateau)

### LandingPage/app.py (4.5 KB) — Flask Web Application

| Component | Details |
|-----------|---------|
| Framework | Flask + Flask-Login + Flask-SQLAlchemy |
| Database | MySQL via PyMySQL |
| User Model | id, username, email, gender, password_hash |
| Routes | `/` (index), `/signup`, `/login`, `/logout`, `/home` |
| Auth | Flask-Login with password hashing |

> [!CAUTION]
> **Security Issues**:
> - `SECRET_KEY = 'Secret@123'` — hardcoded
> - `DB_PASSWORD = 'Secret@1234'` — hardcoded
> - No connection to ML model whatsoever
> - Landing page is **completely disconnected** from the model

### LandingPage/static/ — Frontend Assets

| File | Size | Purpose |
|------|------|---------|
| `script.js` | 29.6 KB | JavaScript for the landing page UI interactions |
| `style.css` | 34.7 KB | CSS styling for the Flask templates |

### LandingPage/templates/ — HTML Templates

| File | Purpose |
|------|---------|
| `index.html` | Landing/welcome page |
| `signup.html` | User registration form |
| `login.html` | User login form |
| `home.html` | Main dashboard page (post-login) |

### ModelPredCode+PklFile/ — Notebooks & Saved Model

| File | Purpose | Notes |
|------|---------|-------|
| `InfosysModelFullCode.ipynb` | Full model training notebook | 53.8 KB. Contains the complete training pipeline with visualizations. |
| `ModelPredictionCode.ipynb` | Prediction-only notebook | 6 KB. Uses the saved pkl model for inference. |
| `rf_pipeline.pkl` | Saved Random Forest model | 940 KB. Serialized sklearn pipeline. |

---

## C. Existing ML Pipeline

```
DatasetFinalCSV.csv
    ↓
load_and_preprocess_data()
    ↓
_create_features()  ← Feature engineering
    ↓
train_test_split (80/20, random)
    ↓
┌─────────────────────────────┐
│ Random Forest (100 trees)   │
│ Linear Regression           │
│ LSTM (64→32, dropout 0.2)   │
└─────────────────────────────┘
    ↓
evaluate_models() → MAE, RMSE, R²
    ↓
Best model by MAE
    ↓
forecast_future_expenses() → Uses RF (hardcoded)
```

**Feature columns used for ML**:
Monthly_Budget, Month_Num, Quarter, Grocery_Ini1, Rent_Ini2, Transport_Ini3, InitialExpense, AmountOfProduct, Avg_Expenses, Expense_Volatility, Avg_Budget, Is_Holiday_Season, Is_Summer

**Target variable**: `Total_Expenses`

---

## D. Existing Prediction Pipeline

- `forecast_future_expenses(user, months_ahead)` uses the trained Random Forest model
- Iterates month-by-month, adjusting Month_Num, Quarter, seasonal flags
- Carries forward the user's last known data point
- Returns DataFrame with: Month, Predicted_Expense, Budget, Predicted_Savings
- **Issue**: Always uses RF regardless of which model won evaluation

---

## E. Existing Recommendation System

`generate_budget_recommendations(user)` — purely rule-based:

| Rule | Trigger | Priority |
|------|---------|----------|
| Budget adjustment | Overspend rate > 50% of months | High |
| Grocery optimization | Grocery > 15% of total | Medium |
| Transport optimization | Transport > 20% of total | Medium |
| Seasonal planning | Holiday spending > 120% of regular | Medium |

**Limitation**: Only 4 rules. No ML-driven recommendations. No anomaly context. No recurrence awareness.

---

## F. Existing Chatbot/AI Functionality

> **None.** There is NO chatbot, NO LLM integration, NO GenAI component in the BudgetWise codebase.

The README mentions "AI Chatbot Assistance" and "Workflow Automation using n8n" but neither is implemented in the repository code.

---

## G. Existing Database/Backend/Frontend

| Layer | Technology | Status |
|-------|-----------|--------|
| Database | MySQL via PyMySQL + SQLAlchemy | ⚠️ Only stores user accounts (username, email, gender, password). No transaction/expense storage. |
| Backend | Flask | ⚠️ Only handles auth (signup/login/logout). No API endpoints for ML. |
| Frontend | HTML/CSS/JS templates | ⚠️ Static landing page only. No dashboard, no charts, no ML integration. |

**The Flask app and the ML model exist as completely separate, unconnected components.**

---

## H. Existing Dataset Structure

**File**: `DatasetFinalCSV.csv`
**Rows**: 240 (+ 1 header)
**Users**: ~20 (User1 through User20)
**Months**: 12 per user (January–December)

| Column | Type | Description |
|--------|------|-------------|
| User | String | User identifier (User1, User2, ...) |
| Month | String | Month name (January–December) |
| Monthly_Budget | Integer | User's monthly budget (₹) |
| Grocery_Ini1 | Integer | Grocery expenses |
| Rent_Ini2 | Integer | Rent expenses |
| Transport_Ini3 | Integer | Transport expenses |
| InitialExpense | Integer | Sum of Grocery + Rent + Transport |
| Have_Balance | Integer | Budget - InitialExpense |
| OtherExpense_name | String | Name of additional product purchased |
| AmountOfProduct | Integer | Cost of the product |
| Remaining_Balance | Integer | Have_Balance - AmountOfProduct |
| Purchase_Allowed | String | Whether purchase was affordable |

> [!IMPORTANT]
> **Critical dataset limitation for FinSight**: This is **budget-level monthly data**, NOT transaction-level data. FinSight requires individual transaction records (date, amount, category, payment method, description). The existing dataset cannot be directly used for transaction-level analytics, anomaly detection, or recurrence analysis.

---

## I. What Can Be Reused

| Component | Reusability | How to Reuse in FinSight |
|-----------|------------|--------------------------|
| Feature engineering concepts | ✅ High | Budget_Utilization, Overspend_Amount, category ratios, seasonal indicators — all applicable |
| ML pipeline structure | ✅ High | Train/evaluate/compare framework is solid and can be adapted |
| Model comparison (RF vs LR vs LSTM) | ✅ High | Same 3-model comparison pattern, same metrics |
| Evaluation metrics (MAE, RMSE, R²) | ✅ High | Directly reusable |
| Recommendation engine structure | ✅ Medium | Extend with more rules + ML-driven suggestions |
| User report format | ✅ Medium | Adapt for Streamlit display |
| Visualization concepts | ✅ Medium | Adapt from matplotlib to Plotly |
| Random Forest saved model pattern | ✅ Medium | Use joblib/pickle pattern for model persistence |

---

## J. What Must Be Modified

| Component | Current | Required Change |
|-----------|---------|-----------------|
| Dataset format | Budget-level monthly | Transaction-level (date, amount, category, etc.) |
| Feature engineering | Tied to dataset columns | Must aggregate transactions → monthly features |
| Data leakage | User stats computed before split | Compute within training set only |
| LSTM data splitting | Random split | Temporal split (chronological) |
| Forecast model | Hardcoded RF | Use actual best model from evaluation |
| Frontend | Flask + HTML/CSS/JS | Streamlit |
| Database | MySQL | SQLite (academic prototype) |
| Visualizations | Static matplotlib | Interactive Plotly |
| Dependencies | Flask-only requirements.txt | Full requirements.txt with all ML/AI libraries |
| Security | Hardcoded secrets | Environment variables via .env |

---

## K. What Is Missing for FinSight

| # | Missing Component | Priority | Complexity |
|---|-------------------|----------|------------|
| 1 | Transaction-level data input (CSV/Excel upload + manual entry) | 🔴 Critical | Medium |
| 2 | Data validation & preprocessing for raw transactions | 🔴 Critical | Medium |
| 3 | Transaction aggregation to monthly features | 🔴 Critical | Medium |
| 4 | Personal financial profile builder | 🔴 Critical | Medium |
| 5 | Anomaly detection module | 🔴 Critical | Medium |
| 6 | Recurrence analysis module | 🔴 Critical | Medium |
| 7 | GenAI/LLM integration (Llama 3.1 + Ollama) | 🔴 Critical | High |
| 8 | Financial chatbot/assistant | 🟡 Important | High |
| 9 | Streamlit multi-page dashboard | 🔴 Critical | High |
| 10 | SQLite database with full schema | 🟡 Important | Medium |
| 11 | Dynamic best-model selection for forecasting | 🟡 Important | Low |
| 12 | Model explainability (feature importance display) | 🟡 Important | Low |
| 13 | Model saving/loading for production use | 🟡 Important | Low |
| 14 | User-specific model personalization | 🟡 Important | Medium |
| 15 | Sample transaction dataset for FinSight | 🔴 Critical | Medium |
| 16 | Environment variable management (.env) | 🟢 Nice | Low |
| 17 | Complete requirements.txt | 🟡 Important | Low |
| 18 | Architecture documentation | 🟡 Important | Low |

---

## L. Potential Bugs/Inconsistencies

| # | Issue | Severity | Location |
|---|-------|----------|----------|
| 1 | **Data leakage**: User aggregate features (Avg_Expenses, Expense_Volatility, Avg_Budget) are computed on the FULL dataset before train/test split. The test set effectively "knows" information from training. | 🔴 High | `model.py: _create_features()` |
| 2 | **LSTM temporal split**: Sequential time-series data is split randomly, not chronologically. This artificially inflates LSTM performance. | 🔴 High | `model.py: train_models()` |
| 3 | **Hardcoded forecast model**: `forecast_future_expenses()` always uses RF regardless of which model performed best in evaluation. | 🟡 Medium | `model.py: forecast_future_expenses()` |
| 4 | **Hardcoded secrets**: SECRET_KEY and DB_PASSWORD are in source code. | 🔴 High | `LandingPage/app.py` |
| 5 | **Disconnected components**: Flask app has zero connection to ML pipeline. They exist as separate projects in one repo. | 🟡 Medium | Architecture |
| 6 | **Incomplete requirements.txt**: Missing all ML/DS libraries. | 🟡 Medium | `requirements.txt` |
| 7 | **NaN handling**: All NaN filled with 0, which may distort financial data. | 🟡 Medium | `model.py: load_and_preprocess_data()` |
| 8 | **README overclaims**: States "Workflow Automation using n8n" and "AI Chatbot Assistance" — neither exists in code. | 🟡 Medium | `README.md` |
| 9 | **Currency inconsistency**: Code uses `$` symbols but dataset values are clearly Indian Rupees (₹). | 🟢 Low | `model.py` (multiple methods) |
| 10 | **LabelEncoder imported but unused** | 🟢 Low | `model.py` imports |
| 11 | **seaborn imported but unused** | 🟢 Low | `model.py` imports |
| 12 | **Emoji encoding**: Console output uses Unicode emojis that may not render correctly on all terminals | 🟢 Low | `model.py` (multiple methods) |

---

## M. Base Paper Summary (For Context)

**Title**: GenAI-Powered Personal Finance Consultant: Integrating ML and GenAI for Personalized Financial Recommendations and Literacy Enhancement

| Aspect | Base Paper | BudgetWise | FinSight Target |
|--------|-----------|------------|-----------------|
| Focus | Investment/savings recommendations | Expense affordability | Expense intelligence + forecasting |
| ML Models | GANs + regression | RF + LR + LSTM | RF + LR + LSTM (retrained) |
| LLM | Llama 3.1 via Ollama | None | Llama 3.1 via Ollama |
| Data Input | Static questionnaire | Fixed CSV | CSV/Excel upload + manual entry |
| Database | Not specified | MySQL (user auth only) | SQLite (full schema) |
| Frontend | Streamlit | Flask + HTML | Streamlit |
| Anomaly Detection | None | None | ✅ Required |
| Recurrence Analysis | None | None | ✅ Required |
| Personalization | User profile → allocation | User stats → forecast | Financial profile → intelligence |
| R² Score | 0.4141 | Not yet evaluated | Target: experimentally determined |

---

## Summary Verdict

The BudgetWise repository provides a **solid ML skeleton** — the model training, evaluation, and comparison framework in `model.py` is well-structured and can be adapted. However:

1. The Flask frontend is a **separate, disconnected** landing page with no ML integration
2. The dataset is **budget-level, not transaction-level** — unsuitable for FinSight's transaction analytics
3. There are **critical data leakage and temporal split bugs** in the ML pipeline
4. **No anomaly detection, recurrence analysis, GenAI, chatbot, or Streamlit** exists
5. The recommendation engine is **minimal and purely rule-based**

**FinSight should reuse the ML pipeline concepts and architecture patterns from `model.py`, but will need substantial new development for all the intelligence layers, GenAI integration, and the Streamlit dashboard.**
