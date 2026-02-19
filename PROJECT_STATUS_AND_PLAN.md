# Daily Seongsu - Project Status & Roadmap

`Level` = 상위 성숙도 단계, `Step` = 각 Level 내부 실행 단위로 관리합니다.

## 1. Project Overview
"Daily Seongsu" is an AI-powered service that predicts real-time crowding at Seongsu Station (Seoul, Line 2). It analyzes subway traffic data and weather conditions to provide insights for visitors.

## 2. Current Status: Level 1 (Data Collection) - **COMPLETE**
We have successfully built the foundation for data collection and infrastructure.

### Features Implemented
- **Subway Data**: Automatically collects daily passenger counts for Seongsu Station from "Seoul Data Square" (User: `SeoulSubwayCollector`).
- **Weather Data**: Fetches real-time weather (temp, rain) for Seongsu-dong from "Korea Meteorological Administration" (User: `WeatherCollector`).
- **Storage**: Data is saved in CSV (Subway) and JSON (Weather) formats at `web/public/data/`.

### Infrastructure (OCI Ampere A1)
- **Server**: Oracle Cloud Infrastructure (ARM64 Architecture).
- **Network**: Ports 80 (HTTP), 443 (HTTPS), and 8501 (Streamlit) are open.
- **Web Server**: Nginx is configured as a reverse proxy with SSL (HTTPS) enabled.
- **Environment**: Docker, Python 3.10+, and OCI CLI are installed.

---

## 3. Roadmap: Level 2 ~ 10

### Level 2: Data Preprocessing
- **Goal**: Prepare data for Machine Learning.
- **Plan**: Clean missing values, remove outliers, and create features (e.g., "Is it a holiday?", "Is it raining?").

### Level 3: Prediction Dashboard (MVP)
- **Goal**: Visualize data for users.
- **Plan**: Build a simple web dashboard using **Streamlit**. Users can see predicted crowding based on date/weather.

### Level 4: AutoML & Optimization
- **Goal**: Find the best AI model.
- **Plan**: Use tools like PyCaret or Optuna to automatically test different models and find the one with the lowest error.

### Level 5: Automation
- **Goal**: Run everything automatically every day.
- **Plan**: Use `cron` jobs to collect data and retrain the model every morning without human input.

### Level 6: CI/CD (DevOps) - **COMPLETE**
- **Goal**: Automatic deployment.
- **Status**: **GitHub Actions** is active. On push, CI tests run and deployment workflow is triggered.

### Level 7: Experiment Tracking
- **Goal**: track AI experiments.
- **Plan**: Use **MLflow** to record which model performed best and why.

### Level 8: Data Versioning
- **Goal**: Track data changes like code.
- **Plan**: Use **DVC (Data Version Control)** to manage history of our datasets.

### Level 9: Monitoring & Containers
- **Goal**: Stability and scaling.
- **Plan**: Dockerize the entire application (Docker Compose) and add monitoring/alerts (e.g., Telegram message if the API fails).

### Level 10: Orchestration
- **Goal**: Manage complex workflows.
- **Plan**: Use **Apache Airflow** to manage the full pipeline: Data Collection -> Processing -> Training -> Deployment.
