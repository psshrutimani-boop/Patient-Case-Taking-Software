import streamlit as st
from datetime import datetime
import re


# ============================================================
# MODULE IMPORTS
# ============================================================

from modules.adaptive_questions import get_follow_up_questions

from modules.voice_input import convert_voice_to_text

from modules.text_to_speech import generate_question_audio

from modules.symptom_extractor import (
    extract_symptoms,
    extract_duration
)

from modules.ocr_processor import extract_text_from_image

from modules.red_flag_detector import detect_red_flags

from modules.ai_case_summary import generate_case_summary

from modules.database import (
    initialize_database,
    save_patient,
    save_case,
    get_patient,
    get_patient_cases,
    get_all_patients,
    get_all_cases
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Patient Case Taking Software",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# DARK HOSPITAL THEME
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #080b10;
        color: #f5f5f5;
    }

    section[data-testid="stSidebar"] {
        background-color: #0d1117;
        border-right: 1px solid #222831;
    }

    .main-title {
        font-size: 38px;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 5px;
    }

    .sub-title {
        font-size: 17px;
        color: #9ca3af;
        margin-bottom: 25px;
    }

    .hospital-card {
        background: #111827;
        padding: 25px;
        border-radius: 16px;
        border: 1px solid #263241;
        margin-bottom: 20px;
    }

    .question-card {
        background: #111827;
        padding: 25px;
        border-radius: 18px;
        border: 1px solid #374151;
        margin-top: 15px;
        margin-bottom: 20px;
    }

    .question-number {
        color: #60a5fa;
        font-size: 14px;
        font-weight: 600;
    }

    .question-text {
        color: #ffffff;
        font-size: 24px;
        font-weight: 600;
        margin-top: 8px;
    }

    .success-card {
        background: #0f2b20;
        border: 1px solid #1f6b4a;
        padding: 20px;
        border-radius: 15px;
    }

    .danger-card {
        background: #2b1111;
        border: 1px solid #7f1d1d;
        padding: 20px;
        border-radius: 15px;
    }

    .metric-card {
        background: #111827;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #263241;
        text-align: center;
    }

    .footer {
        text-align: center;
        color: #6b7280;
        padding: 30px;
        font-size: 13px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

if "database_initialized" not in st.session_state:

    try:

        st.session_state.database_initialized = (
            initialize_database()
        )

    except Exception as e:

        st.session_state.database_initialized = False

        st.error(
            f"SQLite database initialization error: {e}"
        )


# ============================================================
# SESSION STATE
# ============================================================

DEFAULT_SESSION_VALUES = {

    "logged_in": False,

    "role": None,

    "patient": None,

    "case": None,

    "case_history": [],

    "voice_complaint": "",

    "selected_language": "English",

    "selected_patient": None,

    "selected_patient_cases": [],

    # Voice assistant
    "voice_assistant_started": False,

    "voice_assistant_questions": [],

    "voice_assistant_answers": {},

    "voice_assistant_index": 0,

    "voice_assistant_completed": False,

    "voice_assistant_dynamic_questions": [],

    "voice_assistant_current_audio": None,

    # OCR
    "extracted_report_text": "",

    # Current case
    "current_symptoms": [],

    "current_complaint": "",

    "current_duration": "",

    "current_severity": 5,

    "current_history": "",

    "current_medications": "",

    "current_adaptive_answers": {}

}


for key, value in DEFAULT_SESSION_VALUES.items():

    if key not in st.session_state:

        st.session_state[key] = value


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def reset_voice_assistant():

    st.session_state.voice_assistant_started = False

    st.session_state.voice_assistant_questions = []

    st.session_state.voice_assistant_answers = {}

    st.session_state.voice_assistant_index = 0

    st.session_state.voice_assistant_completed = False

    st.session_state.voice_assistant_dynamic_questions = []

    st.session_state.voice_assistant_current_audio = None


def is_error_voice_result(text):

    if not text:
        return True

    error_messages = [

        "Sorry, I could not understand",

        "Voice recognition service is unavailable",

        "Voice processing error"

    ]

    for message in error_messages:

        if text.startswith(message):

            return True

    return False


def get_voice_answer(question):

    return st.session_state.voice_assistant_answers.get(
        question,
        ""
    )


def clean_number(text, default=0):

    try:

        numbers = re.findall(
            r"\d+\.?\d*",
            str(text)
        )

        if numbers:

            return float(numbers[0])

    except Exception:
        pass

    return default


def convert_severity(text):

    value = clean_number(text, 5)

    value = int(round(value))

    if value < 1:
        value = 1

    if value > 10:
        value = 10

    return value


# ============================================================
# LOGIN PAGE
# ============================================================

if not st.session_state.logged_in:

    st.markdown(
        '<div class="main-title">🏥 Patient Case Taking Software</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sub-title">'
        'Smart multilingual patient case-taking and doctor support system'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="hospital-card">',
        unsafe_allow_html=True
    )

    st.subheader("🔐 Secure Login")

    role = st.radio(
        "Select Role",
        ["Patient", "Doctor"],
        horizontal=True
    )

    username = st.text_input(
        "Username"
    )

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button(
        "Login",
        use_container_width=True
    ):

        # ----------------------------------------------------
        # DEMO LOGIN
        # ----------------------------------------------------

        if role == "Doctor":

            if username and password:

                st.session_state.logged_in = True

                st.session_state.role = "Doctor"

                st.success(
                    "Doctor login successful!"
                )

                st.rerun()

            else:

                st.warning(
                    "Please enter username and password."
                )

        else:

            if username and password:

                st.session_state.logged_in = True

                st.session_state.role = "Patient"

                st.success(
                    "Patient login successful!"
                )

                st.rerun()

            else:

                st.warning(
                    "Please enter username and password."
                )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="footer">
        Patient Case Taking Software • Secure Healthcare Assistant
        </div>
        """,
        unsafe_allow_html=True
    )

    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🏥 Patient Case System")

st.sidebar.write(
    f"Logged in as: **{st.session_state.role}**"
)

st.sidebar.markdown("---")


# ============================================================
# PATIENT SIDEBAR
# ============================================================

if st.session_state.role == "Patient":

    menu = st.sidebar.radio(
        "Navigation",
        [
            "Patient Registration",
            "Case Taking",
            "Health Timeline"
        ]
    )


# ============================================================
# DOCTOR SIDEBAR
# ============================================================

else:

    menu = st.sidebar.radio(
        "Navigation",
        [
            "Doctor Dashboard",
            "Patient Records"
        ]
    )


# ============================================================
# LOGOUT
# ============================================================

if st.sidebar.button(
    "🚪 Logout",
    use_container_width=True
):

    st.session_state.logged_in = False

    st.session_state.role = None

    st.session_state.patient = None

    reset_voice_assistant()

    st.rerun()


# ============================================================
# PATIENT REGISTRATION
# ============================================================

if (
    st.session_state.role == "Patient"
    and menu == "Patient Registration"
):

    st.markdown(
        '<div class="main-title">👤 Patient Registration</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Enter your basic information before starting the case."
    )

    with st.form("patient_registration_form"):

        col1, col2 = st.columns(2)

        with col1:

            full_name = st.text_input(
                "Full Name"
            )

            age = st.number_input(
                "Age",
                min_value=1,
                max_value=120,
                value=20
            )

            gender = st.selectbox(
                "Gender",
                [
                    "Male",
                    "Female",
                    "Other"
                ]
            )

            phone = st.text_input(
                "Phone Number"
            )

        with col2:

            email = st.text_input(
                "Email"
            )

            preferred_language = st.selectbox(
                "Preferred Language",
                [
                    "English",
                    "Tamil",
                    "Hindi"
                ]
            )

            emergency_contact = st.text_input(
                "Emergency Contact"
            )

            blood_group = st.selectbox(
                "Blood Group",
                [
                    "Unknown",
                    "A+",
                    "A-",
                    "B+",
                    "B-",
                    "AB+",
                    "AB-",
                    "O+",
                    "O-"
                ]
            )

        submitted = st.form_submit_button(
            "💾 Register Patient",
            use_container_width=True
        )

    if submitted:

        if not full_name:

            st.warning(
                "Please enter patient name."
            )

        else:

            patient_data = {

                "name": full_name,

                "full_name": full_name,

                "age": age,

                "gender": gender,

                "phone": phone,

                "email": email,

                "preferred_language": preferred_language,

                "language": preferred_language,

                "emergency_contact": emergency_contact,

                "blood_group": blood_group,

                "created_at": datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            }

            try:

                patient_id = save_patient(
                    patient_data
                )

                patient_data["id"] = patient_id

                st.session_state.patient = patient_data

                st.session_state.selected_language = (
                    preferred_language
                )

                try:

                    st.session_state.case_history = (
                        get_patient_cases(patient_id)
                    )

                except Exception:

                    st.session_state.case_history = []

                st.success(
                    "✅ Patient registered successfully!"
                )

                st.info(
                    f"Patient ID: {patient_id}"
                )

            except Exception as e:

                st.error(
                    f"Unable to save patient: {e}"
                )


# ============================================================
# PATIENT CASE TAKING
# ============================================================

elif (
    st.session_state.role == "Patient"
    and menu == "Case Taking"
):

    st.markdown(
        '<div class="main-title">🩺 Patient Case Taking</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sub-title">'
        'Answer the questions using text or the AI voice assistant.'
        '</div>',
        unsafe_allow_html=True
    )


    # ========================================================
    # PATIENT CHECK
    # ========================================================

    if not st.session_state.patient:

        st.warning(
            "Please register as a patient first."
        )

        st.stop()


    patient = st.session_state.patient


    # ========================================================
    # LANGUAGE
    # ========================================================

    selected_language = st.selectbox(
        "🌐 Select Conversation Language",
        [
            "English",
            "Tamil",
            "Hindi"
        ],
        index=[
            "English",
            "Tamil",
            "Hindi"
        ].index(
            st.session_state.selected_language
        )
    )

    st.session_state.selected_language = selected_language


    # ========================================================
    # AI VOICE ASSISTANT
    # ========================================================

    st.markdown("---")

    st.subheader(
        "🎙️ AI Voice Case Assistant"
    )

    st.write(
        "The AI assistant asks one question at a time. "
        "Listen to the question, record your answer, "
        "and then continue to the next question."
    )


    # ========================================================
    # START VOICE ASSISTANT
    # ========================================================

    if not st.session_state.voice_assistant_started:

        if st.button(
            "🎙️ Start AI Voice Assistant",
            use_container_width=True
        ):

            reset_voice_assistant()

            st.session_state.voice_assistant_started = True

            st.session_state.voice_assistant_completed = False

            # Initial questions
            initial_questions = [

                "What is your main health problem or complaint?",

                "How long have you been experiencing this problem?",

                "On a scale from 1 to 10, how severe is the problem?",

                "Do you have any previous medical history?",

                "Are you currently taking any medicines?"
            ]

            st.session_state.voice_assistant_questions = (
                initial_questions
            )

            st.session_state.voice_assistant_index = 0

            st.rerun()


    # ========================================================
    # ACTIVE VOICE ASSISTANT
    # ========================================================

    if st.session_state.voice_assistant_started:

        questions = (
            st.session_state.voice_assistant_questions
        )

        current_index = (
            st.session_state.voice_assistant_index
        )


        # ====================================================
        # FINISHED
        # ====================================================

        if current_index >= len(questions):

            st.session_state.voice_assistant_completed = True

            st.session_state.voice_assistant_started = False

            st.success(
                "🎉 Voice case-taking completed successfully!"
            )

            st.balloons()


        else:

            current_question = questions[current_index]


            # =================================================
            # PROGRESS
            # =================================================

            progress = (
                (current_index + 1)
                / len(questions)
            )

            st.progress(
                progress
            )

            st.caption(
                f"Question {current_index + 1} "
                f"of {len(questions)}"
            )


            # =================================================
            # QUESTION CARD
            # =================================================

            st.markdown(
                f"""
                <div class="question-card">

                    <div class="question-number">
                    QUESTION {current_index + 1}
                    </div>

                    <div class="question-text">
                    🤖 {current_question}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )


            # =================================================
            # TEXT TO SPEECH
            # =================================================

            with st.spinner(
                "Preparing question audio..."
            ):

                question_audio = (
                    generate_question_audio(
                        current_question,
                        selected_language
                    )
                )


            if question_audio:

                st.audio(
                    question_audio,
                    format="audio/mp3"
                )

                st.caption(
                    "🔊 Listen to the AI question."
                )

            else:

                st.warning(
                    "Question audio could not be generated. "
                    "You can still read the question and answer."
                )


            # =================================================
            # MICROPHONE
            # =================================================

            audio_answer = st.audio_input(
                "🎤 Record your answer",
                key=f"voice_answer_{current_index}"
            )


            # =================================================
            # SUBMIT
            # =================================================

            if st.button(
                "✅ Submit Answer & Continue",
                key=f"submit_answer_{current_index}",
                use_container_width=True
            ):

                if audio_answer is None:

                    st.warning(
                        "🎤 Please record your answer first."
                    )

                else:

                    with st.spinner(
                        "Converting your answer to text..."
                    ):

                        answer_text = (
                            convert_voice_to_text(
                                audio_answer,
                                language=selected_language
                            )
                        )


                    if is_error_voice_result(
                        answer_text
                    ):

                        st.error(
                            "❌ Your voice could not be "
                            "understood. Please record again."
                        )

                        if answer_text:

                            st.caption(
                                answer_text
                            )

                    else:

                        st.session_state.voice_assistant_answers[
                            current_question
                        ] = answer_text


                        st.success(
                            "Answer recorded successfully."
                        )

                        st.info(
                            f"📝 Your answer: {answer_text}"
                        )


                        # =====================================
                        # ADAPTIVE QUESTION GENERATION
                        # =====================================

                        if current_index == 0:

                            try:

                                detected_symptoms = (
                                    extract_symptoms(
                                        answer_text
                                    )
                                )

                                if isinstance(
                                    detected_symptoms,
                                    str
                                ):

                                    detected_symptoms = [
                                        detected_symptoms
                                    ]

                                st.session_state.current_symptoms = (
                                    detected_symptoms
                                )

                            except Exception:

                                st.session_state.current_symptoms = []


                            try:

                                dynamic_questions = (
                                    get_follow_up_questions(
                                        answer_text,
                                        st.session_state.current_symptoms
                                    )
                                )

                                if dynamic_questions:

                                    for q in dynamic_questions:

                                        if (
                                            q not in
                                            st.session_state.voice_assistant_questions
                                        ):

                                            st.session_state.voice_assistant_questions.insert(
                                                current_index + 1,
                                                q
                                            )

                            except Exception:

                                pass


                        # =====================================
                        # MOVE TO NEXT QUESTION
                        # =====================================

                        st.session_state.voice_assistant_index += 1

                        st.rerun()


    # ========================================================
    # VOICE ANSWERS COMPLETED
    # ========================================================

    if st.session_state.voice_assistant_completed:

        answers = (
            st.session_state.voice_assistant_answers
        )

        if answers:

            st.markdown("---")

            st.subheader(
                "📋 Voice Interview Answers"
            )

            for number, (question, answer) in enumerate(
                answers.items(),
                start=1
            ):

                st.markdown(
                    f"**{number}. {question}**"
                )

                st.info(
                    answer
                )


    # ========================================================
    # NORMAL MANUAL CASE FORM
    # ========================================================

    st.markdown("---")

    st.subheader(
        "📝 Manual Case Details"
    )

    voice_answers = (
        st.session_state.voice_assistant_answers
    )


    # ========================================================
    # GET VOICE VALUES
    # ========================================================

    voice_questions = list(
        voice_answers.keys()
    )


    voice_complaint = ""

    voice_duration = ""

    voice_severity = 5

    voice_history = ""

    voice_medications = ""


    if len(voice_questions) >= 1:

        voice_complaint = voice_answers.get(
            voice_questions[0],
            ""
        )


    if len(voice_questions) >= 2:

        voice_duration = voice_answers.get(
            voice_questions[1],
            ""
        )


    if len(voice_questions) >= 3:

        voice_severity = convert_severity(
            voice_answers.get(
                voice_questions[2],
                "5"
            )
        )


    if len(voice_questions) >= 4:

        voice_history = voice_answers.get(
            voice_questions[3],
            ""
        )


    if len(voice_questions) >= 5:

        voice_medications = voice_answers.get(
            voice_questions[4],
            ""
        )


    # ========================================================
    # COMPLAINT
    # ========================================================

    complaint = st.text_area(
        "Chief Complaint",
        value=voice_complaint,
        height=100
    )


    # ========================================================
    # MANUAL VOICE COMPLAINT
    # ========================================================

    st.subheader(
        "🎤 Quick Voice Complaint"
    )

    quick_voice = st.audio_input(
        "Record your complaint",
        key="quick_voice_complaint"
    )

    if quick_voice:

        if st.button(
            "Convert Complaint to Text",
            key="convert_quick_voice"
        ):

            with st.spinner(
                "Converting voice..."
            ):

                converted = convert_voice_to_text(
                    quick_voice,
                    language=selected_language
                )

            if not is_error_voice_result(
                converted
            ):

                st.session_state.voice_complaint = (
                    converted
                )

                st.success(
                    converted
                )

            else:

                st.error(
                    converted
                )


    if st.session_state.voice_complaint:

        complaint = st.session_state.voice_complaint

        st.info(
            f"Voice complaint: {complaint}"
        )


    # ========================================================
    # SYMPTOM EXTRACTION
    # ========================================================

    st.subheader(
        "🔍 Symptoms"
    )

    detected_symptoms = []

    if complaint:

        try:

            detected_symptoms = extract_symptoms(
                complaint
            )

            if isinstance(
                detected_symptoms,
                str
            ):

                detected_symptoms = [
                    detected_symptoms
                ]

        except Exception:

            detected_symptoms = []


    if not isinstance(
        detected_symptoms,
        list
    ):

        detected_symptoms = []


    symptom_options = [

        "Fever",
        "Headache",
        "Cough",
        "Cold",
        "Stomach Pain",
        "Chest Pain",
        "Vomiting",
        "Nausea",
        "Dizziness",
        "Body Pain",
        "Breathing Difficulty",
        "Fatigue"

    ]


    selected_symptoms = st.multiselect(
        "Select symptoms",
        symptom_options,
        default=[
            s for s in detected_symptoms
            if s in symptom_options
        ]
    )


    # ========================================================
    # DURATION
    # ========================================================

    duration_default = voice_duration

    if not duration_default and complaint:

        try:

            duration_default = extract_duration(
                complaint
            )

        except Exception:

            duration_default = ""


    duration = st.text_input(
        "Duration",
        value=str(duration_default)
    )


    # ========================================================
    # SEVERITY
    # ========================================================

    severity = st.slider(
        "Severity",
        min_value=1,
        max_value=10,
        value=voice_severity
    )


    # ========================================================
    # MEDICAL HISTORY
    # ========================================================

    previous_history = st.text_area(
        "Previous Medical History",
        value=voice_history,
        height=100
    )


    # ========================================================
    # MEDICATIONS
    # ========================================================

    medications = st.text_area(
        "Current Medications",
        value=voice_medications,
        height=100
    )


    # ========================================================
    # ADAPTIVE FOLLOW-UP QUESTIONS
    # ========================================================

    st.subheader(
        "🤖 Adaptive Follow-up Questions"
    )

    adaptive_answers = {}


    try:

        adaptive_questions = (
            get_follow_up_questions(
                complaint,
                selected_symptoms
            )
        )

    except Exception:

        adaptive_questions = []


    if adaptive_questions:

        for i, question in enumerate(
            adaptive_questions
        ):

            adaptive_answers[question] = st.text_input(
                question,
                key=f"adaptive_manual_{i}"
            )

    else:

        st.info(
            "No additional follow-up questions required."
        )


    # ========================================================
    # MEDICAL REPORT OCR
    # ========================================================

    st.subheader(
        "📄 Medical Report OCR"
    )

    uploaded_report = st.file_uploader(
        "Upload medical report image",
        type=[
            "png",
            "jpg",
            "jpeg"
        ]
    )


    extracted_report_text = (
        st.session_state.extracted_report_text
    )


    if uploaded_report:

        try:

            extracted_report_text = (
                extract_text_from_image(
                    uploaded_report
                )
            )

            st.session_state.extracted_report_text = (
                extracted_report_text
            )

            st.success(
                "Medical report text extracted successfully."
            )

            st.text_area(
                "Extracted Report Text",
                extracted_report_text,
                height=200
            )

        except Exception as e:

            st.error(
                f"OCR processing error: {e}"
            )


    # ========================================================
    # SAVE CASE
    # ========================================================

    st.markdown("---")

    if st.button(
        "💾 Save Complete Patient Case",
        use_container_width=True
    ):

        if not complaint:

            st.warning(
                "Please enter or record the chief complaint."
            )

        else:

            try:

                patient = st.session_state.patient

                try:

                    previous_cases = get_patient_cases(
                        patient["id"]
                    )

                    visit_number = (
                        len(previous_cases) + 1
                    )

                except Exception:

                    visit_number = 1


                # =========================================
                # RED FLAG DETECTION
                # =========================================

                red_flags = detect_red_flags(

                    complaint=complaint,

                    symptoms=selected_symptoms,

                    adaptive_answers=adaptive_answers,

                    ocr_text=extracted_report_text
                )


                # =========================================
                # CASE RECORD
                # =========================================

                now = datetime.now()


                case_record = {

                    "visit_number": visit_number,

                    "visit_date": now.strftime(
                        "%Y-%m-%d"
                    ),

                    "visit_time": now.strftime(
                        "%H:%M:%S"
                    ),

                    "visit_datetime": now.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),

                    "complaint": complaint,

                    "symptoms": selected_symptoms,

                    "duration": duration,

                    "severity": severity,

                    "previous_history": previous_history,

                    "medications": medications,

                    "adaptive_answers": adaptive_answers,

                    "language": selected_language,

                    "ocr_text": extracted_report_text,

                    "red_flags": red_flags
                }


                # =========================================
                # AI CASE SUMMARY
                # =========================================

                try:

                    ai_summary = generate_case_summary(
                        case_record
                    )

                except Exception:

                    ai_summary = (
                        f"Patient reported {complaint}. "
                        f"Symptoms: {', '.join(selected_symptoms)}. "
                        f"Duration: {duration}. "
                        f"Severity: {severity}/10."
                    )


                case_record["ai_summary"] = ai_summary

                case_record["summary"] = ai_summary


                # =========================================
                # DATABASE SAVE
                # =========================================

                save_case(
                    patient["id"],
                    case_record
                )


                # =========================================
                # SESSION UPDATE
                # =========================================

                st.session_state.case = case_record

                st.session_state.current_complaint = complaint

                st.session_state.current_symptoms = selected_symptoms

                st.session_state.current_duration = duration

                st.session_state.current_severity = severity

                st.session_state.current_history = previous_history

                st.session_state.current_medications = medications

                st.session_state.current_adaptive_answers = (
                    adaptive_answers
                )


                try:

                    st.session_state.case_history = (
                        get_patient_cases(
                            patient["id"]
                        )
                    )

                except Exception:

                    pass


                st.success(
                    "✅ Patient case saved successfully!"
                )


                # =========================================
                # DISPLAY SUMMARY
                # =========================================

                st.subheader(
                    "📋 AI Case Summary"
                )

                st.info(
                    str(ai_summary)
                )


                # =========================================
                # RED FLAGS
                # =========================================

                st.subheader(
                    "🚨 Red Flag Analysis"
                )

                if red_flags:

                    st.error(
                        f"Potential red flags detected: "
                        f"{red_flags}"
                    )

                else:

                    st.success(
                        "No major red flags detected by the system."
                    )


                # =========================================
                # OCR
                # =========================================

                if extracted_report_text:

                    st.subheader(
                        "📄 Medical Report Information"
                    )

                    st.text_area(
                        "OCR Result",
                        extracted_report_text,
                        height=200
                    )


            except Exception as e:

                st.error(
                    f"Error while saving case: {e}"
                )


