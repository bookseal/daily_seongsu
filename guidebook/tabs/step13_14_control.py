import gradio as gr
import pandas as pd
import time

def create_control_tab():
    with gr.Group(elem_id="step-13-14"):
        gr.Markdown("## 🎛️ Step 13/14: Pipeline Control Room")
        gr.Markdown("## 🚂 Level 4 Trigger: AutoML Training & Governance")
        
        # --- Step 13: Control Room ---
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 1. Training Config")
                chk_feats = gr.CheckboxGroup(
                    ["Lags", "Weather", "Calendar"], 
                    label="Feature Sets", 
                    value=["Lags", "Calendar"]
                )
                slider_split = gr.Slider(0.5, 0.9, value=0.8, label="Train/Test Split")
                btn_train = gr.Button("🔥 Start AutoML Training", variant="stop")
            
            with gr.Column():
                gr.Markdown("### 2. Live Training Logs")
                out_train_logs = gr.Textbox(label="Console Stream", lines=6, value="Ready to train...")
                out_metrics = gr.Dataframe(
                    label="Leaderboard (RMSE)", 
                    headers=["Model", "RMSE", "R2"],
                    datatype=["str", "number", "number"]
                )

        gr.HTML('<hr style="border: none; border-top: 1px solid #4b5563; margin: 24px 0;">')
        
        # --- Step 14: Governance ---
        gr.Markdown("## 📦 Step 14: Model Registry (Governance)")
        gr.Markdown("**Goal**: 모델의 버전 이력(Lineage)과 배포 상태를 관리합니다.")
        
        # Mock Registry Data
        registry_data = pd.DataFrame({
            "Version": ["v1.0", "v1.1", "v2.0"],
            "Algorithm": ["Linear Regression", "XGBoost", "LightGBM"],
            "RMSE": [1500.2, 1200.5, 980.1],
            "Status": ["Archived", "Staging", "Production"],
            "Author": ["Antigravity", "Antigravity", "Antigravity"]
        })
        
        with gr.Row():
            out_registry = gr.Dataframe(value=registry_data, interactive=False)
            with gr.Column():
                dropdown_models = gr.Dropdown(
                    ["v1.0 (Linear)", "v2.0 (XGBoost)", "v2.1 (LightGBM)"], 
                    label="Select Model to Deploy"
                )
                btn_deploy = gr.Button("🚀 Deploy to Production", variant="primary")
                out_deploy_status = gr.Textbox(label="Deployment Status")

        # --- Event Handlers ---
        
        def mock_training(progress=gr.Progress()):
            """가상 학습 진행 시뮬레이션"""
            logs = "Initializing AutoML...\n"
            yield logs, None
            time.sleep(1)
            
            steps = ["Preprocessing Data...", "Training Baseline...", "Tuning Hyperparameters...", "Finalizing Model..."]
            
            for i, step in enumerate(steps):
                progress((i+1)/len(steps), desc=step)
                logs += f"[{i+1}/{len(steps)}] {step}\n"
                yield logs, None
                time.sleep(1.5) # 시뮬레이션 지연
            
            logs += "Training Complete! ✅\n"
            
            # 가상 리더보드 결과
            leaderboard = pd.DataFrame({
                "Model": ["LightGBM", "XGBoost", "LinearRegression"],
                "RMSE": [950.5, 1100.2, 1600.8],
                "R2": [0.92, 0.88, 0.75]
            })
            
            yield logs, leaderboard

        btn_train.click(
            fn=mock_training,
            inputs=[],
            outputs=[out_train_logs, out_metrics]
        )
        
        def mock_deploy(model_name):
            return f"Successfully deployed {model_name} to Production endpoint! 🚀"
            
        btn_deploy.click(fn=mock_deploy, inputs=[dropdown_models], outputs=[out_deploy_status])
