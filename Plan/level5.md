### Level 5: Infrastructure as Code (Dockerization)
**Goal:** Create a "Unified Environment" to eliminate the "It works on my machine" problem.

#### Step 5.1: Dockerfile Creation (The Blueprint)
* **Action:** Build a lightweight Python image based on `python:3.11-slim-bookworm`.
* **Key Point:** * **Multi-stage Build:** 최적화된 이미지 크기를 위해 빌드 단계와 실행 단계를 분리.
    * **Security:** `USER` 명령어를 사용해 Root 권한이 아닌 일반 사용자로 실행 (Security Best Practice).
* **Command:** `docker build -t daily-seongsu:v1 .`

#### Step 5.2: Docker Compose Setup (The Conductor)
* **Action:** Orchestrate the application, environment variables, and volumes.
* **Key Point:**
    * **Env Mapping:** `.env` 파일을 자동으로 읽어와 보안이 중요한 API Key들을 주입.
    * **Restart Policy:** 시스템 장애 시 자동으로 컨테이너를 다시 시작(`unless-stopped`).
* **Command:** `docker-compose up -d`

#### Step 5.3: Volume & Network Management (The Persistence)
* **Action:** Define persistent storage for local logs/cache and isolated virtual network.
* **Key Point:**
    * **Bridge Network:** 외부 노출을 최소화하고 컨테이너 간 안전한 통신망 구축.
    * **Bind Mounts:** 개발 환경에서는 코드가 수정되면 즉시 반영되도록 볼륨 연결.