"""
FinSight AI — Machine Learning Forecasting Pipeline
Multi-model forecasting engine comparing Random Forest, Gradient Boosting,
Ridge Regularization, and Linear Regression with standard financial time-series metrics
(MAE, RMSE, MAPE, and Forecast Accuracy).
"""

import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

try:
    from tensorflow.keras.models import Sequential, load_model as keras_load_model
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.optimizers import Adam
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
    HAS_TENSORFLOW = True
except ImportError:
    HAS_TENSORFLOW = False

from config.settings import ML_CONFIG, MODELS_DIR


def train_linear_regression(X_train, y_train) -> object:
    model = LinearRegression()
    model.fit(X_train, y_train)
    return model


def train_ridge_regression(X_train, y_train, alpha: float = 10.0) -> object:
    model = Ridge(alpha=alpha, random_state=42)
    model.fit(X_train, y_train)
    return model


def train_random_forest(X_train, y_train) -> object:
    model = RandomForestRegressor(
        n_estimators=ML_CONFIG.get("random_forest_n_estimators", 100),
        max_depth=4,
        min_samples_split=2,
        random_state=ML_CONFIG.get("random_forest_random_state", 42)
    )
    model.fit(X_train, y_train)
    return model


def train_gradient_boosting(X_train, y_train) -> object:
    model = GradientBoostingRegressor(
        n_estimators=50,
        max_depth=3,
        learning_rate=0.05,
        random_state=42
    )
    model.fit(X_train, y_train)
    return model


def train_lstm(X_train, y_train, input_shape) -> object:
    if not HAS_TENSORFLOW:
        return None
    model = Sequential([
        LSTM(ML_CONFIG.get("lstm_units_layer1", 64), return_sequences=True, input_shape=input_shape),
        Dropout(ML_CONFIG.get("lstm_dropout", 0.2)),
        LSTM(ML_CONFIG.get("lstm_units_layer2", 32), return_sequences=False),
        Dropout(ML_CONFIG.get("lstm_dropout", 0.2)),
        Dense(16, activation='relu'),
        Dense(1)
    ])
    
    model.compile(
        optimizer=Adam(learning_rate=ML_CONFIG.get("lstm_learning_rate", 0.001)),
        loss='mse',
        metrics=['mae']
    )
    
    callbacks = [
        EarlyStopping(patience=ML_CONFIG.get("lstm_patience", 10), restore_best_weights=True),
        ReduceLROnPlateau(patience=5, factor=0.5)
    ]
    
    model.fit(
        X_train, y_train,
        epochs=ML_CONFIG.get("lstm_epochs", 50),
        batch_size=ML_CONFIG.get("lstm_batch_size", 16),
        validation_split=0.2,
        callbacks=callbacks,
        verbose=0
    )
    return model


def evaluate_model(model, X_test, y_test, model_name: str = '') -> dict:
    predictions = model.predict(X_test)
    if len(predictions.shape) > 1:
        predictions = predictions.flatten()
        
    y_true = np.array(y_test)
    mae = float(mean_absolute_error(y_true, predictions))
    rmse = float(np.sqrt(mean_squared_error(y_true, predictions)))
    
    # Financial Time-Series Metric: MAPE (Mean Absolute Percentage Error) & Accuracy
    nonzero = y_true != 0
    if np.any(nonzero):
        mape = float(np.mean(np.abs((y_true[nonzero] - predictions[nonzero]) / y_true[nonzero])) * 100)
    else:
        mape = 0.0
    accuracy = float(max(0.0, min(100.0, 100.0 - mape)))
    
    r2 = float(r2_score(y_true, predictions))
    
    return {
        "model_name": model_name,
        "mae": mae,
        "rmse": rmse,
        "mape": mape,
        "accuracy": accuracy,
        "r2": r2,
        "predictions": predictions
    }


def compare_models(results: list) -> pd.DataFrame:
    """Format model comparison with industry standard metrics."""
    rows = []
    for r in results:
        rows.append({
            'Model': r.get('model_name', '').replace('_', ' '),
            'Accuracy (%)': round(r.get('accuracy', 0.0), 1),
            'MAE': round(r.get('mae', 0.0), 0),
            'RMSE': round(r.get('rmse', 0.0), 0),
            'MAPE (%)': round(r.get('mape', 0.0), 1),
            'R2': round(r.get('r2', 0.0), 3)
        })
    df = pd.DataFrame(rows)
    return df.sort_values('Accuracy (%)', ascending=False).reset_index(drop=True)


def select_best_model(results: list) -> dict:
    """Select best model primarily by highest Accuracy (lowest MAPE)."""
    return max(results, key=lambda x: x.get('accuracy', 0.0))


def save_model(model, scaler, model_name: str, path=None) -> str:
    save_dir = Path(path) if path else MODELS_DIR
    save_dir.mkdir(parents=True, exist_ok=True)
    
    scaler_path = save_dir / f"{model_name}_scaler.pkl"
    joblib.dump(scaler, scaler_path)
    
    if 'lstm' in model_name.lower() and HAS_TENSORFLOW:
        model_path = save_dir / f"{model_name}.h5"
        model.save(model_path)
    else:
        model_path = save_dir / f"{model_name}.pkl"
        joblib.dump(model, model_path)
        
    return str(save_dir)


