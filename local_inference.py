"""
HuggingFace Inference API Engine
Generates intelligent content using HuggingFace's Inference API.
Uses cloud-based models for better performance without local downloads.
"""

from typing import Optional
import re
import os

try:
    from huggingface_hub import InferenceClient
    HAS_HF_HUB = True
except ImportError:
    HAS_HF_HUB = False


class LocalInferenceEngine:
    """Uses HuggingFace Inference API for intelligent content generation."""
    
    # Best models for code understanding and text generation
    MODELS = [
        "meta-llama/Llama-3.1-8B-Instruct",      # Verified working with this token
        "meta-llama/Meta-Llama-3-8B-Instruct",   # Alternative instruct model
        "Qwen/Qwen2.5-7B-Instruct",              # Strong instruction model
        "mistralai/Mistral-7B-Instruct-v0.2",    # Fallback if provider supports it
    ]
    
    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize the inference engine with HuggingFace API.
        
        Args:
            api_token: HuggingFace API token. If None, tries to load from secrets.toml or env
        """
        self.api_token = api_token or self._load_token()
        self.client = None
        self.current_model = None
        self.initialize_models()
    
    def _load_token(self) -> Optional[str]:
        """Load HuggingFace token from secrets.toml or environment."""
        # Try environment variable
        token = os.getenv("HF_API_TOKEN") or os.getenv("HUGGINGFACE_TOKEN") or os.getenv("HF_TOKEN")
        if token:
            return token
        
        # Try secrets.toml in .streamlit folder
        try:
            import toml
            # Get the directory where this file is located
            current_dir = os.path.dirname(os.path.abspath(__file__))
            secrets_path = os.path.join(current_dir, ".streamlit", "secrets.toml")
            
            if os.path.exists(secrets_path):
                secrets = toml.load(secrets_path)
                token = secrets.get("HF_API_TOKEN")
                if token:
                    print(f"✓ Loaded HF_API_TOKEN from secrets.toml")
                    return token
        except Exception as e:
            print(f"Warning: Could not load secrets.toml: {e}")
        
        return None
    
    def initialize_models(self):
        """Initialize API connection and test models."""
        if not HAS_HF_HUB:
            print("Warning: huggingface_hub not installed. Using fallback methods.")
            return
            
        if not self.api_token:
            print("Warning: No HuggingFace API token found. Using fallback methods.")
            return
        
        try:
            # Create inference client
            self.client = InferenceClient(token=self.api_token)
            
            # Test which model works
            for model in self.MODELS:
                try:
                    # Prefer chat-completions for modern instruct models
                    response = self.client.chat.completions.create(
                        model=model,
                        messages=[{"role": "user", "content": "Say OK"}],
                        max_tokens=6,
                        temperature=0.0,
                    )
                    if response:
                        self.current_model = model
                        print(f"✓ Using HuggingFace model: {model}")
                        return
                except Exception as e:
                    print(f"  Model {model}: {str(e)[:100]}")
                    continue
        except Exception as e:
            print(f"Warning: Could not initialize HF client: {e}")
        
        print("Warning: Could not connect to HuggingFace API. Using fallback methods.")
        self.client = None
    
    def _query(self, prompt: str, max_length: int = 150) -> Optional[str]:
        """
        Query the HuggingFace Inference API.
        
        Args:
            prompt: Input text
            max_length: Maximum response length
            
        Returns:
            Generated text or None
        """
        if not self.client or not self.current_model:
            return None
        
        try:
            response = self.client.chat.completions.create(
                model=self.current_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_length,
                temperature=0.3,
            )

            if response and response.choices and response.choices[0].message:
                content = response.choices[0].message.content
                if content:
                    return content.strip()

        except Exception as e:
            try:
                response = self.client.text_generation(
                    prompt,
                    model=self.current_model,
                    max_new_tokens=max_length,
                    temperature=0.3,
                    return_full_text=False
                )
                if response and isinstance(response, str):
                    return response.strip()
            except Exception:
                print(f"Error querying model: {str(e)[:100]}")
        
        return None
    
    def generate_function_description(self, function_info: dict) -> str:
        """
        Generate a detailed description of a function using HuggingFace API.
        
        Args:
            function_info: Dictionary containing function details
            
        Returns:
            str: Detailed description of the function's purpose
        """
        try:
            func_name = function_info.get("name", "function")
            params = function_info.get("params", {})
            returns = function_info.get("returns", "")
            docstring = function_info.get("docstring", "")
            language = function_info.get("language", "")
            
            # Build a prompt for the model
            param_str = ", ".join(params.keys()) if params else "no parameters"
            
            prompt = f"""Describe what this {language} function does in 1-2 clear sentences:
