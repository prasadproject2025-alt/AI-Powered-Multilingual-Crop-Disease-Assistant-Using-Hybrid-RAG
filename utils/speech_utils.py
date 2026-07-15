"""
Speech utilities for voice input and text-to-speech output.
Supports multiple languages for farmer-friendly interaction.
"""

import speech_recognition as sr
from gtts import gTTS
import os
import platform
import subprocess
from typing import Optional

# Language code mapping for gTTS
LANG_CODES = {
    "hi": "hi",  # Hindi
    "en": "en",  # English
    "te": "te",  # Telugu
    "ta": "ta",  # Tamil
    "mr": "mr",  # Marathi
    "bn": "bn",  # Bengali
    "gu": "gu",  # Gujarati
    "kn": "kn",  # Kannada
    "ml": "ml",  # Malayalam
    "or": "or",  # Odia
    "pa": "pa",  # Punjabi
}

def get_voice_input(language: str = "en") -> Optional[str]:
    """
    Get voice input from microphone.
    
    Args:
        language: Language code for speech recognition (e.g., 'en', 'hi', 'te')
                  Note: SpeechRecognition library primarily supports English well.
                  For other languages, you may need to configure differently.
    
    Returns:
        Recognized text or None if recognition fails
    """
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    
    try:
        print("🎙️ Listening... (speak now)")
        with microphone as source:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            # Listen for audio
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
        
        print("🔄 Processing audio...")
        
        # Try Google Speech Recognition (works best for English)
        # For other languages, you may need to use language parameter
        try:
            # Map language codes for Google Speech Recognition
            lang_map = {
                "hi": "hi-IN",
                "en": "en-US",
                "te": "te-IN",
                "ta": "ta-IN",
                "mr": "mr-IN",
                "bn": "bn-IN",
                "gu": "gu-IN",
                "kn": "kn-IN",
                "ml": "ml-IN",
            }
            
            recognition_lang = lang_map.get(language, "en-US")
            text = recognizer.recognize_google(audio, language=recognition_lang)
            print(f"✅ Recognized: {text}")
            return text
        
        except sr.UnknownValueError:
            print("⚠️ Could not understand audio. Please try again.")
            return None
        except sr.RequestError as e:
            print(f"⚠️ Speech recognition service error: {e}")
            return None
    
    except sr.WaitTimeoutError:
        print("⚠️ No speech detected. Please try again.")
        return None
    except Exception as e:
        print(f"⚠️ Error getting voice input: {e}")
        return None

def clean_text_for_speech(text: str) -> str:
    """
    Remove markdown and special characters from text before TTS.
    
    Args:
        text: Text with markdown
    
    Returns:
        Clean text suitable for speech
    """
    import re
    
    # Remove markdown bold/italic
    text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)  # **bold**
    text = re.sub(r'\*([^\*]+)\*', r'\1', text)      # *italic*
    text = re.sub(r'__([^_]+)__', r'\1', text)       # __bold__
    text = re.sub(r'_([^_]+)_', r'\1', text)         # _italic_
    
    # Remove markdown headers
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    
    # Remove markdown links
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    # Remove special markdown characters
    text = text.replace('⚠️', 'Warning')
    text = text.replace('✅', 'Success')
    text = text.replace('❌', 'Error')
    text = text.replace('💡', 'Tip')
    text = text.replace('🌾', '')
    text = text.replace('🔊', '')
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    return text

def speak_text(text: str, language: str = "en", slow: bool = False):
    """
    Convert text to speech and play it.
    Automatically cleans markdown before speaking.
    
    Args:
        text: Text to speak (may contain markdown)
        language: Language code (e.g., 'en', 'hi', 'te')
        slow: Whether to speak slowly (useful for learning)
    """
    if not text or not text.strip():
        return
    
    try:
        # Clean markdown from text before speaking
        clean_text = clean_text_for_speech(text)
        
        if not clean_text or not clean_text.strip():
            print("⚠️ No text to speak after cleaning")
            return
        
        lang_code = LANG_CODES.get(language.lower(), "en")
        
        # Create TTS object with cleaned text
        tts = gTTS(text=clean_text, lang=lang_code, slow=slow)
        
        # Save to temporary file
        temp_file = "temp_speech.mp3"
        tts.save(temp_file)
        
        # Play the audio file based on OS
        system = platform.system()
        if system == "Windows":
            os.startfile(temp_file)
        elif system == "Darwin":  # macOS
            subprocess.run(["afplay", temp_file])
        else:  # Linux
            subprocess.run(["mpg123", temp_file], check=False)
            # Alternative for Linux: use aplay or other audio player
        
        # Note: File is not deleted immediately to allow playback
        # Consider adding cleanup after playback completes
        print(f"🔊 Speaking: {text[:50]}...")
    
    except Exception as e:
        print(f"⚠️ Text-to-speech error: {e}")
        print(f"📝 Displaying text instead: {text}")

def cleanup_speech_file():
    """Remove temporary speech file if it exists."""
    temp_file = "temp_speech.mp3"
    if os.path.exists(temp_file):
        try:
            os.remove(temp_file)
        except:
            pass  # Ignore cleanup errors