# ============================================================
# PATIENT HEALTH TIMELINE
# ============================================================

elif (
    st.session_state.role == "Patient"
    and menu == "Health Timeline"
):

    st.markdown(
        '<div class="main-title">📅 Health Timeline</div>',
        unsafe_allow_html=True
    )


    if not st.session_state.patient:

        st.warning(
            "Please register as a patient first."
        )

        st.stop()


    patient = st.session_state.patient


    try:

        cases = get_patient_cases(
            patient["id"]
        )

    except Exception as e:

        cases = []

        st.error(
            f"Unable to load cases: {e}"
        )


    if not cases:

        st.info(
            "No previous patient visits found."
        )

    else:

        st.success(
            f"{len(cases)} visit(s) found."
        )


        for index, case in enumerate(
            reversed(cases),
            start=1
        ):

            visit_date = case.get(
                "visit_date",
                "Unknown"
            )

            complaint = case.get(
                "complaint",
                "Not available"
            )

            with st.expander(
                f"Visit {index} • {visit_date} • {complaint}"
            ):

                st.write(
                    f"**Complaint:** {complaint}"
                )

                st.write(
                    f"**Symptoms:** "
                    f"{case.get('symptoms', '')}"
                )

                st.write(
                    f"**Duration:** "
                    f"{case.get('duration', '')}"
                )

                st.write(
                    f"**Severity:** "
                    f"{case.get('severity', '')}/10"
                )

                st.write(
                    f"**Previous History:** "
                    f"{case.get('previous_history', '')}"
                )

                st.write(
                    f"**Medications:** "
                    f"{case.get('medications', '')}"
                )

                if case.get("ai_summary"):

                    st.subheader(
                        "AI Summary"
                    )

                    st.info(
                        str(
                            case.get(
                                "ai_summary"
                            )
                        )
                    )

                if case.get("red_flags"):

                    st.subheader(
                        "Red Flags"
                    )

                    st.warning(
                        str(
                            case.get(
                                "red_flags"
                            )
                        )
                    )

                if case.get("ocr_text"):

                    st.subheader(
                        "Medical Report"

                    )

                    st.text_area(
                        "OCR Text",
                        str(
                            case.get(
                                "ocr_text"
                            )
                        ),
                        height=150,
                        key=f"timeline_ocr_{index}"
                    )


