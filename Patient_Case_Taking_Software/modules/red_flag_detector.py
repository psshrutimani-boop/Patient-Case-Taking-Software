# ============================================================
# RED FLAG DETECTOR
# ============================================================

RED_FLAG_RULES = {
    "Chest Pain": [
        "chest pain",
        "chest pressure",
        "chest tightness",
        "pain in chest"
    ],

    "Severe Breathing Difficulty": [
        "severe breathing difficulty",
        "difficulty breathing",
        "shortness of breath",
        "cannot breathe",
        "can't breathe",
        "breathing problem"
    ],

    "Loss of Consciousness": [
        "unconscious",
        "loss of consciousness",
        "passed out",
        "fainted",
        "fainting"
    ],

    "Seizure": [
        "seizure",
        "convulsion",
        "fits"
    ],

    "Severe Bleeding": [
        "severe bleeding",
        "heavy bleeding",
        "uncontrolled bleeding"
    ],

    "Sudden Weakness / Paralysis": [
        "sudden weakness",
        "paralysis",
        "cannot move",
        "can't move",
        "one side weakness",
        "face drooping"
    ],

    "Severe Allergic Reaction": [
        "severe allergic reaction",
        "anaphylaxis",
        "swelling of throat",
        "throat swelling",
        "difficulty swallowing"
    ],

    "Very Severe Headache": [
        "worst headache",
        "very severe headache",
        "sudden severe headache"
    ],

    "Severe Abdominal Pain": [
        "severe abdominal pain",
        "severe stomach pain",
        "extreme stomach pain"
    ],

    "Blood in Vomit": [
        "vomiting blood",
        "blood in vomit",
        "vomit blood"
    ],

    "Blood in Stool": [
        "blood in stool",
        "bloody stool",
        "rectal bleeding"
    ],

    "Blue Lips / Skin": [
        "blue lips",
        "blue skin",
        "bluish lips",
        "bluish skin"
    ],

    "Confusion": [
        "confusion",
        "sudden confusion",
        "disoriented",
        "not aware"
    ]
}


def detect_red_flags(
    complaint="",
    symptoms=None,
    adaptive_answers=None,
    ocr_text=""
):
    """
    Detect possible red-flag indicators from:
    - chief complaint
    - selected symptoms
    - adaptive answers
    - OCR medical report text

    This function does NOT diagnose a medical condition.
    It only identifies predefined warning indicators.
    """

    symptoms = symptoms or []
    adaptive_answers = adaptive_answers or {}

    combined_text_parts = []

    if complaint:
        combined_text_parts.append(str(complaint))

    if symptoms:
        combined_text_parts.extend(
            [str(symptom) for symptom in symptoms]
        )

    if adaptive_answers:
        for question, answer in adaptive_answers.items():

            if question:
                combined_text_parts.append(str(question))

            if answer:
                combined_text_parts.append(str(answer))

    if ocr_text:
        combined_text_parts.append(str(ocr_text))

    combined_text = " ".join(
        combined_text_parts
    ).lower()

    detected_flags = []

    for flag_name, keywords in RED_FLAG_RULES.items():

        for keyword in keywords:

            if keyword.lower() in combined_text:

                detected_flags.append(flag_name)

                break

    return list(dict.fromkeys(detected_flags))


def has_red_flags(
    complaint="",
    symptoms=None,
    adaptive_answers=None,
    ocr_text=""
):
    """
    Returns True when one or more red flags are detected.
    """

    flags = detect_red_flags(
        complaint=complaint,
        symptoms=symptoms,
        adaptive_answers=adaptive_answers,
        ocr_text=ocr_text
    )

    return len(flags) > 0