import gradio as gr
import pandas as pd
import os

def load_data():
    """Level 2에서 생성된 피처 데이터를 로드합니다 (Fallback for Demo)."""
    # ---------------------------------------------------------
    # Realistic Dummy Data Generator (Auto-Fallback)
    # ---------------------------------------------------------
    dates = pd.date_range(start="2024-01-01", periods=365)
    
    # 1. Base Traffic (Weekly Seasonality)
    base = 40000
    weekly_pattern = [0.8, 1.1, 1.1, 1.1, 1.2, 1.0, 0.7] # Mon-Sun factors
    traffic = []
    
    import random
    import numpy as np
    
    for i, d in enumerate(dates):
        day_factor = weekly_pattern[d.dayofweek]
        noise = random.randint(-2000, 2000)
        trend = i * 10 # Slight upward trend
        val = (base * day_factor) + noise + trend
        traffic.append(val)
        
    df = pd.DataFrame({
        "date": dates,
        "total_traffic": traffic, # Standardized name
        "avg_temp": np.random.normal(15, 10, 365) # Random temp
    })
    
    # 2. Lag Features (Correlated)
    # Lag 1: Shift by 1 day + minor noise (Simulation of good correlation)
    df["traffic_lag_1"] = df["total_traffic"].shift(1) + np.random.normal(0, 500, 365)
    
    return df.dropna()

STEP11_DESC_PART_1 = r"""
## 🟢 Level 3: Data Quality Assurance

---

### L3-S1: Feature Observer
🏥 **Data Health & Distribution Monitoring**

**Goal:** Before triggering the AutoML pipeline, we must perform a "Medical Check-up" on our Feature Store. This ensures the data is representative, high-quality, and free from anomalies that could degrade model performance.

<hr style="border: none; border-top: 1px solid #777777; margin: 24px 0;">

#### 1. Architect's Insight: "Glass Box" Validation
Unlike "Black Box" models, an MLOps pipeline must be transparent. We check for:
- **Stationarity**: Does the mean/variance change over time?
- **Seasonality**: Is there a weekly pattern? (Subway traffic drops on weekends)
- **Correlation**: Does $X_{t-1}$ predict $X_t$?

To ensure the features are "Ready for Training," we calculate the **Pearson Correlation Coefficient ($\rho$)**. 

<div style="font-size: 1.2em; font-weight: bold; background-color: #2d2d2d; padding: 10px; border-radius: 5px; text-align: center;">
$$
\rho_{X,Y} = \frac{\text{cov}(X,Y)}{\sigma_X \sigma_Y}
$$
</div>
"""

STEP11_DESC_PART_2 = r"""
**C. Seasonality Trend (Cycles)**
*   **Concept**: "Do patterns repeat?"
*   **Why it matters**: Humans follow routines (Weekly work cycles, Yearly holidays). The model needs these cycles to forecast accurately.
*   **Target**: Clear peaks at **7-day** (weekly) and **365-day** (yearly) intervals.

<hr style="border: none; border-top: 1px solid #777777; margin: 24px 0;">

#### 3. Technical Logic: Feature Validity
"""
STEP11_DESC_PART_3 = r"""
To ensure the features are "Ready for Training," we calculate the **Pearson Correlation Coefficient ($\rho$)**. 

<div style="font-size: 1.2em; font-weight: bold; background-color: #2d2d2d; padding: 10px; border-radius: 5px; text-align: center;">
$$
\rho_{X,Y} = \frac{\text{cov}(X,Y)}{\sigma_X \sigma_Y}
$$
</div>

*   **Numerator** ($\text{cov}$): Do X and Y increase/decrease together?
*   **Denominator** ($\sigma$): Normalizes the value between -1 and 1.
*   **Interpretation**:
    *   **+1.0**: Perfect straight line (Best).
    *   **0.0**: Random cloud (Worst).

> **Architect's Insight:** We aim for a correlation **$> 0.7$** for our primary Lag features ($t-7$).
"""

