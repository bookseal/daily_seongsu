import gradio as gr
import os
import sys
import pandas as pd
from dotenv import load_dotenv

# Path setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from crawler.verify_apis import verify_seoul_data, verify_kma_data, verify_supabase_connection
from crawler.storage_supabase import SupabaseStorage

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'crawler', '.env'))

# --- 1. HELPER FUNCTIONS ---
def check_apis():
    res_seoul = verify_seoul_data()
    res_kma = verify_kma_data()
    res_supa = verify_supabase_connection()
    
    status = f"SEOUL: {'✅' if res_seoul else '❌'}\n"
    status += f"KMA: {'✅' if res_kma else '❌'}\n"
    status += f"SUPABASE: {'✅' if res_supa else '❌'}"
    return status

def fetch_db_data():
    try:
        storage = SupabaseStorage()
        if not storage.client: 
            err = pd.DataFrame({"Error": ["Supabase not connected"]})
            return err, err

        res_sub = storage.client.table("subway_traffic").select("*").limit(5).order("date", desc=True).execute()
        res_wea = storage.client.table("weather_data").select("*").limit(5).order("measured_at", desc=True).execute()
        
        return (pd.DataFrame(res_sub.data) if res_sub.data else pd.DataFrame({"Status": ["No Data"]})), \
               (pd.DataFrame(res_wea.data) if res_wea.data else pd.DataFrame({"Status": ["No Data"]}))
    except Exception as e:
        err_df = pd.DataFrame({"Error": [str(e)]})
        return err_df, err_df

def read_code(filename):
    try:
        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), filename), "r") as f:
            return f.read()
    except: return "Error reading file"

CODE_VERIFY = read_code("crawler/verify_apis.py")
CODE_STORAGE = read_code("crawler/storage_supabase.py")

# --- 2. MERMAID & HTML ---
MERMAID_SCRIPT = """
<script type="module">
    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
    mermaid.initialize({ startOnLoad: false });
    function renderMermaid() { mermaid.run({ querySelector: '.mermaid' }); }
    const observer = new MutationObserver(() => { renderMermaid(); });
    document.addEventListener('DOMContentLoaded', () => {
        renderMermaid();
        observer.observe(document.body, { childList: true, subtree: true });
    });
    setInterval(renderMermaid, 1000);
</script>
"""

# --- 3. TEXT CONTENT (LOGS & ROADMAP) ---

HTML_VERIFY_FLOW = """
<div class="mermaid">
graph LR
    Start[Start] --> Check{".env Keys?"}
    Check -->|Yes| Request[API Request]
    Request --> Parse{"Valid JSON?"}
    Parse -->|Yes| OK["✅ Success"]
    Parse -->|No| Fail["❌ Error"]
    
    OK --> SupaCheck{"Supabase Connection?"}
    SupaCheck -->|Yes| SupaOK["✅ DB Connected"]
    SupaCheck -->|No| SupaFail["❌ DB Error"]
</div>
"""

HTML_STORAGE_FLOW = """
<div class="mermaid">
graph LR
    Input[Data] --> Connection{"Client Init"}
    Connection --> Process[Formatting]
    Process --> Upsert["Upsert (Date+Line+Station)"]
    Upsert --> DB[("(Supabase DB)")]
</div>
"""

MD_TOC = """
### 📚 MLOps Roadmap Navigation
1. [**Level 1: Cloud Data Engineering**](#level-1-cloud-data-engineering-complete) (✅ Complete)
2. [Level 2: Data Preprocessing](#level-2-data-warehouse-preprocessing) (TODO)
3. [Level 3: Dual-Purpose UI](#level-3-dual-purpose-ui-gradio) (In Progress)
4. [Level 4: AutoML](#level-4-automl-hyperparameter-tuning)
5. [Level 5: Containerization](#level-5-infrastructure-as-code-docker)
6. [Level 6: CI/CD](#level-6-cicd-pipeline-github-actions)
7. [Level 7: MLflow](#level-7-experiment-tracking-mlflow)
8. [Level 8: DVC](#level-8-data-versioning-dvc)
9. [Level 9: Observability](#level-9-system-observability)
10. [Level 10: Orchestration](#level-10-full-orchestration-airflow)
"""

MD_LEVEL1 = """
<h2 id="level-1-cloud-data-engineering-complete">🟢 Level 1: Cloud Data Engineering (Complete)</h2>

**Objective**: Migrate from local file storage to a scalable Cloud Database (**Supabase**).

### 📝 Key Learnings (from Logs)
1.  **Environment Security**: API Keys are never hardcoded. Used `.env` and `python-dotenv`.
2.  **Supabase & PostgreSQL**: 
    - Replaced `CSV/JSON` with Relational Tables (`subway_traffic`, `weather_data`).
    - Used **SQL** for schema definition.
3.  **Upsert Strategy**:
    - **Problem**: Running the crawler daily creates duplicates.
    - **Solution**: Used `upsert` (Update or Insert) based on unique keys (`date` + `line` + `station`).
4.  **Hardware**: Hosted on **OCI Ampere A1** (ARM64).
"""

MD_LEVEL2 = """
<h2 id="level-2-data-warehouse-preprocessing">🟡 Level 2: Data Warehouse & Preprocessing</h2>

**Goal**: Create a clean, ML-ready dataset.
- **Plan**:
    - Load data from Supabase using `Pandas`.
    - Handle missing values (e.g., sensor failures).
    - Feature Engineering: Add `is_holiday`, `weather_severity` scores.
"""

