"""
Utility modules for the AI-Powered Crop Disease Assistant.
"""

from .translator import translate_text, detect_language
from .kb_search import load_kb, search_kb, detect_crop_name
from .gemini_integration import initialize_gemini, generate_response
from .speech_utils import get_voice_input, speak_text

__all__ = [
    'translate_text',
    'detect_language',
    'load_kb',
    'search_kb',
    'detect_crop_name',
    'initialize_gemini',
    'generate_response',
    'get_voice_input',
    'speak_text',
]
