import gradio as gr


def create_cicd_tab():
    """Level 6: CI/CD Pipeline — Step-by-step implementation guide."""

    with gr.Group(elem_id="level-6-cicd"):
        gr.Markdown("""
> **Goal**: GitHub Actions를 활용하여 테스트와 배포를 자동화합니다.
> 
> 이 레벨은 GitHub 리포지토리와 직접 연동되며, push/PR 이벤트에 따라 자동으로 파이프라인이 실행됩니다.
        """)

        gr.HTML('<hr style="border: none; border-top: 1px solid #4b5563; margin: 24px 0;">')

        # =============================================
        # Step 6.1: GitHub Actions Basics
        # =============================================
        gr.Markdown("### Step 6.1: GitHub Actions Basics")
        gr.Markdown("""
**📝 설명**: GitHub Actions workflow 파일(`.github/workflows/*.yml`)을 작성하여 
코드 변경 시 자동으로 CI 파이프라인이 실행되도록 합니다.

**📋 TODO**:
- [ ] `.github/workflows/ci.yml` 파일 생성
- [ ] 트리거 설정: `push` (main branch) + `pull_request`
- [ ] Python 환경 설정 (3.10+)
- [ ] 의존성 설치 (`pip install -r requirements.txt`)
- [ ] Lint 체크 (`flake8` 또는 `ruff`)
        """)

        with gr.Accordion("🔧 Workflow 예시 (🏷️ MOCK)", open=False):
            gr.Markdown("""
> [!🏷️ MOCK] 아래는 **실제 적용 전 예시**입니다. 실제 리포지토리에 반영되면 이 뱃지가 제거됩니다.

```yaml
# .github/workflows/ci.yml
name: Daily Seongsu CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install -r requirements.txt

      - name: Lint with ruff
        run: |
          pip install ruff
          ruff check .

      - name: Run tests
        run: pytest tests/ -v
```
            """)

        # --- Mock: CI Status ---
        with gr.Accordion("📊 CI 실행 현황 (🏷️ MOCK)", open=True):
            gr.Markdown("> 🏷️ **MOCK**: 아래 데이터는 시뮬레이션입니다. GitHub Actions 연동 후 실제 데이터로 교체됩니다.")
            mock_ci_data = [
                ["#12", "fix: update requirements", "main", "✅ Success", "45s", "2026-02-11"],
                ["#11", "feat: add docker tab", "main", "✅ Success", "52s", "2026-02-10"],
                ["#10", "feat: automl step14", "feature/automl", "❌ Failed", "38s", "2026-02-09"],
                ["#9", "chore: lint fixes", "main", "✅ Success", "41s", "2026-02-08"],
            ]
            gr.Dataframe(
                value=mock_ci_data,
                headers=["Run #", "Commit Message", "Branch", "Status", "Duration", "Date"],
                interactive=False,
                label="Recent CI Runs"
            )

        gr.HTML('<hr style="border: none; border-top: 1px solid #4b5563; margin: 24px 0;">')

        # =============================================
        # Step 6.2: Automated Testing
        # =============================================
        gr.Markdown("### Step 6.2: Automated Testing")
        gr.Markdown("""
**📝 설명**: `pytest`를 활용하여 핵심 모듈의 유닛 테스트를 작성하고, 
PR 생성 시 자동으로 테스트가 실행되도록 합니다. 실패 시 머지를 차단합니다.

**📋 TODO**:
- [ ] `tests/` 디렉토리 구조 설계
- [ ] `tests/test_pipeline.py` — DataPipeline 핵심 로직 테스트
- [ ] `tests/test_crawler.py` — 크롤러 데이터 수집 테스트
- [ ] `tests/test_preprocessing.py` — 전처리 파이프라인 테스트
- [ ] GitHub Branch Protection Rule 설정 (테스트 통과 필수)
- [ ] 테스트 커버리지 리포트 (`pytest-cov`)
        """)

        with gr.Accordion("🔧 테스트 코드 예시 (🏷️ MOCK)", open=False):
            gr.Markdown("""
> [!🏷️ MOCK] 아래는 **실제 적용 전 예시**입니다.

```python
# tests/test_pipeline.py
import pytest
from crawler.pipeline import DataPipeline

@pytest.fixture
def pipeline():
    return DataPipeline()

class TestDataPipeline:
    def test_pipeline_initialization(self, pipeline):
        \"\"\"파이프라인이 정상적으로 초기화되는지 확인\"\"\"
        assert pipeline is not None

    def test_fetch_subway_data(self, pipeline):
        \"\"\"지하철 데이터 수집이 정상 작동하는지 확인\"\"\"
        result = pipeline.fetch_subway_data("20260101")
        assert result is not None
        assert len(result) > 0

    def test_data_preprocessing(self, pipeline):
        \"\"\"전처리 파이프라인이 올바른 컬럼을 생성하는지 확인\"\"\"
        df = pipeline.preprocess()
        expected_cols = ["date", "station", "total_traffic"]
        for col in expected_cols:
            assert col in df.columns
```
            """)

        with gr.Accordion("📊 테스트 커버리지 (🏷️ MOCK)", open=True):
            gr.Markdown("> 🏷️ **MOCK**: 아래는 목표 커버리지입니다. 실제 테스트 작성 후 업데이트됩니다.")
            mock_coverage = [
                ["crawler/pipeline.py", "85%", "12", "2", "🟢"],
                ["crawler/subway.py", "72%", "8", "3", "🟡"],
                ["crawler/weather.py", "68%", "10", "4", "🟡"],
                ["guidebook/gradio_app.py", "—", "—", "—", "⚪ (UI, 제외)"],
            ]
            gr.Dataframe(
                value=mock_coverage,
                headers=["Module", "Coverage", "Tests", "Failures", "Status"],
                interactive=False,
                label="Test Coverage Report"
            )

        gr.HTML('<hr style="border: none; border-top: 1px solid #4b5563; margin: 24px 0;">')

        # =============================================
        # Step 6.3: Auto-Deploy to Production
        # =============================================
        gr.Markdown("### Step 6.3: Auto-Deploy to Production")
        gr.Markdown("""
**📝 설명**: `main` 브랜치에 머지되면 자동으로 Docker 이미지를 빌드하고 
프로덕션 서버(OCI Ampere A1)에 배포합니다.

**📋 TODO**:
- [ ] `deploy.yml` workflow 작성 (main push 시 트리거)
- [ ] Docker Hub / GHCR에 이미지 push
- [ ] SSH를 통한 서버 접속 및 `docker compose pull && docker compose up -d`
- [ ] GitHub Secrets 설정 (`SSH_KEY`, `SERVER_HOST`, `DOCKER_TOKEN`)
- [ ] 배포 완료 후 Slack/Telegram 알림
- [ ] Rollback 전략 정의 (이전 이미지 태그로 복구)
        """)

        with gr.Accordion("🔧 배포 Workflow 예시 (🏷️ MOCK)", open=False):
            gr.Markdown("""
> [!🏷️ MOCK] 아래는 **실제 적용 전 예시**입니다.

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    needs: [lint-and-test]  # CI 통과 후 실행
    steps:
      - uses: actions/checkout@v4

      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_TOKEN }}

      - name: Build & Push Docker Image
        run: |
          docker build -t daily-seongsu:latest .
          docker tag daily-seongsu:latest ${{ secrets.DOCKER_USERNAME }}/daily-seongsu:latest
          docker push ${{ secrets.DOCKER_USERNAME }}/daily-seongsu:latest

      - name: Deploy to Server via SSH
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ubuntu
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /home/ubuntu/workspace/daily_seongsu
            docker compose pull
            docker compose up -d
            echo "✅ Deployment complete!"
```
            """)

        # --- Mock: Deployment History ---
        with gr.Accordion("📊 배포 이력 (🏷️ MOCK)", open=True):
            gr.Markdown("> 🏷️ **MOCK**: 아래 데이터는 시뮬레이션입니다. 실제 배포 파이프라인 구축 후 자동 업데이트됩니다.")
            mock_deploy_data = [
                ["v2.3.0", "2026-02-11 09:30", "✅ Active", "feat: L5 docker tab", "ubuntu"],
                ["v2.2.1", "2026-02-10 14:15", "📦 Archived", "fix: nginx config", "ubuntu"],
                ["v2.2.0", "2026-02-09 11:00", "📦 Archived", "feat: automl integration", "ubuntu"],
            ]
            gr.Dataframe(
                value=mock_deploy_data,
                headers=["Version", "Deployed At", "Status", "Changes", "Author"],
                interactive=False,
                label="Deployment History"
            )

        # --- Overall Progress ---
        gr.HTML('<hr style="border: none; border-top: 2px solid #6366f1; margin: 32px 0;">')
        gr.Markdown("""
### 📈 Level 6 전체 진행 현황

| Step | 설명 | 상태 | 비고 |
|------|------|------|------|
| 6.1 | GitHub Actions Basics | 🟡 계획 완료 | Workflow YAML 설계 완료 (MOCK) |
| 6.2 | Automated Testing | 🟡 계획 완료 | 테스트 구조 설계 완료 (MOCK) |
| 6.3 | Auto-Deploy to Production | 🟡 계획 완료 | 배포 파이프라인 설계 완료 (MOCK) |

> 💡 **다음 단계**: Step 6.1의 `.github/workflows/ci.yml` 파일을 실제로 생성하여 GitHub에 push합니다.
        """)
