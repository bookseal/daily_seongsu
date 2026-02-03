import gradio as gr
import pandas as pd
import plotly.express as px
import os

def load_data():
    """Level 2에서 생성된 피처 데이터를 로드합니다."""
    # Fallback/Dummy Data generator
    return pd.DataFrame({
        "date": pd.date_range(start="2024-01-01", periods=100),
        "traffic": [1000 + i*10 for i in range(100)],
        "traffic_lag_1": [990 + i*10 for i in range(100)],
        "temp_avg": [20 for _ in range(100)]
    })

STEP11_DESC_PART_1 = """
### Step 11: Feature Observer
🏥 **Data Health & Distribution Monitoring**

**Goal:** Before triggering the AutoML pipeline, we must perform a "Medical Check-up" on our Feature Store. This ensures the data is representative, high-quality, and free from anomalies that could degrade model performance.

<hr style="border: none; border-top: 1px solid #777777; margin: 24px 0;">

#### 1. Why do we need an "Observer"?
Machine learning models follow the **GIGO (Garbage In, Garbage Out)** principle. If our features (Lags, Trends) are corrupted or shifted, the prediction will fail regardless of how advanced the model is. 

*   **Feature Drift:** Detecting if today's traffic pattern has fundamentally changed compared to last year (e.g., due to new subway lines or pandemics).
*   **Correlation Integrity:** Verifying if our engineered features (like "Traffic 1 week ago") actually help predict "Today's Traffic".

<hr style="border: none; border-top: 1px solid #777777; margin: 24px 0;">

#### 2. Key Monitoring Components (Deep Dive)

We monitor three vital signs of our data. Here is what they mean in plain English:

**A. Lag Correlation (Predictive Power)**
*   **Concept**: "Does the past predict the future?"
*   **Why it matters**: If `Traffic(t-7)` (last week) has a strong relationship with `Traffic(t)` (today), our model can easily learn this pattern.
*   **Target**: A correlation close to **1.0** (perfect positive relationship). If it's near **0**, the feature is useless.

**B. Distribution Check (Consistency)**
*   **Concept**: "Is these exam questions similar to the textbook?"
*   **Why it matters**: We train the model on 2022-2023 data. If 2024 data looks completely different (e.g., traffic doubled), the model will fail.
*   **Target**: The probability curves should overlap. Large deviation means **Drift** has occurred.

**C. Seasonality Trend (Cycles)**
*   **Concept**: "Do patterns repeat?"
*   **Why it matters**: Humans follow routines (Weekly work cycles, Yearly holidays). The model needs these cycles to forecast accurately.
*   **Target**: Clear peaks at **7-day** (weekly) and **365-day** (yearly) intervals.

<hr style="border: none; border-top: 1px solid #777777; margin: 24px 0;">

#### 3. Technical Logic: Feature Validity

To ensure the features are "Ready for Training," we calculate the **Pearson Correlation Coefficient ($\rho$)**. 

<div style="font-size: 1.2em; font-weight: bold; background-color: #2d2d2d; padding: 10px; border-radius: 5px; text-align: center;">
$$
\\rho_{X,Y} = \\frac{\\text{cov}(X,Y)}{\\sigma_X \\sigma_Y}
$$
</div>

*   **Numerator** ($\text{cov}$): Do X and Y increase/decrease together?
*   **Denominator** ($\sigma$): Normalizes the value between -1 and 1.
*   **Interpretation**:
    *   **+1.0**: Perfect straight line (Best).
    *   **0.0**: Random cloud (Worst).

> **Architect's Insight:** We aim for a correlation **$> 0.7$** for our primary Lag features ($t-7$).

<hr style="border: none; border-top: 1px solid #777777; margin: 24px 0;">

#### 4. Data Flow Architecture (Mermaid)
"""

STEP11_MERMAID = """
<div class="mermaid">
graph TD
    A[Supabase: model_features] -->|Fetch Batch| B(Feature Observer Engine)
    
    subgraph "Validation Process"
        B --> C{Null Check}
        C -->|Failed| D[Alert: Data Missing]
        C -->|Passed| E{Range Check}
        E -->|Outlier| F[Log: Anomalous Traffic]
    end
    
    subgraph "Visualization (Gradio UI)"
        E -->|Passed| G[Correlation Heatmap]
        G --> H[Yearly Seasonality Trend]
        H --> I[Feature Importance Preview]
    end
    
    I --> J(("Ready for Level 4: AutoML"))
</div>
"""

def create_observer_tab():
    with gr.Group(elem_id="step-11"):
        gr.Markdown(STEP11_DESC_PART_1)
        gr.HTML(STEP11_MERMAID)
        
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
        
        btn_refresh = gr.Button("🔄 Refresh Charts (Load Level 2 Data)", variant="secondary")
        
        def refresh_charts():
            # Force absolute path explicitly
            base_dir = "/home/ubuntu/workspace/daily_seongsu"
            data_path = os.path.join(base_dir, "data_features_level2.csv")
            
            source = "Real Data"
            if os.path.exists(data_path):
                df = pd.read_csv(data_path)
            else:
                source = "Dummy Data"
                df = load_data() # Fallback to dummy
            
            gr.Info(f"Loaded {len(df)} rows from {source}")
            
            # 1. Target Column Check
            target_col = 'total_traffic' if 'total_traffic' in df.columns else 'traffic'
            
            # 2. Lag Column Check
            if 'lag_1d' in df.columns:
                lag_col = 'lag_1d'
            elif 'traffic_lag_1' in df.columns:
                lag_col = 'traffic_lag_1'
            else:
                lag_col = target_col # Fallback
            
            # Drop NaNs for valid plotting
            df_clean = df.dropna(subset=[lag_col, target_col])
            
            if df_clean.empty:
                gr.Warning(f"Correlation Plot Error: No valid data found after dropping NaNs for columns '{lag_col}' and '{target_col}'. Data loaded: {len(df)} rows.")

                
            fig_scatter = px.scatter(
                df_clean, x=lag_col, y=target_col, 
                title=f"Correlation: {target_col} vs {lag_col}",
                template="plotly_white",
                opacity=0.6
            )
            
            # 2. Line Plot (Traffic over Date)
            fig_line = px.line(
                df, x='date', y=target_col, 
                title="Traffic Trend over Time",
                template="plotly_white"
            )
            
            return fig_scatter, fig_line

        # 버튼 클릭 시 차트 갱신
        btn_refresh.click(fn=refresh_charts, inputs=[], outputs=[plot_scatter, plot_line])

        
        # 탭 로드 시 자동 실행 (Optional, but Gradio requires trigger usually)
        # gr.load 연결은 복잡할 수 있으므로 사용자 명시적 클릭 유도 혹은 데모용 텍스트 추가
        gr.Markdown("*(버튼을 눌러 최신 데이터를 시각화하세요)*")
