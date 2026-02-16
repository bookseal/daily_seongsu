import os
import pandas as pd
import numpy as np

# Mocking paths
base_dir = "/home/ubuntu/workspace/daily_seongsu"
data_path = os.path.join(base_dir, "data_features_level2.csv")

try:
    print("--- Step 4.1: Data Prep ---")
    if not os.path.exists(data_path):
        print("❌ Feature file not found. Please complete Level 2 first.")
    else:
        df = pd.read_csv(data_path)
        print(f"✅ Loaded {len(df)} rows")
        
        # Check required columns
        required = ['total_traffic', 'lag_1d', 'lag_7d']
        missing = [c for c in required if c not in df.columns]
        if missing:
            print(f"⚠️ Missing columns: {missing}")
        else:
            print("Columns OK")
            
        # Time-series split (last 20% for test)
        split_idx = int(len(df) * 0.8)
        train_df = df.iloc[:split_idx]
        test_df = df.iloc[split_idx:]
        
        print(f"Train/Test Split: {len(train_df)}/{len(test_df)}")
        train_df.to_csv(os.path.join(base_dir, "train_data.csv"), index=False)
        test_df.to_csv(os.path.join(base_dir, "test_data.csv"), index=False)
        print("Files saved.")

    print("\n--- Step 4.2: Model Comparison ---")
    train_path = os.path.join(base_dir, "train_data.csv")
    test_path = os.path.join(base_dir, "test_data.csv")
    
    if not os.path.exists(train_path):
        print("Error: Train data missing")
    else:
        train_df = pd.read_csv(train_path)
        test_df = pd.read_csv(test_path)
        
        # Fix: rolling_7d_avg vs rolling_7d_mean check
        feature_cols = ['lag_1d', 'lag_7d', 'rolling_7d_avg']
        # Check if 'rolling_7d_avg' exists, maybe it is 'rolling_7d_mean'
        if 'rolling_7d_avg' not in train_df.columns and 'rolling_7d_mean' in train_df.columns:
            feature_cols = ['lag_1d', 'lag_7d', 'rolling_7d_mean']
            print("Using rolling_7d_mean instead of avg")
            
        valid_features = [c for c in feature_cols if c in train_df.columns]
        print(f"Using features: {valid_features}")
        
        target_col = 'total_traffic' if 'total_traffic' in train_df.columns else 'traffic'
        
        X_train = train_df[valid_features].fillna(0)
        y_train = train_df[target_col].fillna(0)
        X_test = test_df[valid_features].fillna(0)
        y_test = test_df[target_col].fillna(0)
        
        from sklearn.linear_model import LinearRegression
        from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
        from sklearn.metrics import mean_squared_error
        
        models = {
            "Linear Regression": LinearRegression(),
            "Random Forest": RandomForestRegressor(n_estimators=10, max_depth=5, random_state=42), # Reduced for speed
            "Gradient Boosting": GradientBoostingRegressor(n_estimators=10, max_depth=3, random_state=42)
        }
        
        results = []
        for name, model in models.items():
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            print(f"{name}: RMSE={rmse:.2f}")
            results.append({"Model": name, "RMSE_Val": rmse})
            
        best_model_name = min(results, key=lambda x: x["RMSE_Val"])["Model"]
        with open(os.path.join(base_dir, "best_model_name.txt"), "w") as f:
            f.write(best_model_name)
        print(f"✅ Best Model: {best_model_name}")

    print("\n--- Step 4.3: Hyperparameter Tuning ---")
    if not os.path.exists(train_path):
         print("Error: Train data missing for tuning")
    else:
        from sklearn.model_selection import GridSearchCV
        
        # Reduced grid for speed
        param_grid = {
            'n_estimators': [10, 20],
            'max_depth': [3, 5]
        }
        
        print("Starting Grid Search...")
        grid_search = GridSearchCV(
            RandomForestRegressor(random_state=42),
            param_grid,
            cv=2,
            scoring='neg_mean_squared_error',
            n_jobs=-1
        )
        
        grid_search.fit(X_train, y_train)
        print(f"✅ Best Params: {grid_search.best_params_}")
        
except Exception:
    import traceback
    traceback.print_exc()