# ============================================================
# DOCTOR DASHBOARD
# ============================================================

elif (
    st.session_state.role == "Doctor"
    and menu == "Doctor Dashboard"
):

    st.markdown(
        '<div class="main-title">👨‍⚕️ Doctor Dashboard</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sub-title">'
        'Patient overview, visit history and case analysis'
        '</div>',
        unsafe_allow_html=True
    )


    # ========================================================
    # LOAD DATA
    # ========================================================

    try:

        patients = get_all_patients()

    except Exception:

        patients = []


    try:

        cases = get_all_cases()

    except Exception:

        cases = []


    # ========================================================
    # METRICS
    # ========================================================

    alert_count = 0


    for case in cases:

        red_flags = case.get(
            "red_flags",
            ""
        )

        if red_flags:

            alert_count += 1


    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "Total Patients",
            len(patients)
        )


    with col2:

        st.metric(
            "Total Visits",
            len(cases)
        )


    with col3:

        st.metric(
            "Alert Cases",
            alert_count
        )


    st.markdown("---")


    # ========================================================
    # RECENT CASES
    # ========================================================

    st.subheader(
        "🕐 Recent Cases"
    )


    if cases:

        recent_cases = cases[-10:]

        for index, case in enumerate(
            reversed(recent_cases),
            start=1
        ):

            complaint = case.get(
                "complaint",
                "Unknown complaint"
            )

            visit_date = case.get(
                "visit_date",
                ""
            )

            with st.expander(
                f"{index}. {complaint} • {visit_date}"
            ):

                st.write(
                    f"**Patient ID:** "
                    f"{case.get('patient_id', 'N/A')}"
                )

                st.write(
                    f"**Complaint:** "
                    f"{complaint}"
                )

                st.write(
                    f"**Symptoms:** "
                    f"{case.get('symptoms', '')}"
                )

                st.write(
                    f"**Severity:** "
                    f"{case.get('severity', '')}/10"
                )

                if case.get("ai_summary"):

                    st.subheader(
                        "AI Summary"
                    )

                    st.info(
                        str(
                            case.get(
                                "ai_summary"
                            )
                        )
                    )

                if case.get("red_flags"):

                    st.error(
                        f"Red Flags: "
                        f"{case.get('red_flags')}"
                    )

    else:

        st.info(
            "No patient cases available."
        )


