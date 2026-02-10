import gradio as gr
import os

def create_docker_tab():
    """Level 5: Infrastructure as Code (Docker)"""
    
    gr.Markdown("""
    > **Goal**: Containerize the entire application for portability and reproducibility.
    
    | Step | Description | Status |
    |------|-------------|--------|
    | 5.1 | Dockerfile Creation | ✅ |
    | 5.2 | Docker Compose Setup | ✅ |
    | 5.3 | Volume & Network Management | ✅ |
    """)
    
    gr.HTML('<hr style="border: none; border-top: 1px solid #4b5563; margin: 24px 0;">')
    
    gr.Markdown("### 🐳 Docker Implementation Ready")
    gr.Markdown("""
    **Infrastructure as Code (IaC)** files have been generated:
    
    1.  `Dockerfile`: Multi-stage build (Builder + Runtime) for minimal size and security.
    2.  `docker-compose.yml`: Orchestrates the app, volumes, and networks.
    3.  `.dockerignore`: Optimization to exclude unnecessary files.
    """)
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 🛠️ How to Run (Local)")
            gr.Code("""
# 1. Build and Run
docker-compose up -d --build

# 2. Check Logs
docker-compose logs -f

# 3. Stop
docker-compose down
            """, label="Terminal Commands")
            
        with gr.Column():
            gr.Markdown("### 🔍 Configuration")
            gr.Markdown("""
            - **Port**: `7860` (Mapped to Host)
            - **User**: `appuser` (Non-root security)
            - **Volumes**:
                - `data/` → `/app/data` (Persistence)
            - **Healthcheck**: `curl http://localhost:7860/`
            """)

    gr.HTML('<hr style="border: none; border-top: 1px solid #4b5563; margin: 24px 0;">')

    gr.Markdown("### 📂 Source Code Preview")
    
    def read_file(filename):
        try:
            with open(filename, "r") as f:
                return f.read()
        except: return "File not found"

    with gr.Accordion("Dockerfile", open=False):
        gr.Code(read_file("Dockerfile"), language="dockerfile")
    
    with gr.Accordion("docker-compose.yml", open=False):
        gr.Code(read_file("docker-compose.yml"), language="yaml")
