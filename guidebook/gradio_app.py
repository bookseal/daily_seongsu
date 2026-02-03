
import gradio as gr
import os
import sys
from dotenv import load_dotenv

# Path setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawler.pipeline import DataPipeline
from guidebook.tabs.intro import create_intro_tab
from guidebook.tabs.pipeline_controls import create_pipeline_controls
from guidebook.tabs.step11_observer import create_observer_tab
from guidebook.tabs.step12_sandbox import create_sandbox_tab
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
    indicator.style.top = '20px';
    indicator.style.right = '20px';
    indicator.style.padding = '8px 16px';
    indicator.style.background = 'rgba(31, 41, 55, 0.8)'; // Dark gray with opacity
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

        // Find the last heading that is above the viewport center or top
        for (let i = 0; i < headings.length; i++) {
            const h = headings[i];
            const rect = h.getBoundingClientRect();
            // Trigger line: 200px from top
            if (rect.top < 200) {
                if (h.innerText.includes('Level') || h.innerText.includes('Daily Seongsu')) {
                    currentSection = h.innerText.split(':')[0].trim();
                    found = true;
                }
            }
        }

        indicator.innerText = currentSection;
        
        // Show/Hide logic
        if (window.scrollY > 100) {
            indicator.style.opacity = '1';
        } else {
            indicator.style.opacity = '0';
        }
    });
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
    
    // Fallback polling
    setInterval(renderMermaid, 500);
</script>
"""

with gr.Blocks(title="Daily Seongsu Guidebook", head=MERMAID_SCRIPT, js=JS_DARK_MODE, theme=gr.themes.Soft()) as app:
    # Custom Divider
    def divider(margin="24px"):
        return gr.HTML(f'<hr style="border: none; border-top: 1px solid #4b5563; margin: {margin} 0;">')

    
    # Roadmap (Brief)
    # TABS STRUCTURE - Organized by Phases
    with gr.Tabs():
        # TAB 1: Dashboard
        create_intro_tab()

        # TAB 2: Phase 1 (Foundation)
        with gr.Tab("🏗️ Phase 1: Foundation"):
            gr.Markdown("## Phase 1: Building the Data Engine")
            with gr.Tabs():
                with gr.Tab("Level 1-2: Pipeline Control"):
                    create_pipeline_controls(pipeline)
                with gr.Tab("Level 3 (Step 11): Feature Observer"):
                    create_observer_tab()

        # TAB 3: Phase 2 (Acceleration)
        with gr.Tab("🚀 Phase 2: Acceleration"):
            gr.Markdown("## Phase 2: Automating Intelligence")
            with gr.Tabs():
                with gr.Tab("Level 3 (Step 12): Simulation Sandbox"):
                    create_sandbox_tab()
                with gr.Tab("Level 3 & 4 (Step 13): Training Control"):
                    create_control_tab()

        # TAB 4: Phase 3 (Operation)
        with gr.Tab("⚙️ Phase 3: Operation"):
            gr.Markdown("## Phase 3: Reliability at Scale (Coming Soon)")
            gr.Info("Levels 7-10 (MLflow, DVC, Airflow) are currently under development.")
            # Placeholder or move Governance here if desired. 
            # For now, Governance is inside Control Room (Phase 2).


    gr.Markdown("<br><br><br>")
    divider()
    gr.Markdown("© 2026 Daily Seongsu Project")

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860)