MD_LEVEL3 = """
<h2 id="level-3-dual-purpose-ui-gradio">⚪ Level 3: Dual-Purpose UI (Gradio)</h2>

**Goal**: Unified Interface for Recruiter (Guide) and User (Service).
- **Current Status**: We are here! Building this interactive Guidebook.
"""

MD_LEVEL4 = """
<h2 id="level-4-automl-hyperparameter-tuning">⚪ Level 4: AutoML & Hyperparameter Tuning</h2>

**Goal**: Maximize model performance with minimal manual effort.
- **Tools**: PyCaret, Optuna.
"""

MD_LEVEL5 = """
<h2 id="level-5-infrastructure-as-code-docker">⚪ Level 5: Infrastructure as Code (Docker)</h2>

**Goal**: Portability and Reproducibility.
- **Plan**: `docker-compose.yml` for Airflow, MLflow, and Gradio.
"""

MD_LEVEL6 = """
<h2 id="level-6-cicd-pipeline-github-actions">⚪ Level 6: CI/CD Pipeline (GitHub Actions)</h2>

**Goal**: Automated Testing & Deployment.
- **Trigger**: Push to `main`.
- **Action**: Run tests on Runner -> Deploy to OCI.
"""

MD_LEVEL7 = """
<h2 id="level-7-experiment-tracking-mlflow">⚪ Level 7: Experiment Tracking (MLflow)</h2>

**Goal**: Manage model lifecycle.
- **Plan**: Centralized MLflow server on OCI. Track `RMSE`, `MAE`.
"""

MD_LEVEL8 = """
<h2 id="level-8-data-versioning-dvc">⚪ Level 8: Data Versioning (DVC)</h2>

**Goal**: Version Control for Datasets.
- **Concept**: "Git for Data". Connects code versions to specific data snapshots.
"""

MD_LEVEL9 = """
<h2 id="level-9-system-observability">⚪ Level 9: System Observability</h2>

**Goal**: Monitor System Health.
- **Plan**: Show Real-time API Latency and Airflow DAG status directly on this UI.
"""

MD_LEVEL10 = """
<h2 id="level-10-full-orchestration-airflow">⚪ Level 10: Full Orchestration (Airflow)</h2>

**Goal**: End-to-End Automation.
- **Workflow**: Ingest -> Process -> Train -> Evaluate -> Deploy.
"""

# --- 4. APP LAYOUT ---
JS_DARK_MODE = """
function() {
    document.body.classList.add('dark');
    document.querySelector('gradio-app').classList.add('dark');
}
"""

with gr.Blocks(title="Daily Seongsu Guidebook", head=MERMAID_SCRIPT, js=JS_DARK_MODE, theme=gr.themes.Soft()) as app:
    gr.Markdown("# 🚇 Daily Seongsu: Senior MLOps Portfolio")
    gr.Markdown("**Architect**: Antigravity | **Platform**: OCI + Supabase + Hugging Face")
    
    # Table of Contents
    with gr.Accordion("🗺️ Roadmap Navigation (Click to Jump)", open=True):
        gr.Markdown(MD_TOC)
    
    gr.Markdown("---")

    # --- LEVEL 1 CONTENT ---
    gr.Markdown(MD_LEVEL1) # Changed HTML to Markdown to render **bold**
    
    with gr.Group():
        gr.Markdown("### 🛠️ Interactive Lab: Verify Data Pipeline")
        
        # STEP 1
        with gr.Group():
            gr.Markdown("#### Step 1: API Connectivity")
            gr.HTML(HTML_VERIFY_FLOW) # Keep HTML for Mermaid div
            
            with gr.Accordion("📜 View Source Code: verify_apis.py", open=False):
                gr.Code(CODE_VERIFY, language="python", lines=10)
                
            btn_check = gr.Button("▶ Run Verification", size="sm", variant="secondary")
            out_status = gr.Textbox(label="Result", lines=2)
            btn_check.click(check_apis, [], out_status)

        # STEP 2
        with gr.Group():
            gr.Markdown("#### Step 2: Supabase Storage")
            gr.HTML(HTML_STORAGE_FLOW) # Keep HTML for Mermaid div
            
            with gr.Accordion("📜 View Source Code: storage_supabase.py", open=False):
                gr.Code(CODE_STORAGE, language="python", lines=15)
                
            btn_fetch = gr.Button("▶ Fetch Live Data", size="sm", variant="secondary")
            out_sub = gr.Dataframe(label="Subway Stats")
            out_wea = gr.Dataframe(label="Weather Stats")
            btn_fetch.click(fetch_db_data, [], [out_sub, out_wea])
    
    gr.Markdown("---")
    
    # --- LEVEL 2-10 CONTENT ---
    # Change HTML to Markdown
    gr.Markdown(MD_LEVEL2)
    gr.Markdown("---")
    gr.Markdown(MD_LEVEL3)
    gr.Markdown("---")
    gr.Markdown(MD_LEVEL4)
    gr.Markdown("---")
    gr.Markdown(MD_LEVEL5)
    gr.Markdown("---")
    gr.Markdown(MD_LEVEL6)
    gr.Markdown("---")
    gr.Markdown(MD_LEVEL7)
    gr.Markdown("---")
    gr.Markdown(MD_LEVEL8)
    gr.Markdown("---")
    gr.Markdown(MD_LEVEL9)
    gr.Markdown("---")
    gr.Markdown(MD_LEVEL10)
    gr.Markdown("---")
    gr.Markdown("© 2026 Daily Seongsu Project")

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860)
