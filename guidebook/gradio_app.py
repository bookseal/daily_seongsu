import gradio as gr
import os
import sys
import pandas as pd
from dotenv import load_dotenv

# Path setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from crawler.verify_apis import verify_seoul_data, verify_kma_data, verify_supabase_connection
from crawler.storage_supabase import SupabaseStorage
from crawler.pipeline import DataPipeline
from crawler.backfill_subway import run_subway_backfill
from crawler.backfill_weather import run_weather_backfill
from crawler.check_status import check_readiness_stats, get_data_preview

# Instantiate Pipeline (Stateful)
pipeline = DataPipeline()

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

def trigger_subway(start, end):
    logs = ""
    for chunk in run_subway_backfill(start, end):
        logs += chunk
        yield logs

def trigger_weather(start, end):
    logs = ""
    for chunk in run_weather_backfill(start, end):
        logs += chunk
        yield logs

def check_readiness_and_preview():
    status = check_readiness_stats()
    df = get_data_preview()
    return status, df

def read_code(filename):
    try:
        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), filename), "r") as f:
            return f.read()
    except: return "Error reading file"

CODE_VERIFY = read_code("crawler/verify_apis.py")
CODE_STORAGE = read_code("crawler/storage_supabase.py")
CODE_BACKFILL = read_code("crawler/backfill_subway.py")
CODE_WEATHER = read_code("crawler/backfill_weather.py")
CODE_CHECK = read_code("crawler/check_status.py")
CODE_PIPELINE = read_code("crawler/pipeline.py")

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

HTML_BACKFILL_FLOW = """
<div class="mermaid">
graph LR
    User[User Click] --> Check{Inputs Valid?}
    Check -->|Yes| Trigger[trigger_backfill]
    Trigger --> Gen[Generator Loop]
    Gen --> Fetch[SeoulSubwayCollector<br>.fetch_daily_passenger_count]
    Gen --> Save[SupabaseStorage<br>.save_subway_data]
    Save --> Yield[Subway Log]
</div>
"""

HTML_READINESS_FLOW = """
<div class="mermaid">
graph LR
    User[User Click] --> Call[check_readiness_and_preview]
    Call --> Stats[check_readiness_stats]
    Call --> Preview[get_data_preview]
    Stats --> Count["Supabase...select(count)"]
    Preview --> Fetch["Supabase...select(limit)"]
    Count --> UI1[Status Textbox]
    Fetch --> UI2[Dataframe]
</div>
"""

HTML_PIPELINE_FLOW = """
<div class="mermaid">
graph TD
    A[Raw Data] --> B{DataPipeline.run()};
    B --> C[step_6_calendar_features];
    C --> D[step_7_data_integration];
    D --> E[step_8_feature_generation];
    E --> F[step_9_save_features];
    F --> G[ML-Ready Features];
</div>
"""

# --- 3. APP LAYOUT ---
JS_DARK_MODE = """
function() {
    document.body.classList.add('dark');
    document.querySelector('gradio-app').classList.add('dark');
}
"""

