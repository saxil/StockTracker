import unittest
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta

# Ensure src is in path for tests if running from root or tests directory
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.stock_tracker.services.prediction_service import PredictionService
# TechnicalAnalysis is imported within PredictionService, which has a mock fallback.

# Suppress most logging output during tests unless specifically testing logging
logging.basicConfig(level=logging.CRITICAL)


def create_sample_data(num_rows: int, start_date_str: str = '2023-01-01') -> pd.DataFrame:
    """Generates a DataFrame with 'Date' (as index), 'Open', 'High', 'Low', 'Close', 'Volume'."""
    start_date = pd.to_datetime(start_date_str)
    dates = pd.date_range(start_date, periods=num_rows, freq='B') # Business days
    data = pd.DataFrame({
        'Open': np.random.uniform(90, 110, size=num_rows),
        'High': np.random.uniform(100, 120, size=num_rows),
        'Low': np.random.uniform(80, 100, size=num_rows),
        'Close': np.random.uniform(95, 115, size=num_rows),
        'Volume': np.random.randint(100000, 1000000, size=num_rows)
    }, index=dates)
    # Ensure High is >= Open/Close and Low is <= Open/Close
    data['High'] = data[['High', 'Open', 'Close']].max(axis=1)
    data['Low'] = data[['Low', 'Open', 'Close']].min(axis=1)
    data.index.name = 'Date'
    return data

