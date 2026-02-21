"""
Repo Intelligence Engine — Streamlit Application
Advanced repository intelligence analysis and AI architectural review.
"""

import json
import os
from typing import Optional

import streamlit as st

from github_fetcher import fetch_repository, parse_github_url
from file_classifier import (
    classify_all_files,
    detect_primary_language,
    detect_project_type,
)
from static_parser import analyze_all_sources
from config_parser import parse_all_configs
from graph_builder import build_all_graphs
from ai_interpreter import get_ai_review
from semantic_inference import generate_description, enhance_function_descriptions
from pdf_generator import generate_comprehensive_pdf_report

# ──────────────────────────────────────────────
# Page Configuration
# ──────────────────────────────────────────────

st.set_page_config(
    page_title="Repo Intelligence Engine",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# Custom Styling
# ──────────────────────────────────────────────

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #4e8cff, #61dafb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #888;
        margin-top: 0;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #262730;
        border-radius: 10px;
        padding: 1.2rem;
        border-left: 4px solid #4e8cff;
    }
    .stExpander {
        border: 1px solid #333;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Secrets / Environment
# ──────────────────────────────────────────────

def _get_secret(key: str) -> Optional[str]:
    """Get secret from Streamlit secrets or environment."""
    try:
        value = st.secrets.get(key)
        if value:
            return value
    except Exception:
        pass
    return os.environ.get(key)


def _get_github_token() -> Optional[str]:
    return _get_secret("GITHUB_TOKEN")


def _get_hf_token() -> Optional[str]:
    return _get_secret("HF_API_TOKEN")


# ──────────────────────────────────────────────
# Analysis Pipeline
# ──────────────────────────────────────────────

def run_analysis(repo_url: str) -> dict:
    """Execute the full analysis pipeline."""
    github_token = _get_github_token()
    results = {}

    # Step 1: Fetch repository
    status = st.status("Analyzing repository...", expanded=True)

    with status:
        st.write("📡 Fetching repository tree...")
        progress_bar = st.progress(0, text="Connecting to GitHub...")

        def progress_callback(current, total, path):
            pct = current / total if total > 0 else 0
            progress_bar.progress(pct, text=f"Fetching {current}/{total}: {path}")

        repo_data = fetch_repository(repo_url, token=github_token, progress_callback=progress_callback)
        files = repo_data["files"]
        progress_bar.progress(1.0, text=f"Fetched {len(files)} files")

        # Step 2: Classify files
        st.write("📂 Classifying files...")
        classification = classify_all_files(files)
        primary_lang = detect_primary_language(files)
        project_type = detect_project_type(files)

        # Step 3: Parse source files
        st.write("🔍 Parsing source code...")
        source_analysis = analyze_all_sources(files)
        
        # Step 3.5: Enhance with static semantic inference
        st.write("🧠 Generating semantic descriptions...")
        for analysis in source_analysis:
            # Generate file-level description
            description = generate_description(analysis)
            if description:
                analysis["semantic_description"] = description
            
            # Enhance function descriptions
            if analysis.get("functions"):
                analysis["functions"] = enhance_function_descriptions(
                    analysis["functions"],
                    analysis["file_path"],
                    analysis.get("language", "")
                )

        # Step 4: Parse config files
        st.write("⚙️ Analyzing configurations...")
        config_data = parse_all_configs(files)

        # Step 5: Build graphs
        st.write("📊 Building architecture diagrams...")
        graphs = build_all_graphs(source_analysis)

        status.update(label="Analysis complete!", state="complete")

    # Build master JSON
    master_json = _build_master_json(
        repo_data, classification, primary_lang,
        project_type, source_analysis, config_data, graphs
    )

    return {
        "repo_data": repo_data,
        "classification": classification,
        "primary_lang": primary_lang,
        "project_type": project_type,
        "source_analysis": source_analysis,
        "config_data": config_data,
        "graphs": graphs,
        "master_json": master_json,
    }


def _build_master_json(
    repo_data: dict,
    classification: dict,
    primary_lang: str,
    project_type: dict,
    source_analysis: list,
    config_data: dict,
    graphs: dict,
) -> dict:
    """Build the structured master JSON output."""
    return {
        "project_metadata": {
            "owner": repo_data["owner"],
            "repo": repo_data["repo"],
            "branch": repo_data["branch"],
            "primary_language": primary_lang,
            "total_files": len(repo_data["files"]),
            "source_files": len(classification["source"]),
            "config_files": len(classification["config"]),
            "documentation_files": len(classification["documentation"]),
            "asset_files": len(classification["asset"]),
            "frontend_detected": project_type["frontend_detected"],
            "backend_detected": project_type["backend_detected"],
            "is_nextjs": project_type.get("is_nextjs", False),
            "is_vite": project_type.get("is_vite", False),
        },
        "source_analysis": source_analysis,
        "dependencies": {
            "frontend": config_data.get("frontend_dependencies", []),
            "backend": config_data.get("backend_dependencies", []),
        },
        "frameworks": {
            "frontend": config_data.get("frontend_frameworks", []),
            "backend": config_data.get("backend_frameworks", []),
        },
        "infrastructure": {
            "docker_used": config_data.get("docker_used", False),
            "ci_cd_detected": classification.get("ci_cd_detected", False),
            "dockerfile": config_data.get("dockerfile"),
            "docker_compose": config_data.get("docker_compose"),
        },
        "graph_adjacency": {
            "module_dependencies": graphs["module_dependency"]["adjacency"],
            "api_routes": graphs["api_routes"]["adjacency"],
            "component_graph": graphs["component_graph"]["adjacency"],
        },
    }


# ──────────────────────────────────────────────
# UI Rendering
# ──────────────────────────────────────────────

def render_header():
    """Render application header."""
    st.markdown('<p class="main-header">🔍 Repo Intelligence Engine</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Advanced repository intelligence analysis with AI architectural review</p>',
        unsafe_allow_html=True,
    )


def render_project_overview(results: dict):
    """Render project overview section."""
    st.header("📋 Project Overview")
    meta = results["master_json"]["project_metadata"]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Files", meta["total_files"])
    col2.metric("Primary Language", meta["primary_language"])
    col3.metric("Source Files", meta["source_files"])
    col4.metric("Config Files", meta["config_files"])

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Documentation", meta["documentation_files"])
    col6.metric("Assets", meta["asset_files"])
    col7.metric("Frontend", "✅" if meta["frontend_detected"] else "❌")
    col8.metric("Backend", "✅" if meta["backend_detected"] else "❌")

    # Project type badges
    badges = []
    if meta.get("is_nextjs"):
        badges.append("Next.js")
    if meta.get("is_vite"):
        badges.append("Vite")

    pt = results["project_type"]
    for fw in pt.get("frameworks", []):
        badges.append(fw)

    if badges:
        st.markdown("**Detected Frameworks:** " + " · ".join(f"`{b}`" for b in badges))


def render_dependencies(results: dict):
    """Render dependencies section."""
    st.header("📦 Dependencies")
    config = results["config_data"]
    deps = results["master_json"]["dependencies"]
    frameworks = results["master_json"]["frameworks"]

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Frontend")
        if frameworks.get("frontend"):
            st.markdown("**Frameworks:** " + ", ".join(f"`{f}`" for f in frameworks["frontend"]))
        if deps.get("frontend"):
            with st.expander(f"Dependencies ({len(deps['frontend'])})", expanded=False):
                for dep in sorted(deps["frontend"]):
                    st.markdown(f"- `{dep}`")
        else:
            st.info("No frontend dependencies detected.")

    with col2:
        st.subheader("Backend")
        if frameworks.get("backend"):
            st.markdown("**Frameworks:** " + ", ".join(f"`{f}`" for f in frameworks["backend"]))
        if deps.get("backend"):
            with st.expander(f"Dependencies ({len(deps['backend'])})", expanded=False):
                for dep in sorted(deps["backend"]):
                    st.markdown(f"- `{dep}`")
        else:
            st.info("No backend dependencies detected.")

    # Scripts
    pkg = config.get("package_json")
    if pkg and pkg.get("scripts"):
        with st.expander("📜 npm Scripts", expanded=False):
            for name, cmd in pkg["scripts"].items():
                st.code(f"{name}: {cmd}", language="bash")


def render_file_breakdown(results: dict):
    """Render file breakdown with expandable details."""
    st.header("📁 File Breakdown")
    classification = results["classification"]
    source_analysis = results["source_analysis"]

    # Source files
    if classification["source"]:
        with st.expander(f"🔧 Source Files ({len(classification['source'])})", expanded=True):
            for analysis in source_analysis:
                fp = analysis["file_path"]
                lang = analysis.get("language", "")
                classes = analysis.get("classes", [])
                functions = analysis.get("functions", [])
                components = analysis.get("components", [])
                routes = analysis.get("routes", [])
                imports = analysis.get("imports", [])

                with st.expander(f"📄 {fp} [{lang}]", expanded=False):
                    # Generate file summary
                    summary = _generate_file_summary(analysis)
                    if summary:
                        st.info(f"**Summary:** {summary}")
                    
                    # Display static semantic description
                    semantic_desc = analysis.get("semantic_description", "")
                    if semantic_desc:
                        st.success(f"**🧠 Semantic Analysis:** {semantic_desc}")
                    
                    cols = st.columns(4)
                    cols[0].metric("Classes", len(classes))
                    cols[1].metric("Functions", len(functions))
                    cols[2].metric("Components", len(components))
                    cols[3].metric("Imports", len(imports))

                    if classes:
                        st.markdown("**Classes:**")
                        for c in classes:
                            name = c["name"] if isinstance(c, dict) else c
                            bases = c.get("bases", []) if isinstance(c, dict) else []
                            decorators = c.get("decorators", []) if isinstance(c, dict) else []
                            base_str = f" extends {', '.join(bases)}" if bases else ""
                            dec_str = f" @{', @'.join(decorators[:2])}" if decorators else ""
                            st.markdown(f"- `{name}`{base_str}{dec_str}")

                    if functions:
                        st.markdown("**Functions:**")
                        for f in functions[:30]:
                            if isinstance(f, dict):
                                name = f.get("name", "")
                                desc = f.get("description", "")
                                decorators = f.get("decorators", [])
                                dec_str = f" @{', @'.join(decorators[:2])}" if decorators else ""
                                if desc:
                                    st.markdown(f"- `{name}()`{dec_str} — {desc}")
                                else:
                                    st.markdown(f"- `{name}()`{dec_str}")
                            else:
                                st.markdown(f"- `{f}()`")

                    if components:
                        st.markdown("**React Components:**")
                        for comp in components:
                            st.markdown(f"- `<{comp}/>`")
                        
                        # Show hooks if present
                        hooks = analysis.get("react_hooks", [])
                        if hooks:
                            st.markdown(f"  **Hooks used:** {', '.join(f'`{h}`' for h in hooks)}")

                    if routes:
                        st.markdown("**Routes:**")
                        for r in routes:
                            method = r.get("method", "")
                            path = r.get("path", r.get("decorator", ""))
                            st.markdown(f"- `{method} {path}`")

    # Config files
    if classification["config"]:
        with st.expander(f"⚙️ Configuration Files ({len(classification['config'])})", expanded=False):
            for f in classification["config"]:
                st.markdown(f"- `{f['path']}` ({f['size']} bytes)")

    # Documentation
    if classification["documentation"]:
        with st.expander(f"📝 Documentation ({len(classification['documentation'])})", expanded=False):
            for f in classification["documentation"]:
                st.markdown(f"- `{f['path']}`")

    # Assets
    if classification["asset"]:
        with st.expander(f"🎨 Assets ({len(classification['asset'])})", expanded=False):
            for f in classification["asset"]:
                st.markdown(f"- `{f['path']}` ({f['size']} bytes)")


def render_infrastructure(results: dict):
    """Render infrastructure details."""
    st.header("🏗️ Infrastructure")
    infra = results["master_json"]["infrastructure"]
    config = results["config_data"]

    col1, col2 = st.columns(2)
    col1.metric("Docker", "✅ Used" if infra["docker_used"] else "❌ Not detected")
    col2.metric("CI/CD", "✅ Detected" if infra["ci_cd_detected"] else "❌ Not detected")

    # Dockerfile details
    if config.get("dockerfile"):
        df = config["dockerfile"]
        with st.expander("🐳 Dockerfile Details", expanded=True):
            st.markdown(f"**Base Image(s):** {', '.join(f'`{img}`' for img in df.get('base_images', []))}")
            if df.get("exposed_ports"):
                st.markdown(f"**Exposed Ports:** {', '.join(df['exposed_ports'])}")
            if df.get("cmd"):
                st.markdown(f"**CMD:** `{df['cmd']}`")
            if df.get("entrypoint"):
                st.markdown(f"**ENTRYPOINT:** `{df['entrypoint']}`")
            if df.get("is_multistage"):
                st.markdown(f"**Multi-stage Build:** ✅ ({df['stages']} stages)")

    # Docker Compose details
    if config.get("docker_compose"):
        dc = config["docker_compose"]
        with st.expander("🐙 Docker Compose Details", expanded=False):
            if dc.get("services"):
                st.markdown(f"**Services:** {', '.join(f'`{s}`' for s in dc['services'])}")
            st.markdown(f"**Volumes:** {'✅' if dc.get('has_volumes') else '❌'}")
            st.markdown(f"**Networks:** {'✅' if dc.get('has_networks') else '❌'}")


def render_architecture_diagrams(results: dict):
    """Render architecture diagrams."""
    st.header("📊 Architecture Diagrams")
    graphs = results["graphs"]

    has_any_diagram = False

    # Module Dependencies
    if graphs["module_dependency"]["png"]:
        has_any_diagram = True
        with st.expander("🔗 Module Dependency Graph", expanded=True):
            try:
                st.image(graphs["module_dependency"]["png"], use_container_width=True)
                st.caption("Visual representation of module imports and dependencies")
            except Exception as e:
                st.error(f"Could not render module dependency graph: {e}")
    elif graphs["module_dependency"]["adjacency"]:
        has_any_diagram = True
        with st.expander("🔗 Module Dependency Graph (Data)", expanded=True):
            st.caption("Graphviz not available. Showing adjacency list instead.")
            st.json(graphs["module_dependency"]["adjacency"])

    # API Routes
    if graphs["api_routes"]["png"]:
        has_any_diagram = True
        with st.expander("🛣️ API Route Flow", expanded=True):
            try:
                st.image(graphs["api_routes"]["png"], use_container_width=True)
                st.caption("API endpoints and their handler functions")
            except Exception as e:
                st.error(f"Could not render API route graph: {e}")
    elif graphs["api_routes"]["adjacency"]:
        has_any_diagram = True
        with st.expander("🛣️ API Route Flow (Data)", expanded=True):
            st.caption("Graphviz not available. Showing adjacency list instead.")
            st.json(graphs["api_routes"]["adjacency"])

    # Component Graph
    if graphs["component_graph"]["png"]:
        has_any_diagram = True
        with st.expander("⚛️ React Component Graph", expanded=True):
            try:
                st.image(graphs["component_graph"]["png"], use_container_width=True)
                st.caption("React component relationships and dependencies")
            except Exception as e:
                st.error(f"Could not render component graph: {e}")
    elif graphs["component_graph"]["adjacency"]:
        has_any_diagram = True
        with st.expander("⚛️ React Component Graph (Data)", expanded=True):
            st.caption("Graphviz not available. Showing adjacency list instead.")
            st.json(graphs["component_graph"]["adjacency"])

    if not has_any_diagram:
        st.info("No architecture diagrams were generated. This may happen for very small repositories or when Graphviz is not installed.")
        st.markdown("**Install Graphviz:**")
        st.code("Ubuntu/Debian: sudo apt install graphviz\nmacOS: brew install graphviz\nWindows: choco install graphviz OR download from graphviz.org", language="bash")


def render_ai_review(results: dict):
    """Render AI architectural review section."""
    st.header("🤖 AI Architectural Review")
    hf_token = _get_hf_token()

    if not hf_token:
        st.warning(
            "**Hugging Face API token not configured.**\n\n"
            "To enable AI-powered architectural review:\n"
            "1. Get a token from [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)\n"
            "2. Set `HF_API_TOKEN` environment variable before starting Streamlit\n\n"
            "✅ **Static semantic analysis completed successfully** — see File Breakdown section for detailed insights."
        )
        return

    ai_result = results.get("ai_review")
    if ai_result and ai_result.get("success"):
        st.markdown(ai_result["review"])
    elif ai_result:
        st.info(
            f"**AI review unavailable:** {ai_result.get('error', 'Unknown error')}\n\n"
            "✅ **Static semantic analysis completed successfully** — see File Breakdown section for detailed insights."
        )


def render_raw_json(results: dict):
    """Render downloadable raw JSON."""
    with st.expander("📋 Raw Analysis JSON", expanded=False):
        json_str = json.dumps(results["master_json"], indent=2, default=str)
        st.download_button(
            label="⬇️ Download Full Analysis JSON",
            data=json_str,
            file_name=f"{results['repo_data']['repo']}_analysis.json",
            mime="application/json",
        )
        st.json(results["master_json"])


def _generate_file_summary(analysis: dict) -> str:
    """Generate a brief human-readable summary of what a file does."""
    fp = analysis["file_path"]
    lang = analysis.get("language", "")
    classes = analysis.get("classes", [])
    functions = analysis.get("functions", [])
    components = analysis.get("components", [])
    routes = analysis.get("routes", [])
    
    summary_parts = []
    
    if components:
        summary_parts.append(f"Defines {len(components)} React component(s): {', '.join(components[:3])}")
    elif classes:
        class_names = [c["name"] if isinstance(c, dict) else c for c in classes[:3]]
        summary_parts.append(f"Defines {len(classes)} class(es): {', '.join(class_names)}")
    elif routes:
        route_methods = [r.get("method", "ROUTE") for r in routes[:3]]
        summary_parts.append(f"API endpoint file with {len(routes)} route(s): {', '.join(set(route_methods))}")
    elif functions and len(functions) > 0:
        func_names = [f["name"] if isinstance(f, dict) else f for f in functions[:3]]
        summary_parts.append(f"{lang} module with {len(functions)} function(s) including {', '.join(func_names)}")
    
    if "test" in fp.lower() or "spec" in fp.lower():
        summary_parts.append("Test file")
    
    return " • ".join(summary_parts) if summary_parts else f"{lang} source file"


# PDF generation is now handled by the dedicated pdf_generator module
# See pdf_generator.py for the comprehensive PDF generation implementation


def render_pdf_export(results: dict):
    """Render PDF export button."""
    st.header("📄 Export Report")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("📥 Generate PDF Report", type="primary", use_container_width=True):
            with st.spinner("Generating comprehensive PDF report..."):
                try:
                    pdf_bytes = generate_comprehensive_pdf_report(results)
                    st.download_button(
                        label="⬇️ Download PDF Report",
                        data=pdf_bytes,
                        file_name=f"{results['repo_data']['repo']}_intelligence_report.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                    st.success("PDF generated successfully!")
                except Exception as e:
                    st.error(f"Failed to generate PDF: {e}")


# ──────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────

def render_sidebar():
    """Render sidebar with configuration."""
    with st.sidebar:
        st.markdown("### 📖 About")
        st.markdown(
            "Repo Intelligence Engine performs deep static analysis "
            "of public GitHub repositories and generates AI-powered "
            "architectural reviews.\n\n"
            "**Features:**\n"
            "- Multi-language source parsing\n"
            "- Dependency analysis\n"
            "- Architecture diagrams\n"
            "- React component detection\n"
            "- API route mapping\n"
            "- AI architectural review"
        )

        st.divider()
        st.caption("Built with Streamlit · Graphviz · Hugging Face")


# ──────────────────────────────────────────────
# Main Application
# ──────────────────────────────────────────────

def main():
    """Main application entry point."""
    # Log API token status to console
    github_token = _get_github_token()
    hf_token = _get_hf_token()
    
    print("\n" + "="*60)
    print("🔧 Repo Intelligence Engine - API Configuration")
    print("="*60)
    print(f"GitHub Token: {'✅ Configured' if github_token else '❌ Not Set (rate limited)'}")
    print(f"HF API Token: {'✅ Configured' if hf_token else '❌ Not Set (no AI review)'}")
    print("="*60 + "\n")
    
    render_header()
    render_sidebar()

    # URL Input
    repo_url = st.text_input(
        "🔗 GitHub Repository URL",
        placeholder="https://github.com/owner/repo",
        help="Enter a public GitHub repository URL to analyze.",
    )

    col1, col2, col3 = st.columns([1, 1, 4])
    analyze_btn = col1.button("🚀 Analyze", type="primary", use_container_width=True)
    clear_btn = col2.button("🗑️ Clear", use_container_width=True)

    if clear_btn:
        st.session_state.pop("analysis_results", None)
        st.rerun()

    # Run analysis
    if analyze_btn and repo_url:
        # Validate URL
        try:
            parse_github_url(repo_url)
        except ValueError as e:
            st.error(str(e))
            return

        try:
            results = run_analysis(repo_url)
            st.session_state["analysis_results"] = results
        except ValueError as e:
            st.error(f"❌ {str(e)}")
            return
        except RuntimeError as e:
            st.error(f"❌ {str(e)}")
            return
        except Exception as e:
            st.error(f"❌ An unexpected error occurred: {str(e)}")
            return

    elif analyze_btn and not repo_url:
        st.warning("Please enter a GitHub repository URL.")
        return

    # Render results
    if "analysis_results" in st.session_state:
        results = st.session_state["analysis_results"]

        st.divider()
        render_project_overview(results)
        st.divider()
        render_dependencies(results)
        st.divider()
        render_file_breakdown(results)
        st.divider()
        render_infrastructure(results)
        st.divider()
        render_architecture_diagrams(results)
        st.divider()
        
        # AI Review with result storage
        hf_token = _get_hf_token()
        if hf_token and "ai_review" not in results:
            with st.spinner("🧠 Generating AI architectural review..."):
                ai_result = get_ai_review(results["master_json"], hf_token=hf_token)
                results["ai_review"] = ai_result
        
        render_ai_review(results)
        st.divider()
        render_pdf_export(results)
        st.divider()
        render_raw_json(results)


if __name__ == "__main__":
    main()
