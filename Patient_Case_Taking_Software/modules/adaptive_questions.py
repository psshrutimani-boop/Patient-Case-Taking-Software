def get_follow_up_questions(complaint, symptoms):

    questions = []

    complaint = complaint.lower()

    # Stomach / abdominal problems
    if "stomach" in complaint or "abdominal" in complaint:

        questions = [
            "Where exactly is the stomach pain?",
            "When did the pain start?",
            "Is the pain continuous or does it come and go?",
            "Do you have fever?",
            "Do you have vomiting?",
            "Does eating make the pain better or worse?"
        ]

    # Chest problems
    elif "chest" in complaint:

        questions = [
            "Where exactly is the chest pain?",
            "When did the pain start?",
            "Is the pain continuous or intermittent?",
            "Do you have breathing difficulty?",
            "Do you have sweating or dizziness?"
        ]

    # Headache
    elif "headache" in complaint:

        questions = [
            "Where is the headache located?",
            "When did the headache start?",
            "How severe is the headache?",
            "Do you have nausea or vomiting?",
            "Do you have dizziness or blurred vision?"
        ]

    # Fever
    elif "fever" in complaint or "fever" in symptoms:

        questions = [
            "When did the fever start?",
            "Do you have chills?",
            "Do you have cough or cold?",
            "Do you have body pain?",
            "Have you measured your temperature?"
        ]

    # General case
    else:

        questions = [
            "When did the problem start?",
            "Has the problem become better or worse?",
            "How severe is the problem?",
            "Have you experienced this problem before?",
            "Are you currently taking any medication?"
        ]

    return questions