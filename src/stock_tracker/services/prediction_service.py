import logging
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split
from typing import Optional, Tuple, Dict, Any

# Attempt to import TechnicalAnalysis, handle if not found for standalone testing
try:
    from src.stock_tracker.utils.technical_analysis import TechnicalAnalysis
except ImportError:
    # Mock TechnicalAnalysis if not found (e.g. running file standalone without full project structure)
    class TechnicalAnalysis:
        @staticmethod
        def analyze_stock(data: pd.DataFrame) -> Dict[str, pd.Series]:
            # Return a dictionary of empty series or series with NaNs of the same index as data
            # This allows the rest of the code to run without the actual TA library for basic tests
            mock_ta_output = {}
            indicators = ['SMA_10', 'SMA_30', 'EMA_10', 'EMA_30', 'RSI', 'MACD_line', 'MACD_signal', 'BB_upper', 'BB_middle', 'BB_lower']
            for indicator in indicators:
                mock_ta_output[indicator] = pd.Series(np.nan, index=data.index)
            # Add some simple MAs that were used before as a fallback for the mock
            mock_ta_output['MA_10'] = data['Close'].rolling(window=10).mean()
            mock_ta_output['MA_50'] = data['Close'].rolling(window=50).mean()
            return mock_ta_output

class PredictionService:
    def __init__(self, model_type: str, prediction_days: int):
        self.model_type = model_type
        self.prediction_days = prediction_days
        self.logger = logging.getLogger(__name__)
        self.model = None
        self.feature_names = [] # Store feature names for consistent ordering
        self.supported_models = ["Random Forest", "Linear Regression", "Gradient Boosting Regressor"]

        if self.model_type not in self.supported_models:
            self.logger.warning(f"Model type '{self.model_type}' is not explicitly supported. Behavior might be undefined.")


    def _create_features_for_prediction(self, hist_data: pd.DataFrame) -> tuple[Optional[pd.DataFrame], Optional[pd.Series]]:
        """
        Creates enhanced features and targets for prediction from historical stock data.
        Uses TechnicalAnalysis class and other common features.
        """
        self.logger.info(f"Creating enhanced features for {self.model_type}")

        if not all(col in hist_data.columns for col in ['Open', 'High', 'Low', 'Close', 'Volume']):
            self.logger.error("Historical data must contain 'Open', 'High', 'Low', 'Close', 'Volume' columns.")
            return None, None

        data = hist_data.copy()

        # 1. Calculate Technical Indicators using TechnicalAnalysis
        try:
            ta_indicators_dict = TechnicalAnalysis.analyze_stock(data)
            ta_indicators_df = pd.DataFrame(ta_indicators_dict)
            # Merge TA indicators. Ensure index alignment.
            data = data.merge(ta_indicators_df, left_index=True, right_index=True, how='left')
        except Exception as e:
            self.logger.error(f"Error during technical analysis calculation: {e}", exc_info=True)
            # Continue without TA features if there's an error, or return None, None
            # For now, let's log and continue, features will be NaN and then dropped.

        # 2. Add other features
        data['Prev_Close'] = data['Close'].shift(1)
        data['Price_Change'] = data['Close'].diff()
        data['Volume_Change'] = data['Volume'].diff()
        data['Open_Close_Diff'] = data['Open'] - data['Close']
        data['High_Low_Diff'] = data['High'] - data['Low']

        for i in range(1, 4): # Lag features for 'Close'
            data[f'Close_Lag_{i}'] = data['Close'].shift(i)

        # 3. Define target variable
        data['Target'] = data['Close'].shift(-1) # Predict next day's close

        # 4. Handle NaNs
        data.dropna(inplace=True)

        if data.empty:
            self.logger.warning("Data is empty after feature engineering and NaN removal.")
            return None, None

        # 5. Select features (X) and target (y)
        features_to_exclude = ['Target']
        X = data.drop(columns=features_to_exclude)
        y = data['Target']

        self.feature_names = X.columns.tolist()

        if X.empty or y.empty:
            self.logger.warning("Feature set (X) or target (y) is empty after processing.")
            return None, None

        return X, y

    def _get_historical_lags(self, hist_data_for_lags: pd.DataFrame, last_feature_date_index) -> tuple:
        """Helper to get lag values from historical data for the iterative prediction's start."""
        c_t = hist_data_for_lags.loc[last_feature_date_index, 'Close']
        c_t_minus_1 = hist_data_for_lags['Close'].shift(1).loc[last_feature_date_index]
        c_t_minus_2 = hist_data_for_lags['Close'].shift(2).loc[last_feature_date_index]
        return c_t, c_t_minus_1, c_t_minus_2

    def train_and_predict(self, hist_data: pd.DataFrame) -> tuple[Optional[np.ndarray], Optional[float], Optional[float]]:
        self.logger.info(f"Starting train_and_predict for model type: {self.model_type}")

        if hist_data.empty:
            self.logger.warning("Historical data is empty. Cannot train model.")
            return None, None, None

        original_hist_data_for_lags = hist_data.copy() # Used for fetching actual values for initial lags

        if not isinstance(hist_data.index, pd.DatetimeIndex):
            if 'Date' in hist_data.columns:
                try:
                    hist_data = hist_data.set_index(pd.to_datetime(hist_data['Date']))
                    original_hist_data_for_lags = original_hist_data_for_lags.set_index(pd.to_datetime(original_hist_data_for_lags['Date']))
                except Exception as e:
                    self.logger.error(f"Failed to set Date index: {e}")
            # else: self.logger.warning("No 'Date' column to set as index...")


        future_predictions_array: Optional[np.ndarray] = None
        mae: Optional[float] = None
        rmse: Optional[float] = None
        X: Optional[pd.DataFrame] = None
        y: Optional[pd.Series] = None

        try:
            if self.model_type == "Random Forest" or self.model_type == "Gradient Boosting Regressor":
                self.logger.info(f"Processing {self.model_type} model with enhanced features.")

                X, y = self._create_features_for_prediction(hist_data.copy())

                if X is None or y is None or X.empty or y.empty:
                    self.logger.warning(f"Feature creation failed or resulted in empty data for {self.model_type}.")
                    return None, None, None

                if len(X) < 2:
                    self.logger.warning(f"Not enough data ({len(X)} samples) for training {self.model_type} after feature engineering.")
                    return None, None, None

                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, shuffle=False)

                if X_train.empty or X_test.empty:
                    self.logger.warning(f"Training or testing set is empty for {self.model_type}.")
                    return None, None, None

                if self.model_type == "Random Forest":
                    self.model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1, max_depth=10, min_samples_split=5)
                elif self.model_type == "Gradient Boosting Regressor":
                    self.model = GradientBoostingRegressor(n_estimators=100, random_state=42, learning_rate=0.1, max_depth=3)

                self.model.fit(X_train, y_train)

                predictions = self.model.predict(X_test)
                mae = mean_absolute_error(y_test, predictions)
                rmse = np.sqrt(mean_squared_error(y_test, predictions))
                self.logger.info(f"{self.model_type} Test MAE: {mae:.2f}, RMSE: {rmse:.2f}")

                if not X.empty:
                    current_prediction_features_df = X.iloc[-1:].copy()
                    future_predictions_list = []

                    last_feature_date_index = X.index[-1]
                    # Use original_hist_data_for_lags as it's not processed by _create_features_for_prediction
                    c_t, c_t_minus_1, c_t_minus_2 = self._get_historical_lags(original_hist_data_for_lags, last_feature_date_index)

                    val_prev_close = c_t
                    val_lag1 = c_t
                    val_lag2 = c_t_minus_1
                    val_lag3 = c_t_minus_2

                    for _ in range(self.prediction_days):
                        current_prediction_features_df['Prev_Close'] = val_prev_close
                        current_prediction_features_df['Close_Lag_1'] = val_lag1
                        current_prediction_features_df['Close_Lag_2'] = val_lag2
                        current_prediction_features_df['Close_Lag_3'] = val_lag3

                        # Ensure correct feature order for prediction
                        next_pred = self.model.predict(current_prediction_features_df[self.feature_names])[0]
                        future_predictions_list.append(next_pred)

                        val_lag3 = val_lag2
                        val_lag2 = val_lag1
                        val_lag1 = val_prev_close # current val_prev_close was the actual or predicted close of the prior step
                        val_prev_close = next_pred # new prev_close is the current prediction

                    future_predictions_array = np.array(future_predictions_list)


            elif self.model_type == "Linear Regression":
                self.logger.info("Processing Linear Regression model.")
                data_lr = hist_data.copy()

                if 'Close' not in data_lr.columns:
                     self.logger.error("LR: 'Close' column missing.")
                     return None, None, None

                if isinstance(data_lr.index, pd.DatetimeIndex):
                    data_lr.reset_index(inplace=True)

                X_lr = np.array(range(len(data_lr))).reshape(-1, 1)
                y_lr = data_lr['Close'].values

                if len(X_lr) < 2:
                    self.logger.warning(f"Not enough data ({len(X_lr)} samples) for Linear Regression.")
                    return None, None, None

                X_train_lr, X_test_lr, y_train_lr, y_test_lr = train_test_split(X_lr, y_lr, test_size=0.2, random_state=42, shuffle=False)

                if X_train_lr.shape[0] == 0 or X_test_lr.shape[0] == 0 :
                    self.logger.warning("Training or testing set is empty for Linear Regression.")
                    return None, None, None

                self.model = LinearRegression()
                self.model.fit(X_train_lr, y_train_lr)

                predictions_lr = self.model.predict(X_test_lr)
                mae = mean_absolute_error(y_test_lr, predictions_lr)
                rmse = np.sqrt(mean_squared_error(y_test_lr, predictions_lr))
                self.logger.info(f"Linear Regression Test MAE: {mae:.2f}, RMSE: {rmse:.2f}")

                last_index_lr = X_lr[-1][0]
                future_indices_lr = np.array(range(last_index_lr + 1, last_index_lr + 1 + self.prediction_days)).reshape(-1, 1)
                future_predictions_array = self.model.predict(future_indices_lr)

            else:
                self.logger.error(f"Unsupported model type: {self.model_type}")
                return None, None, None

            self.logger.info(f"Successfully trained model {self.model_type} and made predictions.")

        except Exception as e:
            self.logger.error(f"Error during model training or prediction for {self.model_type}: {e}", exc_info=True)
            return None, None, None

        return future_predictions_array, mae, rmse

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    main_logger = logging.getLogger(__name__)

    num_days = 150
    start_date = pd.to_datetime('2023-01-01')
    dates = pd.date_range(start_date, periods=num_days, freq='B')

    data_main = pd.DataFrame({
        'Open': np.random.rand(num_days) * 100 + 100,
        'High': np.random.rand(num_days) * 100 + 110,
        'Low': np.random.rand(num_days) * 100 + 90,
        'Close': np.random.rand(num_days) * 100 + 100,
        'Volume': np.random.rand(num_days) * 1000000 + 50000
    }, index=dates)
    data_main.index.name = 'Date'

    main_logger.info(f"Initial dummy data created with {len(data_main)} points.")

    # Test Random Forest
    rf_service = PredictionService(model_type="Random Forest", prediction_days=5)
    main_logger.info(f"\n--- Testing Random Forest ({len(data_main)} data points) ---")
    rf_data_input = data_main.copy()
    rf_future_preds, rf_mae, rf_rmse = rf_service.train_and_predict(rf_data_input)
    if rf_future_preds is not None:
        main_logger.info(f"Random Forest - Future Predictions: {rf_future_preds}")
        main_logger.info(f"Random Forest - MAE: {rf_mae:.4f}, RMSE: {rf_rmse:.4f}")
    else:
        main_logger.warning("Random Forest prediction failed.")

    # Test Gradient Boosting Regressor
    gb_service = PredictionService(model_type="Gradient Boosting Regressor", prediction_days=5)
    main_logger.info(f"\n--- Testing Gradient Boosting Regressor ({len(data_main)} data points) ---")
    gb_data_input = data_main.copy()
    gb_future_preds, gb_mae, gb_rmse = gb_service.train_and_predict(gb_data_input)
    if gb_future_preds is not None:
        main_logger.info(f"Gradient Boosting - Future Predictions: {gb_future_preds}")
        main_logger.info(f"Gradient Boosting - MAE: {gb_mae:.4f}, RMSE: {gb_rmse:.4f}")
    else:
        main_logger.warning("Gradient Boosting prediction failed.")

    # Test Linear Regression
    lr_service = PredictionService(model_type="Linear Regression", prediction_days=5)
    main_logger.info(f"\n--- Testing Linear Regression ({len(data_main)} data points) ---")
    lr_data_input = data_main.copy()
    lr_future_preds, lr_mae, lr_rmse = lr_service.train_and_predict(lr_data_input)
    if lr_future_preds is not None:
        main_logger.info(f"Linear Regression - Future Predictions: {lr_future_preds}")
        main_logger.info(f"Linear Regression - MAE: {lr_mae:.4f}, RMSE: {lr_rmse:.4f}")
    else:
        main_logger.warning("Linear Regression prediction failed.")

    # Test _create_features_for_prediction directly
    main_logger.info("\n--- Directly testing _create_features_for_prediction ---")
    test_service_features = PredictionService("TestFeatures", 1) # Model type here is just for logging in _create_features
    feature_test_data = data_main.head(60).copy() # Need enough for TA and lags
    main_logger.info(f"Feature test data input head:\n{feature_test_data.head()}")
    X_feat, y_feat = test_service_features._create_features_for_prediction(feature_test_data)
    if X_feat is not None and y_feat is not None:
        main_logger.info(f"Features created: X shape {X_feat.shape}, y shape {y_feat.shape}")
        if not X_feat.empty:
            main_logger.info(f"Feature names: {X_feat.columns.tolist()}")
            main_logger.info(f"First feature row (X.iloc[0]):\n{X_feat.iloc[0]}")
            main_logger.info(f"First target (y.iloc[0]): {y_feat.iloc[0]}")
    else:
        main_logger.warning("_create_features_for_prediction returned None or empty data.")

    # Test with insufficient data for feature creation
    insufficient_data = data_main.head(10).copy() # Too small for many TAs and lags + dropna
    main_logger.info(f"\n--- Testing _create_features_for_prediction with insufficient data ({len(insufficient_data)} points) ---")
    X_insufficient, y_insufficient = test_service_features._create_features_for_prediction(insufficient_data)
    if X_insufficient is None or X_insufficient.empty:
        main_logger.info("_create_features_for_prediction correctly handled insufficient data by returning None or empty DataFrame.")
    else:
        main_logger.warning(f"_create_features_for_prediction processed insufficient data unexpectedly: X shape {X_insufficient.shape}")

    # Test GB with very small data
    very_small_data_gb = data_main.head(40).copy()
    gb_service_small = PredictionService(model_type="Gradient Boosting Regressor", prediction_days=3)
    main_logger.info(f"\n--- Testing Gradient Boosting with {len(very_small_data_gb)} data points (very small data) ---")
    gb_future_preds_s, _, _ = gb_service_small.train_and_predict(very_small_data_gb)
    if gb_future_preds_s is None:
        main_logger.info("Gradient Boosting correctly returned None for very small data that becomes empty after featurization.")
    else:
        main_logger.info(f"Gradient Boosting (small data) predictions: {gb_future_preds_s}")
```
