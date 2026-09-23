import streamlit as st
from datetime import datetime

from modules.adaptive_questions import get_follow_up_questions
from modules.voice_input import convert_voice_to_text
from modules.symptom_extractor import extract_symptoms
from modules.ocr_processor import extract_text_from_image
from modules.red_flag_detector import detect_red_flags
from modules.ai_case_summary import generate_case_summary

# ============================================================
# STEP 13 - SQLITE DATABASE
# ============================================================

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
    page_title="Patient Case Taking System",
    page_icon="🏥",
    layout="wide"
)


# ============================================================
# DARK HOSPITAL THEME
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #0b1117;
        color: white;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    .main-title {
        text-align: center;
        color: #4da6ff;
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        color: #aab7c4;
        font-size: 17px;
        margin-bottom: 30px;
    }

    .card {
        background-color: #121c26;
        border: 1px solid #263746;
        border-radius: 18px;
        padding: 28px;
        margin-top: 20px;
        margin-bottom: 20px;
        box-shadow: 0px 8px 30px rgba(0, 0, 0, 0.4);
    }

    .section-title {
        color: #4da6ff;
        font-size: 25px;
        font-weight: 600;
        margin-bottom: 18px;
    }

    .step-title {
        color: #66b3ff;
        font-size: 21px;
        font-weight: 600;
        margin-top: 25px;
        margin-bottom: 12px;
    }

    .success-box {
        background-color: #10251b;
        border: 1px solid #1f7a46;
        border-radius: 12px;
        padding: 15px;
        color: #8ff0b2;
    }

    .warning-box {
        background-color: #2b2110;
        border: 1px solid #9a6b1e;
        border-radius: 12px;
        padding: 15px;
        color: #ffd27a;
    }

    .danger-box {
        background-color: #321416;
        border: 1px solid #b83a40;
        border-radius: 12px;
        padding: 18px;
        color: #ff9da3;
    }

    .timeline-card {
        background-color: #111d27;
        border-left: 4px solid #1677ff;
        border-radius: 12px;
        padding: 20px;
        margin-top: 15px;
        margin-bottom: 15px;
    }

    .timeline-date {
        color: #66b3ff;
        font-size: 19px;
        font-weight: 700;
    }

    .timeline-label {
        color: #aab7c4;
        font-size: 14px;
    }

    .timeline-value {
        color: white;
        font-size: 16px;
    }

    .stButton > button {
        width: 100%;
        background-color: #1677ff;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px;
        font-size: 16px;
        font-weight: 600;
    }

    .stButton > button:hover {
        background-color: #0d5fd1;
        color: white;
    }

    .footer {
        text-align: center;
        color: #71808f;
        font-size: 13px;
        margin-top: 40px;
        padding-bottom: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# STEP 13 - INITIALIZE SQLITE DATABASE
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
# SESSION STATE INITIALIZATION
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "role" not in st.session_state:
    st.session_state.role = ""

if "patient" not in st.session_state:
    st.session_state.patient = None

if "case" not in st.session_state:
    st.session_state.case = None

if "case_history" not in st.session_state:
    st.session_state.case_history = []

if "voice_complaint" not in st.session_state:
    st.session_state.voice_complaint = ""

if "selected_language" not in st.session_state:
    st.session_state.selected_language = "English"

if "selected_patient" not in st.session_state:
    st.session_state.selected_patient = None

if "selected_patient_cases" not in st.session_state:
    st.session_state.selected_patient_cases = []


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🏥 Patient Case Taking System</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'AI-Powered Adaptive Patient Case Management'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# LOGIN PAGE
# ============================================================

if not st.session_state.logged_in:

    col1, col2, col3 = st.columns([1, 1.5, 1])

    with col2:

        st.markdown(
            '<div class="card">',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-title">🔐 Secure Login</div>',
            unsafe_allow_html=True
        )

        role = st.selectbox(
            "Login As",
            [
                "Patient",
                "Doctor"
            ]
        )

        username = st.text_input(
            "Username",
            placeholder="Enter your username"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password"
        )

        if st.button("Login"):

            if username.strip() and password.strip():

                st.session_state.logged_in = True

                st.session_state.role = role

                st.rerun()

            else:

                st.warning(
                    "⚠️ Please enter username and password."
                )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )


# ============================================================
# PATIENT PORTAL
# ============================================================

