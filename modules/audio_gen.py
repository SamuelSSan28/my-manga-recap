from typing import Optional
import pyttsx3


def _clean_script(script: str) -> str:
    """Remove metadata tags from script before speech synthesis."""
    cleaned = []
    for line in script.splitlines():
        if line.startswith("[IMAGEM"):
            continue
        cleaned.append(line.replace("[PAUSA]", ". "))
    return "\n".join(cleaned)


def text_to_speech(
    script: str,
    output_path: str,
    lang: str = "pt",
    voice_name: Optional[str] = None,
    use_tts: bool = False,
) -> None:
    """Generate speech audio from text using pyttsx3 or Coqui TTS if available."""

    script = _clean_script(script)

    if use_tts:
        try:
            from TTS.api import TTS

            tts = TTS()
            tts.tts_to_file(text=script, file_path=output_path, speaker=voice_name)
            return
        except Exception as exc:
            print(f"TTS synthesis failed ({exc}), falling back to pyttsx3")

    engine = pyttsx3.init()

    if voice_name:
        for voice in engine.getProperty("voices"):
            if voice_name.lower() in voice.name.lower():
                engine.setProperty("voice", voice.id)
                break
    else:
        for voice in engine.getProperty("voices"):
            if lang in voice.languages[0].decode("utf-8"):
                engine.setProperty("voice", voice.id)
                break

    engine.save_to_file(script, output_path)
    engine.runAndWait()
