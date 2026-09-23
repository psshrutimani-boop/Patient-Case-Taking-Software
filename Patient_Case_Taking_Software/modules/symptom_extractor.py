
import re


# =========================================================
# SYMPTOM KEYWORDS
# =========================================================

SYMPTOM_KEYWORDS = {

    "Fever": [
        "fever",
        "temperature",
        "காய்ச்சல்",
        "बुखार"
    ],

    "Headache": [
        "headache",
        "head pain",
        "தலைவலி",
        "सिर दर्द"
    ],

    "Cough": [
        "cough",
        "இருமல்",
        "खांसी"
    ],

    "Cold": [
        "cold",
        "runny nose",
        "சளி",
        "जुकाम"
    ],

    "Stomach Pain": [
        "stomach pain",
        "abdominal pain",
        "belly pain",
        "வயிற்று வலி",
        "पेट दर्द"
    ],

    "Chest Pain": [
        "chest pain",
        "மார்பு வலி",
        "सीने में दर्द"
    ],

    "Vomiting": [
        "vomiting",
        "vomit",
        "வாந்தி",
        "उल्टी"
    ],

    "Nausea": [
        "nausea",
        "feeling sick",
        "குமட்டல்",
        "मतली"
    ],

    "Dizziness": [
        "dizziness",
        "dizzy",
        "தலைசுற்றல்",
        "चक्कर"
    ],

    "Body Pain": [
        "body pain",
        "muscle pain",
        "உடல் வலி",
        "शरीर में दर्द"
    ],

    "Breathing Difficulty": [
        "breathing difficulty",
        "shortness of breath",
        "difficulty breathing",
        "மூச்சுத்திணறல்",
        "सांस लेने में कठिनाई"
    ],

    "Fatigue": [
        "fatigue",
        "tiredness",
        "weakness",
        "சோர்வு",
        "थकान"
    ]

}


# =========================================================
# SYMPTOM EXTRACTION FUNCTION
# =========================================================

def extract_symptoms(text):

    if not text:

        return []

    text = text.lower().strip()

    detected_symptoms = []

    for symptom, keywords in SYMPTOM_KEYWORDS.items():

        for keyword in keywords:

            if keyword.lower() in text:

                detected_symptoms.append(symptom)

                break

    return detected_symptoms


# =========================================================
# DURATION EXTRACTION
# =========================================================

def extract_duration(text):

    if not text:

        return ""

    patterns = [

        r"\b\d+\s*(day|days|week|weeks|month|months|year|years)\b",

        r"\b\d+\s*(நாள்|வாரம்|மாதம்)\b",

        r"\b\d+\s*(दिन|हफ्ते|महीने)\b"

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text.lower()
        )

        if match:

            return match.group(0)

    return ""