import io
import speech_recognition as sr


# ============================================================
# LANGUAGE CODES
# ============================================================

LANGUAGE_CODES = {
    "English": "en-IN",
    "Tamil": "ta-IN",
    "Hindi": "hi-IN"
}


# ============================================================
# GET LANGUAGE CODE
# ============================================================

def get_language_code(language="English"):

    return LANGUAGE_CODES.get(
        language,
        "en-IN"
    )


# ============================================================
# VOICE TO TEXT
# ============================================================

def convert_voice_to_text(
    audio_bytes,
    language="English"
):

    if not audio_bytes:
        return ""

    try:

        # Streamlit AudioInput / UploadedFile support
        if hasattr(audio_bytes, "getvalue"):
            audio_bytes = audio_bytes.getvalue()

        recognizer = sr.Recognizer()

        language_code = get_language_code(language)

        audio_file = io.BytesIO(audio_bytes)

        with sr.AudioFile(audio_file) as source:

            # Record complete audio
            audio = recognizer.record(source)

        # Google Speech Recognition
        text = recognizer.recognize_google(
            audio,
            language=language_code
        )

        return text.strip()

    except sr.UnknownValueError:

        return (
            "Sorry, I could not understand your voice. "
            "Please speak clearly and try again."
        )

    except sr.RequestError:

        return (
            "Voice recognition service is unavailable. "
            "Please check your internet connection."
        )

    except Exception as e:

        return (
            f"Voice processing error: {str(e)}"
        )
