"""
Local Inference Engine
Generates intelligent content using pre-trained models from HuggingFace Transformers library.
Runs entirely offline without API calls.
"""

from typing import Optional
import re

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False


class LocalInferenceEngine:
    """Uses pre-trained models for intelligent content generation."""
    
    def __init__(self):
        """Initialize the inference engine with pre-trained models."""
        self.generator = None
        self.initialize_models()
    
    def initialize_models(self):
        """Initialize transformers pipelines for different tasks."""
        if not HAS_TRANSFORMERS:
            return
        
        try:
            # Use Flan-T5-small for lightweight inference
            # This model excels at various NLP tasks including summarization
            self.generator = pipeline(
                "text2text-generation",
                model="google/flan-t5-small",
                device=-1  # CPU only to avoid GPU memory issues
            )
        except Exception as e:
            print(f"Warning: Could not initialize transformers: {e}")
            self.generator = None
    
    def generate_function_description(self, function_info: dict) -> str:
        """
        Generate a detailed description of a function using the local model.
        
        Args:
            function_info: Dictionary containing function details
            
        Returns:
            str: Detailed description of the function's purpose
        """
        if not HAS_TRANSFORMERS or not self.generator:
            return self._fallback_description(function_info)
        
        try:
            func_name = function_info.get("name", "function")
            params = function_info.get("params", {})
            returns = function_info.get("returns", "")
            docstring = function_info.get("docstring", "")
            language = function_info.get("language", "")
            
            # Build a prompt for the model
            param_str = ", ".join(params.keys()) if params else "no parameters"
            
            prompt = f"""Analyze and describe this code function concisely:
Function name: {func_name}
Language: {language}
Parameters: {param_str}
Return type: {returns if returns else 'unknown'}
Docstring: {docstring if docstring else 'none provided'}

Provide a brief technical description of what this function does and why it's important. Keep it to 1-2 sentences."""
            
            # Generate using the model
            result = self.generator(
                prompt,
                max_length=100,
                min_length=20,
                do_sample=False
            )
            
            if result and len(result) > 0:
                return result[0]['generated_text'].strip()
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
        if not HAS_TRANSFORMERS or not self.generator:
            return self._fallback_file_summary(file_info)
        
        try:
            file_path = file_info.get("file_path", "file.js")
            language = file_info.get("language", "Unknown")
            classes = file_info.get("classes", [])
            functions = file_info.get("functions", [])
            imports = file_info.get("imports", [])
            
            class_str = ", ".join(classes[:3]) if classes else "none"
            func_str = ", ".join(f['name'] for f in functions[:3] if isinstance(f, dict)) if functions else "none"
            
            prompt = f"""Analyze this code file and describe its purpose:
File: {file_path}
Language: {language}
Classes/Components: {class_str}
Functions: {func_str}
Key imports: {', '.join(str(i)[:30] for i in imports[:5]) if imports else 'standard'}

Provide a clear, concise description of what this file does in the codebase. Keep it to 2-3 sentences."""
            
            result = self.generator(
                prompt,
                max_length=150,
                min_length=30,
                do_sample=False
            )
            
            if result and len(result) > 0:
                return result[0]['generated_text'].strip()
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
        if not HAS_TRANSFORMERS or not self.generator:
            return self._fallback_class_description(class_info)
        
        try:
            class_name = class_info.get("name", "Class")
            methods = class_info.get("methods", [])
            properties = class_info.get("properties", [])
            
            method_str = ", ".join(methods[:5]) if methods else "none"
            prop_str = ", ".join(properties[:5]) if properties else "none"
            
            prompt = f"""Describe the purpose of this class:
Class name: {class_name}
Methods: {method_str}
Properties: {prop_str}

What is the responsibility of this class? Keep it to 1-2 sentences."""
            
            result = self.generator(
                prompt,
                max_length=80,
                min_length=15,
                do_sample=False
            )
            
            if result and len(result) > 0:
                return result[0]['generated_text'].strip()
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
