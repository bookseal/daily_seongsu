import gradio as gr



import os

def read_workflow_file(filename):
    try:
        # __file__ 기준으로 프로젝트 루트를 동적으로 계산 (컨테이너/로컬 모두 호환)
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        filepath = os.path.join(base_path, filename)
        with open(filepath, "r") as f:
            return f.read()
    except Exception as e:
        return f"# Error reading file: {e}\n# Tried path: {os.path.join(base_path, filename)}"

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
**✅ 구현 완료**: GitHub 연동이 완료되어, 코드를 올릴 때마다 자동으로 테스트가 실행됩니다.

**🔍 핵심 포인트**:
1. **`.github/workflows/ci.yml`**: GitHub Actions에게 "무엇을 테스트할지" 알려주는 설정 파일입니다.
2. **Push Trigger**: 코드를 Push하면 GitHub 서버에서 자동으로 이 파일을 읽고 테스트를 시작합니다.
3. **Lint & Test**: 코드 스타일 검사(Ruff)와 기능 테스트(Pytest)를 수행합니다.
        """)
        
        with gr.Accordion("🔧 실제 적용된 CI Workflow (✅ LIVE)", open=True):
            gr.Markdown("> 아래는 현재 리포지토리에서 작동 중인 실제 설정 파일입니다.")
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
        gr.Markdown("### Step 6.2: Automated Testing (Local vs CI)")
        gr.Markdown("""
**✅ 구현 완료**: `pytest`를 활용하여 핵심 모듈의 유닛 테스트를 작성했습니다.

**❓ GitHub Actions가 있는데 왜 로컬에서 테스트하나요?**
- **로컬 (`pytest`)**: 코드 작성 중 **실시간(1초)**으로 오류를 잡습니다. (개발자용)
- **CI (Actions)**: 코드를 합치기 전 **최종(1분)**으로 안전성을 검증합니다. (팀장/Manager용)
*👉 즉, 로컬에서 `pytest`로 먼저 확인하고, 통과하면 Push하는 것이 정석입니다.*

**💻 실행 방법**:
터미널에서 아래 명령어를 입력하여 현재 코드 상태를 점검하세요:
```bash
pytest tests/
```
""")

        with gr.Accordion("🔧 실제 작성된 테스트 코드 (✅ LIVE)", open=False):
            gr.Markdown("> ✅ **LIVE**: 실제 `tests/test_basic.py` 파일의 내용입니다.")
            gr.Code(read_workflow_file("tests/test_basic.py"), language="python")

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
**✅ 구현 완료**: 테스트(CI)를 통과한 코드를 서버에 자동으로 배포하는 설정입니다.

**🚀 배포 전략 (SSH Pull)**:
1. GitHub Actions가 OCI 서버에 **SSH로 접속**합니다.
2. 서버에서 `git pull`을 실행하여 최신 코드를 받습니다.
3. `docker compose up --build`로 컨테이너를 재생성합니다.
*(ARM64 서버 호환성을 위해 서버에서 직접 빌드하는 방식을 채택했습니다)*
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
| 6.1 | GitHub Actions Basics | ✅ 구현 완료 | CI 파이프라인 (Ruff + Pytest) |
| 6.2 | Automated Testing | 🟡 진행 중 | 유닛 테스트 추가 필요 (현재 18%) |
| 6.3 | Auto-Deploy to Production | ✅ 설정 완료 | SSH 배포 (Secrets 설정 필요) |

> 💡 **다음 단계**: Step 6.2의 테스트 커버리지를 높이기 위해 `test_pipeline.py`, `test_crawler.py` 등을 추가합니다.
        """)
