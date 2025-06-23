from typing import Optional
import pyttsx3


def text_to_speech(script: str, output_path: str, lang: str = "pt") -> None:
    """Generate speech audio from text using pyttsx3."""
    engine = pyttsx3.init()
    # Attempt to set language voice
    for voice in engine.getProperty('voices'):
        if lang in voice.languages[0].decode('utf-8'):
            engine.setProperty('voice', voice.id)
            break
    engine.save_to_file(script, output_path)
    engine.runAndWait()
