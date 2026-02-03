import gradio as gr
import pandas as pd
import os
import sys
from crawler.verify_apis import verify_seoul_data, verify_kma_data, verify_supabase_connection
from crawler.storage_supabase import SupabaseStorage
from crawler.backfill_subway import run_subway_backfill
from crawler.backfill_weather import run_weather_backfill
from crawler.check_status import check_readiness_stats, get_data_preview

# --- HELPER FUNCTIONS ---
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
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        with open(os.path.join(base_path, filename), "r") as f:
            return f.read()
    except: return "Error reading file"

# --- MERMAID & HTML CONSTANTS ---
HTML_VERIFY_FLOW = """<div class="mermaid">
graph LR
    Start[Start] --> Check{".env Keys?"}
    Check -->|Yes| Request[API Request]
    Request --> Parse{"Valid JSON?"}
    Parse -->|Yes| OK["✅ Success"]
    Parse -->|No| Fail["❌ Error"]
    OK --> SupaCheck{"Supabase Connection?"}
    SupaCheck -->|Yes| SupaOK["✅ DB Connected"]
    SupaCheck -->|No| SupaFail["❌ DB Error"]
</div>"""

HTML_STORAGE_FLOW = """<div class="mermaid">
graph LR
    Input[Data] --> Connection{"Client Init"}
    Connection --> Process[Formatting]
    Process --> Upsert["Upsert (Date+Line+Station)"]
    Upsert --> DB[("(Supabase DB)")]
</div>"""

HTML_BACKFILL_FLOW = """<div class="mermaid">
graph LR
    User[User Click] --> Check{Inputs Valid?}
    Check -->|Yes| Trigger[trigger_backfill]
    Trigger --> Gen[Generator Loop]
    Gen --> Fetch[SeoulSubwayCollector<br>.fetch_daily_passenger_count]
    Gen --> Save[SupabaseStorage<br>.save_subway_data]
    Save --> Yield[Subway Log]
</div>"""

HTML_READINESS_FLOW = """<div class="mermaid">
graph LR
    User[User Click] --> Call[check_readiness_and_preview]
    Call --> Stats[check_readiness_stats]
    Call --> Preview[get_data_preview]
    Stats --> Count["Supabase...select(count)"]
    Preview --> Fetch["Supabase...select(limit)"]
    Count --> UI1[Status Textbox]
    Fetch --> UI2[Dataframe]
</div>"""

