import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
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

from config.settings import ML_CONFIG

def train_linear_regression(X_train, y_train) -> object:
    model = LinearRegression()
    model.fit(X_train, y_train)
    return model

def train_random_forest(X_train, y_train) -> object:
    model = RandomForestRegressor(
        n_estimators=ML_CONFIG.get("random_forest_n_estimators", 100),
        random_state=ML_CONFIG.get("random_forest_random_state", 42)
    )
    model.fit(X_train, y_train)
    return model

def train_lstm(X_train, y_train, input_shape) -> object:
    if not HAS_TENSORFLOW:
        print("  ⚠ TensorFlow not installed — skipping LSTM training")
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
        
    return {
        "model_name": model_name,
        "mae": mean_absolute_error(y_test, predictions),
        "rmse": np.sqrt(mean_squared_error(y_test, predictions)),
        "r2": r2_score(y_test, predictions),
        "predictions": predictions
    }

def compare_models(results: list[dict]) -> pd.DataFrame:
    display_keys = {'model_name', 'mae', 'rmse', 'r2'}
    rows = [{k: v for k, v in r.items() if k in display_keys} for r in results]
    df = pd.DataFrame(rows)
    if 'model_name' in df.columns:
        df = df.rename(columns={'model_name': 'Model', 'mae': 'MAE', 'rmse': 'RMSE', 'r2': 'R2'})
    return df.sort_values('MAE').reset_index(drop=True) if 'MAE' in df.columns else df

def select_best_model(results: list[dict]) -> dict:
    return min(results, key=lambda x: x['mae'])

def save_model(model, scaler, model_name: str, path=None) -> str:
    save_dir = Path(path) if path else Path.cwd()
    save_dir.mkdir(parents=True, exist_ok=True)
    
    scaler_path = save_dir / f"{model_name}_scaler.pkl"
    joblib.dump(scaler, scaler_path)
    
    if 'lstm' in model_name.lower():
        model_path = save_dir / f"{model_name}.h5"
        model.save(model_path)
    else:
        model_path = save_dir / f"{model_name}.pkl"
        joblib.dump(model, model_path)
        
    return str(save_dir)

def load_model(model_name: str, path=None) -> tuple:
    load_dir = Path(path) if path else Path.cwd()
    
    scaler = joblib.load(load_dir / f"{model_name}_scaler.pkl")
    
    if 'lstm' in model_name.lower():
        model = keras_load_model(load_dir / f"{model_name}.h5")
    else:
        model = joblib.load(load_dir / f"{model_name}.pkl")
        
    return model, scaler

def predict_next_month(model, scaler, latest_features: pd.DataFrame) -> float:
    # Ensure correct shape
    scaled_features = scaler.transform(latest_features)
    # Check if LSTM
    if len(scaled_features.shape) == 2 and 'lstm' in str(type(model)).lower():
        # reshape for lstm
        scaled_features = scaled_features.reshape(1, scaled_features.shape[0], scaled_features.shape[1])
        
    pred = model.predict(scaled_features)
    return float(pred[0]) if isinstance(pred, (list, np.ndarray)) else float(pred)

def train_and_evaluate_all(X_train, X_test, y_train, y_test, X_lstm_train=None, X_lstm_test=None, y_lstm_train=None, y_lstm_test=None) -> dict:
    print("Training ML Models...")
    scaler = MinMaxScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    model_results = []
    
    # Linear Regression
    lr = train_linear_regression(X_train_scaled, y_train)
    lr_result = evaluate_model(lr, X_test_scaled, y_test, 'Linear_Regression')
    lr_result['model'] = lr
    lr_result['scaler'] = scaler
    lr_result['y_test'] = y_test.values if hasattr(y_test, 'values') else y_test
    model_results.append(lr_result)
    
    # Random Forest
    rf = train_random_forest(X_train_scaled, y_train)
    rf_result = evaluate_model(rf, X_test_scaled, y_test, 'Random_Forest')
    rf_result['model'] = rf
    rf_result['scaler'] = scaler
    rf_result['y_test'] = y_test.values if hasattr(y_test, 'values') else y_test
    model_results.append(rf_result)
    
    # LSTM (optional — requires TensorFlow)
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
                
                lstm_res = {
                    "model_name": "LSTM",
                    "mae": mean_absolute_error(y_lstm_test, preds),
                    "rmse": np.sqrt(mean_squared_error(y_lstm_test, preds)),
                    "r2": r2_score(y_lstm_test, preds),
                    "predictions": preds,
                    "model": lstm,
                    "scaler": lstm_scaler_x,
                    "y_test": y_lstm_test
                }
                model_results.append(lstm_res)
        except Exception as e:
            print(f"  LSTM training skipped: {e}")
    elif not HAS_TENSORFLOW:
        print("  ℹ TensorFlow not installed — LSTM skipped (RF and LR will be used)")
        
    comparison_df = compare_models(model_results)
    best = select_best_model(model_results)
    
    return {
        "model_results": model_results,
        "best_model": best,
        "comparison_df": comparison_df,
        "scaler": scaler
    }