# ============================================================
# DOCTOR PATIENT RECORDS
# ============================================================

elif (
    st.session_state.role == "Doctor"
    and menu == "Patient Records"
):

    st.markdown(
        '<div class="main-title">👥 Patient Records</div>',
        unsafe_allow_html=True
    )


    try:

        patients = get_all_patients()

    except Exception as e:

        st.error(
            f"Unable to load patients: {e}"
        )

        patients = []


    # ========================================================
    # SEARCH
    # ========================================================

    search_text = st.text_input(
        "🔎 Search patient by name or phone"
    )


    filtered_patients = []


    for patient in patients:

        name = str(
            patient.get(
                "name",
                patient.get(
                    "full_name",
                    ""
                )
            )
        ).lower()

        phone = str(
            patient.get(
                "phone",
                ""
            )
        ).lower()


        if (
            not search_text
            or search_text.lower() in name
            or search_text.lower() in phone
        ):

            filtered_patients.append(
                patient
            )


    # ========================================================
    # PATIENT LIST
    # ========================================================

    if not filtered_patients:

        st.info(
            "No patients found."
        )

    else:

        for patient in filtered_patients:

            patient_id = patient.get(
                "id"
            )

            name = patient.get(
                "name",
                patient.get(
                    "full_name",
                    "Unknown"
                )
            )

            with st.expander(
                f"👤 {name} • ID: {patient_id}"
            ):

                col1, col2 = st.columns(2)


                with col1:

                    st.write(
                        f"**Age:** "
                        f"{patient.get('age', '')}"
                    )

                    st.write(
                        f"**Gender:** "
                        f"{patient.get('gender', '')}"
                    )

                    st.write(
                        f"**Phone:** "
                        f"{patient.get('phone', '')}"
                    )


                with col2:

                    st.write(
                        f"**Email:** "
                        f"{patient.get('email', '')}"
                    )

                    st.write(
                        f"**Language:** "
                        f"{patient.get('preferred_language', patient.get('language', ''))}"
                    )

                    st.write(
                        f"**Blood Group:** "
                        f"{patient.get('blood_group', '')}"
                    )


                # =========================================
                # PATIENT VISITS
                # =========================================

                try:

                    patient_cases = (
                        get_patient_cases(
                            patient_id
                        )
                    )

                except Exception:

                    patient_cases = []


                st.markdown("---")

                st.subheader(
                    f"📅 Visit History ({len(patient_cases)})"
                )


                if not patient_cases:

                    st.info(
                        "No visit records."
                    )

                else:

                    for visit_index, case in enumerate(
                        reversed(patient_cases),
                        start=1
                    ):

                        visit_date = case.get(
                            "visit_date",
                            ""
                        )

                        complaint = case.get(
                            "complaint",
                            "Unknown"
                        )

                        with st.expander(
                            f"Visit {visit_index} • {visit_date} • {complaint}"
                        ):

                            st.write(
                                f"**Symptoms:** "
                                f"{case.get('symptoms', '')}"
                            )

                            st.write(
                                f"**Duration:** "
                                f"{case.get('duration', '')}"
                            )

                            st.write(
                                f"**Severity:** "
                                f"{case.get('severity', '')}/10"
                            )

                            st.write(
                                f"**Previous History:** "
                                f"{case.get('previous_history', '')}"
                            )

                            st.write(
                                f"**Medications:** "
                                f"{case.get('medications', '')}"
                            )


                            if case.get(
                                "adaptive_answers"
                            ):

                                st.subheader(
                                    "Adaptive Answers"
                                )

                                st.json(
                                    case.get(
                                        "adaptive_answers"
                                    )
                                )


                            if case.get(
                                "ai_summary"
                            ):

                                st.subheader(
                                    "AI Case Summary"
                                )

                                st.info(
                                    str(
                                        case.get(
                                            "ai_summary"
                                        )
                                    )
                                )


                            if case.get(
                                "red_flags"
                            ):

                                st.subheader(
                                    "🚨 Red Flags"
                                )

                                st.error(
                                    str(
                                        case.get(
                                            "red_flags"
                                        )
                                    )
                                )


                            if case.get(
                                "ocr_text"
                            ):

                                st.subheader(
                                    "📄 OCR Medical Report"
                                )

                                st.text_area(
                                    "Extracted Text",
                                    str(
                                        case.get(
                                            "ocr_text"
                                        )
                                    ),
                                    height=200,
                                    key=f"doctor_ocr_{patient_id}_{visit_index}"
                                )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        🏥 Patient Case Taking Software |
        Multilingual Voice Assistant |
        NLP |
        Adaptive Questioning |
        OCR |
        Red Flag Detection |
        AI Case Summary |
        Patient Timeline
    </div>
    """,
    unsafe_allow_html=True
)
