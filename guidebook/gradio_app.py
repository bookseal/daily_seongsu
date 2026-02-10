
import gradio as gr
import os
import sys
from dotenv import load_dotenv

# Path setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawler.pipeline import DataPipeline
from guidebook.tabs.intro import create_intro_tab
from guidebook.tabs.pipeline_controls import create_level1_controls, create_level2_controls
from guidebook.tabs.step11_observer import create_observer_tab
from guidebook.tabs.step14_automl import create_automl_tab
from guidebook.tabs.step15_docker import create_docker_tab
from guidebook.tabs.step13_14_control import create_control_tab

# Instantiate Pipeline (Stateful - Shared across tabs)
pipeline = DataPipeline()

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'crawler', '.env'))

# --- 2. JS & Theme ---
JS_DARK_MODE = """
function() {
    // 1. Dark Mode Init
    document.body.classList.add('dark');
    if (document.querySelector('gradio-app')) {
        document.querySelector('gradio-app').classList.add('dark');
    }

    // 2. Scroll Indicator (Context Awareness)
    const indicator = document.createElement('div');
    indicator.id = 'level-indicator';
    indicator.style.position = 'fixed';
    indicator.style.bottom = '20px';
    indicator.style.right = '20px';
    indicator.style.padding = '8px 16px';
    indicator.style.background = 'rgba(31, 41, 55, 0.8)';
    indicator.style.color = '#e5e7eb';
    indicator.style.borderRadius = '9999px';
    indicator.style.zIndex = '9999';
    indicator.style.fontWeight = '600';
    indicator.style.fontSize = '14px';
    indicator.style.backdropFilter = 'blur(4px)';
    indicator.style.border = '1px solid rgba(75, 85, 99, 0.4)';
    indicator.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1)';
    indicator.innerText = '🚇 Daily Seongsu';
    indicator.style.opacity = '0';
    indicator.style.transition = 'opacity 0.3s ease';
    document.body.appendChild(indicator);

    // Track scroll to update text
    window.addEventListener('scroll', () => {
        const headings = Array.from(document.querySelectorAll('h1, h2, h3'));
        let currentSection = 'Overview';
        let found = false;

        for (let i = 0; i < headings.length; i++) {
            const h = headings[i];
            const rect = h.getBoundingClientRect();
            if (rect.top < 200) {
                if (h.innerText.includes('Level') || h.innerText.includes('Daily Seongsu')) {
                    currentSection = h.innerText.split(':')[0].trim();
                    found = true;
                }
            }
        }

        indicator.innerText = currentSection;
        
        if (window.scrollY > 100) {
            indicator.style.opacity = '1';
        } else {
            indicator.style.opacity = '0';
        }
    });

    // 3. URL <-> Tab Sync
    const tabParentMap = {
        'tab-l1': 'tab-p1', 'tab-l2': 'tab-p1', 'tab-l3': 'tab-p1',
        'tab-l4': 'tab-p2', 'tab-l5': 'tab-p2', 'tab-l6': 'tab-p2',
        'tab-l7': 'tab-p3', 'tab-l8': 'tab-p3', 'tab-l9': 'tab-p3', 'tab-l10': 'tab-p3'
    };

    const trackableTabs = [
        'tab-p1', 'tab-p2', 'tab-p3',
        'tab-l1', 'tab-l2', 'tab-l3', 'tab-l4', 'tab-l5', 'tab-l6', 'tab-l7', 'tab-l8', 'tab-l9', 'tab-l10'
    ];

    const updateUrlForTab = (tabId, push = true) => {
        const nextHash = '#' + tabId;
        if (window.location.hash === nextHash) return;
        if (push) {
            history.pushState(null, '', nextHash);
        } else {
            history.replaceState(null, '', nextHash);
        }
    };

    const bindTabButtons = () => {
        trackableTabs.forEach((tabId) => {
            const btn = document.getElementById(tabId + '-button');
            if (!btn || btn.dataset.urlBound === '1') return;
            btn.dataset.urlBound = '1';
            btn.addEventListener('click', () => updateUrlForTab(tabId, true));
        });
    };

    const applyHashRoute = () => {
        const tabId = window.location.hash.replace('#', '');
        if (!tabId) return;

        const parentId = tabParentMap[tabId];
        if (parentId) {
            const parentBtn = document.getElementById(parentId + '-button');
            if (parentBtn) parentBtn.click();
            setTimeout(() => {
                const childBtn = document.getElementById(tabId + '-button');
                if (childBtn) childBtn.click();
            }, 120);
            return;
        }

        const targetBtn = document.getElementById(tabId + '-button');
        if (targetBtn) targetBtn.click();
    };

    const setupUrlSync = () => {
        bindTabButtons();
        applyHashRoute();

        const tabObserver = new MutationObserver(() => bindTabButtons());
        tabObserver.observe(document.body, { childList: true, subtree: true });

        window.addEventListener('hashchange', () => {
            applyHashRoute();
        });
    };

    setupUrlSync();

    // 4. Global Tab Switcher
    window.switchTab = (phaseId, levelId) => {
        console.log("Switching to:", phaseId, levelId);
        
        const pBtn = document.getElementById(phaseId + '-button');
        if(pBtn) {
            pBtn.click();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
        
        if(levelId) {
            setTimeout(() => {
                const lBtn = document.getElementById(levelId + '-button');
                if(lBtn) lBtn.click();
            }, 150);
            updateUrlForTab(levelId, true);
            return;
        }
        updateUrlForTab(phaseId, true);
    }
}
"""

