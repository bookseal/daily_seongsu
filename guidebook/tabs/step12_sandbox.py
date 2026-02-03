import gradio as gr
import json

def create_sandbox_tab():
    with gr.Group(elem_id="step-12"):
        gr.Markdown("## 🧪 Step 12: What-if Sandbox")
        gr.Markdown("### 🔮 Prediction Simulator (What-if?)")
        gr.Markdown("**Goal**: 가상의 날씨/날짜 조건을 입력하여 예측 결과가 어떻게 변하는지 시뮬레이션합니다. (Level 4 모델 연동 전 Mockup)")
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 🎛️ Control Panel")
                inp_date = gr.Textbox(label="Virtual Date", value="2026-05-05")
                inp_temp = gr.Slider(-20, 40, value=25, label="Temperature (°C)")
                inp_rain = gr.Slider(0, 100, value=0, label="Rain (mm)")
                
                # 시뮬레이션 트리거
                btn_sim = gr.Button("🚀 Simulate Feature Vector", variant="primary")
            
            with gr.Column(scale=2):
                gr.Markdown("### 🧠 Model's View & Prediction")
                out_vector = gr.JSON(label="Generated Feature Vector")
                out_pred = gr.Number(label="Predicted Traffic (Simulated)", precision=0)
                
        def simulate_prediction(date, temp, rain):
            # 1. Feature Vector 구성 (Mock)
            feature_vector = {
                "date": date,
                "temp_avg": temp,
                "rain_mm": rain,
                "is_weekend": 1 if "Sun" in date or "Sat" in date else 0, # 간단 로직
                "traffic_lag_1d": 25000, # 고정값 가정
                "traffic_lag_1w": 26000
            }
            
            # 2. Heuristic Rule (Level 4 이전 임시 로직)
            # 기본 20000 + 온도*100 - 비*50
            predicted_traffic = 20000 + (temp * 100) - (rain * 50)
            
            return feature_vector, predicted_traffic

        btn_sim.click(
            fn=simulate_prediction,
            inputs=[inp_date, inp_temp, inp_rain],
            outputs=[out_vector, out_pred]
        )