class TestPredictionService(unittest.TestCase):

    def setUp(self):
        # Create sample data that is generally sufficient for most tests
        self.sample_hist_data_large = create_sample_data(num_rows=200) # Enough for TA features and train/test split
        self.sample_hist_data_small = create_sample_data(num_rows=30)  # Potentially insufficient for some TA features after dropna
        self.sample_hist_data_tiny = create_sample_data(num_rows=5)   # Definitely insufficient

    def test_initialization(self):
        service_rf = PredictionService(model_type="Random Forest", prediction_days=10)
        self.assertEqual(service_rf.model_type, "Random Forest")
        self.assertEqual(service_rf.prediction_days, 10)
        self.assertIsNotNone(service_rf.logger)

        service_lr = PredictionService(model_type="Linear Regression", prediction_days=5)
        self.assertEqual(service_lr.model_type, "Linear Regression")
        self.assertEqual(service_lr.prediction_days, 5)

        service_gb = PredictionService(model_type="Gradient Boosting Regressor", prediction_days=7)
        self.assertEqual(service_gb.model_type, "Gradient Boosting Regressor")
        self.assertEqual(service_gb.prediction_days, 7)

        # Test unsupported model type (relies on internal warning, does not raise error by design)
        with self.assertLogs(level='WARNING') as log: # Check for logged warning
            service_unsupported = PredictionService(model_type="Unsupported Model", prediction_days=5)
            self.assertEqual(service_unsupported.model_type, "Unsupported Model")
        self.assertIn("Model type 'Unsupported Model' is not explicitly supported.", log.output[0])


    def test_create_features_for_prediction(self):
        service = PredictionService(model_type="Random Forest", prediction_days=5)
        # Use data that's reasonably long to avoid TA indicators being all NaN
        # _create_features_for_prediction drops NaNs, so X can be shorter than input
        data_for_features = create_sample_data(num_rows=100)

        X, y = service._create_features_for_prediction(data_for_features.copy())

        self.assertIsNotNone(X, "X should not be None")
        self.assertIsNotNone(y, "y should not be None")

        if X is not None and y is not None: # Proceed if X, y are not None
            self.assertFalse(X.empty, "X DataFrame should not be empty")
            self.assertFalse(y.empty, "y Series should not be empty")
            self.assertTrue(len(X) == len(y), "X and y should have the same length")

            # Check for NaNs in X (should be none after dropna)
            self.assertFalse(X.isnull().values.any(), "X should not contain NaN values")

            # Check if y is shifted 'Close' prices (Target = Close.shift(-1))
            # This means y.iloc[i] should correspond to data_for_features['Close'].iloc[X.index[i]+1_day_equivalent]
            # More simply, y is a Series of Close prices.
            self.assertTrue(pd.api.types.is_numeric_dtype(y), "Target y should be numeric.")

            # Check feature_names
            self.assertIsNotNone(service.feature_names, "feature_names should be populated")
            self.assertEqual(list(X.columns), service.feature_names, "X columns should match service.feature_names")
        else:
            self.fail("_create_features_for_prediction returned None for X or y with sufficient data.")

    def test_train_and_predict_random_forest(self):
        service = PredictionService(model_type="Random Forest", prediction_days=5)
        predictions, mae, rmse = service.train_and_predict(self.sample_hist_data_large.copy())

        self.assertIsNotNone(predictions, "RF: Predictions should not be None with sufficient data")
        if predictions is not None:
            self.assertIsInstance(predictions, np.ndarray, "RF: Predictions should be a NumPy array")
            self.assertEqual(len(predictions), 5, "RF: Predictions array length should match prediction_days")

        self.assertIsInstance(mae, (float, np.float64), "RF: MAE should be a float")
        self.assertIsInstance(rmse, (float, np.float64), "RF: RMSE should be a float")
        self.assertGreaterEqual(mae, 0, "RF: MAE should be non-negative")
        self.assertGreaterEqual(rmse, 0, "RF: RMSE should be non-negative")

    def test_train_and_predict_linear_regression(self):
        service = PredictionService(model_type="Linear Regression", prediction_days=10)
        # Linear regression can work with less data than RF/GBR due to simpler features
        predictions, mae, rmse = service.train_and_predict(self.sample_hist_data_large.copy())

        self.assertIsNotNone(predictions, "LR: Predictions should not be None")
        if predictions is not None:
            self.assertIsInstance(predictions, np.ndarray, "LR: Predictions should be a NumPy array")
            self.assertEqual(len(predictions), 10, "LR: Predictions array length should match prediction_days")

        self.assertIsInstance(mae, (float, np.float64), "LR: MAE should be a float")
        self.assertIsInstance(rmse, (float, np.float64), "LR: RMSE should be a float")

    def test_train_and_predict_gradient_boosting(self):
        service = PredictionService(model_type="Gradient Boosting Regressor", prediction_days=7)
        predictions, mae, rmse = service.train_and_predict(self.sample_hist_data_large.copy())

        self.assertIsNotNone(predictions, "GB: Predictions should not be None")
        if predictions is not None:
            self.assertIsInstance(predictions, np.ndarray, "GB: Predictions should be a NumPy array")
            self.assertEqual(len(predictions), 7, "GB: Predictions array length should match prediction_days")

        self.assertIsInstance(mae, (float, np.float64), "GB: MAE should be a float")
        self.assertIsInstance(rmse, (float, np.float64), "GB: RMSE should be a float")

    def test_insufficient_data_handling_for_tree_models(self):
        # Test Random Forest with insufficient data
        service_rf = PredictionService(model_type="Random Forest", prediction_days=5)
        predictions_rf, mae_rf, rmse_rf = service_rf.train_and_predict(self.sample_hist_data_small.copy()) # small data
        if predictions_rf is not None: # It might produce if small is still enough for some features
             self.assertIsInstance(predictions_rf, np.ndarray) # If it does, check type
        else: # Expect None if data truly becomes empty after features
            self.assertIsNone(predictions_rf, "RF (small data): Predictions should be None if data too small after features")
            self.assertIsNone(mae_rf, "RF (small data): MAE should be None")
            self.assertIsNone(rmse_rf, "RF (small data): RMSE should be None")

        predictions_rf_tiny, _, _ = service_rf.train_and_predict(self.sample_hist_data_tiny.copy()) # tiny data
        self.assertIsNone(predictions_rf_tiny, "RF (tiny data): Predictions should be None")


        # Test Gradient Boosting with insufficient data
        service_gb = PredictionService(model_type="Gradient Boosting Regressor", prediction_days=5)
        predictions_gb, mae_gb, rmse_gb = service_gb.train_and_predict(self.sample_hist_data_small.copy())
        if predictions_gb is not None:
             self.assertIsInstance(predictions_gb, np.ndarray)
        else:
            self.assertIsNone(predictions_gb, "GB (small data): Predictions should be None")
            self.assertIsNone(mae_gb, "GB (small data): MAE should be None")
            self.assertIsNone(rmse_gb, "GB (small data): RMSE should be None")

        predictions_gb_tiny, _, _ = service_gb.train_and_predict(self.sample_hist_data_tiny.copy())
        self.assertIsNone(predictions_gb_tiny, "GB (tiny data): Predictions should be None")


    def test_insufficient_data_handling_linear_regression(self):
        # Linear Regression has simpler features and might still run with very few points
        # The service has a general check for X length < 2.
        service_lr = PredictionService(model_type="Linear Regression", prediction_days=5)

        # Test with data that would result in X having fewer than 2 rows after split (if any split)
        # For LR, X is just an arange. So len(X) is len(hist_data).
        # train_test_split(shuffle=False) means test_size=0.2 of e.g. 5 rows is 1 row for test.
        # If len(X_lr) < 2, it returns None.
        # 2 samples are not enough for train_test_split to make non-empty train and test.
        # e.g. len=2, train=1, test=1. len=1, train=0, test=1.
        # Need at least 2 samples for X_train and X_test to be non-empty with test_size=0.2
        # if len(X)=1, X_train=0, X_test=1.
        # if len(X)=2, X_train=1, X_test=1.
        # if len(X)=3, X_train=2, X_test=1.
        # if len(X)=4, X_train=3, X_test=1.
        # The service checks `if X_train_lr.shape[0] == 0 or X_test_lr.shape[0] == 0:`

        data_lr_min = create_sample_data(num_rows=1) # Will cause empty train set
        predictions_lr_min, _, _ = service_lr.train_and_predict(data_lr_min.copy())
        self.assertIsNone(predictions_lr_min, "LR: Predictions should be None with 1 data point")

        data_lr_two = create_sample_data(num_rows=2) # Might also fail if test_size makes one empty
        predictions_lr_two, _, _ = service_lr.train_and_predict(data_lr_two.copy())
        # Depending on split exacts, this might be None or run.
        # With test_size=0.2, 2 rows -> train=1, test=1. Should run.
        self.assertIsNotNone(predictions_lr_two, "LR: Predictions should not be None with 2 data points")

        data_lr_sufficient = create_sample_data(num_rows=10) # Should be fine
        predictions_lr_suff, _, _ = service_lr.train_and_predict(data_lr_sufficient.copy())
        self.assertIsNotNone(predictions_lr_suff, "LR: Predictions should not be None with 10 data points")


if __name__ == '__main__':
    unittest.main()
```
