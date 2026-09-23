import io
from gtts import gTTS


LANGUAGE_CODES = {
    "English": "en",
    "Tamil": "ta",
    "Hindi": "hi"
}


def generate_question_audio(text, language="English"):

    if not text:
        return None

    try:

        language_code = LANGUAGE_CODES.get(
            language,
            "en"
        )

        tts = gTTS(
            text=text,
            lang=language_code,
            slow=False
        )

        audio_buffer = io.BytesIO()

        tts.write_to_fp(audio_buffer)

        audio_buffer.seek(0)

        return audio_buffer

    except Exception:
        return None
