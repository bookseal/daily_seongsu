import gradio as gr
import json

def create_sandbox_tab():
    with gr.Group(elem_id="step-12"):
        gr.Markdown("## 🟢 Level 4: Business Intelligence (Sandbox)")
        gr.Markdown("---")
        gr.Markdown("### 🔮 AI Business Simulator")
        gr.Markdown("비즈니스 담당자가 날씨와 이벤트 시나리오를 설정하면, AI가 성수역 예상 트래픽과 그 근거를 시각화하여 제시합니다.")
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 🎛️ Scenario Control")
                inp_date = gr.Textbox(label="Simulation Date (YYYY-MM-DD)", value="2026-05-05")
                inp_temp = gr.Slider(-20, 40, value=22, label="Temperature Avg (°C)")
                inp_rain = gr.Slider(0, 100, value=0, label="Rainfall (mm)")
                inp_event = gr.Checkbox(label="Special Event (Pop-up/Holiday)", value=False)
                
                btn_sim = gr.Button("🚀 Run Simulation", variant="primary")
            
            with gr.Column(scale=2):
                gr.Markdown("### 📊 AI Prediction Result & Insights")
                out_pred_text = gr.Markdown("### ⏳ Waiting for simulation...")
                out_chart = gr.Plot(label="Feature Contribution Analysis")
                out_vector = gr.JSON(label="Internal Feature Vector", visible=False)
                
        def simulate_prediction(date, temp, rain, event):
            import plotly.graph_objects as go
            
            # 1. Base Logic (Mock Model)
            # 성수역 가정: 기본 8만명
            base_traffic = 80000
            
            # Seasonality: 주말엔 +2만 (단순 가정)
            # (실제로는 date 파싱해서 요일 확인해야 하지만, 여기선 Mock으로 토/일 문자열 체크)
            is_weekend = False # "Sat" in date or "Sun" in date # (Not reliable without parsing, assume Weekday base)
            
            # 2. Feature Impact Calculation
            # 온도: 20도 기준으로 따뜻하면 좋고, 너무 덥거나 추우면 감소
            # (20도에서 0, 멀어질수록 감소하는 2차 함수 형태 가정 or 단순 선형)
            # 여기선 단순하게: 10~25도 사이가 최적(+5000), 그 외는 감소
            if 10 <= temp <= 25:
                temp_impact = 5000
            else:
                temp_impact = -1 * abs(temp - 20) * 200
                
            # 강수량: 비오면 무조건 감소 (-500 * mm)
            rain_impact = -500 * rain
            
            # 이벤트: 있으면 대폭 상승 (+15000)
            event_impact = 15000 if event else 0
            
            predicted_traffic = base_traffic + temp_impact + rain_impact + event_impact
            
            # 3. Visualization (Waterfall Chart)
            fig = go.Figure(go.Waterfall(
                name = "Feature Contribution", orientation = "v",
                measure = ["relative", "relative", "relative", "relative", "total"],
                x = ["Base Traffic", "Temperature Effect", "Rain Impact", "Event Bonus", "Final Prediction"],
                textposition = "outside",
                text = [f"{base_traffic/1000:.1f}k", f"{temp_impact/1000:.1f}k", f"{rain_impact/1000:.1f}k", f"{event_impact/1000:.1f}k", f"{predicted_traffic/1000:.1f}k"],
                y = [base_traffic, temp_impact, rain_impact, event_impact, predicted_traffic],
                connector = {"line":{"color":"white"}},
                decreasing = {"marker":{"color":"#ef4444"}},
                increasing = {"marker":{"color":"#22c55e"}},
                totals = {"marker":{"color":"#3b82f6"}}
            ))

            fig.update_layout(
                title = "Why this prediction? (Explainable AI)",
                showlegend = False,
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white")
            )

            # Result Text
            result_markdown = f"""
            # 🎯 Predicted Traffic: <span style="color:#60a5fa">{int(predicted_traffic):,}</span>
            > *Compared to Base (80k):* **{((predicted_traffic - 80000)/80000)*100:+.1f}%**
            """
            
            feature_vector = {
                "date_input": date,
                "temp_input": temp,
                "rain_input": rain,
                "is_event": event
            }
            
            return result_markdown, fig, feature_vector

        btn_sim.click(
            fn=simulate_prediction,
            inputs=[inp_date, inp_temp, inp_rain, inp_event],
            outputs=[out_pred_text, out_chart, out_vector]
        )
