import gradio as gr
import pandas as pd
import numpy as np
import os

def create_automl_tab():
    """Level 4: AutoML - Steps 4.1, 4.2, 4.3"""
    
    # Step Overview Table
    gr.Markdown("""
    > **Goal**: Automatically train, evaluate, and tune multiple ML models to find the best predictor for Seongsu Station traffic.
    
    | Step | Description | Status |
    |------|-------------|--------|
    | 4.1 | Data Preparation & Train/Test Split | ✅ |
    | 4.2 | Model Comparison (Linear, GBM, RandomForest) | ✅ |
    | 4.3 | Hyperparameter Tuning (Best Model) | ✅ |
    """)
    
    gr.HTML('<hr style="border: none; border-top: 1px solid #4b5563; margin: 24px 0;">')
    
    # ============================================
    # STEP 4.1: Data Preparation
    # ============================================
    gr.Markdown("### Step 4.1: Data Preparation & Train/Test Split")
    gr.Markdown("🔧 **Splitting data into training (80%) and testing (20%) sets**")
    

    gr.Markdown("""
    **Overfitting Prevention**: If we evaluate the model on the same data it was trained on, it will **memorize** rather than **learn patterns**.
    
    **Real-World Simulation**: The test set simulates "future unseen data" to measure how well the model generalizes.
    
    **Standard Split**: 80% training, 20% testing (for time-series, we use the latest 20% as test).
    """)
    
    btn_prepare = gr.Button("📦 Load & Split Data", variant="secondary")
    with gr.Row():
        data_stats = gr.Textbox(label="Dataset Statistics", lines=5)
        split_preview = gr.Dataframe(label="Sample (First 5 rows)", height=200)
    
    def prepare_data():
        logs = []
        base_dir = "/home/ubuntu/workspace/daily_seongsu"
        data_path = os.path.join(base_dir, "data_features_level2.csv")
        
        if not os.path.exists(data_path):
            return "❌ Feature file not found. Please complete Level 2 first.", pd.DataFrame()
        
        df = pd.read_csv(data_path)
        logs.append(f"✅ Loaded {len(df)} rows, {len(df.columns)} columns")
        
        # Check required columns
        required = ['total_traffic', 'lag_1d', 'lag_7d']
        missing = [c for c in required if c not in df.columns]
        if missing:
            logs.append(f"⚠️ Missing columns: {missing}")
            logs.append(f"Available: {list(df.columns)}")
        
        # Time-series split (last 20% for test)
        split_idx = int(len(df) * 0.8)
        train_df = df.iloc[:split_idx]
        test_df = df.iloc[split_idx:]
        
        logs.append(f"\n📊 Train Set: {len(train_df)} rows")
        logs.append(f"📊 Test Set: {len(test_df)} rows")
        logs.append(f"📅 Train Date Range: {train_df['date'].min()} ~ {train_df['date'].max()}")
        logs.append(f"📅 Test Date Range: {test_df['date'].min()} ~ {test_df['date'].max()}")
        
        # Save to global state (in a real app, use gr.State)
        train_df.to_csv(os.path.join(base_dir, "train_data.csv"), index=False)
        test_df.to_csv(os.path.join(base_dir, "test_data.csv"), index=False)
        
        return "\n".join(logs), df.head()
    
    btn_prepare.click(fn=prepare_data, inputs=[], outputs=[data_stats, split_preview])
    
    # ============================================
    # STEP 4.2: Model Comparison
    # ============================================
    gr.HTML('<hr style="border: none; border-top: 1px solid #4b5563; margin: 48px 0;">')
    gr.Markdown("### Step 4.2: Model Comparison")
    gr.Markdown("🏆 **Train 3 Models and Compare Performance**")
    

    gr.Markdown("""
    We test 3 algorithms:
    1. **Linear Regression**: Simple baseline (assumes linear relationship)
    2. **Random Forest**: Ensemble of decision trees (handles non-linearity)
    3. **Gradient Boosting (LightGBM)**: State-of-the-art for tabular data
    
    **Evaluation Metric**: RMSE (Root Mean Squared Error) - lower is better.
    """)
    
    btn_compare = gr.Button("🚀 Train & Compare Models", variant="primary")
    with gr.Row():
        model_results = gr.Dataframe(label="Model Comparison Results", height=200)
        comparison_chart = gr.Plot(label="RMSE Comparison")
    
    def train_and_compare():
        try:
            import plotly.graph_objects as go
            from sklearn.linear_model import LinearRegression
            from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
            from sklearn.metrics import mean_squared_error
            
            base_dir = "/home/ubuntu/workspace/daily_seongsu"
            train_path = os.path.join(base_dir, "train_data.csv")
            test_path = os.path.join(base_dir, "test_data.csv")
            
            if not os.path.exists(train_path):
                return pd.DataFrame({"Error": ["Please run Step 4.1 first"]}), None
            
            train_df = pd.read_csv(train_path)
            test_df = pd.read_csv(test_path)
            
            # Feature engineering (use lag features) - FIXED: rolling_7d_avg not rolling_7d_mean
            feature_cols = ['lag_1d', 'lag_7d', 'rolling_7d_avg']
            feature_cols = [c for c in feature_cols if c in train_df.columns]
            
            if not feature_cols:
                return pd.DataFrame({"Error": ["No valid feature columns found"]}), None
            
            target_col = 'total_traffic' if 'total_traffic' in train_df.columns else 'traffic'
            
            X_train = train_df[feature_cols].fillna(0)
            y_train = train_df[target_col].fillna(0)
            X_test = test_df[feature_cols].fillna(0)
            y_test = test_df[target_col].fillna(0)
            
            # Train models
            models = {
                "Linear Regression": LinearRegression(),
                "Random Forest": RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42),
                "Gradient Boosting": GradientBoostingRegressor(n_estimators=50, max_depth=5, random_state=42)
            }
            
            results = []
            for name, model in models.items():
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                results.append({"Model": name, "RMSE": f"{rmse:.2f}", "RMSE_Val": rmse})
            
            results_df = pd.DataFrame(results)
            
            # Chart
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=[r["Model"] for r in results],
                y=[r["RMSE_Val"] for r in results],
                marker=dict(color=['#60a5fa', '#a78bfa', '#34d399']),
                text=[r["RMSE"] for r in results],
                textposition='outside'
            ))
            
            fig.update_layout(
                title="Model Performance Comparison (Lower is Better)",
                xaxis_title="Model",
                yaxis_title="RMSE",
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(30,30,30,0.5)',
                font=dict(color='white'),
                height=400
            )
            
            # Save best model name
            best_model_name = min(results, key=lambda x: x["RMSE_Val"])["Model"]
            with open(os.path.join(base_dir, "best_model_name.txt"), "w") as f:
                f.write(best_model_name)
            
            return results_df[["Model", "RMSE"]], fig
        except Exception as e:
            import traceback
            error_msg = f"❌ Error: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            return pd.DataFrame({"Error": [str(e)]}), None
    
    btn_compare.click(fn=train_and_compare, inputs=[], outputs=[model_results, comparison_chart])
    
    # ============================================
    # STEP 4.3: Hyperparameter Tuning
    # ============================================
    gr.HTML('<hr style="border: none; border-top: 1px solid #4b5563; margin: 48px 0;">')
    gr.Markdown("### Step 4.3: Hyperparameter Tuning")
    gr.Markdown("⚙️ **Fine-tune the Best Model with Grid Search**")
    

    gr.Markdown("""
    **Hyperparameters** are settings that control how a model learns (e.g., tree depth, number of trees).
    
    **Grid Search**: Automatically test multiple combinations and pick the best.
    
    **Example**: For Random Forest, we test different values of `n_estimators` (50, 100, 200) and `max_depth` (5, 10, 15).
    """)
    
    btn_tune = gr.Button("🔍 Run Grid Search", variant="primary")
    with gr.Row():
        tuning_log = gr.Textbox(label="Tuning Log", lines=8)
        tuned_chart = gr.Plot(label="Before vs After Tuning")
    
    def hyperparameter_tuning():
        try:
            import plotly.graph_objects as go
            from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
            from sklearn.model_selection import GridSearchCV
            from sklearn.metrics import mean_squared_error
            
            base_dir = "/home/ubuntu/workspace/daily_seongsu"
            train_path = os.path.join(base_dir, "train_data.csv")
            test_path = os.path.join(base_dir, "test_data.csv")
            
            if not os.path.exists(train_path):
                return "❌ Please run Step 4.2 first", None
            
            train_df = pd.read_csv(train_path)
            test_df = pd.read_csv(test_path)
            
            feature_cols = ['lag_1d', 'lag_7d', 'rolling_7d_avg']
            feature_cols = [c for c in feature_cols if c in train_df.columns]
            target_col = 'total_traffic' if 'total_traffic' in train_df.columns else 'traffic'
            
            X_train = train_df[feature_cols].fillna(0)
            y_train = train_df[target_col].fillna(0)
            X_test = test_df[feature_cols].fillna(0)
            y_test = test_df[target_col].fillna(0)
            
            logs = []
            logs.append("🔍 Starting Grid Search...")
            
            # Default model
            default_model = RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42)
            default_model.fit(X_train, y_train)
            default_pred = default_model.predict(X_test)
            default_rmse = np.sqrt(mean_squared_error(y_test, default_pred))
            logs.append(f"📊 Default RMSE: {default_rmse:.2f}")
            
            # Grid Search
            param_grid = {
                'n_estimators': [50, 100, 150],
                'max_depth': [5, 10, 15],
                'min_samples_split': [2, 5]
            }
            
            grid_search = GridSearchCV(
                RandomForestRegressor(random_state=42),
                param_grid,
                cv=3,
                scoring='neg_mean_squared_error',
                n_jobs=-1
            )
            
            grid_search.fit(X_train, y_train)
            best_model = grid_search.best_estimator_
            
            logs.append(f"\n✅ Best Parameters: {grid_search.best_params_}")
            
            # Evaluate
            tuned_pred = best_model.predict(X_test)
            tuned_rmse = np.sqrt(mean_squared_error(y_test, tuned_pred))
            logs.append(f"📊 Tuned RMSE: {tuned_rmse:.2f}")
            logs.append(f"🎯 Improvement: {((default_rmse - tuned_rmse) / default_rmse * 100):.2f}%")
            
            # Chart
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=["Before Tuning", "After Tuning"],
                y=[default_rmse, tuned_rmse],
                marker=dict(color=['#ef4444', '#22c55e']),
                text=[f"{default_rmse:.2f}", f"{tuned_rmse:.2f}"],
                textposition='outside'
            ))
            
            fig.update_layout(
                title="Hyperparameter Tuning Impact",
                yaxis_title="RMSE (Lower is Better)",
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(30,30,30,0.5)',
                font=dict(color='white'),
                height=400
            )
            
            return "\n".join(logs), fig
        except Exception as e:
            import traceback
            error_msg = f"❌ Error: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            return error_msg, None
    
    btn_tune.click(fn=hyperparameter_tuning, inputs=[], outputs=[tuning_log, tuned_chart])
