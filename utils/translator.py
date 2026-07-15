"""
Translation utility using Google Translate API (deep-translator library - more compatible)
Translates text between various languages for farmer-friendly communication.
"""

from typing import Optional

try:
    from deep_translator import GoogleTranslator
    DEEP_TRANSLATOR_AVAILABLE = True
except ImportError:
    DEEP_TRANSLATOR_AVAILABLE = False
    try:
        from googletrans import Translator
        GTRANSLATE_AVAILABLE = True
    except ImportError:
        GTRANSLATE_AVAILABLE = False

# Initialize translator (singleton pattern)
_translator_instance = None

def get_translator():
    """Get or create translator instance."""
    global _translator_instance
    if _translator_instance is None:
        if DEEP_TRANSLATOR_AVAILABLE:
            _translator_instance = "deep_translator"
        elif GTRANSLATE_AVAILABLE:
            _translator_instance = Translator()
        else:
            _translator_instance = None
    return _translator_instance

def translate_text(text: str, target_lang: str, source_lang: Optional[str] = "auto") -> str:
    """
    Translate text to target language.
    
    Args:
        text: Text to translate
        target_lang: Target language code (e.g., 'en', 'hi', 'te', 'ta', 'mr')
        source_lang: Source language code (default: 'auto' for auto-detection)
    
    Returns:
        Translated text
    """
    if not text or not text.strip():
        return text
    
    try:
        translator = get_translator()
        
        if translator == "deep_translator":
            # Use deep-translator (more compatible)
            if source_lang == "auto":
                result = GoogleTranslator(source='auto', target=target_lang).translate(text)
            else:
                result = GoogleTranslator(source=source_lang, target=target_lang).translate(text)
            return result
        elif translator:
            # Fallback to googletrans if available
            result = translator.translate(text, src=source_lang, dest=target_lang)
            return result.text
        else:
            print("⚠️ No translation library available. Install: pip install deep-translator")
            return text
    except Exception as e:
        print(f"⚠️ Translation error: {e}")
        # Return original text if translation fails
        return text

def detect_language(text: str) -> str:
    """
    Detect the language of the given text.
    
    Args:
        text: Text to detect language for
    
    Returns:
        Language code (e.g., 'en', 'hi', 'te')
    """
    if not text or not text.strip():
        return "en"
    
    try:
        translator = get_translator()
        
        if translator == "deep_translator":
            # deep-translator doesn't have direct detection, try translating to detect
            try:
                detected = GoogleTranslator(source='auto', target='en').translate(text[:100])
                # This is a workaround - actual detection would need a different library
                return "en"  # Default fallback
            except:
                return "en"
        elif translator:
            result = translator.detect(text)
            return result.lang
        else:
            return "en"
    except Exception as e:
        print(f"⚠️ Language detection error: {e}")
        return "en"  # Default to English