Function: {func_name}({param_str})
Returns: {returns if returns else 'unknown'}
{f'Docstring: {docstring[:200]}' if docstring else ''}

Description:"""
            
            # Query HuggingFace API
            result = self._query(prompt, max_length=100)
            
            if result and len(result) > 10:
                return result
        except Exception as e:
            print(f"Error generating description: {e}")
        
        return self._fallback_description(function_info)
    
    def generate_file_summary(self, file_info: dict) -> str:
        """
        Generate a comprehensive summary of a file's purpose.
        
        Args:
            file_info: File analysis dictionary
            
        Returns:
            str: Summary of the file's purpose
        """
        try:
            file_path = file_info.get("file_path", "file.js")
            language = file_info.get("language", "Unknown")
            classes = file_info.get("classes", [])
            functions = file_info.get("functions", [])
            imports = file_info.get("imports", [])
            
            class_str = ", ".join(classes[:3]) if classes else "none"
            func_str = ", ".join(f['name'] for f in functions[:3] if isinstance(f, dict)) if functions else "none"
            
            prompt = f"""Describe what this {language} source file does in 2-3 sentences:
File: {file_path}
Classes: {class_str}
Functions: {func_str}
Key imports: {', '.join(str(i)[:30] for i in imports[:5]) if imports else 'standard'}

Summary:"""
            
            result = self._query(prompt, max_length=150)
            
            if result and len(result) > 10:
                return result
        except Exception as e:
            print(f"Error generating file summary: {e}")
        
        return self._fallback_file_summary(file_info)
    
    def generate_class_description(self, class_info: dict) -> str:
        """
        Generate a detailed description of a class.
        
        Args:
            class_info: Dictionary containing class details
            
        Returns:
            str: Detailed description of the class
        """
        try:
            class_name = class_info.get("name", "Class")
            methods = class_info.get("methods", [])
            properties = class_info.get("properties", [])
            
            method_str = ", ".join(methods[:5]) if methods else "none"
            prop_str = ", ".join(properties[:5]) if properties else "none"
            
            prompt = f"""Describe the purpose of this class in 1-2 sentences:
Class: {class_name}
Methods: {method_str}
Properties: {prop_str}