STEP11_MERMAID = """
<div class="mermaid">
flowchart LR
    A[Supabase] --> B[Observer Engine]
    B --> C{Validation}
    C -->|Fail| D[Alert]
    C -->|Pass| E[Visualization]
    E --> F[Level 4 Ready]
</div>
"""

def create_observer_tab():
    """Level 3: Data Quality Assurance - L3-S1 and L3-S2."""
    
    # Level/Step Overview Table
    gr.Markdown("""
    > **Goal**: Before triggering AutoML, perform a "Medical Check-up" on the Feature Store to ensure data quality.
    
    | Level | Level Status | Step ID | Description | Step Status |
    |------|--------------|--------|-------------|-------------|
    | L3 | ✅ Complete | L3-S1 | Feature Observer (Correlation Analysis) | ✅ Complete |
    | L3 | ✅ Complete | L3-S2 | Distribution Monitoring | ✅ Complete |
    """)
    
    gr.HTML('<hr style="border: none; border-top: 1px solid #4b5563; margin: 24px 0;">')
    
    # L3-S1
    gr.Markdown("### L3-S1: Feature Observer")
    gr.Markdown("🏥 **Data Health & Correlation Monitoring**")
    
    gr.Markdown(STEP11_DESC_PART_1)
    gr.Markdown(STEP11_DESC_PART_2)
    gr.Markdown(STEP11_DESC_PART_3)
    gr.HTML(STEP11_MERMAID)
    
    # Data Preview Section (OUTSIDE accordion)
    gr.Markdown("### 📋 Data Preview (Feature Store)")
    data_preview = gr.Dataframe(label="Feature Store Snapshot", interactive=False, max_height=200)

    with gr.Row():
        with gr.Column():
            gr.Markdown("### 📊 1. Traffic vs. Lags (Correlation)")
            plot_scatter = gr.Plot(label="Lag Correlation")
            gr.Markdown(
                "**🔍 How to Interpret:**\n"
                "- **Good:** Dots form a tight, diagonal line ( / ). This means past traffic strongly predicts today.\n"
                "- **Bad:** Dots are scattered like a random cloud. The feature is weak."
            )
        with gr.Column():
            gr.Markdown("### 📈 2. Time-Series Trend (Yearly)")
            plot_line = gr.Plot(label="Traffic Trend")
            gr.Markdown(
                "**🔍 How to Interpret:**\n"
                "- **Check for Gaps:** Are there any missing periods?\n"
                "- **Check for Outliers:** Are there sudden spikes (e.g., 0 or 10,000) that look like errors?"
            )
    
    btn_refresh = gr.Button("🔄 Refresh Charts (Load Level 2 Data)", variant="primary")
    status_log = gr.Markdown("### 📝 System Logs\n*Click refresh to see details...*")
    
    def refresh_charts():
        logs = []
        logs.append("### 🚀 Starting Data Load Process...")
        
        # Force absolute path explicitly
        base_dir = "/home/ubuntu/workspace/daily_seongsu"
        data_path = os.path.join(base_dir, "data_features_level2.csv")
        
        # source = "Real Data"
        df = pd.DataFrame()
        
        if os.path.exists(data_path):
            try:
                df = pd.read_csv(data_path)
                logs.append(f"- ✅ Loaded **{len(df)} rows** from `{data_path}`")
                if len(df) > 0:
                    logs.append(f"- 📋 Columns found: `{', '.join(df.columns[:5])}...`")
            except Exception as e:
                logs.append(f"- ❌ Error reading CSV: {str(e)}")
        else:
            logs.append(f"- ⚠️ File not found at `{data_path}`. Using Dummy Data.")
        
        if df.empty:
            # source = "Dummy Data"
            df = load_data() # Fallback to dummy
            logs.append(f"- ℹ️ Generated **{len(df)} rows** of dummy data.")
        
        # 1. Target Column Check
        target_col = 'total_traffic' if 'total_traffic' in df.columns else 'traffic'
        
        # 2. Lag Column Check
        if 'lag_1d' in df.columns:
            lag_col = 'lag_1d'
        elif 'traffic_lag_1' in df.columns:
            lag_col = 'traffic_lag_1'
        else:
            lag_col = target_col # Fallback
        
        logs.append(f"- 🎯 Target Column: `{target_col}`")
        logs.append(f"- ⏳ Lag Column: `{lag_col}`")
        
        try:
            # Force numeric conversion to avoid type issues
            df[target_col] = pd.to_numeric(df[target_col], errors='coerce')
            df[lag_col] = pd.to_numeric(df[lag_col], errors='coerce')
            
            # Check NaNs before drop
            nan_target = df[target_col].isna().sum()
            nan_lag = df[lag_col].isna().sum()
            logs.append(f"- 🔍 Pre-clean NaNs: Target={nan_target}, Lag={nan_lag}")

            # Drop NaNs for valid plotting
            df_clean = df.dropna(subset=[lag_col, target_col])
            logs.append(f"- 🧹 Data after dropna: **{len(df_clean)} rows**")
            
            # Limit to last 180 days for better performance but only if sorted or we don't care about order yet
            # Ideally sort by date first if possible
            if 'date' in df_clean.columns:
                try:
                    df_clean['date'] = pd.to_datetime(df_clean['date'])
                    df_clean = df_clean.sort_values('date')
                except Exception as e:
                    logs.append(f"⚠️ Date sorting failed: {e}")
            
            if len(df_clean) > 180:
                df_clean = df_clean.tail(180)
                logs.append("- ✂️ limited to last 180 rows for plotting")
            
            if df_clean.empty:
                logs.append("❌ All data dropped! Cannot plot graphs. Please check if columns contain valid numeric data.")
                # Return empty charts with annotation
                import plotly.graph_objects as go
                
                fig_scatter = go.Figure()
                fig_scatter.add_annotation(text="No valid data found for correlation analysis", showarrow=False)
                
                fig_line = go.Figure()
                fig_line.add_annotation(text="No valid time-series data found", showarrow=False)
                # We return head of original df so user can inspect it
                return df.head(100), fig_scatter, fig_line, "\n".join(logs)

            # DEBUG: Log Data Stats
            logs.append("### 📊 Data Statistics for Plotting")
            logs.append(f"- **{lag_col} (X-axis)**: Min={df_clean[lag_col].min()}, Max={df_clean[lag_col].max()}, Mean={df_clean[lag_col].mean():.2f}")
            logs.append(f"- **{target_col} (Y-axis)**: Min={df_clean[target_col].min()}, Max={df_clean[target_col].max()}, Mean={df_clean[target_col].mean():.2f}")
            if 'date' in df_clean.columns:
                 logs.append(f"- **Date Range**: {df_clean['date'].min()} to {df_clean['date'].max()}")
            
            logs.append(f"#### Data Types:\n{df_clean[[lag_col, target_col]].dtypes}")
            
            # Import graph_objects explicitly
            import plotly.graph_objects as go
            
            # -----------------------------------------------------
            # SAFE PLOTTING STRATEGY
            # 1. Force copy to avoid Slice/View issues
            # 2. Convert to list to avoid Index serialization issues
            # -----------------------------------------------------
            df_clean = df_clean.copy()
            x_vals = df_clean[lag_col].tolist()
            y_vals = df_clean[target_col].tolist()
            
            logs.append("#### Plotting Data Check:")
            logs.append(f"- X (first 3): {x_vals[:3]}")
            logs.append(f"- Y (first 3): {y_vals[:3]}")

            # 1. Scatter Plot (Manual GO for maximum control)
            fig_scatter = go.Figure()
            fig_scatter.add_trace(go.Scatter(
                x=x_vals, 
                y=y_vals, 
                mode='markers',
                marker=dict(size=10, color='#60a5fa', line=dict(width=1, color='white'), opacity=0.7),
                name='Correlation'
            ))

            fig_scatter.update_layout(
                title=f"Correlation: {target_col} (y) vs {lag_col} (x)",
                xaxis_title=f"Yesterday's Traffic ({lag_col})",
                yaxis_title=f"Today's Traffic ({target_col})",
                margin=dict(l=40, r=40, t=60, b=40),
                height=450,
                template="plotly_dark",
                # Safe Dark Theme Settings
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(30,30,30,0.5)',
                font=dict(color='white'),
                xaxis=dict(autorange=True),
                yaxis=dict(autorange=True)
            )
            
            # 2. Line Plot (Traffic over Date)
            # Ensure date is properly parsed
            df_sorted = df.copy()
            df_sorted['date'] = pd.to_datetime(df_sorted['date'])
            df_sorted = df_sorted.sort_values('date').tail(180)  # Last 180 days only
            
            x_line = df_sorted['date'].tolist()
            y_line = df_sorted[target_col].tolist()
            
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(
                x=x_line,
                y=y_line,
                mode='lines',
                line=dict(color='#60a5fa', width=2),
                name='Traffic Trend'
            ))
            
            fig_line.update_layout(
                title="Traffic Trend over Time (Last 180 Days)",
                template="plotly_dark",
                xaxis_title="Date",
                yaxis_title="Total Traffic",
                margin=dict(l=40, r=40, t=60, b=40),
                height=450,
                hovermode='x unified',
                # Safe Dark Theme Settings
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(30,30,30,0.5)',
                font=dict(color='white'),
                xaxis=dict(autorange=True),
                yaxis=dict(autorange=True)
            )
            
            # Analysis Log
            logs.append("✅ Graphs generated.")
            logs.append("💡 **Insight**: The linear shape (Slope ≈ 1) means 'Yesterday's traffic is the best predictor for Today'.")
            
            return df.head(100), fig_scatter, fig_line, "\n".join(logs)

        except Exception as e:
            import traceback
            error_msg = f"❌ Unexpected Error: {str(e)}\n{traceback.format_exc()}"
            logs.append(error_msg)
            print(error_msg)
            return df.head(100), None, None, "\n".join(logs)

    # Load on button click
    btn_refresh.click(fn=refresh_charts, inputs=[], outputs=[data_preview, plot_scatter, plot_line, status_log])

    # ============================================
    # STEP 3.2: Distribution Monitoring
    # ============================================
    gr.HTML('<hr style="border: none; border-top: 2px solid #60a5fa; margin: 60px 0;">')
    gr.Markdown("### L3-S2: Distribution Monitoring")
    gr.Markdown("📊 **Detecting Data Drift & Anomalies**")
    
    gr.Markdown("""
    **Data Drift** occurs when the statistical properties of input features change over time. This can cause model performance degradation even if the model itself hasn't changed.
    
    **What we check:**
    - **Shape**: Is the distribution still bell-curved (normal)?
    - **Outliers**: Are there extreme values far from the mean?
    - **Shifts**: Has the mean/median moved significantly?
    
    **Example Scenario:**  
    If subway traffic suddenly drops by 50% (e.g., pandemic lockdown), our model trained on pre-pandemic data will fail. Distribution monitoring helps catch this **before** the model goes live.
    """)
    
    gr.Markdown("#### 📊 Feature Distributions (Histogram)")
    
    with gr.Row():
        with gr.Column():
            plot_hist_traffic = gr.Plot(label="Traffic Distribution")
        with gr.Column():
            plot_hist_lag = gr.Plot(label="Lag Feature Distribution")
    
    btn_analyze_dist = gr.Button("🔍 Analyze Distributions", variant="secondary")
    dist_log = gr.Markdown("### 📝 Distribution Analysis Log\n*Click the button above to analyze...*")
    
    def analyze_distributions():
        logs = []
        logs.append("### 🔍 Starting Distribution Analysis...")
        
        # Load data
        base_dir = "/home/ubuntu/workspace/daily_seongsu"
        data_path = os.path.join(base_dir, "data_features_level2.csv")
        
        df = pd.DataFrame()
        if os.path.exists(data_path):
            try:
                df = pd.read_csv(data_path)
                logs.append(f"- ✅ Loaded {len(df)} rows")
            except Exception as e:
                logs.append(f"- ❌ Error: {e}")
        
        if df.empty:
            df = load_data()
            logs.append(f"- ℹ️ Using dummy data ({len(df)} rows)")
        
        # Column detection
        target_col = 'total_traffic' if 'total_traffic' in df.columns else 'traffic'
        if 'lag_1d' in df.columns:
            lag_col = 'lag_1d'
        elif 'traffic_lag_1' in df.columns:
            lag_col = 'traffic_lag_1'
        else:
            lag_col = target_col
        
        try:
            # Force numeric
            df[target_col] = pd.to_numeric(df[target_col], errors='coerce')
            df[lag_col] = pd.to_numeric(df[lag_col], errors='coerce')
            df_clean = df.dropna(subset=[target_col, lag_col])
            
            import plotly.graph_objects as go
            
            # Histogram 1: Traffic
            fig_traffic = go.Figure()
            fig_traffic.add_trace(go.Histogram(
                x=df_clean[target_col].tolist(),
                nbinsx=30,
                marker=dict(color='#60a5fa', line=dict(color='white', width=1)),
                name='Traffic'
            ))
            
            # Add mean line
            mean_val = df_clean[target_col].mean()
            fig_traffic.add_vline(
                x=mean_val, 
                line=dict(color='#fbbf24', width=2, dash='dash'),
                annotation_text=f"Mean: {mean_val:.0f}",
                annotation_position="top"
            )
            
            fig_traffic.update_layout(
                title=f"Distribution of {target_col}",
                xaxis_title="Traffic Count",
                yaxis_title="Frequency",
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(30,30,30,0.5)',
                font=dict(color='white'),
                height=400
            )
            
            # Histogram 2: Lag
            fig_lag = go.Figure()
            fig_lag.add_trace(go.Histogram(
                x=df_clean[lag_col].tolist(),
                nbinsx=30,
                marker=dict(color='#a78bfa', line=dict(color='white', width=1)),
                name='Lag Feature'
            ))
            
            mean_lag = df_clean[lag_col].mean()
            fig_lag.add_vline(
                x=mean_lag,
                line=dict(color='#fbbf24', width=2, dash='dash'),
                annotation_text=f"Mean: {mean_lag:.0f}",
                annotation_position="top"
            )
            
            fig_lag.update_layout(
                title=f"Distribution of {lag_col}",
                xaxis_title="Lag Value",
                yaxis_title="Frequency",
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(30,30,30,0.5)',
                font=dict(color='white'),
                height=400
            )
            
            # Statistical Summary
            logs.append("### 📊 Statistical Summary")
            logs.append(f"**{target_col}:**")
            logs.append(f"- Mean: {df_clean[target_col].mean():.2f}")
            logs.append(f"- Std Dev: {df_clean[target_col].std():.2f}")
            logs.append(f"- Min: {df_clean[target_col].min():.0f}, Max: {df_clean[target_col].max():.0f}")
            
            logs.append(f"\n**{lag_col}:**")
            logs.append(f"- Mean: {df_clean[lag_col].mean():.2f}")
            logs.append(f"- Std Dev: {df_clean[lag_col].std():.2f}")
            logs.append(f"- Min: {df_clean[lag_col].min():.0f}, Max: {df_clean[lag_col].max():.0f}")
            
            # Outlier Detection (Simple IQR method)
            Q1 = df_clean[target_col].quantile(0.25)
            Q3 = df_clean[target_col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = df_clean[(df_clean[target_col] < Q1 - 1.5*IQR) | (df_clean[target_col] > Q3 + 1.5*IQR)]
            
            logs.append("\n### 🚨 Outlier Detection")
            logs.append(f"- Found **{len(outliers)} outliers** ({len(outliers)/len(df_clean)*100:.1f}% of data)")
            if len(outliers) > 0:
                logs.append(f"- Range: {outliers[target_col].min():.0f} ~ {outliers[target_col].max():.0f}")
            
            logs.append("\n✅ Distribution analysis complete.")
            
            return fig_traffic, fig_lag, "\n".join(logs)
            
        except Exception as e:
            import traceback
            error_msg = f"❌ Error: {str(e)}\n{traceback.format_exc()}"
            logs.append(error_msg)
            return None, None, "\n".join(logs)
    
    btn_analyze_dist.click(fn=analyze_distributions, inputs=[], outputs=[plot_hist_traffic, plot_hist_lag, dist_log])
