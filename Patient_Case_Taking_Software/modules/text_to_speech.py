import io
from gtts import gTTS


# ============================================================
# LANGUAGE CODES
# ============================================================

LANGUAGE_CODES = {
    "English": "en",
    "Tamil": "ta",
    "Hindi": "hi"
}


# ============================================================
# GENERATE QUESTION AUDIO
# ============================================================

def generate_question_audio(
    text,
    language="English"
):

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

        tts.write_to_fp(
            audio_buffer
        )

        audio_buffer.seek(0)

        return audio_buffer

    except Exception as e:

        return None
