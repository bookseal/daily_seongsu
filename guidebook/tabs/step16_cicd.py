import gradio as gr



import os

def read_workflow_file(filename):
    try:
        base_path = "/home/ubuntu/workspace/daily_seongsu" 
        with open(os.path.join(base_path, filename), "r") as f:
            return f.read()
    except Exception:
        return "# Error reading file"

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

        with gr.Accordion("📘 ci.yml 파일이란? (파일 용도 설명)", open=True):
            gr.Markdown("""
### 📂 파일 위치 및 목적

`.github/workflows/ci.yml`은 **GitHub Actions의 자동화 스크립트**입니다.

- **위치**: 프로젝트 루트에서 `.github/workflows/ci.yml`
- **역할**: 코드가 push되거나 PR이 생성될 때마다 **자동으로 실행**되어 코드 품질을 검증합니다
- **실행 환경**: GitHub의 클라우드 서버(runner)에서 독립적으로 실행됩니다

### 🔍 CI 파일의 핵심 구성 요소

| 섹션 | 설명 |
|------|------|
| `name` | Workflow의 이름 (GitHub Actions UI에 표시됨) |
| `on` | **트리거 조건** — 언제 이 파일이 실행될지 정의 |
| `jobs` | 실제로 수행할 작업 목록 (여러 개 정의 가능) |
| `steps` | 각 job 내에서 순차적으로 실행되는 명령들 |

### 📋 ci.yml 내용 상세 분석

아래 예시 파일의 각 부분이 무엇을 하는지 설명합니다:

#### 1. `on` (트리거)
```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
```
- **의미**: `main` 브랜치에 push하거나, `main`으로 PR을 열면 자동 실행
- **효과**: 매번 코드 변경 시 자동으로 검증되어 **버그를 조기에 발견**

#### 2. `jobs` → `runs-on`
```yaml
jobs:
  lint-and-test:
    runs-on: ubuntu-latest
```
- **의미**: Ubuntu 최신 버전의 가상 서버에서 실행
- **효과**: 로컬 환경과 무관하게 **일관된 환경에서 테스트** 가능

#### 3. `steps` → Checkout
```yaml
- uses: actions/checkout@v4
```
- **의미**: GitHub 리포지토리의 코드를 runner에 다운로드
- **효과**: 파이프라인이 최신 코드를 사용할 수 있게 함

#### 4. Python 설치
```yaml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.10'
```
- **의미**: Python 3.10을 설치
- **효과**: 프로젝트 요구사항과 동일한 Python 버전 보장

#### 5. 의존성 설치
```yaml
- name: Install dependencies
  run: |
    pip install --upgrade pip
    pip install -r requirements.txt
```
- **의미**: `requirements.txt`에 명시된 모든 라이브러리 설치
- **효과**: 테스트 실행에 필요한 환경 구축

#### 6. Lint 검사
```yaml
- name: Lint with ruff
  run: |
    pip install ruff
    ruff check .
```
- **의미**: `ruff`로 코드 스타일 및 잠재적 오류 검사
- **효과**: **코드 품질 유지** — 스타일 위반이나 사용되지 않는 변수 등 발견

#### 7. 테스트 실행
```yaml
- name: Run tests
  run: pytest tests/ -v
```
- **의미**: `tests/` 디렉토리의 모든 테스트 실행
- **효과**: 기능이 정상 작동하는지 자동 검증

### ✅ CI가 제공하는 가치

1. **자동 검증**: 코드 변경 시 매번 수동으로 테스트하지 않아도 됨
2. **조기 발견**: PR 단계에서 버그를 미리 차단
3. **일관성**: 개발자 로컬 환경과 무관하게 동일한 조건에서 검증
4. **협업 효율**: 팀원들이 안전하게 코드 머지 가능
            """)

        with gr.Accordion("🔧 실제 적용된 Workflow (✅ LIVE)", open=False):
            gr.Markdown("> ✅ **LIVE**: 실제 `.github/workflows/ci.yml` 파일의 내용입니다.")
            gr.Code(read_workflow_file(".github/workflows/ci.yml"), language="yaml")

        # --- CI Status ---
        with gr.Accordion("📊 CI 실행 현황", open=True):
            gr.Markdown("> ✅ **LIVE**: 아래는 실제 GitHub Actions 워크플로우 실행 결과입니다.")
            ci_data = [
                ["#1", "feat(L6): Add GitHub Actions CI workflow and basic tests", "main", "✅ Success", "49s", "2026-02-12"],
            ]
            gr.Dataframe(
                value=ci_data,
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

        with gr.Accordion("🔧 실제 적용된 CD Workflow (✅ LIVE)", open=False):
            gr.Markdown("> ✅ **LIVE**: 실제 `.github/workflows/deploy.yml` 파일의 내용입니다.")
            gr.Code(read_workflow_file(".github/workflows/deploy.yml"), language="yaml")

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
| 6.1 | GitHub Actions Basics | ✅ 구현 완료 | CI 파이프라인 배포 및 작동 확인 완료 |
| 6.2 | Automated Testing | 🟡 진행 중 | 기본 테스트 9개 작성 완료, 추가 테스트 필요 |
| 6.3 | Auto-Deploy to Production | 🟡 계획 완료 | 배포 파이프라인 설계 완료 (MOCK) |

> 💡 **다음 단계**: Step 6.2의 테스트 커버리지를 높이기 위해 `test_pipeline.py`, `test_crawler.py` 등을 추가합니다.
        """)
