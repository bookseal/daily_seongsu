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
        
        # NEW: Phase/Level/Step Hierarchy Table
        gr.Markdown("## 📚 MLOps Roadmap: Phase → Level → Step")
        
        gr.HTML(
            """
            <style>
                .roadmap-table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                .roadmap-table th, .roadmap-table td { padding: 12px; text-align: left; border-bottom: 1px solid #374151; }
                .roadmap-table th { background-color: #1f2937; color: #9ca3af; font-weight: 600; }
                .roadmap-table tr:hover { background-color: rgba(96, 165, 250, 0.1); }
                .phase-1 { color: #60a5fa; }
                .phase-2 { color: #f472b6; }
                .phase-3 { color: #34d399; }
                .status-done { color: #10b981; }
                .status-wip { color: #f59e0b; }
                .status-planned { color: #6b7280; }
                .clickable { cursor: pointer; text-decoration: underline; }
            </style>
            
            <table class="roadmap-table">
                <thead>
                    <tr>
                        <th>Phase</th>
                        <th>Level</th>
                        <th>Name</th>
                        <th>Steps</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    <!-- Phase 1: Foundation -->
                    <tr onclick="switchTab('tab-p1', 'tab-l1')">
                        <td rowspan="3" class="phase-1" style="font-weight: bold; vertical-align: top;">🏗️ P1: Foundation</td>
                        <td class="clickable phase-1">L1</td>
                        <td>Cloud Data Engineering</td>
                        <td>Supabase Setup, Seoul API, Upsert Logic</td>
                        <td class="status-done">✅ Done</td>
                    </tr>
                    <tr onclick="switchTab('tab-p1', 'tab-l2')">
                        <td class="clickable phase-1">L2</td>
                        <td>Preprocessing Pipeline</td>
                        <td>Weather Backfill, Lag/Rolling, Feature Store</td>
                        <td class="status-done">✅ Done</td>
                    </tr>
                    <tr onclick="switchTab('tab-p1', 'tab-l3')">
                        <td class="clickable phase-1">L3</td>
                        <td>Data Quality Assurance</td>
                        <td>Feature Observer, Distribution Monitoring</td>
                        <td class="status-done">✅ Done</td>
                    </tr>
                    
                    <!-- Phase 2: Acceleration -->
                    <tr onclick="switchTab('tab-p2', 'tab-l4')">
                        <td rowspan="3" class="phase-2" style="font-weight: bold; vertical-align: top;">🚀 P2: Acceleration</td>
                        <td class="clickable phase-2">L4</td>
                        <td>AutoML</td>
                        <td>PyCaret Setup, Model Compare, Tuning</td>
                        <td class="status-done">✅ Done</td>
                    </tr>
                    <tr onclick="switchTab('tab-p2', 'tab-l5')">
                        <td class="clickable phase-2">L5</td>
                        <td>Infrastructure as Code</td>
                        <td>Dockerfile, Compose, Volumes</td>
                        <td class="status-done">✅ Done</td>
                    </tr>
                    <tr onclick="switchTab('tab-p2', 'tab-l6')">
                        <td class="clickable phase-2">L6</td>
                        <td>CI/CD Pipeline</td>
                        <td>GitHub Actions, Testing, Auto-Deploy</td>
                        <td class="status-planned">⚪ Planned</td>
                    </tr>
                    
                    <!-- Phase 3: Operation -->
                    <tr onclick="switchTab('tab-p3', 'tab-l7')">
                        <td rowspan="4" class="phase-3" style="font-weight: bold; vertical-align: top;">⚙️ P3: Operation</td>
                        <td class="clickable phase-3">L7</td>
                        <td>Experiment Tracking</td>
                        <td>MLflow Setup, Metrics, Registry</td>
                        <td class="status-planned">⚪ Planned</td>
                    </tr>
                    <tr onclick="switchTab('tab-p3', 'tab-l8')">
                        <td class="clickable phase-3">L8</td>
                        <td>Data Versioning</td>
                        <td>DVC Init, Remote Storage, History</td>
                        <td class="status-planned">⚪ Planned</td>
                    </tr>
                    <tr onclick="switchTab('tab-p3', 'tab-l9')">
                        <td class="clickable phase-3">L9</td>
                        <td>System Observability</td>
                        <td>Health API, Alerting, Latency Dashboard</td>
                        <td class="status-planned">⚪ Planned</td>
                    </tr>
                    <tr onclick="switchTab('tab-p3', 'tab-l10')">
                        <td class="clickable phase-3">L10</td>
                        <td>Orchestration</td>
                        <td>Airflow DAGs, Dependencies, Lifecycle</td>
                        <td class="status-planned">⚪ Planned</td>
                    </tr>
                </tbody>
            </table>
            """
        )
        
        gr.Markdown("<br>")
        
        # Quick Navigation Cards (3 Phases)
        gr.Markdown("### 🚀 Quick Navigation")
        with gr.Row():
            # Phase 1
            with gr.Column(scale=1, min_width=300):
                gr.HTML(
                    """
                    <div style="background-color: #1f2937; padding: 20px; border-radius: 10px; height: 100%;">
                        <h3 style="color: #60a5fa; margin-bottom: 10px;">🏗️ Phase 1: Foundation</h3>
                        <p style="color: #9ca3af; font-size: 0.9em;">Levels 1-3 • Data Engine & Basic UI</p>
                        <ul style="list-style: none; padding: 0; margin-top: 15px;">
                            <li style="margin: 8px 0;"><span style="color: #10b981;">✅</span> L1: Cloud Data Engineering</li>
                            <li style="margin: 8px 0;"><span style="color: #10b981;">✅</span> L2: Preprocessing Pipeline</li>
                            <li style="margin: 8px 0;"><span style="color: #10b981;">✅</span> L3: Data Quality Assurance</li>
                        </ul>
                    </div>
                    """
                )

            # Phase 2
            with gr.Column(scale=1, min_width=300):
                gr.HTML(
                    """
                    <div style="background-color: #1f2937; padding: 20px; border-radius: 10px; height: 100%;">
                        <h3 style="color: #f472b6; margin-bottom: 10px;">🚀 Phase 2: Acceleration</h3>
                        <p style="color: #9ca3af; font-size: 0.9em;">Levels 4-6 • Automation & Deployment</p>
                        <ul style="list-style: none; padding: 0; margin-top: 15px;">
                            <li style="margin: 8px 0;"><span style="color: #10b981;">✅</span> L4: AutoML</li>
                            <li style="margin: 8px 0;"><span style="color: #10b981;">✅</span> L5: Infrastructure as Code</li>
                            <li style="margin: 8px 0;"><span style="color: #6b7280;">⚪</span> L6: CI/CD Pipeline</li>
                        </ul>
                    </div>
                    """
                )

            # Phase 3
            with gr.Column(scale=1, min_width=300):
                gr.HTML(
                    """
                    <div style="background-color: #1f2937; padding: 20px; border-radius: 10px; height: 100%;">
                        <h3 style="color: #34d399; margin-bottom: 10px;">⚙️ Phase 3: Operation</h3>
                        <p style="color: #9ca3af; font-size: 0.9em;">Levels 7-10 • Reliability & Scale</p>
                        <ul style="list-style: none; padding: 0; margin-top: 15px;">
                            <li style="margin: 8px 0;"><span style="color: #6b7280;">⚪</span> L7: Experiment Tracking</li>
                            <li style="margin: 8px 0;"><span style="color: #6b7280;">⚪</span> L8: Data Versioning</li>
                            <li style="margin: 8px 0;"><span style="color: #6b7280;">⚪</span> L9: Observability</li>
                            <li style="margin: 8px 0;"><span style="color: #6b7280;">⚪</span> L10: Orchestration</li>
                        </ul>
                    </div>
                    """
                )
