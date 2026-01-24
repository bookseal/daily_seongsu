# Daily Seongsu (성수역 혼잡도 예측 서비스) - Professional MLOps

**Daily Seongsu** is an AI-powered service that predicts real-time crowding at Seongsu Station.
It is built on a **Professional MLOps Pipeline** hosted on **OCI Ampere A1 (ARM64)**, utilizing **Supabase** for robust data storage and a **Dual-Frontend** strategy for service and education.

## System Architecture

```mermaid
graph TD
    subgraph OCI_Ampere_A1 [OCI Ampere A1 Server (Ubuntu/Docker)]
        Airflow[Apache Airflow <br> (Orchestrator)]
        Dashboard[Streamlit <br> (Guidebook UI)]
        ServiceUI[Gradio <br> (Prediction Service UI)]
        MLflow[MLflow <br> (Experiment Tracking)]
        
        subgraph Containers
            Crawler[Data Crawler]
            Trainer[Model Trainer]
        end
    end
    
    subgraph Data_Layer [Supabase (Cloud DB)]
        Postgres[(PostgreSQL <br> Data Warehouse)]
    end
    
    External[External APIs <br> (Seoul Data / KMA)] --> Crawler
    Crawler -->|Insert Data| Postgres
    Postgres -->|Fetch Data| Trainer
    Trainer -->|Log Metrics| MLflow
    Trainer -->|Save Model| Airflow
    Airflow -->|Deploy Model| ServiceUI
    
    User((User)) --> ServiceUI
    User --> Dashboard
```

## Professional MLOps Roadmap (Level 1 - 10)

### Level 1: Cloud Data Engineering (Supabase)
- **Goal**: Replace local files with a robust cloud database.
- **Action**: 
  - Integrate **Supabase (PostgreSQL)**.
  - Implement `SeoulSubwayCollector` and `WeatherCollector` to insert data directly into Supabase tables (`subway_traffic`, `weather_data`).

### Level 2: Data Warehouse & Preprocessing
- **Goal**: scalable data processing.
- **Action**: Use **Pandas** (or SQL within Supabase) to clean data, handle missing values, and generate features (e.g., Holidays, Weather Condition).

### Level 3: Dual-Frontend Deployment
- **Goal**: Serve both end-users and developers.
- **Action**:
  - **Gradio (Service)**: Lightweight, high-performance interface for real-time crowding prediction.
  - **Streamlit (Guidebook)**: Interactive educational hub showing the MLOps pipeline status and project docs.

### Level 4: AutoML & Hyperparameter Tuning
- **Goal**: Maximize model performance.
- **Action**: Use **PyCaret** or **Optuna** to automatically select the best model and tune hyperparameters.

### Level 5: Containerization (Docker Compose)
- **Goal**: Infrastructure as Code & Portability.
- **Action**: Define the entire stack (Airflow, MLflow, Gradio, Streamlit) in `docker-compose.yml` optimized for ARM64.

### Level 6: CI/CD (GitHub Actions)
- **Goal**: Automated testing and deployment.
- **Action**: GitHub Actions pipeline to run tests, build Docker images, and deploy to OCI upon push.

### Level 7: Experiment Tracking (MLflow)
- **Goal**: Reproducibility and Metric Tracking.
- **Action**: centralized **MLflow** server to log parameters, metrics (RMSE), and artifacts for every training run.

### Level 8: Data Versioning (DVC)
- **Goal**: Version control for large datasets.
- **Action**: Integrate **DVC** to track changes in the dataset alongside codegit.

### Level 9: Monitoring & Alerting
- **Goal**: Proactive system health checks.
- **Action**: Prometheus/Grafana or simple Python-based alerts (Telegram/Slack) for pipeline failures or model drift.

### Level 10: Orchestration (Apache Airflow)
- **Goal**: Fully automated, dependency-aware workflows.
- **Action**: Replace cron with **Apache Airflow** DAGs to manage the complex dependencies of the entire lifecycle (Ingest -> Train -> Deploy).

## Infrastructure Setup (ARM64)

### Prerequisites
- OCI Ampere A1 Instance
- Ports: 80, 443, 8501 (Streamlit), 7860 (Gradio), 8080 (Airflow), 5000 (MLflow)

### Setup
Scripts in `infra/` help bootstrap the server.
```bash
./infra/setup_arm64.sh  # Install Docker/Python
./infra/setup_network.sh # Configure Firewall
```

## Running the Crawler (Migration to Supabase)
Ensure `.env` contains Supabase credentials (`SUPABASE_URL`, `SUPABASE_KEY`).

```bash
cd crawler
pip install -r requirements.txt
python main.py
```