Purpose:"""
            
            result = self._query(prompt, max_length=80)
            
            if result and len(result) > 10:
                return result
        except Exception as e:
            print(f"Error generating class description: {e}")
        
        return self._fallback_class_description(class_info)
    
    @staticmethod
    def _fallback_description(function_info: dict) -> str:
        """Fallback description when model is unavailable."""
        func_name = function_info.get("name", "function")
        params = function_info.get("params", {})
        returns = function_info.get("returns", "")
        docstring = function_info.get("docstring", "")
        
        description = f"The '{func_name}' function"
        
        if params:
            description += f" accepts {len(params)} parameter(s)"
        
        if returns:
            description += f" and returns {returns}"
        
        if docstring:
            description += f". {docstring[:100]}"
        else:
            description += " performs specific operations within the codebase."
        
        return description
    
    @staticmethod
    def _fallback_file_summary(file_info: dict) -> str:
        """Fallback file summary when model is unavailable."""
        file_path = file_info.get("file_path", "file")
        language = file_info.get("language", "Unknown")
        classes = file_info.get("classes", [])
        functions = file_info.get("functions", [])
        
        parts = file_path.split("/")
        file_name = parts[-1] if parts else file_path
        
        summary = f"This {language} file ({file_name}) contains "
        
        if classes:
            summary += f"{len(classes)} class(es)"
            if functions:
                summary += f" and {len(functions)} function(s)"
        elif functions:
            summary += f"{len(functions)} function(s)"
        else:
            summary += "utility code"
        
        summary += " for the project."
        return summary
    
    @staticmethod
    def _fallback_class_description(class_info: dict) -> str:
        """Fallback class description when model is unavailable."""
        class_name = class_info.get("name", "Class")
        methods = class_info.get("methods", [])
        
        desc = f"The {class_name} class"
        if methods:
            desc += f" provides {len(methods)} method(s) for"
        else:
            desc += " defines"
        
        desc += " core functionality in the codebase."
        return desc


# Global instance
_inference_engine = None


def get_inference_engine() -> LocalInferenceEngine:
    """Get or create the global inference engine instance."""
    global _inference_engine
    if _inference_engine is None:
        _inference_engine = LocalInferenceEngine()
    return _inference_engine


def generate_function_description(function_info: dict) -> str:
    """Generate description for a function."""
    engine = get_inference_engine()
    return engine.generate_function_description(function_info)


def generate_file_summary(file_info: dict) -> str:
    """Generate summary for a file."""
    engine = get_inference_engine()
    return engine.generate_file_summary(file_info)


def generate_class_description(class_info: dict) -> str:
    """Generate description for a class."""
    engine = get_inference_engine()
    return engine.generate_class_description(class_info)


def generate_repo_summary(repo_info: dict) -> str:
    """
    Generate an intelligent summary of the entire repository.
    
    Args:
        repo_info: Dictionary containing repository metrics
        
    Returns:
        str: Summary of the repository's purpose and structure
    """
    try:
        total_files = repo_info.get("total_source_files", 0)
        total_functions = repo_info.get("total_functions", 0)
        total_classes = repo_info.get("total_classes", 0)
        top_files = repo_info.get("top_function_files", [])
        
        engine = get_inference_engine()
        
        # Build prompt for AI model
        top_files_str = ", ".join(top_files[:3]) if top_files else "various"
        prompt = f"""Summarize what this repository does in 1-2 sentences:
Total Files: {total_files}
Total Functions: {total_functions}
Total Classes: {total_classes}
Key Files: {top_files_str}

Summary:"""
        
        result = engine._query(prompt, max_length=120) if engine.client else None
        
        if result and len(result) > 20:
            return result
    except Exception as e:
        print(f"Error generating repo summary: {e}")
    
    # Fallback summary
    parts = []
    if total_files:
        parts.append(f"{total_files} source files")
    if total_classes:
        parts.append(f"{total_classes} classes")
    if total_functions:
        parts.append(f"{total_functions} functions")
    
    if parts:
        return f"This repository contains {', '.join(parts)} organized across multiple modules."
    return "A software project with multiple code files and components."


def get_model_status() -> dict:
    """
    Get the current status of the inference model.
    
    Returns:
        dict: Status dictionary with keys:
            - model: Current model name (or None if unavailable)
            - hf_disabled: Boolean indicating if HF API is disabled
            - reason: Reason if disabled
    """
    engine = get_inference_engine()
    
    status = {
        "model": engine.current_model,
        "hf_disabled": False,
        "reason": None,
    }
    
    if not engine.client or not engine.current_model:
        status["hf_disabled"] = True
        
        if not HAS_HF_HUB:
            status["reason"] = "huggingface_hub library not installed"
        elif not engine.api_token:
            status["reason"] = "HF_API_TOKEN not configured"
        else:
            status["reason"] = "Could not connect to HuggingFace API"
    
    return status
