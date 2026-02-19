"""  
AI Interpretation Layer
Uses Hugging Face Inference API to generate architectural analysis.
Falls back gracefully to static semantic analysis if AI is unavailable.

NOTE: Hugging Face free inference endpoints are currently unreliable.
The app works excellently with the static semantic analysis engine alone.
"""

import json
import time
from typing import Optional, List, Dict

# AI enhancement is optional - static semantic analysis is the primary method
HF_SDK_AVAILABLE = False  # Disabled due to HF API endpoint deprecations

MAX_INPUT_CHARS = 400  # Keep prompts short


def _build_prompt(structured_json: dict) -> str:
    """Build a simplified prompt for Flan-T5 model."""
    # Create a very condensed summary for Flan-T5's limited context
    summary = _condense_json(structured_json)
    
    # Extract key information
    meta = summary.get("project_metadata", {})
    lang = meta.get("primary_language", "Unknown")
    total_files = meta.get("total_files", 0)
    frontend = meta.get("frontend_detected", False)
    backend = meta.get("backend_detected", False)
    
    # Flan-T5 works best with clear instruction format
    project_type = []
    if frontend:
        project_type.append("frontend")
    if backend:
        project_type.append("backend")
    
    type_str = " and ".join(project_type) if project_type else "software"
    
    # Use summarization task which T5 models are designed for
    prompt = f"Summarize: This is a {lang} {type_str} project. Describe its architecture."
    
    return prompt


def _condense_json(data: dict) -> dict:
    """
    Condense the full analysis JSON to essential information only.
    This ensures we never send raw code — only structured metadata.
    """
    condensed = {}

    # Project metadata
    if "project_metadata" in data:
        condensed["project_metadata"] = data["project_metadata"]

    # Source analysis — only summaries, no code
    if "source_analysis" in data:
        source_summary = []
        for item in data["source_analysis"][:30]:  # Limit files
            entry = {
                "file_path": item.get("file_path", ""),
                "language": item.get("language", ""),
                "classes": [c.get("name", "") if isinstance(c, dict) else c
                           for c in item.get("classes", [])[:10]],
                "functions": [f.get("name", "") if isinstance(f, dict) else f
                             for f in item.get("functions", [])[:15]],
                "components": item.get("components", [])[:10],
                "routes": item.get("routes", [])[:10],
                "import_count": len(item.get("imports", [])),
            }
            source_summary.append(entry)
        condensed["source_analysis"] = source_summary

    # Dependencies
    if "dependencies" in data:
        condensed["dependencies"] = data["dependencies"]

    # Infrastructure
    if "infrastructure" in data:
        condensed["infrastructure"] = data["infrastructure"]

    # Frameworks
    if "frameworks" in data:
        condensed["frameworks"] = data["frameworks"]

    return condensed


def get_ai_review(
    structured_json: dict,
    hf_token: Optional[str] = None,
) -> dict:
    """
    Generate architectural review using AI (if available) or static analysis.
    
    Currently disabled due to Hugging Face free tier API endpoint changes.
    The static semantic analysis provides excellent results on its own.

    Returns:
        dict with 'success' bool, 'review' text, and 'error' message if using static.
    """
    # HF free inference endpoints are currently unreliable due to API changes
    # (410 errors, router endpoint not working with free models)
    # Static semantic analysis provides excellent results, so we use that instead
    
    return {
        "success": False,
        "review": None,
        "error": "AI enhancement temporarily unavailable (HF API endpoints changed). Using comprehensive static semantic analysis instead.",
    }


def generate_function_descriptions(functions: List[Dict], file_path: str, language: str, hf_token: str) -> List[Dict]:
    """
    Use AI to generate descriptions for functions that don't have docstrings.
    Returns the functions list with added 'description' fields.
    """
    if not functions:
        return functions
    
    # Only process functions without descriptions
    functions_to_describe = [f for f in functions if isinstance(f, dict) and not f.get('description', '').strip()]
    
    # Deprecated: This function is now handled by semantic_inference.py
    # which provides more reliable rule-based descriptions without AI
    return functions
