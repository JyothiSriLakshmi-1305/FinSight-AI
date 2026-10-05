import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
import warnings
warnings.filterwarnings('ignore')

class BudgetWiseForecaster:
    """
    BudgetWise AI-based Expense Forecasting Tool

    This class implements a complete pipeline for expense forecasting including:
    - Data preprocessing and feature engineering
    - Multiple forecasting models (LSTM, Random Forest, Linear Regression)
    - Budget optimization strategies
    - Personalized recommendations
    """

    def __init__(self):
        self.df = None
        self.processed_data = None
        self.scalers = {}
        self.models = {}
        self.predictions = {}
        self.recommendations = []

    def load_and_preprocess_data(self, filepath):
        """Load and preprocess the financial data"""
        print("=== LOADING AND PREPROCESSING DATA ===")

        # Load data
        self.df = pd.read_csv(filepath)
        print(f"Dataset shape: {self.df.shape}")

        # Handle missing values
        self.df.fillna(0, inplace=True)

        # Create month ordering
        months_order = ["January", "February", "March", "April", "May", "June",
                       "July", "August", "September", "October", "November", "December"]
        self.df["Month"] = pd.Categorical(self.df["Month"], categories=months_order, ordered=True)

        # Feature Engineering
        self._create_features()

        print("✓ Data preprocessing completed")
        return self.df

    def _create_features(self):
        """Create engineered features for better predictions"""

        # Basic expense categories
        expense_columns = ["Grocery_Ini1", "Rent_Ini2", "Transport_Ini3", "InitialExpense", "AmountOfProduct"]
        self.df["Total_Expenses"] = self.df[expense_columns].sum(axis=1)

        # Budget performance metrics
        self.df['Budget_Utilization'] = self.df['Total_Expenses'] / self.df['Monthly_Budget']
        self.df['Budget_Remaining'] = self.df['Monthly_Budget'] - self.df['Total_Expenses']
        self.df['Overspend_Amount'] = np.maximum(0, self.df['Total_Expenses'] - self.df['Monthly_Budget'])

        # Categorical features
        self.df['Month_Num'] = self.df['Month'].cat.codes + 1
        self.df['Quarter'] = np.ceil(self.df['Month_Num'] / 3)

        # User spending patterns
        user_stats = self.df.groupby('User').agg({
            'Total_Expenses': ['mean', 'std'],
            'Monthly_Budget': 'mean'
        }).round(2)
        user_stats.columns = ['Avg_Expenses', 'Expense_Volatility', 'Avg_Budget']
        self.df = self.df.merge(user_stats, on='User', how='left')

        # Spending ratios by category
        for col in ["Grocery_Ini1", "Rent_Ini2", "Transport_Ini3"]:
            self.df[f'{col}_Ratio'] = self.df[col] / (self.df['Total_Expenses'] + 1e-8)

        # Seasonal indicators
        self.df['Is_Holiday_Season'] = self.df['Month'].isin(['November', 'December', 'January']).astype(int)
        self.df['Is_Summer'] = self.df['Month'].isin(['June', 'July', 'August']).astype(int)

        print("✓ Feature engineering completed")

    def prepare_lstm_data(self, sequence_length=3):
        """Prepare data for LSTM model"""

        # Select relevant features for LSTM
        lstm_features = [
            'Monthly_Budget', 'Total_Expenses', 'Budget_Utilization',
            'Month_Num', 'Quarter', 'Grocery_Ini1', 'Rent_Ini2', 'Transport_Ini3',
            'Is_Holiday_Season', 'Is_Summer'
        ]

        # Create user-month sequences
        lstm_data = []
        for user in self.df['User'].unique():
            user_data = self.df[self.df['User'] == user].sort_values('Month_Num')

            if len(user_data) >= sequence_length + 1:
                for i in range(len(user_data) - sequence_length):
                    # Input sequence
                    X_seq = user_data[lstm_features].iloc[i:i+sequence_length].values
                    # Target (next month's total expenses)
                    y_seq = user_data['Total_Expenses'].iloc[i+sequence_length]
                    lstm_data.append((X_seq, y_seq))

        if not lstm_data:
            print("Warning: Not enough sequential data for LSTM")
            return None, None

        X_lstm = np.array([item[0] for item in lstm_data])
        y_lstm = np.array([item[1] for item in lstm_data])

        # Scale the data
        self.scalers['lstm_X'] = MinMaxScaler()
        self.scalers['lstm_y'] = MinMaxScaler()

        X_lstm_scaled = self.scalers['lstm_X'].fit_transform(
            X_lstm.reshape(-1, X_lstm.shape[-1])
        ).reshape(X_lstm.shape)

        y_lstm_scaled = self.scalers['lstm_y'].fit_transform(y_lstm.reshape(-1, 1)).flatten()

        return X_lstm_scaled, y_lstm_scaled

    def build_lstm_model(self, input_shape):
        """Build and compile LSTM model"""

        model = Sequential([
            LSTM(64, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(32, return_sequences=False),
            Dropout(0.2),
            Dense(16, activation='relu'),
            Dense(1)
        ])

        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )

        return model

    def train_models(self):
        """Train all forecasting models"""
        print("\n=== TRAINING FORECASTING MODELS ===")

        # Prepare features for traditional ML models
        feature_columns = [
            'Monthly_Budget', 'Month_Num', 'Quarter', 'Grocery_Ini1', 'Rent_Ini2',
            'Transport_Ini3', 'InitialExpense', 'AmountOfProduct', 'Avg_Expenses',
            'Expense_Volatility', 'Avg_Budget', 'Is_Holiday_Season', 'Is_Summer'
        ]

        X = self.df[feature_columns]
        y = self.df['Total_Expenses']

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Scale data for traditional models
        self.scalers['traditional'] = MinMaxScaler()
        X_train_scaled = self.scalers['traditional'].fit_transform(X_train)
        X_test_scaled = self.scalers['traditional'].transform(X_test)

        # 1. Random Forest Model
        print("Training Random Forest...")
        self.models['rf'] = RandomForestRegressor(n_estimators=100, random_state=42)
        self.models['rf'].fit(X_train_scaled, y_train)

        rf_pred = self.models['rf'].predict(X_test_scaled)
        self.predictions['rf'] = {
            'y_test': y_test,
            'y_pred': rf_pred,
            'mae': mean_absolute_error(y_test, rf_pred),
            'rmse': np.sqrt(mean_squared_error(y_test, rf_pred)),
            'r2': r2_score(y_test, rf_pred)
        }

        # 2. Linear Regression Model
        print("Training Linear Regression...")
        self.models['lr'] = LinearRegression()
        self.models['lr'].fit(X_train_scaled, y_train)

        lr_pred = self.models['lr'].predict(X_test_scaled)
        self.predictions['lr'] = {
            'y_test': y_test,
            'y_pred': lr_pred,
            'mae': mean_absolute_error(y_test, lr_pred),
            'rmse': np.sqrt(mean_squared_error(y_test, lr_pred)),
            'r2': r2_score(y_test, lr_pred)
        }

        # 3. LSTM Model
        print("Training LSTM...")
        X_lstm, y_lstm = self.prepare_lstm_data()

        if X_lstm is not None:
            X_lstm_train, X_lstm_test, y_lstm_train, y_lstm_test = train_test_split(
                X_lstm, y_lstm, test_size=0.2, random_state=42
            )

            self.models['lstm'] = self.build_lstm_model((X_lstm.shape[1], X_lstm.shape[2]))

            callbacks = [
                EarlyStopping(patience=10, restore_best_weights=True),
                ReduceLROnPlateau(patience=5, factor=0.5)
            ]

            history = self.models['lstm'].fit(
                X_lstm_train, y_lstm_train,
                epochs=50,
                batch_size=16,
                validation_split=0.2,
                callbacks=callbacks,
                verbose=0
            )

            lstm_pred_scaled = self.models['lstm'].predict(X_lstm_test)
            lstm_pred = self.scalers['lstm_y'].inverse_transform(lstm_pred_scaled.reshape(-1, 1)).flatten()
            y_lstm_test_original = self.scalers['lstm_y'].inverse_transform(y_lstm_test.reshape(-1, 1)).flatten()

            self.predictions['lstm'] = {
                'y_test': y_lstm_test_original,
                'y_pred': lstm_pred,
                'mae': mean_absolute_error(y_lstm_test_original, lstm_pred),
                'rmse': np.sqrt(mean_squared_error(y_lstm_test_original, lstm_pred)),
                'r2': r2_score(y_lstm_test_original, lstm_pred),
                'history': history.history
            }

        print("✓ Model training completed")

    def evaluate_models(self):
        """Evaluate and compare all models"""
        print("\n=== MODEL EVALUATION ===")

        results_df = pd.DataFrame({
            'Model': [],
            'MAE': [],
            'RMSE': [],
            'R²': []
        })

        for model_name, pred_data in self.predictions.items():
            results_df = pd.concat([results_df, pd.DataFrame({
                'Model': [model_name.upper()],
                'MAE': [pred_data['mae']],
                'RMSE': [pred_data['rmse']],
                'R²': [pred_data['r2']]
            })], ignore_index=True)

        print(results_df.round(4))

        # Find best model
        best_model = results_df.loc[results_df['MAE'].idxmin(), 'Model']
        print(f"\n🏆 Best performing model: {best_model} (Lowest MAE)")

        return results_df

    def forecast_future_expenses(self, user, months_ahead=3):
        """Forecast future expenses for a specific user"""

        user_data = self.df[self.df['User'] == user].copy()
        if user_data.empty:
            print(f"No data found for user: {user}")
            return None

        # Use the best performing model (Random Forest as default)
        model = self.models.get('rf')
        scaler = self.scalers.get('traditional')

        if model is None or scaler is None:
            print("Models not trained yet. Please run train_models() first.")
            return None

        # Get user's latest data point
        latest_data = user_data.sort_values('Month_Num').iloc[-1]

        forecasts = []
        feature_columns = [
            'Monthly_Budget', 'Month_Num', 'Quarter', 'Grocery_Ini1', 'Rent_Ini2',
            'Transport_Ini3', 'InitialExpense', 'AmountOfProduct', 'Avg_Expenses',
            'Expense_Volatility', 'Avg_Budget', 'Is_Holiday_Season', 'Is_Summer'
        ]

        for i in range(1, months_ahead + 1):
            # Create future data point
            future_month_num = (latest_data['Month_Num'] + i - 1) % 12 + 1
            future_quarter = np.ceil(future_month_num / 3)

            future_data = latest_data[feature_columns].copy()
            future_data['Month_Num'] = future_month_num
            future_data['Quarter'] = future_quarter
            future_data['Is_Holiday_Season'] = 1 if future_month_num in [11, 12, 1] else 0
            future_data['Is_Summer'] = 1 if future_month_num in [6, 7, 8] else 0

            # Predict
            future_scaled = scaler.transform([future_data.values])
            predicted_expense = model.predict(future_scaled)[0]

            forecasts.append({
                'Month': future_month_num,
                'Predicted_Expense': predicted_expense,
                'Budget': latest_data['Monthly_Budget'],
                'Predicted_Savings': latest_data['Monthly_Budget'] - predicted_expense
            })

        return pd.DataFrame(forecasts)

    def generate_budget_recommendations(self, user):
        """Generate personalized budget recommendations"""

        user_data = self.df[self.df['User'] == user].copy()
        if user_data.empty:
            return []

        recommendations = []
        avg_expenses = user_data['Total_Expenses'].mean()
        avg_budget = user_data['Monthly_Budget'].mean()
        overspend_rate = len(user_data[user_data['Total_Expenses'] > user_data['Monthly_Budget']]) / len(user_data)

        # Budget adjustment recommendations
        if overspend_rate > 0.5:
            recommended_budget = avg_expenses * 1.1
            recommendations.append({
                'type': 'budget_adjustment',
                'priority': 'high',
                'message': f"Consider increasing monthly budget to ${recommended_budget:.2f} (current: ${avg_budget:.2f})",
                'savings_potential': 0
            })

        # Category-specific recommendations
        categories = ['Grocery_Ini1', 'Rent_Ini2', 'Transport_Ini3']
        for category in categories:
            avg_category_spend = user_data[category].mean()
            category_percentage = avg_category_spend / avg_expenses * 100

            if category == 'Grocery_Ini1' and category_percentage > 15:
                potential_savings = avg_category_spend * 0.1
                recommendations.append({
                    'type': 'category_optimization',
                    'priority': 'medium',
                    'message': f"Food expenses are {category_percentage:.1f}% of total spending. Consider meal planning to save ~${potential_savings:.2f}/month",
                    'savings_potential': potential_savings
                })

            elif category == 'Transport_Ini3' and category_percentage > 20:
                potential_savings = avg_category_spend * 0.15
                recommendations.append({
                    'type': 'category_optimization',
                    'priority': 'medium',
                    'message': f"Transportation costs are high ({category_percentage:.1f}%). Consider carpooling or public transport to save ~${potential_savings:.2f}/month",
                    'savings_potential': potential_savings
                })

        # Seasonal spending recommendations
        seasonal_data = user_data.groupby('Is_Holiday_Season')['Total_Expenses'].mean()
        if len(seasonal_data) > 1 and seasonal_data[1] > seasonal_data[0] * 1.2:
            recommendations.append({
                'type': 'seasonal_planning',
                'priority': 'medium',
                'message': f"Holiday spending is {((seasonal_data[1]/seasonal_data[0]-1)*100):.1f}% higher. Consider setting aside ${(seasonal_data[1]-seasonal_data[0]):.2f}/month for holiday expenses",
                'savings_potential': 0
            })

        return recommendations

    def create_dashboard_visualizations(self):
        """Create comprehensive dashboard visualizations"""

        fig = plt.figure(figsize=(20, 16))

        # 1. Model Performance Comparison
        plt.subplot(3, 3, 1)
        models = list(self.predictions.keys())
        maes = [self.predictions[model]['mae'] for model in models]
        colors = ['skyblue', 'lightcoral', 'lightgreen'][:len(models)]

        plt.bar(models, maes, color=colors, alpha=0.8)
        plt.title('Model Performance (MAE)', fontsize=14, fontweight='bold')
        plt.ylabel('Mean Absolute Error')
        plt.xticks(rotation=45)

        # 2. Actual vs Predicted (Best Model)
        plt.subplot(3, 3, 2)
        best_model = min(self.predictions.keys(), key=lambda x: self.predictions[x]['mae'])
        y_test = self.predictions[best_model]['y_test']
        y_pred = self.predictions[best_model]['y_pred']

        plt.scatter(y_test, y_pred, alpha=0.6, color='darkblue')
        plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
        plt.xlabel('Actual Expenses')
        plt.ylabel('Predicted Expenses')
        plt.title(f'{best_model.upper()} - Actual vs Predicted', fontsize=14, fontweight='bold')

        # 3. Feature Importance (Random Forest)
        if 'rf' in self.models:
            plt.subplot(3, 3, 3)
            feature_names = [
                'Monthly_Budget', 'Month_Num', 'Quarter', 'Grocery', 'Rent',
                'Transport', 'InitialExpense', 'Products', 'Avg_Expenses',
                'Expense_Volatility', 'Avg_Budget', 'Holiday_Season', 'Summer'
            ]
            importances = self.models['rf'].feature_importances_
            indices = np.argsort(importances)[::-1][:8]

            plt.bar(range(len(indices)), importances[indices], alpha=0.8, color='orange')
            plt.title('Feature Importance (Random Forest)', fontsize=14, fontweight='bold')
            plt.xticks(range(len(indices)), [feature_names[i] for i in indices], rotation=45)
            plt.ylabel('Importance')

        # 4. Monthly Expense Trends
        plt.subplot(3, 3, 4)
        monthly_avg = self.df.groupby('Month', observed=True)['Total_Expenses'].mean()
        plt.plot(monthly_avg.index, monthly_avg.values, marker='o', linewidth=3, markersize=8, color='green')
        plt.title('Average Monthly Expense Trends', fontsize=14, fontweight='bold')
        plt.ylabel('Average Expenses ($)')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)

        # 5. User Expense Distribution
        plt.subplot(3, 3, 5)
        self.df.boxplot(column='Total_Expenses', by='User', ax=plt.gca())
        plt.title('Expense Distribution by User', fontsize=14, fontweight='bold')
        plt.suptitle('')  # Remove default title
        plt.ylabel('Total Expenses ($)')
        plt.xticks(rotation=45)

        # 6. Budget Utilization Histogram
        plt.subplot(3, 3, 6)
        plt.hist(self.df['Budget_Utilization'], bins=20, alpha=0.7, color='purple', edgecolor='black')
        plt.axvline(x=1, color='red', linestyle='--', linewidth=2, label='Budget Limit')
        plt.title('Budget Utilization Distribution', fontsize=14, fontweight='bold')
        plt.xlabel('Budget Utilization Ratio')
        plt.ylabel('Frequency')
        plt.legend()

        # 7. Category Spending Patterns
        plt.subplot(3, 3, 7)
        categories = ['Grocery_Ini1', 'Rent_Ini2', 'Transport_Ini3', 'InitialExpense', 'AmountOfProduct']
        avg_spending = [self.df[cat].mean() for cat in categories]
        category_labels = ['Grocery', 'Rent', 'Transport', 'Initial', 'Products']

        plt.pie(avg_spending, labels=category_labels, autopct='%1.1f%%', startangle=90)
        plt.title('Average Spending by Category', fontsize=14, fontweight='bold')

        # 8. Seasonal Spending Analysis
        plt.subplot(3, 3, 8)
        seasonal_spending = self.df.groupby(['Quarter', 'Is_Holiday_Season'])['Total_Expenses'].mean().unstack()
        seasonal_spending.plot(kind='bar', ax=plt.gca(), color=['lightblue', 'salmon'])
        plt.title('Seasonal Spending Patterns', fontsize=14, fontweight='bold')
        plt.xlabel('Quarter')
        plt.ylabel('Average Expenses ($)')
        plt.legend(['Regular', 'Holiday Season'])
        plt.xticks(rotation=0)

        # 9. Forecast Example (if available)
        plt.subplot(3, 3, 9)
        if self.df['User'].nunique() > 0:
            sample_user = self.df['User'].iloc[0]
            forecast = self.forecast_future_expenses(sample_user, months_ahead=6)

            if forecast is not None:
                plt.plot(range(1, 7), forecast['Predicted_Expense'], marker='o', linewidth=2, markersize=8, color='blue', label='Predicted')
                plt.axhline(y=forecast['Budget'].iloc[0], color='red', linestyle='--', label='Budget')
                plt.title(f'6-Month Forecast - {sample_user}', fontsize=14, fontweight='bold')
                plt.xlabel('Months Ahead')
                plt.ylabel('Predicted Expenses ($)')
                plt.legend()
                plt.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

        # LSTM Training History (if available)
        if 'lstm' in self.predictions and 'history' in self.predictions['lstm']:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))

            history = self.predictions['lstm']['history']

            ax1.plot(history['loss'], label='Training Loss', color='blue')
            ax1.plot(history['val_loss'], label='Validation Loss', color='red')
            ax1.set_title('LSTM Model Loss', fontsize=14, fontweight='bold')
            ax1.set_xlabel('Epoch')
            ax1.set_ylabel('Loss')
            ax1.legend()
            ax1.grid(True, alpha=0.3)

            ax2.plot(history['mae'], label='Training MAE', color='blue')
            ax2.plot(history['val_mae'], label='Validation MAE', color='red')
            ax2.set_title('LSTM Model MAE', fontsize=14, fontweight='bold')
            ax2.set_xlabel('Epoch')
            ax2.set_ylabel('Mean Absolute Error')
            ax2.legend()
            ax2.grid(True, alpha=0.3)

            plt.tight_layout()
            plt.show()

    def generate_user_report(self, user):
        """Generate a comprehensive report for a specific user"""

        print(f"\n{'='*60}")
        print(f"BUDGETWISE AI REPORT - USER: {user}")
        print(f"{'='*60}")

        user_data = self.df[self.df['User'] == user].copy()
        if user_data.empty:
            print(f"No data found for user: {user}")
            return

        # Basic Statistics
        print(f"\n📊 SPENDING SUMMARY:")
        print(f"   • Average Monthly Budget: ${user_data['Monthly_Budget'].mean():.2f}")
        print(f"   • Average Monthly Expenses: ${user_data['Total_Expenses'].mean():.2f}")
        print(f"   • Budget Utilization: {user_data['Budget_Utilization'].mean():.1%}")
        print(f"   • Months Over Budget: {len(user_data[user_data['Total_Expenses'] > user_data['Monthly_Budget']])}/{len(user_data)}")

        # Category Breakdown
        print(f"\n🛍️ CATEGORY BREAKDOWN:")
        categories = ['Grocery_Ini1', 'Rent_Ini2', 'Transport_Ini3', 'InitialExpense', 'AmountOfProduct']
        category_names = ['Grocery', 'Rent', 'Transport', 'Initial', 'Products']

        for i, cat in enumerate(categories):
            avg_spend = user_data[cat].mean()
            percentage = avg_spend / user_data['Total_Expenses'].mean() * 100
            print(f"   • {category_names[i]}: ${avg_spend:.2f} ({percentage:.1f}%)")

        # Forecasts
        print(f"\n🔮 3-MONTH FORECAST:")
        forecast = self.forecast_future_expenses(user, months_ahead=3)
        if forecast is not None:
            for _, row in forecast.iterrows():
                month_name = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                             "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][int(row['Month'])]
                print(f"   • {month_name}: ${row['Predicted_Expense']:.2f} (Savings: ${row['Predicted_Savings']:.2f})")

        # Recommendations
        print(f"\n💡 PERSONALIZED RECOMMENDATIONS:")
        recommendations = self.generate_budget_recommendations(user)
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                priority_emoji = "🔴" if rec['priority'] == 'high' else "🟡"
                print(f"   {i}. {priority_emoji} {rec['message']}")
                if rec['savings_potential'] > 0:
                    print(f"      💰 Potential Annual Savings: ${rec['savings_potential']*12:.2f}")
        else:
            print("   ✅ Your spending patterns look healthy!")

        total_savings_potential = sum([rec['savings_potential'] for rec in recommendations])
        if total_savings_potential > 0:
            print(f"\n💰 TOTAL POTENTIAL ANNUAL SAVINGS: ${total_savings_potential*12:.2f}")

# Example Usage
if __name__ == "__main__":
    # Initialize BudgetWise
    budgetwise = BudgetWiseForecaster()

    # Load and preprocess data
    budgetwise.load_and_preprocess_data("DatasetFinalCSV.csv")

    # Train all models
    budgetwise.train_models()

    # Evaluate models
    results = budgetwise.evaluate_models()

    # Create visualizations
    budgetwise.create_dashboard_visualizations()

    # Generate user reports
    for user in budgetwise.df['User'].unique():
        budgetwise.generate_user_report(user)