def load_model(model_name: str, path=None) -> tuple:
    load_dir = Path(path) if path else MODELS_DIR
    scaler = joblib.load(load_dir / f"{model_name}_scaler.pkl")
    
    if 'lstm' in model_name.lower() and HAS_TENSORFLOW:
        model = keras_load_model(load_dir / f"{model_name}.h5")
    else:
        model = joblib.load(load_dir / f"{model_name}.pkl")
        
    return model, scaler


def predict_next_month(model, scaler, latest_features: pd.DataFrame) -> float:
    scaled_features = scaler.transform(latest_features)
    if len(scaled_features.shape) == 2 and 'lstm' in str(type(model)).lower():
        scaled_features = scaled_features.reshape(1, scaled_features.shape[0], scaled_features.shape[1])
        
    pred = model.predict(scaled_features)
    return float(pred[0]) if isinstance(pred, (list, np.ndarray)) else float(pred)


def train_and_evaluate_all(X_train, X_test, y_train, y_test, X_lstm_train=None, X_lstm_test=None, y_lstm_train=None, y_lstm_test=None) -> dict:
    scaler = MinMaxScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    model_results = []
    
    # 1. Random Forest Regressor
    rf = train_random_forest(X_train_scaled, y_train)
    rf_result = evaluate_model(rf, X_test_scaled, y_test, 'Random Forest')
    rf_result['model'] = rf
    rf_result['scaler'] = scaler
    rf_result['y_test'] = y_test.values if hasattr(y_test, 'values') else y_test
    model_results.append(rf_result)
    
    # 2. Gradient Boosting Regressor
    gb = train_gradient_boosting(X_train_scaled, y_train)
    gb_result = evaluate_model(gb, X_test_scaled, y_test, 'Gradient Boosting')
    gb_result['model'] = gb
    gb_result['scaler'] = scaler
    gb_result['y_test'] = y_test.values if hasattr(y_test, 'values') else y_test
    model_results.append(gb_result)

    # 3. Ridge Regression (L2 Regularization)
    ridge = train_ridge_regression(X_train_scaled, y_train)
    ridge_result = evaluate_model(ridge, X_test_scaled, y_test, 'Ridge Regression')
    ridge_result['model'] = ridge
    ridge_result['scaler'] = scaler
    ridge_result['y_test'] = y_test.values if hasattr(y_test, 'values') else y_test
    model_results.append(ridge_result)

    # 4. Standard Linear Regression
    lr = train_linear_regression(X_train_scaled, y_train)
    lr_result = evaluate_model(lr, X_test_scaled, y_test, 'Linear Regression')
    lr_result['model'] = lr
    lr_result['scaler'] = scaler
    lr_result['y_test'] = y_test.values if hasattr(y_test, 'values') else y_test
    model_results.append(lr_result)
    
    # 5. LSTM (if TensorFlow installed)
    if X_lstm_train is not None and len(X_lstm_train) > 0 and HAS_TENSORFLOW:
        try:
            lstm_scaler_x = MinMaxScaler()
            lstm_scaler_y = MinMaxScaler()
            orig_shape_train = X_lstm_train.shape
            orig_shape_test = X_lstm_test.shape
            
            X_lstm_train_scaled = lstm_scaler_x.fit_transform(X_lstm_train.reshape(-1, orig_shape_train[-1])).reshape(orig_shape_train)
            X_lstm_test_scaled = lstm_scaler_x.transform(X_lstm_test.reshape(-1, orig_shape_test[-1])).reshape(orig_shape_test)
            y_lstm_train_scaled = lstm_scaler_y.fit_transform(y_lstm_train.reshape(-1, 1))
            
            lstm = train_lstm(X_lstm_train_scaled, y_lstm_train_scaled, (orig_shape_train[1], orig_shape_train[2]))
            if lstm is not None:
                preds_scaled = lstm.predict(X_lstm_test_scaled)
                preds = lstm_scaler_y.inverse_transform(preds_scaled).flatten()
                lstm_res = evaluate_model(lstm, X_lstm_test_scaled, y_lstm_test, 'LSTM')
                lstm_res['predictions'] = preds
                lstm_res['model'] = lstm
                lstm_res['scaler'] = lstm_scaler_x
                lstm_res['y_test'] = y_lstm_test
                model_results.append(lstm_res)
        except Exception as e:
            print(f"  LSTM training skipped: {e}")
    elif not HAS_TENSORFLOW:
        print("  [INFO] TensorFlow not installed - LSTM skipped (RF, GB, Ridge, LR active)")
        
    comparison_df = compare_models(model_results)
    best = select_best_model(model_results)
    
    # Auto-cache best model to models/
    try:
        save_model(best['model'], scaler, "best_model", MODELS_DIR)
    except Exception:
        pass
        
    return {
        "model_results": model_results,
        "best_model": best,
        "comparison_df": comparison_df,
        "scaler": scaler
    }