def create_pipeline_controls(pipeline):
    # LEVEL 1 HEADER
    with gr.Group(elem_id="level-1"):
        gr.Markdown("## 🟢 Level 1: Cloud Data Engineering")
        gr.Info("Objective: Migrate from local file storage to a scalable Cloud Database (Supabase) and establish a robust Data Pipeline.")
        gr.Markdown("""### 📝 Key Learnings
        1. **Environment Security**: API Keys are never hardcoded. Used `.env` and `python-dotenv`.
        2. **Supabase & PostgreSQL**: Replaced `CSV/JSON` with Relational Tables using SQL schema.
        3. **Upsert Strategy**: Implemented `upsert` (Update or Insert) based on unique keys to prevent duplicates.
        4. **Hardware**: Hosted on **OCI Ampere A1** (ARM64).
        """)
        
    gr.Markdown("<br><br>")
    
    # STEP 1
    gr.Markdown("## Step 1: API Connectivity Check")
    gr.HTML(HTML_VERIFY_FLOW)
    with gr.Accordion("📜 Source Code: verify_apis.py", open=False):
        gr.Code(read_code("crawler/verify_apis.py"), language="python", lines=10)
    
    btn_check = gr.Button("▶ Run Verification", size="lg", variant="secondary")
    out_status = gr.Textbox(label="Result", lines=3)
    btn_check.click(check_apis, [], out_status)
    
    gr.HTML('<hr style="border: none; border-top: 1px solid #4b5563; margin: 48px 0;">')

    # STEP 2
    gr.Markdown("## Step 2: Supabase Storage Check")
    gr.HTML(HTML_STORAGE_FLOW)
    with gr.Accordion("📜 Source Code: storage_supabase.py", open=False):
        gr.Code(read_code("crawler/storage_supabase.py"), language="python", lines=15)

    btn_fetch = gr.Button("▶ Fetch Live Data", size="lg", variant="secondary")
    with gr.Row():
        out_sub = gr.Dataframe(label="Subway Stats", height=200)
        out_wea = gr.Dataframe(label="Weather Stats", height=200)
    btn_fetch.click(fetch_db_data, [], [out_sub, out_wea])
    
    gr.HTML('<hr style="border: none; border-top: 1px solid #4b5563; margin: 48px 0;">')

    # STEP 3
    gr.Markdown("## Step 3: Subway Data Backfill (Target Y)")
    gr.HTML(HTML_BACKFILL_FLOW.replace("Yield Log", "Subway Log"))
    with gr.Accordion("📜 Source Code: backfill_subway.py", open=False):
        gr.Code(read_code("crawler/backfill_subway.py"), language="python", lines=15)
        
    with gr.Row():
        inp_start_sub = gr.Textbox(label="Start Date", value="20220101")
        inp_end_sub = gr.Textbox(label="End Date", value="20251231")
    btn_subway = gr.Button("▶ Start Subway Backfill", size="lg", variant="primary")
    out_subway = gr.Textbox(label="Subway Logs", lines=10)
    btn_subway.click(trigger_subway, [inp_start_sub, inp_end_sub], out_subway)
    
    gr.HTML('<hr style="border: none; border-top: 1px solid #4b5563; margin: 48px 0;">')

    # STEP 4
    gr.Markdown("## Step 4: Weather Data Backfill (Feature X)")
    with gr.Accordion("📜 Source Code: backfill_weather.py", open=False):
        gr.Code(read_code("crawler/backfill_weather.py"), language="python", lines=15)
        
    with gr.Row():
        inp_start_wea = gr.Textbox(label="Start Date", value="20220101")
        inp_end_wea = gr.Textbox(label="End Date", value="20251231")
    btn_weather = gr.Button("▶ Start Weather Backfill", size="lg", variant="primary")
    out_weather = gr.Textbox(label="Weather Logs", lines=10)
    btn_weather.click(trigger_weather, [inp_start_wea, inp_end_wea], out_weather)
    
    gr.HTML('<hr style="border: none; border-top: 1px solid #4b5563; margin: 48px 0;">')

    # STEP 5
    gr.Markdown("## Step 5: Level 2 Readiness Check")
    gr.HTML(HTML_READINESS_FLOW)
    with gr.Accordion("📜 Source Code: check_status.py", open=False):
        gr.Code(read_code("crawler/check_status.py"), language="python", lines=15)
    btn_ready = gr.Button("▶ Check Readiness (X + Y)", size="lg", variant="secondary")
    with gr.Row():
        out_ready_status = gr.Textbox(label="Status Report", lines=4)
        out_ready_df = gr.Dataframe(label="Subway Data Preview", height=300, wrap=True)
    btn_ready.click(check_readiness_and_preview, [], [out_ready_status, out_ready_df])
    
    gr.HTML('<hr style="border: none; border-top: 1px solid #4b5563; margin: 48px 0;">')

    # LEVEL 2 HEADER
    with gr.Group(elem_id="level-2"):
        gr.Markdown("## 🟡 Level 2: Data Preprocessing & Feature Engineering")
        gr.Info("Objective: Transform raw data into ML-ready features (Lags, Calendar, Weather).")
        gr.Markdown("""### 📝 Planned Steps
        1. **Calendar Features**: Add Holidays, Weekends.
        2. **Data Integration**: Merge Subway (Y) and Weather (X).
        3. **Feature Generation**: Create Lags (t-1, t-7) and Rolling Averages.
        4. **Feature Store**: Save processed data to `model_features` table.
        """)

    gr.Markdown("<br><br>")

    # STEP 6
    gr.Markdown("## Step 6: Calendar Engineering")
    btn_cal = gr.Button("▶ Generate Calendar Features", size="lg", variant="secondary")
    out_cal = gr.Dataframe(label="Calendar Preview", height=200)
    btn_cal.click(pipeline.step_6_calendar, [], out_cal)
    
    gr.Markdown("<br><br>")

    # STEP 7
    gr.Markdown("## Step 7: Data Integration (Merge)")
    with gr.Accordion("📜 Source Code: pipeline.py", open=False):
        gr.Code(read_code("crawler/pipeline.py"), language="python", lines=15)
    btn_merge = gr.Button("▶ Merge Datasets", size="lg", variant="secondary")
    with gr.Row():
        out_merge_status = gr.Textbox(label="Merge Status", lines=2)
        out_merge_df = gr.Dataframe(label="Merged Data Preview", height=200)
    btn_merge.click(pipeline.step_7_merge, [], [out_merge_status, out_merge_df])
    
    gr.Markdown("<br><br>")

    # STEP 8
    gr.Markdown("## Step 8: Feature Generation (Lag & Rolling)")
    btn_feat = gr.Button("▶ Generate Features", size="lg", variant="secondary")
    with gr.Row():
        out_feat_status = gr.Textbox(label="Feature Stats", lines=2)
        out_feat_df = gr.Dataframe(label="Feature Preview", height=200)
    btn_feat.click(pipeline.step_8_features, [], [out_feat_status, out_feat_df])
    
    gr.Markdown("<br><br>")

    # STEP 9
    gr.Markdown("## Step 9: Feature Store Provisioning")
    btn_store = gr.Button("▶ Upload to Feature Store", size="lg", variant="secondary")
    out_store = gr.Textbox(label="Upload Log", lines=4)
    btn_store.click(pipeline.step_9_store, [], out_store)
    
    gr.Markdown("<br><br>")

    # STEP 10
    gr.Markdown("## Step 10: Cloud Database Verification")
    btn_verify_final = gr.Button("▶ Run Final Integrity Check", size="lg", variant="primary")
    with gr.Row():
        out_verify_msg = gr.Textbox(label="Verification Report", lines=3)
        out_verify_df = gr.Dataframe(label="Live DB Preview")
    btn_verify_final.click(pipeline.step_10_verify, [], [out_verify_msg, out_verify_df])
