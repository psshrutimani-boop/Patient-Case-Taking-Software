def generate_case_summary(case):
    """
    Generate a structured doctor-readable summary
    from the patient's case information.
    """

    complaint = case.get("complaint", "").strip()

    symptoms = case.get(
        "symptoms",
        []
    )

    duration = case.get(
        "duration",
        ""
    ).strip()

    severity = case.get(
        "severity",
        "Not available"
    )

    previous_history = case.get(
        "previous_history",
        ""
    ).strip()

    medications = case.get(
        "medications",
        ""
    ).strip()

    language = case.get(
        "language",
        "English"
    )

    adaptive_answers = case.get(
        "adaptive_answers",
        {}
    )

    ocr_text = case.get(
        "ocr_text",
        ""
    ).strip()

    red_flags = case.get(
        "red_flags",
        []
    )


    # ========================================================
    # PATIENT COMPLAINT
    # ========================================================

    summary_parts = []

    if complaint:

        summary_parts.append(
            f"The patient presents with "
            f"{complaint}."
        )

    else:

        summary_parts.append(
            "No chief complaint was recorded."
        )


    # ========================================================
    # SYMPTOMS
    # ========================================================

    if symptoms:

        symptom_text = ", ".join(symptoms)

        summary_parts.append(
            f"Reported symptoms include "
            f"{symptom_text}."
        )

    else:

        summary_parts.append(
            "No additional symptoms were recorded."
        )


    # ========================================================
    # DURATION
    # ========================================================

    if duration:

        summary_parts.append(
            f"The reported duration is {duration}."
        )


    # ========================================================
    # SEVERITY
    # ========================================================

    if severity != "Not available":

        summary_parts.append(
            f"The reported severity is "
            f"{severity}/10."
        )


    # ========================================================
    # MEDICAL HISTORY
    # ========================================================

    if previous_history:

        summary_parts.append(
            f"Relevant previous medical history: "
            f"{previous_history}."
        )

    else:

        summary_parts.append(
            "No previous medical history was reported."
        )


    # ========================================================
    # CURRENT MEDICATIONS
    # ========================================================

    if medications:

        summary_parts.append(
            f"Current medications reported: "
            f"{medications}."
        )

    else:

        summary_parts.append(
            "No current medications were reported."
        )


    # ========================================================
    # ADAPTIVE QUESTIONS
    # ========================================================

    answered_questions = []

    for question, answer in adaptive_answers.items():

        if answer and answer.strip():

            answered_questions.append(
                f"{question}: {answer.strip()}"
            )


    if answered_questions:

        summary_parts.append(
            "Additional follow-up information: "
            + "; ".join(answered_questions)
            + "."
        )


    # ========================================================
    # OCR REPORT
    # ========================================================

    if ocr_text:

        cleaned_ocr = ocr_text.replace(
            "\n",
            " "
        ).strip()

        # Keep the summary manageable
        if len(cleaned_ocr) > 500:

            cleaned_ocr = (
                cleaned_ocr[:500]
                + "..."
            )

        summary_parts.append(
            f"Previous medical report information "
            f"was extracted using OCR: {cleaned_ocr}"
        )


    # ========================================================
    # RED FLAGS
    # ========================================================

    if red_flags:

        summary_parts.append(
            "Potential warning indicators detected: "
            + ", ".join(red_flags)
            + "."
        )

    else:

        summary_parts.append(
            "No predefined red-flag indicators "
            "were detected."
        )


    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    final_summary = " ".join(
        summary_parts
    )


    # ========================================================
    # STRUCTURED SUMMARY
    # ========================================================

    structured_summary = {

        "Chief Complaint":
            complaint
            if complaint
            else "Not recorded",

        "Symptoms":
            ", ".join(symptoms)
            if symptoms
            else "None",

        "Duration":
            duration
            if duration
            else "Not recorded",

        "Severity":
            f"{severity}/10",

        "Previous Medical History":
            previous_history
            if previous_history
            else "None reported",

        "Current Medications":
            medications
            if medications
            else "None reported",

        "Follow-up Information":
            answered_questions
            if answered_questions
            else ["No additional information"],

        "OCR Report Available":
            "Yes"
            if ocr_text
            else "No",

        "Red Flags":
            red_flags
            if red_flags
            else ["None detected"],

        "Language":
            language,

        "Summary":
            final_summary
    }


    return structured_summary