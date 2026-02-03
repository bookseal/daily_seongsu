import gradio as gr
import datetime
import random


def create_intro_tab():
    with gr.Tab("🚀 Dashboard"):
        # Hero Section
        gr.Markdown(
            """
            <div style="text-align: center; padding: 40px 0;">
                <h1 style="font-size: 3em; margin-bottom: 10px;">🚇 Daily Seongsu</h1>
                <p style="font-size: 1.2em; color: #6b7280;">
                    End-to-end MLOps Portfolio: From raw data to real-time service.
                </p>
                <div style="margin-top: 20px;">
                    <span style="background-color: #d1fae5; color: #065f46; padding: 5px 10px; border-radius: 15px; font-size: 0.9em; margin: 0 5px;">OCI Ampere A1</span>
                    <span style="background-color: #bfdbfe; color: #1e40af; padding: 5px 10px; border-radius: 15px; font-size: 0.9em; margin: 0 5px;">Supabase</span>
                    <span style="background-color: #fce7f3; color: #9d174d; padding: 5px 10px; border-radius: 15px; font-size: 0.9em; margin: 0 5px;">Hugging Face</span>
                </div>
            </div>
            """
        )

        # Mock Live Forecast UI
        with gr.Group():
            gr.Markdown("### 🔮 Today's Live Forecast (Mockup)")
            with gr.Row():
                # Get today's date
                today = datetime.datetime.now().strftime("%Y-%m-%d (%a)")
                
                # Mock Data
                mock_temp = f"{random.randint(-5, 30)}°C"
                mock_rain = f"{random.randint(0, 100)}%"
                mock_traffic = f"{random.randint(40000, 90000):,}"
                crowd_level = "High" if int(mock_traffic.replace(",", "")) > 70000 else "Moderate"
                color = "red" if crowd_level == "High" else "green"

                with gr.Column():
                    gr.Markdown(f"**📅 Date**: {today}")
                with gr.Column():
                    gr.Markdown(f"**🌡️ Weather**: {mock_temp} / ☔ {mock_rain}")
                with gr.Column():
                    gr.Markdown(f"**🚇 Predicted Traffic**: <span style='color:{color}; font-weight:bold; font-size:1.2em'>{mock_traffic}</span>")
                    gr.Markdown(f"**🚦 Crowd Level**: {crowd_level}")
        
        gr.Markdown("<br>")
        
        # 3 Phases Layout
        with gr.Row():
            # Phase 1: Foundation
            with gr.Column(scale=1, min_width=300):
                gr.HTML(
                    """
                    <div style="background-color: #1f2937; padding: 20px; border-radius: 10px; height: 100%;">
                        <h2 style="color: #60a5fa; border-bottom: 2px solid #374151; padding-bottom: 10px;">Phase 1: Foundation</h2>
                        <p style="color: #9ca3af; font-size: 0.9em; margin-bottom: 20px;">Building the Data Engine & Basic UI</p>
                        
                        <ul style="list-style-type: none; padding: 0;">
                            <li style="margin-bottom: 15px; display: flex; align-items: center;">
                                <span style="margin-right: 10px;">✅</span>
                                <div>
                                    <strong style="color: #e5e7eb;">Level 1: Cloud Data Eng</strong>
                                    <div style="color: #6b7280; font-size: 0.8em;">Supabase Upsert & Airflow Setup</div>
                                </div>
                            </li>
                            <li style="margin-bottom: 15px; display: flex; align-items: center;">
                                <span style="margin-right: 10px;">✅</span>
                                <div>
                                    <strong style="color: #e5e7eb;">Level 2: Preprocessing</strong>
                                    <div style="color: #6b7280; font-size: 0.8em;">Lags, Rolling, Holidays</div>
                                </div>
                            </li>
                            <li style="margin-bottom: 15px; display: flex; align-items: center;">
                                <span style="margin-right: 10px;">✅</span>
                                <div>
                                    <strong style="color: #e5e7eb;">Level 3: Dual-Purpose UI</strong>
                                    <div style="color: #6b7280; font-size: 0.8em;">Glass Box Architecture</div>
                                </div>
                            </li>
                        </ul>
                    </div>
                    """
                )

            # Phase 2: Acceleration
            with gr.Column(scale=1, min_width=300):
                gr.HTML(
                    """
                    <div style="background-color: #1f2937; padding: 20px; border-radius: 10px; height: 100%;">
                        <h2 style="color: #f472b6; border-bottom: 2px solid #374151; padding-bottom: 10px;">Phase 2: Acceleration</h2>
                        <p style="color: #9ca3af; font-size: 0.9em; margin-bottom: 20px;">Automating Intelligence & Deployments</p>
                        
                        <ul style="list-style-type: none; padding: 0;">
                            <li style="margin-bottom: 15px; display: flex; align-items: center;">
                                <span style="margin-right: 10px;">⚪</span>
                                <div>
                                    <strong style="color: #9ca3af;">Level 4: AutoML</strong>
                                    <div style="color: #4b5563; font-size: 0.8em;">PyCaret / Target Optimized</div>
                                </div>
                            </li>
                            <li style="margin-bottom: 15px; display: flex; align-items: center;">
                                <span style="margin-right: 10px;">⚪</span>
                                <div>
                                    <strong style="color: #9ca3af;">Level 5: IaC (Docker)</strong>
                                    <div style="color: #4b5563; font-size: 0.8em;">Containerized Engine Room</div>
                                </div>
                            </li>
                            <li style="margin-bottom: 15px; display: flex; align-items: center;">
                                <span style="margin-right: 10px;">⚪</span>
                                <div>
                                    <strong style="color: #9ca3af;">Level 6: CI/CD</strong>
                                    <div style="color: #4b5563; font-size: 0.8em;">GitHub Actions Auto-Deploy</div>
                                </div>
                            </li>
                        </ul>
                    </div>
                    """
                )

            # Phase 3: Operation
            with gr.Column(scale=1, min_width=300):
                gr.HTML(
                    """
                    <div style="background-color: #1f2937; padding: 20px; border-radius: 10px; height: 100%;">
                        <h2 style="color: #34d399; border-bottom: 2px solid #374151; padding-bottom: 10px;">Phase 3: Operation</h2>
                        <p style="color: #9ca3af; font-size: 0.9em; margin-bottom: 20px;">Reliability & Scale</p>
                        
                        <ul style="list-style-type: none; padding: 0;">
                            <li style="margin-bottom: 15px; display: flex; align-items: center;">
                                <span style="margin-right: 10px;">⚪</span>
                                <div>
                                    <strong style="color: #9ca3af;">Level 7: MLflow Tracking</strong>
                                    <div style="color: #4b5563; font-size: 0.8em;">Experiment Registry</div>
                                </div>
                            </li>
                            <li style="margin-bottom: 15px; display: flex; align-items: center;">
                                <span style="margin-right: 10px;">⚪</span>
                                <div>
                                    <strong style="color: #9ca3af;">Level 8: Data Versioning</strong>
                                    <div style="color: #4b5563; font-size: 0.8em;">DVC Integration</div>
                                </div>
                            </li>
                            <li style="margin-bottom: 15px; display: flex; align-items: center;">
                                <span style="margin-right: 10px;">⚪</span>
                                <div>
                                    <strong style="color: #9ca3af;">Level 9: Observability</strong>
                                    <div style="color: #4b5563; font-size: 0.8em;">System Health Monitoring</div>
                                </div>
                            </li>
                            <li style="margin-bottom: 15px; display: flex; align-items: center;">
                                <span style="margin-right: 10px;">⚪</span>
                                <div>
                                    <strong style="color: #9ca3af;">Level 10: Orchestration</strong>
                                    <div style="color: #4b5563; font-size: 0.8em;">Full Airflow DAGs</div>
                                </div>
                            </li>
                        </ul>
                    </div>
                    """
                )
        