elif st.session_state.role == "Patient":

    st.success(
        "✅ Patient login successful!"
    )


    # ========================================================
    # PATIENT REGISTRATION
    # ========================================================

    if st.session_state.patient is None:

        st.markdown(
            '<div class="card">',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-title">'
            '👤 Patient Registration'
            '</div>',
            unsafe_allow_html=True
        )

        st.write(
            "Please enter your basic information."
        )

        col1, col2 = st.columns(2)


        # ----------------------------------------------------
        # LEFT COLUMN
        # ----------------------------------------------------

        with col1:

            name = st.text_input(
                "Full Name",
                placeholder="Enter your full name"
            )

            age = st.number_input(
                "Age",
                min_value=1,
                max_value=120,
                value=18
            )

            gender = st.selectbox(
                "Gender",
                [
                    "Select",
                    "Male",
                    "Female",
                    "Other"
                ]
            )

            phone = st.text_input(
                "Phone Number",
                placeholder="Enter phone number"
            )


        # ----------------------------------------------------
        # RIGHT COLUMN
        # ----------------------------------------------------

        with col2:

            email = st.text_input(
                "Email",
                placeholder="Enter email address"
            )

            language = st.selectbox(
                "Preferred Language",
                [
                    "English",
                    "Tamil",
                    "Hindi"
                ]
            )

            emergency_contact = st.text_input(
                "Emergency Contact",
                placeholder="Enter emergency contact"
            )

            blood_group = st.selectbox(
                "Blood Group",
                [
                    "Select",
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


        # ----------------------------------------------------
        # REGISTER PATIENT
        # ----------------------------------------------------

        if st.button(
            "Register Patient"
        ):

            if (
                name.strip()
                and phone.strip()
                and gender != "Select"
            ):

                patient_data = {

                    "name":
                        name.strip(),

                    "age":
                        int(age),

                    "gender":
                        gender,

                    "phone":
                        phone.strip(),

                    "email":
                        email.strip(),

                    "language":
                        language,

                    "emergency_contact":
                        emergency_contact.strip(),

                    "blood_group":
                        blood_group
                }


                # ============================================
                # STEP 13 - SAVE PATIENT TO SQLITE
                # ============================================

                try:

                    patient_id = save_patient(
                        patient_data
                    )

                    patient_data["id"] = patient_id

                    st.session_state.patient = (
                        patient_data
                    )

                    st.session_state.selected_language = (
                        language
                    )


                    # Load existing patient history

                    st.session_state.case_history = (
                        get_patient_cases(
                            patient_id
                        )
                    )


                    st.success(
                        "✅ Patient registered successfully!"
                    )

                    st.info(
                        f"🆔 Patient ID: {patient_id}"
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"❌ Database error: {str(e)}"
                    )

            else:

                st.warning(
                    "⚠️ Please enter Name, Phone Number "
                    "and Gender."
                )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )


    # ========================================================
    # CASE TAKING
    # ========================================================

    else:

        patient = st.session_state.patient

        st.markdown(
            '<div class="card">',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-title">'
            '🩺 New Patient Case'
            '</div>',
            unsafe_allow_html=True
        )

        st.info(
            f"Patient ID: {patient.get('id', 'N/A')} | "
            f"Patient: {patient['name']} | "
            f"Age: {patient['age']} | "
            f"Gender: {patient['gender']}"
        )


        # ====================================================
        # STEP 1 - CHIEF COMPLAINT
        # ====================================================

        st.markdown(
            '<div class="step-title">'
            '1. Chief Complaint'
            '</div>',
            unsafe_allow_html=True
        )

        st.write(
            "You can type your complaint or record it "
            "using your microphone."
        )

        complaint_text = st.text_area(
            "Type your health problem",
            placeholder="Example: I have stomach pain...",
            key="complaint_text"
        )


        # ====================================================
        # STEP 7 - MULTILINGUAL VOICE INPUT
        # ====================================================

        st.markdown(
            '<div class="step-title">'
            '2. 🎤 Multilingual Voice Input'
            '</div>',
            unsafe_allow_html=True
        )

        st.write(
            "Select your language and record your complaint."
        )

        default_language = patient.get(
            "language",
            "English"
        )

        language_options = [
            "English",
            "Tamil",
            "Hindi"
        ]

        if default_language in language_options:

            default_index = language_options.index(
                default_language
            )

        else:

            default_index = 0

        selected_language = st.selectbox(
            "Select Voice Language",
            language_options,
            index=default_index,
            key="voice_language"
        )

        st.session_state.selected_language = (
            selected_language
        )


        # ----------------------------------------------------
        # LANGUAGE INSTRUCTION
        # ----------------------------------------------------

        if selected_language == "English":

            st.info(
                "🎤 Please speak in English."
            )

        elif selected_language == "Tamil":

            st.info(
                "🎤 தமிழில் உங்கள் உடல்நலப் பிரச்சனையைப் பேசவும்."
            )

        elif selected_language == "Hindi":

            st.info(
                "🎤 कृपया हिंदी में अपनी स्वास्थ्य समस्या बताएं।"
            )


        # ----------------------------------------------------
        # AUDIO INPUT
        # ----------------------------------------------------

        audio_value = st.audio_input(
            "Record your complaint",
            key="patient_voice"
        )

        if audio_value is not None:

            audio_bytes = audio_value.getvalue()

            with st.spinner(
                f"Converting {selected_language} voice to text..."
            ):

                try:

                    voice_text = convert_voice_to_text(
                        audio_bytes,
                        language=selected_language
                    )

                except TypeError:

                    try:

                        voice_text = convert_voice_to_text(
                            audio_bytes
                        )

                    except Exception as e:

                        voice_text = (
                            f"Voice processing error: {str(e)}"
                        )

                except Exception as e:

                    voice_text = (
                        f"Voice processing error: {str(e)}"
                    )

            if voice_text:

                invalid_messages = [
                    "Sorry",
                    "Voice processing",
                    "Voice recognition"
                ]

                is_error = any(
                    voice_text.startswith(message)
                    for message in invalid_messages
                )

                if not is_error:

                    st.session_state.voice_complaint = (
                        voice_text
                    )

                    st.success(
                        "✅ Voice converted successfully!"
                    )

                    st.write(
                        f"**Detected Language:** "
                        f"{selected_language}"
                    )

                    st.write(
                        f"**You said:** {voice_text}"
                    )

                else:

                    st.warning(
                        voice_text
                    )


        # ====================================================
        # FINAL COMPLAINT
        # ====================================================

        if st.session_state.voice_complaint:

            complaint = (
                st.session_state.voice_complaint
            )

            st.info(
                f"🎤 Using voice complaint: {complaint}"
            )

            if st.button(
                "📝 Use Typed Complaint Instead"
            ):

                st.session_state.voice_complaint = ""

                st.rerun()

        else:

            complaint = complaint_text.strip()


        # ====================================================
        # STEP 8 - NLP SYMPTOM EXTRACTION
        # ====================================================

        st.markdown(
            '<div class="step-title">'
            '3. 🤖 NLP Symptom Extraction'
            '</div>',
            unsafe_allow_html=True
        )

        detected_symptoms = []

        if complaint:

            try:

                detected_symptoms = extract_symptoms(
                    complaint
                )

                if detected_symptoms:

                    st.success(
                        "✅ Symptoms detected automatically!"
                    )

                    st.write(
                        "**NLP Detected Symptoms:**"
                    )

                    st.write(
                        ", ".join(
                            detected_symptoms
                        )
                    )

                else:

                    st.info(
                        "No symptoms detected automatically. "
                        "You can select them manually."
                    )

            except Exception as e:

                st.warning(
                    f"NLP extraction could not be completed: {e}"
                )

        else:

            st.info(
                "Enter a complaint to automatically "
                "extract symptoms."
            )


        # ====================================================
        # MANUAL SYMPTOM SELECTION
        # ====================================================

        st.markdown(
            '<div class="step-title">'
            '4. Symptoms'
            '</div>',
            unsafe_allow_html=True
        )

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

        manual_symptoms = st.multiselect(
            "Select additional symptoms",
            symptom_options,
            key="manual_symptoms"
        )


        # ====================================================
        # COMBINE SYMPTOMS
        # ====================================================

        symptoms = list(
            dict.fromkeys(
                detected_symptoms
                + manual_symptoms
            )
        )

        if symptoms:

            st.write(
                f"**Final Symptoms:** "
                f"{', '.join(symptoms)}"
            )


        # ====================================================
        # DURATION
        # ====================================================

        st.markdown(
            '<div class="step-title">'
            '5. Duration'
            '</div>',
            unsafe_allow_html=True
        )

        duration = st.text_input(
            "How long have you had this problem?",
            placeholder="Example: 3 days",
            key="duration"
        )


        # ====================================================
        # SEVERITY
        # ====================================================

        st.markdown(
            '<div class="step-title">'
            '6. Severity'
            '</div>',
            unsafe_allow_html=True
        )

        severity = st.slider(
            "Rate your problem severity",
            min_value=1,
            max_value=10,
            value=5,
            key="severity"
        )

        st.write(
            f"Severity Level: **{severity}/10**"
        )


        # ====================================================
        # PREVIOUS MEDICAL HISTORY
        # ====================================================

        st.markdown(
            '<div class="step-title">'
            '7. Previous Medical History'
            '</div>',
            unsafe_allow_html=True
        )

        previous_history = st.text_area(
            "Mention previous diseases, surgeries or conditions",
            placeholder=(
                "Example: Diabetes, asthma, previous surgery..."
            ),
            key="previous_history"
        )


        # ====================================================
        # CURRENT MEDICATIONS
        # ====================================================

        st.markdown(
            '<div class="step-title">'
            '8. Current Medications'
            '</div>',
            unsafe_allow_html=True
        )

        medications = st.text_area(
            "Enter your current medications",
            placeholder=(
                "Example: Paracetamol, insulin..."
            ),
            key="medications"
        )


        # ====================================================
        # STEP 5 - ADAPTIVE AI QUESTIONS
        # ====================================================

        st.markdown(
            '<div class="step-title">'
            '9. 🤖 Adaptive AI Questions'
            '</div>',
            unsafe_allow_html=True
        )

        answers = {}

        if complaint:

            try:

                adaptive_questions = (
                    get_follow_up_questions(
                        complaint,
                        symptoms
                    )
                )

            except Exception as e:

                adaptive_questions = []

                st.warning(
                    f"Adaptive question generation error: {e}"
                )


            if adaptive_questions:

                st.write(
                    "Based on the patient's complaint and "
                    "symptoms, the system generated "
                    "the following follow-up questions:"
                )

                for i, question in enumerate(
                    adaptive_questions
                ):

                    answers[question] = st.text_input(
                        question,
                        key=f"adaptive_{i}"
                    )

            else:

                st.info(
                    "No additional adaptive questions "
                    "were generated."
                )

        else:

            st.info(
                "Enter the chief complaint to generate "
                "adaptive questions."
            )


        # ====================================================
        # STEP 9 - MEDICAL REPORT UPLOAD + OCR
        # ====================================================

        st.markdown(
            '<div class="step-title">'
            '10. 📄 Medical Report Upload + OCR'
            '</div>',
            unsafe_allow_html=True
        )

        st.write(
            "Upload a previous medical report image. "
            "The system will extract readable text from it."
        )

        uploaded_report = st.file_uploader(
            "Upload Medical Report",
            type=[
                "png",
                "jpg",
                "jpeg"
            ],
            key="medical_report"
        )

        extracted_report_text = ""

        if uploaded_report is not None:

            st.success(
                "✅ Medical report uploaded successfully!"
            )

            st.image(
                uploaded_report,
                caption="Uploaded Medical Report",
                use_container_width=True
            )

            report_bytes = (
                uploaded_report.getvalue()
            )

            with st.spinner(
                "Extracting text from medical report..."
            ):

                try:

                    extracted_report_text = (
                        extract_text_from_image(
                            report_bytes
                        )
                    )

                except Exception as e:

                    extracted_report_text = (
                        f"OCR processing error: {str(e)}"
                    )


            if extracted_report_text:

                if extracted_report_text.startswith(
                    "OCR processing error"
                ):

                    st.error(
                        extracted_report_text
                    )

                else:

                    st.success(
                        "✅ Text extracted successfully!"
                    )

                    st.text_area(
                        "Extracted Medical Report Text",
                        value=extracted_report_text,
                        height=250,
                        key="ocr_result"
                    )

            else:

                st.warning(
                    "No readable text was found in "
                    "the uploaded report."
                )


        # ====================================================
        # STEP 10 - RED-FLAG ALERT SYSTEM
        # ====================================================

        st.markdown(
            '<div class="step-title">'
            '11. 🚨 Red-Flag Alert System'
            '</div>',
            unsafe_allow_html=True
        )

        st.write(
            "The system checks the patient's complaint, "
            "symptoms, adaptive answers and uploaded "
            "report text for predefined warning indicators."
        )

        try:

            red_flags = detect_red_flags(

                complaint=complaint,

                symptoms=symptoms,

                adaptive_answers=answers,

                ocr_text=extracted_report_text
            )

        except Exception as e:

            red_flags = []

            st.warning(
                f"Red-flag detection error: {e}"
            )


        if red_flags:

            st.markdown(
                """
                <div class="danger-box">
                <h3>🚨 Potential Red-Flag Indicators Detected</h3>
                <p>
                Please review these findings carefully
                and seek appropriate clinical assessment.
                </p>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.write(
                "### Detected Warning Indicators"
            )

            for flag in red_flags:

                st.error(
                    f"⚠️ {flag}"
                )

            st.info(
                "⚠️ This is a decision-support alert only. "
                "It does not diagnose a medical condition."
            )

        else:

            st.success(
                "✅ No predefined red-flag indicators detected."
            )

            st.caption(
                "Absence of an alert does not rule out "
                "a medical emergency."
            )


        # ====================================================
        # SAVE PATIENT CASE
        # ====================================================

        st.markdown("---")

        st.markdown(
            '<div class="section-title">'
            '💾 Save Patient Case'
            '</div>',
            unsafe_allow_html=True
        )

        if st.button(
            "💾 Save Complete Patient Case"
        ):

            if not complaint:

                st.warning(
                    "⚠️ Please enter the chief complaint."
                )

            elif not duration.strip():

                st.warning(
                    "⚠️ Please enter the duration."
                )

            else:

                # =============================================
                # CREATE VISIT DATE AND TIME
                # =============================================

                visit_datetime = datetime.now()

                visit_date = visit_datetime.strftime(
                    "%d-%m-%Y"
                )

                visit_time = visit_datetime.strftime(
                    "%I:%M %p"
                )


                # =============================================
                # GET EXISTING CASES FROM DATABASE
                # =============================================

                try:

                    existing_cases = (
                        get_patient_cases(
                            patient["id"]
                        )
                    )

                    visit_number = (
                        len(existing_cases) + 1
                    )

                except Exception:

                    visit_number = (
                        len(
                            st.session_state.case_history
                        ) + 1
                    )


                # =============================================
                # CREATE COMPLETE CASE RECORD
                # =============================================

                case_record = {

                    "visit_number":
                        visit_number,

                    "visit_date":
                        visit_date,

                    "visit_time":
                        visit_time,

                    "visit_datetime":
                        visit_datetime.strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),

                    "complaint":
                        complaint,

                    "symptoms":
                        symptoms,

                    "duration":
                        duration.strip(),

                    "severity":
                        severity,

                    "previous_history":
                        previous_history.strip(),

                    "medications":
                        medications.strip(),

                    "adaptive_answers":
                        answers,

                    "language":
                        selected_language,

                    "ocr_text":
                        extracted_report_text,

                    "red_flags":
                        red_flags
                }


                # =============================================
                # STEP 12 - AI CASE SUMMARY
                # =============================================

                try:

                    ai_summary_data = (
                        generate_case_summary(
                            case_record
                        )
                    )

                except Exception as e:

                    ai_summary_data = {

                        "Chief Complaint":
                            complaint,

                        "Symptoms":
                            ", ".join(symptoms)
                            if symptoms
                            else "None",

                        "Duration":
                            duration.strip(),

                        "Severity":
                            f"{severity}/10",

                        "Previous Medical History":
                            previous_history.strip()
                            if previous_history.strip()
                            else "None",

                        "Current Medications":
                            medications.strip()
                            if medications.strip()
                            else "None",

                        "Follow-up Information":
                            [
                                "Summary generation error"
                            ],

                        "OCR Report Available":
                            "Yes"
                            if extracted_report_text
                            else "No",

                        "Red Flags":
                            red_flags
                            if red_flags
                            else [
                                "None detected"
                            ],

                        "Language":
                            selected_language,

                        "Summary":
                            (
                                "AI summary generation error: "
                                f"{str(e)}"
                            )
                    }


                # =============================================
                # STORE AI SUMMARY
                # =============================================

                case_record[
                    "ai_summary"
                ] = ai_summary_data


                # =============================================
                # STEP 13 - SAVE CASE TO SQLITE
                # =============================================

                try:

                    case_id = save_case(
                        patient["id"],
                        case_record
                    )

                    case_record["id"] = case_id


                    # Reload history from SQLite

                    st.session_state.case_history = (
                        get_patient_cases(
                            patient["id"]
                        )
                    )

                    st.session_state.case = (
                        case_record
                    )


                    st.success(
                        "✅ Complete patient case saved successfully!"
                    )

                    st.success(
                        f"🕒 Visit {visit_number} "
                        "added to Patient Health Timeline."
                    )

                    st.info(
                        f"💾 SQLite Database Case ID: {case_id}"
                    )

                except Exception as e:

                    st.error(
                        f"❌ SQLite database save error: {str(e)}"
                    )

                    st.stop()


                # =============================================
                # CASE SUMMARY
                # =============================================

                st.markdown(
                    "### 📋 Saved Case Summary"
                )

                st.write(
                    f"**Visit:** "
                    f"{case_record['visit_number']}"
                )

                st.write(
                    f"**Date:** "
                    f"{visit_date}"
                )

                st.write(
                    f"**Time:** "
                    f"{visit_time}"
                )

                st.write(
                    f"**Chief Complaint:** "
                    f"{complaint}"
                )

                st.write(
                    f"**Language:** "
                    f"{selected_language}"
                )

                st.write(
                    f"**Symptoms:** "
                    f"{', '.join(symptoms) if symptoms else 'None'}"
                )

                st.write(
                    f"**Duration:** "
                    f"{duration}"
                )

                st.write(
                    f"**Severity:** "
                    f"{severity}/10"
                )

                st.write(
                    f"**Previous History:** "
                    f"{previous_history if previous_history else 'None'}"
                )

                st.write(
                    f"**Medications:** "
                    f"{medications if medications else 'None'}"
                )


                # =============================================
                # ADAPTIVE ANSWERS
                # =============================================

                st.markdown(
                    "### 🤖 Follow-up Answers"
                )

                if answers:

                    for question, answer in answers.items():

                        st.write(
                            f"**{question}**"
                        )

                        st.write(
                            answer
                            if answer
                            else "Not answered"
                        )

                else:

                    st.write(
                        "No follow-up questions."
                    )


                # =============================================
                # OCR RESULT
                # =============================================

                if extracted_report_text:

                    st.markdown(
                        "### 📄 OCR Medical Report"
                    )

                    st.text_area(
                        "Extracted Report",
                        value=extracted_report_text,
                        height=200,
                        key="saved_ocr_display"
                    )


                # =============================================
                # RED FLAGS
                # =============================================

                st.markdown(
                    "### 🚨 Red-Flag Status"
                )

                if red_flags:

                    for flag in red_flags:

                        st.error(
                            f"⚠️ {flag}"
                        )

                else:

                    st.success(
                        "No predefined red flags detected."
                    )


                # =============================================
                # STEP 12 - AI CASE SUMMARY DISPLAY
                # =============================================

                st.markdown("---")

                st.markdown(
                    '<div class="section-title">'
                    '🤖 AI Case Summary'
                    '</div>',
                    unsafe_allow_html=True
                )

                st.write(
                    "A structured summary has been generated "
                    "from the information collected during "
                    "this patient visit."
                )

                summary_data = case_record.get(
                    "ai_summary",
                    {}
                )

                if summary_data:

                    st.success(
                        "✅ AI case summary generated successfully!"
                    )


                    # -----------------------------------------
                    # CLINICAL CASE OVERVIEW
                    # -----------------------------------------

                    st.markdown(
                        "### 🩺 Clinical Case Overview"
                    )

                    st.write(
                        summary_data.get(
                            "Summary",
                            "Summary not available."
                        )
                    )


                    # -----------------------------------------
                    # STRUCTURED SUMMARY
                    # -----------------------------------------

                    st.markdown(
                        "### 📋 Structured Case Summary"
                    )

                    col1, col2 = st.columns(2)

                    with col1:

                        st.write(
                            "**Chief Complaint**"
                        )

                        st.write(
                            summary_data.get(
                                "Chief Complaint",
                                "Not available"
                            )
                        )

                        st.write(
                            "**Symptoms**"
                        )

                        st.write(
                            summary_data.get(
                                "Symptoms",
                                "None"
                            )
                        )

                        st.write(
                            "**Duration**"
                        )

                        st.write(
                            summary_data.get(
                                "Duration",
                                "Not available"
                            )
                        )

                        st.write(
                            "**Severity**"
                        )

                        st.write(
                            summary_data.get(
                                "Severity",
                                "Not available"
                            )
                        )

                    with col2:

                        st.write(
                            "**Previous Medical History**"
                        )

                        st.write(
                            summary_data.get(
                                "Previous Medical History",
                                "None"
                            )
                        )

                        st.write(
                            "**Current Medications**"
                        )

                        st.write(
                            summary_data.get(
                                "Current Medications",
                                "None"
                            )
                        )

                        st.write(
                            "**Report Available**"
                        )

                        st.write(
                            summary_data.get(
                                "OCR Report Available",
                                "No"
                            )
                        )

                        st.write(
                            "**Language**"
                        )

                        st.write(
                            summary_data.get(
                                "Language",
                                "English"
                            )
                        )


                    # -----------------------------------------
                    # FOLLOW-UP INFORMATION
                    # -----------------------------------------

                    st.markdown(
                        "### 🤖 Follow-up Information"
                    )

                    follow_up_information = (
                        summary_data.get(
                            "Follow-up Information",
                            []
                        )
                    )

                    if follow_up_information:

                        for information in (
                            follow_up_information
                        ):

                            st.write(
                                f"• {information}"
                            )

                    else:

                        st.write(
                            "No additional follow-up information."
                        )


                    # -----------------------------------------
                    # RED FLAG SUMMARY
                    # -----------------------------------------

                    st.markdown(
                        "### 🚨 Red-Flag Summary"
                    )

                    summary_red_flags = (
                        summary_data.get(
                            "Red Flags",
                            []
                        )
                    )

                    if summary_red_flags:

                        for flag in summary_red_flags:

                            if flag == "None detected":

                                st.success(
                                    "✅ No predefined red flags detected."
                                )

                            else:

                                st.warning(
                                    f"⚠️ {flag}"
                                )

                    else:

                        st.success(
                            "No predefined red flags detected."
                        )


                    st.info(
                        "ℹ️ This AI-generated summary is a "
                        "documentation and decision-support "
                        "feature. It is not a diagnosis or a "
                        "substitute for professional clinical "
                        "judgment."
                    )


        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )


        # ========================================================
        # PATIENT HEALTH TIMELINE
        # ========================================================

        st.markdown(
            '<div class="card">',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-title">'
            '🕒 Patient Health Timeline'
            '</div>',
            unsafe_allow_html=True
        )

        st.write(
            "Previous case records are permanently loaded "
            "from the SQLite database."
        )


        # ========================================================
        # REFRESH TIMELINE FROM DATABASE
        # ========================================================

        try:

            database_history = (
                get_patient_cases(
                    patient["id"]
                )
            )

            st.session_state.case_history = (
                database_history
            )

        except Exception as e:

            st.warning(
                f"Could not refresh database history: {e}"
            )


        total_visits = len(
            st.session_state.case_history
        )

        if total_visits > 0:

            st.info(
                f"📊 Total recorded visits: "
                f"**{total_visits}**"
            )

        else:

            st.info(
                "No previous patient visits have been recorded yet."
            )


        # ========================================================
        # DISPLAY TIMELINE
        # ========================================================

        if st.session_state.case_history:

            history = list(
                reversed(
                    st.session_state.case_history
                )
            )

            for case_index, history_case in enumerate(
                history
            ):

                visit_number = history_case.get(
                    "visit_number",
                    case_index + 1
                )

                visit_date = history_case.get(
                    "visit_date",
                    "Not available"
                )

                visit_time = history_case.get(
                    "visit_time",
                    "Not available"
                )

                complaint_history = history_case.get(
                    "complaint",
                    "Not available"
                )

                history_symptoms = history_case.get(
                    "symptoms",
                    []
                )

                history_duration = history_case.get(
                    "duration",
                    "Not available"
                )

                history_severity = history_case.get(
                    "severity",
                    "Not available"
                )

                history_language = history_case.get(
                    "language",
                    "English"
                )

                history_red_flags = history_case.get(
                    "red_flags",
                    []
                )


                # ==============================================
                # TIMELINE CARD
                # ==============================================

                st.markdown(
                    '<div class="timeline-card">',
                    unsafe_allow_html=True
                )

                st.markdown(
                    f'<div class="timeline-date">'
                    f'🩺 Visit {visit_number} '
                    f'— {visit_date} at {visit_time}'
                    f'</div>',
                    unsafe_allow_html=True
                )

                st.markdown(
                    '</div>',
                    unsafe_allow_html=True
                )


                # ==============================================
                # EXPANDABLE VISIT DETAILS
                # ==============================================

                with st.expander(
                    f"View Visit {visit_number} Details"
                ):

                    col1, col2 = st.columns(2)

                    with col1:

                        st.write(
                            "**Chief Complaint**"
                        )

                        st.write(
                            complaint_history
                        )

                        st.write(
                            "**Symptoms**"
                        )

                        st.write(
                            ", ".join(history_symptoms)
                            if history_symptoms
                            else "None"
                        )

                        st.write(
                            "**Duration**"
                        )

                        st.write(
                            history_duration
                        )

                        st.write(
                            "**Severity**"
                        )

                        st.write(
                            f"{history_severity}/10"
                        )

                        st.write(
                            "**Language**"
                        )

                        st.write(
                            history_language
                        )

                    with col2:

                        st.write(
                            "**Previous Medical History**"
                        )

                        st.write(
                            history_case.get(
                                "previous_history"
                            )
                            or "None"
                        )

                        st.write(
                            "**Current Medications**"
                        )

                        st.write(
                            history_case.get(
                                "medications"
                            )
                            or "None"
                        )


                    # ==========================================
                    # ADAPTIVE ANSWERS
                    # ==========================================

                    st.markdown("---")

                    st.write(
                        "### 🤖 Adaptive Question Answers"
                    )

                    timeline_answers = history_case.get(
                        "adaptive_answers",
                        {}
                    )

                    if timeline_answers:

                        for question, answer in (
                            timeline_answers.items()
                        ):

                            st.write(
                                f"**{question}**"
                            )

                            st.write(
                                answer
                                if answer
                                else "Not answered"
                            )

                    else:

                        st.write(
                            "No adaptive questions recorded."
                        )


                    # ==========================================
                    # AI CASE SUMMARY
                    # ==========================================

                    st.markdown("---")

                    st.write(
                        "### 🤖 AI Case Summary"
                    )

                    history_ai_summary = history_case.get(
                        "ai_summary",
                        {}
                    )

                    if history_ai_summary:

                        st.write(
                            history_ai_summary.get(
                                "Summary",
                                "Summary not available."
                            )
                        )

                        with st.expander(
                            "View Structured AI Summary"
                        ):

                            st.write(
                                "**Chief Complaint:** "
                                + str(
                                    history_ai_summary.get(
                                        "Chief Complaint",
                                        "Not available"
                                    )
                                )
                            )

                            st.write(
                                "**Symptoms:** "
                                + str(
                                    history_ai_summary.get(
                                        "Symptoms",
                                        "None"
                                    )
                                )
                            )

                            st.write(
                                "**Duration:** "
                                + str(
                                    history_ai_summary.get(
                                        "Duration",
                                        "Not available"
                                    )
                                )
                            )

                            st.write(
                                "**Severity:** "
                                + str(
                                    history_ai_summary.get(
                                        "Severity",
                                        "Not available"
                                    )
                                )
                            )

                            st.write(
                                "**Previous Medical History:** "
                                + str(
                                    history_ai_summary.get(
                                        "Previous Medical History",
                                        "None"
                                    )
                                )
                            )

                            st.write(
                                "**Current Medications:** "
                                + str(
                                    history_ai_summary.get(
                                        "Current Medications",
                                        "None"
                                    )
                                )
                            )

                            st.write(
                                "**Report Available:** "
                                + str(
                                    history_ai_summary.get(
                                        "OCR Report Available",
                                        "No"
                                    )
                                )
                            )

                            st.write(
                                "**Language:** "
                                + str(
                                    history_ai_summary.get(
                                        "Language",
                                        "English"
                                    )
                                )
                            )

                    else:

                        st.info(
                            "No AI summary is available "
                            "for this visit."
                        )


                    # ==========================================
                    # OCR HISTORY
                    # ==========================================

                    timeline_ocr = history_case.get(
                        "ocr_text",
                        ""
                    )

                    st.markdown("---")

                    st.write(
                        "### 📄 Medical Report"
                    )

                    if timeline_ocr:

                        st.text_area(
                            "OCR Extracted Text",
                            value=timeline_ocr,
                            height=180,
                            key=f"timeline_ocr_{visit_number}"
                        )

                    else:

                        st.info(
                            "No medical report was uploaded "
                            "for this visit."
                        )


                    # ==========================================
                    # RED FLAGS HISTORY
                    # ==========================================

                    st.markdown("---")

                    st.write(
                        "### 🚨 Red-Flag Status"
                    )

                    if history_red_flags:

                        for flag in history_red_flags:

                            st.error(
                                f"⚠️ {flag}"
                            )

                    else:

                        st.success(
                            "No predefined red-flag indicators "
                            "were detected for this visit."
                        )


        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )


# ============================================================
# DOCTOR DASHBOARD
# ============================================================

elif st.session_state.role == "Doctor":

    st.success(
        "✅ Doctor login successful!"
    )

    st.markdown(
        '<div class="card">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-title">'
        '👨‍⚕️ Doctor Dashboard'
        '</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Doctor dashboard for reviewing registered "
        "patients and their case history."
    )


    # ========================================================
    # LOAD ALL PATIENTS FROM SQLITE
    # ========================================================

    try:

        all_patients = get_all_patients()

    except Exception as e:

        all_patients = []

        st.error(
            f"Could not load patients: {e}"
        )


    try:

        all_cases = get_all_cases()

    except Exception as e:

        all_cases = []

        st.error(
            f"Could not load cases: {e}"
        )


    # ========================================================
    # DASHBOARD STATISTICS
    # ========================================================

    total_patients = len(
        all_patients
    )

    total_cases = len(
        all_cases
    )

    total_alert_cases = sum(
        1
        for case_item in all_cases
        if case_item.get("red_flags")
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "👥 Total Patients",
            total_patients
        )

    with col2:

        st.metric(
            "🩺 Total Visits",
            total_cases
        )

    with col3:

        st.metric(
            "🚨 Alert Cases",
            total_alert_cases
        )


    # ========================================================
    # PATIENT SEARCH
    # ========================================================

    st.markdown("---")

    st.subheader(
        "🔎 Search Patient"
    )

    search_text = st.text_input(
        "Search by patient name or phone number",
        placeholder="Enter patient name or phone..."
    )

    filtered_patients = all_patients

    if search_text.strip():

        search_lower = search_text.lower()

        filtered_patients = [

            patient_item

            for patient_item in all_patients

            if (
                search_lower
                in str(
                    patient_item.get(
                        "name",
                        ""
                    )
                ).lower()
                or
                search_lower
                in str(
                    patient_item.get(
                        "phone",
                        ""
                    )
                ).lower()
            )
        ]


    # ========================================================
    # PATIENT LIST
    # ========================================================

    st.subheader(
        "👥 Registered Patients"
    )

    if filtered_patients:

        for patient_item in filtered_patients:

            patient_id = patient_item.get(
                "id"
            )

            patient_name = patient_item.get(
                "name",
                "Unknown"
            )

            with st.expander(
                f"Patient #{patient_id} — {patient_name}"
            ):

                col1, col2 = st.columns(2)

                with col1:

                    st.write(
                        f"**Age:** "
                        f"{patient_item.get('age', 'N/A')}"
                    )

                    st.write(
                        f"**Gender:** "
                        f"{patient_item.get('gender', 'N/A')}"
                    )

                    st.write(
                        f"**Phone:** "
                        f"{patient_item.get('phone', 'N/A')}"
                    )

                    st.write(
                        f"**Blood Group:** "
                        f"{patient_item.get('blood_group', 'N/A')}"
                    )

                with col2:

                    st.write(
                        f"**Email:** "
                        f"{patient_item.get('email', 'N/A')}"
                    )

                    st.write(
                        f"**Language:** "
                        f"{patient_item.get('language', 'N/A')}"
                    )

                    st.write(
                        f"**Emergency Contact:** "
                        f"{patient_item.get('emergency_contact', 'N/A')}"
                    )

                    st.write(
                        f"**Registered:** "
                        f"{patient_item.get('created_at', 'N/A')}"
                    )


                # ==========================================
                # PATIENT CASES
                # ==========================================

                try:

                    patient_cases = (
                        get_patient_cases(
                            patient_id
                        )
                    )

                except Exception:

                    patient_cases = []


                st.markdown("---")

                st.write(
                    "### 🩺 Patient Visit History"
                )

                if patient_cases:

                    for patient_case in patient_cases:

                        visit_number = patient_case.get(
                            "visit_number",
                            "N/A"
                        )

                        visit_date = patient_case.get(
                            "visit_date",
                            "N/A"
                        )

                        with st.expander(
                            f"Visit {visit_number} "
                            f"| {visit_date}"
                        ):

                            st.write(
                                f"**Chief Complaint:** "
                                f"{patient_case.get('complaint', 'N/A')}"
                            )

                            case_symptoms = (
                                patient_case.get(
                                    "symptoms",
                                    []
                                )
                            )

                            st.write(
                                f"**Symptoms:** "
                                f"{', '.join(case_symptoms) if case_symptoms else 'None'}"
                            )

                            st.write(
                                f"**Duration:** "
                                f"{patient_case.get('duration', 'N/A')}"
                            )

                            st.write(
                                f"**Severity:** "
                                f"{patient_case.get('severity', 'N/A')}/10"
                            )

                            st.write(
                                f"**Previous History:** "
                                f"{patient_case.get('previous_history') or 'None'}"
                            )

                            st.write(
                                f"**Medications:** "
                                f"{patient_case.get('medications') or 'None'}"
                            )


                            # ----------------------------------
                            # AI SUMMARY
                            # ----------------------------------

                            doctor_summary = (
                                patient_case.get(
                                    "ai_summary",
                                    {}
                                )
                            )

                            if doctor_summary:

                                st.markdown(
                                    "#### 🤖 AI Case Summary"
                                )

                                st.info(
                                    doctor_summary.get(
                                        "Summary",
                                        "Summary not available."
                                    )
                                )


                            # ----------------------------------
                            # RED FLAGS
                            # ----------------------------------

                            doctor_flags = (
                                patient_case.get(
                                    "red_flags",
                                    []
                                )
                            )

                            st.markdown(
                                "#### 🚨 Red-Flag Status"
                            )

                            if doctor_flags:

                                for flag in doctor_flags:

                                    st.warning(
                                        f"⚠️ {flag}"
                                    )

                            else:

                                st.success(
                                    "No predefined red flags detected."
                                )


                            # ----------------------------------
                            # OCR
                            # ----------------------------------

                            doctor_ocr = (
                                patient_case.get(
                                    "ocr_text",
                                    ""
                                )
                            )

                            if doctor_ocr:

                                st.markdown(
                                    "#### 📄 OCR Medical Report"
                                )

                                st.text_area(
                                    "Extracted Report",
                                    value=doctor_ocr,
                                    height=180,
                                    key=(
                                        f"doctor_ocr_"
                                        f"{patient_id}_"
                                        f"{visit_number}"
                                    )
                                )

                else:

                    st.info(
                        "No visits recorded for this patient."
                    )

    else:

        st.info(
            "No matching patients found."
        )


    # ========================================================
    # RECENT CASES
    # ========================================================

    st.markdown("---")

    st.subheader(
        "📋 Recent Patient Cases"
    )

    if all_cases:

        for recent_case in all_cases[:20]:

            patient_name = recent_case.get(
                "patient_name",
                "Unknown"
            )

            visit_number = recent_case.get(
                "visit_number",
                "N/A"
            )

            visit_date = recent_case.get(
                "visit_date",
                "N/A"
            )

            with st.expander(
                f"{patient_name} | "
                f"Visit {visit_number} | "
                f"{visit_date}"
            ):

                st.write(
                    f"**Complaint:** "
                    f"{recent_case.get('complaint', 'N/A')}"
                )

                recent_symptoms = (
                    recent_case.get(
                        "symptoms",
                        []
                    )
                )

                st.write(
                    f"**Symptoms:** "
                    f"{', '.join(recent_symptoms) if recent_symptoms else 'None'}"
                )

                st.write(
                    f"**Severity:** "
                    f"{recent_case.get('severity', 'N/A')}/10"
                )

                recent_flags = (
                    recent_case.get(
                        "red_flags",
                        []
                    )
                )

                if recent_flags:

                    st.error(
                        "🚨 Red Flags: "
                        + ", ".join(recent_flags)
                    )

                else:

                    st.success(
                        "No predefined red flags detected."
                    )

                recent_summary = (
                    recent_case.get(
                        "ai_summary",
                        {}
                    )
                )

                if recent_summary:

                    st.info(
                        recent_summary.get(
                            "Summary",
                            "No summary available."
                        )
                    )

    else:

        st.info(
            "No patient cases available."
        )


    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    '<div class="footer">'
    'Secure • Smart • Patient-Centered Healthcare • '
    'SQLite Database'
    '</div>',
    unsafe_allow_html=True
)