with gr.Blocks(title="Daily Seongsu Guidebook", head=MERMAID_SCRIPT, js=JS_DARK_MODE, theme=gr.themes.Soft()) as app:
    # Header
    gr.Markdown("# 🚇 Daily Seongsu: Senior MLOps Portfolio")
    gr.Markdown("**Architect**: Antigravity | **Platform**: OCI + Supabase + Hugging Face")
    
    # Table of Contents
    with gr.Accordion("🗺️ Roadmap Navigation (Levels 1-10)", open=True):
        gr.Markdown("""
        1. [**Level 1: Cloud Data Engineering**](#level-1) (✅ Complete)
        2. [**Level 2: Data Preprocessing**](#level-2) (🟡 In Progress)
        3. [Level 3: Dual-Purpose UI](#level-3)
        4. [Level 4: AutoML](#level-4)
        5. [Level 5: Containerization](#level-5)
        6. [Level 6: CI/CD](#level-6)
        7. [Level 7: MLflow](#level-7)
        8. [Level 8: DVC](#level-8)
        9. [Level 9: Observability](#level-9)
        10. [Level 10: Orchestration](#level-10)
        """)
    
    gr.Markdown("---")
    
    # LEVEL 1 HEADER (Colored Box via Info)
    with gr.Group(elem_id="level-1"):
        gr.Markdown("## 🟢 Level 1: Cloud Data Engineering")
        gr.Info("Objective: Migrate from local file storage to a scalable Cloud Database (Supabase) and establish a robust Data Pipeline.")
        
        # Key Learnings (Expanded, No Toggle)
        gr.Markdown("### 📝 Key Learnings")
        gr.Markdown("""
        1. **Environment Security**: API Keys are never hardcoded. Used `.env` and `python-dotenv`.
        2. **Supabase & PostgreSQL**: Replaced `CSV/JSON` with Relational Tables using SQL schema.
        3. **Upsert Strategy**: Implemented `upsert` (Update or Insert) based on unique keys to prevent duplicates.
        4. **Hardware**: Hosted on **OCI Ampere A1** (ARM64).
        """)

    gr.Markdown("<br><br>")
    
    # STEP 1
    gr.Markdown("## Step 1: API Connectivity Check")
    gr.Markdown("Verify that our server can talk to External APIs and our Database.")
    gr.HTML(HTML_VERIFY_FLOW)
    
    # Source Code (Stacked, Above Buttons)
    with gr.Accordion("📜 Source Code: verify_apis.py", open=False):
        gr.Code(CODE_VERIFY, language="python", lines=10)
    
    btn_check = gr.Button("▶ Run Verification", size="lg", variant="secondary")
    out_status = gr.Textbox(label="Result", lines=3)
    btn_check.click(check_apis, [], out_status)

    gr.Markdown("<br><br>")
    gr.Markdown("---")
    gr.Markdown("<br><br>")

    # STEP 2
    gr.Markdown("## Step 2: Supabase Storage Check")
    gr.Markdown("Check if we can read/write to the Cloud Database.")
    gr.HTML(HTML_STORAGE_FLOW)
    
    with gr.Accordion("📜 Source Code: storage_supabase.py", open=False):
        gr.Code(CODE_STORAGE, language="python", lines=15)

    btn_fetch = gr.Button("▶ Fetch Live Data", size="lg", variant="secondary")
    with gr.Row():
        out_sub = gr.Dataframe(label="Subway Stats", height=200)
        out_wea = gr.Dataframe(label="Weather Stats", height=200)
    btn_fetch.click(fetch_db_data, [], [out_sub, out_wea])

    gr.Markdown("<br><br>")
    gr.Markdown("---")
    gr.Markdown("<br><br>")


    # STEP 3
    gr.Markdown("## Step 3: Subway Data Backfill (Target Y)")
    gr.Markdown("**Action**: Collect **Daily Passengers** (Target Variable).")
    gr.HTML(HTML_BACKFILL_FLOW.replace("Yield Log", "Subway Log"))
    
    with gr.Accordion("📜 Source Code: backfill_subway.py", open=False):
        gr.Code(CODE_BACKFILL, language="python", lines=15)
        
    with gr.Row():
        inp_start_sub = gr.Textbox(label="Start Date", value="20220101")
        inp_end_sub = gr.Textbox(label="End Date", value="20251231")
        
    btn_subway = gr.Button("▶ Start Subway Backfill", size="lg", variant="primary")
    out_subway = gr.Textbox(label="Subway Logs", lines=10)
    
    btn_subway.click(trigger_subway, [inp_start_sub, inp_end_sub], out_subway)

    gr.Markdown("<br><br>")
    gr.Markdown("---")
    gr.Markdown("<br><br>")

    # STEP 4: WEATHER
    gr.Markdown("## Step 4: Weather Data Backfill (Feature X)")
    gr.Markdown("**Action**: Collect **Temperature & Rain** (Input Features) from Open-Meteo.")
    
    with gr.Accordion("📜 Source Code: backfill_weather.py", open=False):
        gr.Code(CODE_WEATHER, language="python", lines=15)
        
    with gr.Row():
        inp_start_wea = gr.Textbox(label="Start Date", value="20220101")
        inp_end_wea = gr.Textbox(label="End Date", value="20251231")
        
    btn_weather = gr.Button("▶ Start Weather Backfill", size="lg", variant="primary")
    out_weather = gr.Textbox(label="Weather Logs", lines=10)
    
    btn_weather.click(trigger_weather, [inp_start_wea, inp_end_wea], out_weather)

    gr.Markdown("<br><br>")
    gr.Markdown("---")
    gr.Markdown("<br><br>")

    # STEP 5
    gr.Markdown("## Step 5: Level 2 Readiness Check")
    gr.Markdown("**Question**: Do we have enough Data (X and Y) to train?")
    gr.Markdown("""
    **Supabase**: [Link to Dashboard](https://supabase.com/dashboard/project/_/editor) (Requires Login)
    *(Note: Supabase tables are private by default. You need to log in to view raw data on the web.)*
    """)
    gr.HTML(HTML_READINESS_FLOW)
    
    with gr.Accordion("📜 Source Code: check_status.py", open=False):
        gr.Code(CODE_CHECK, language="python", lines=15)

    btn_ready = gr.Button("▶ Check Readiness (X + Y)", size="lg", variant="secondary")
    
    with gr.Row():
        out_ready_status = gr.Textbox(label="Status Report", lines=4)
        out_ready_df = gr.Dataframe(label="Subway Data Preview", height=300, wrap=True)
    
    btn_ready.click(check_readiness_and_preview, [], [out_ready_status, out_ready_df])

    gr.Markdown("<br><br>")
    gr.Markdown("---")
    gr.Markdown("<br><br>")

    # LEVEL 2 HEADER
    with gr.Group(elem_id="level-2"):
        gr.Markdown("## 🟡 Level 2: Data Preprocessing & Feature Engineering")
        gr.Info("Objective: Transform raw data into ML-ready features (Lags, Calendar, Weather).")
        
        gr.Markdown("### 📝 Planned Steps")
        gr.Markdown("""
        1. **Calendar Features**: Add Holidays, Weekends.
        2. **Data Integration**: Merge Subway (Y) and Weather (X).
        3. **Feature Generation**: Create Lags (t-1, t-7) and Rolling Averages.
        4. **Feature Store**: Save processed data to `model_features` table.
        """)

    gr.Markdown("<br><br>")

    # STEP 6: Calendar
    gr.Markdown("## Step 6: Calendar Engineering")
    gr.Markdown("**Action**: Enrich data with `is_holiday`, `is_weekend`, `day_of_week`.")
    gr.HTML("""
    <div class="mermaid">
    graph LR
        Date[Date Column] --> Holidays{Is Holiday?}
        Date --> Weekend{Is Weekend?}
        Holidays -->|Yes/No| Features[New Columns]
        Weekend -->|Yes/No| Features
    </div>
    """)
    btn_cal = gr.Button("▶ Generate Calendar Features", size="lg", variant="secondary")
    out_cal = gr.Dataframe(label="Calendar Preview", height=200)
    
    btn_cal.click(pipeline.step_6_calendar, [], out_cal)

    gr.Markdown("<br><br>")

    # STEP 7: Integration
    gr.Markdown("## Step 7: Data Integration (Merge)")
    gr.Markdown("**Action**: Join Subway Traffic with Weather History on `date`.")
    gr.HTML("""
    <div class="mermaid">
    graph LR
        Sub[Subway Data] --> Join{Merge on Date}
        Wea[Weather Data] --> Join
        Join --> Clean[Drop NaNs]
        Clean --> Unified[Unified DataFrame]
    </div>
    """)
    
    with gr.Accordion("📜 Source Code: pipeline.py", open=False):
        gr.Code(CODE_PIPELINE, language="python", lines=15)
        
    btn_merge = gr.Button("▶ Merge Datasets", size="lg", variant="secondary")
    with gr.Row():
        out_merge_status = gr.Textbox(label="Merge Status", lines=2)
        out_merge_df = gr.Dataframe(label="Merged Data Preview", height=200)
    
    btn_merge.click(pipeline.step_7_merge, [], [out_merge_status, out_merge_df])

    gr.Markdown("<br><br>")

    # STEP 8: Features
    gr.Markdown("## Step 8: Feature Generation (Lag & Rolling)")
    gr.Markdown("""
    **Concept**: Time-series models require "memory" to predict the future. We transform historical data into new features to provide temporal context.

    ### 1. Lag Features (Historical Snapshots)
    * **Lag (t-1)**: Capture the immediate continuity (Yesterday's traffic).
    * **Lag (t-7)**: Capture weekly seasonality (Same day last week).
    * **Lag (t-364)**: Capture yearly seasonality (52 weeks ago, Day-of-Week aligned).

    ### 2. Rolling Window Features (Trend Analysis)
    * **7d Rolling Avg**: Smooth out daily noise and capture the general "vibe" or trend of the past week.

    ### 3. Calendar Encoding
    * **Day of Week & Week Number**: Help the model learn general human behavior patterns.
    """)
    gr.HTML("""
    <div class="mermaid">
    graph LR
        Unified["Unified Data"] --> Sort["Sort by Date"]
        Sort --> Lag1["Lag (t-1)<br>(Daily)"]
        Sort --> Lag7["Lag (t-7)<br>(Weekly)"]
        Sort --> Lag364["Lag (t-364)<br>(Yearly)"]
        Sort --> Roll["Rolling (7d)<br>(Trend)"]
        Lag1 --> Final["Feature Set"]
        Lag7 --> Final
        Lag364 --> Final
        Roll --> Final
    </div>
    """)
    btn_feat = gr.Button("▶ Generate Features", size="lg", variant="secondary")
    with gr.Row():
        out_feat_status = gr.Textbox(label="Feature Stats", lines=2)
        out_feat_df = gr.Dataframe(label="Feature Preview", height=200)
        
    btn_feat.click(pipeline.step_8_features, [], [out_feat_status, out_feat_df])

    gr.Markdown("<br><br>")

    # STEP 9: Store
    gr.Markdown("## Step 9: Feature Store Provisioning & Integrity Check")
    gr.Markdown("""
    **Action**: Beyond simple uploading, we establish a **Feature Store** to bridge the gap between Data Engineering and Model Training.

    ### 1. Automated Schema Validation
    * Ensure no `Null` values exist in critical columns (Lags, Rolling Averages).
    * Validate data ranges (e.g., Traffic count must be $\ge 0$).

    ### 2. Feature Versioning & Metadata
    * Tag each dataset with a **Version ID** linked to the pipeline logic.
    * This ensures **Reproducibility**.

    ### 3. Seamless Integration with Supabase
    * Use `Upsert` logic to maintain a single source of truth without duplicates.
    * **Ready-for-Training**: The `model_features` table is now optimized for the AutoML pipeline in Level 4.
    """)
    gr.HTML("""
    <div class="mermaid">
    graph LR
        Final["Feature Set"] --> Validate{"Schema Check"}
        Validate -->|Pass| Version["Add Metadata<br>(Version ID)"]
        Validate -->|Fail| Alert["❌ Drop/Warn"]
        Version --> Upsert["Supabase Upsert"]
        Upsert --> Store[("Feature Store<br>model_features")]
        Store --> AutoML[("Ready for Level 4<br>AutoML")]
    </div>
    """)
    btn_store = gr.Button("▶ Upload to Feature Store", size="lg", variant="secondary")
    out_store = gr.Textbox(label="Upload Log", lines=4)
    
    btn_store.click(pipeline.step_9_store, [], out_store)

    gr.Markdown("<br><br>")

    # STEP 10: Verify
    gr.Markdown("## Step 10: Cloud Database Verification (Live Query)")
    gr.Markdown("""
    **Action**: Query the actual `model_features` table in Supabase (not local cache).
    
    **Expected Results**:
    1. **Connection**: Successful read from Supabase.
    2. **Row Count**: Should match Step 9 (e.g., **636 rows**).
    3. **Schema**: confirm `lag_364d` and `version_id` columns exist.
    """)
    
    btn_verify_final = gr.Button("▶ Run Final Integrity Check", size="lg", variant="primary")
    with gr.Row():
        out_verify_msg = gr.Textbox(label="Verification Report", lines=3)
        out_verify_df = gr.Dataframe(label="Live DB Preview")
    
    btn_verify_final.click(pipeline.step_10_verify, [], [out_verify_msg, out_verify_df])

    gr.Markdown("<br><br><br>")
    gr.Markdown("---")
    gr.Markdown("© 2026 Daily Seongsu Project")

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860)