MERMAID_SCRIPT = """
<script type="module">
    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
    mermaid.initialize({
        startOnLoad: false,
        theme: 'dark',
    });

    async function renderMermaid() {
        const elements = document.querySelectorAll('.mermaid:not([data-processed])');
        if (elements.length === 0) return;
        
        await mermaid.run({
            nodes: elements
        });
    }

    const observer = new MutationObserver(() => {
        renderMermaid();
    });

    document.addEventListener('DOMContentLoaded', () => {
        observer.observe(document.body, { childList: true, subtree: true });
        renderMermaid();
    });
    
    setInterval(renderMermaid, 500);
</script>
"""

with gr.Blocks(title="Daily Seongsu Guidebook", head=MERMAID_SCRIPT, js=JS_DARK_MODE, theme=gr.themes.Soft()) as app:
    def divider(margin="24px"):
        return gr.HTML(f'<hr style="border: none; border-top: 1px solid #4b5563; margin: {margin} 0;">')

    
    with gr.Tabs():
        # TAB 1: Dashboard
        create_intro_tab()

        # ============================================
        # PHASE 1: FOUNDATION (Levels 1-3)
        # ============================================
        with gr.Tab("🏗️ Building the Data Engine", elem_id="tab-p1"):
            gr.Markdown("## Phase 1: Building the Data Engine")
            gr.Markdown("*Levels 1-3: From raw data collection to feature quality assurance.*")
            
            with gr.Tabs():
                # Level 1: Cloud Data Engineering
                with gr.Tab("L1: Data Engineering", elem_id="tab-l1"):
                    gr.Markdown("## 🔵 Level 1: Cloud Data Engineering")
                    create_level1_controls(pipeline)
                
                # Level 2: Preprocessing
                with gr.Tab("L2: Preprocessing", elem_id="tab-l2"):
                    gr.Markdown("## 🔵 Level 2: Preprocessing Pipeline")
                    create_level2_controls(pipeline)
                
                # Level 3: Data Quality
                with gr.Tab("L3: Data Quality", elem_id="tab-l3"):
                    gr.Markdown("## 🔵 Level 3: Data Quality Assurance")
                    create_observer_tab()

        # ============================================
        # PHASE 2: ACCELERATION (Levels 4-6)
        # ============================================
        with gr.Tab("🚀 Automating Intelligence", elem_id="tab-p2"):
            gr.Markdown("## Phase 2: Automating Intelligence")
            gr.Markdown("*Levels 4-6: From model training to automated deployment.*")
            
            with gr.Tabs():
                # Level 4: AutoML
                with gr.Tab("L4: AutoML", elem_id="tab-l4"):
                    gr.Markdown("## 🟣 Level 4: AutoML")
                    create_automl_tab()
                
                # Level 5: Docker
                with gr.Tab("L5: Docker", elem_id="tab-l5"):
                    gr.Markdown("## 🟣 Level 5: Infrastructure as Code")
                    create_docker_tab()
                
                # Level 6: CI/CD
                with gr.Tab("L6: CI/CD", elem_id="tab-l6"):
                    gr.Markdown("## 🟣 Level 6: CI/CD Pipeline")
                    gr.Markdown("""
                    > **Goal**: Automate testing and deployment with GitHub Actions.
                    
                    | Step | Description | Status |
                    |------|-------------|--------|
                    | 6.1 | GitHub Actions Basics | ⚪ Planned |
                    | 6.2 | Automated Testing | ⚪ Planned |
                    | 6.3 | Auto-Deploy to Production | ⚪ Planned |
                    """)
                    create_control_tab()

        # ============================================
        # PHASE 3: OPERATION (Levels 7-10)
        # ============================================
        with gr.Tab("⚙️ Reliability at Scale", elem_id="tab-p3"):
            gr.Markdown("## Phase 3: Reliability at Scale")
            gr.Markdown("*Levels 7-10: From experiment tracking to full orchestration.*")
            
            with gr.Tabs():
                # Level 7: MLflow
                with gr.Tab("L7: MLflow", elem_id="tab-l7"):
                    gr.Markdown("## 🟢 Level 7: Experiment Tracking")
                    gr.Markdown("""
                    > **Goal**: Track experiments, log metrics, and manage model versions.
                    
                    | Step | Description | Status |
                    |------|-------------|--------|
                    | 7.1 | MLflow Setup | ⚪ Planned |
                    | 7.2 | Metric Logging | ⚪ Planned |
                    | 7.3 | Model Registry | ⚪ Planned |
                    """)
                    gr.Info("🚧 Coming Soon: Centralized logging of model metrics and artifacts.")
                
                # Level 8: DVC
                with gr.Tab("L8: DVC", elem_id="tab-l8"):
                    gr.Markdown("## 🟢 Level 8: Data Versioning")
                    gr.Markdown("""
                    > **Goal**: Version control for datasets, just like Git for code.
                    
                    | Step | Description | Status |
                    |------|-------------|--------|
                    | 8.1 | DVC Init | ⚪ Planned |
                    | 8.2 | Remote Storage Link | ⚪ Planned |
                    | 8.3 | Dataset History Tracking | ⚪ Planned |
                    """)
                    gr.Info("🚧 Coming Soon: Tracking large datasets alongside code changes.")
                
                # Level 9: Observability
                with gr.Tab("L9: Observability", elem_id="tab-l9"):
                    gr.Markdown("## 🟢 Level 9: System Observability")
                    gr.Markdown("""
                    > **Goal**: Monitor system health, set up alerts, and track latency.
                    
                    | Step | Description | Status |
                    |------|-------------|--------|
                    | 9.1 | Health Check API | ⚪ Planned |
                    | 9.2 | Alerting (Telegram/Slack) | ⚪ Planned |
                    | 9.3 | Latency Dashboard | ⚪ Planned |
                    """)
                    gr.Info("🚧 Coming Soon: Real-time monitoring of API latency and system health.")
                
                # Level 10: Airflow
                with gr.Tab("L10: Airflow", elem_id="tab-l10"):
                    gr.Markdown("## 🟢 Level 10: Orchestration")
                    gr.Markdown("""
                    > **Goal**: Manage complex multi-step workflows with Airflow DAGs.
                    
                    | Step | Description | Status |
                    |------|-------------|--------|
                    | 10.1 | Airflow DAG Design | ⚪ Planned |
                    | 10.2 | Task Dependencies | ⚪ Planned |
                    | 10.3 | Full Lifecycle Automation | ⚪ Planned |
                    """)
                    gr.Info("🚧 Coming Soon: Complex dependency management for the full ML lifecycle.")


    gr.Markdown("<br><br><br>")
    divider()
    gr.Markdown("© 2026 Daily Seongsu Project")

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860)
