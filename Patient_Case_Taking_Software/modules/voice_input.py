
import io
import speech_recognition as sr


def get_language_code(language):

    language_codes = {
        "English": "en-IN",
        "Tamil": "ta-IN",
        "Hindi": "hi-IN"
    }

    return language_codes.get(
        language,
        "en-IN"
    )


def convert_voice_to_text(
    audio_bytes,
    language="English"
):

    recognizer = sr.Recognizer()

    try:

        language_code = get_language_code(
            language
        )

        audio_file = io.BytesIO(
            audio_bytes
        )

        with sr.AudioFile(audio_file) as source:

            audio = recognizer.record(
                source
            )

        text = recognizer.recognize_google(
            audio,
            language=language_code
        )

        return text

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