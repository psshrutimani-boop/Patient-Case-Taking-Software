import sqlite3
import json
from pathlib import Path


# ============================================================
# DATABASE LOCATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_FOLDER = BASE_DIR / "database"

DATABASE_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)

DATABASE_PATH = DATABASE_FOLDER / "patient_case.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():

    connection = sqlite3.connect(
        str(DATABASE_PATH),
        check_same_thread=False
    )

    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# CREATE TABLES
# ============================================================

def create_tables():

    connection = get_connection()

    cursor = connection.cursor()

    # --------------------------------------------------------
    # PATIENTS TABLE
    # --------------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS patients (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            age INTEGER,

            gender TEXT,

            phone TEXT,

            email TEXT,

            language TEXT,

            emergency_contact TEXT,

            blood_group TEXT,

            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # --------------------------------------------------------
    # PATIENT CASES TABLE
    # --------------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS patient_cases (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            patient_id INTEGER NOT NULL,

            visit_number INTEGER,

            visit_date TEXT,

            visit_time TEXT,

            visit_datetime TEXT,

            complaint TEXT,

            symptoms TEXT,

            duration TEXT,

            severity INTEGER,

            previous_history TEXT,

            medications TEXT,

            adaptive_answers TEXT,

            language TEXT,

            ocr_text TEXT,

            red_flags TEXT,

            ai_summary TEXT,

            created_at TEXT DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (patient_id)
            REFERENCES patients(id)
            ON DELETE CASCADE
        )
        """
    )

    connection.commit()

    cursor.close()
    connection.close()


# ============================================================
# SAVE PATIENT
# ============================================================

def save_patient(patient_data):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO patients
        (
            name,
            age,
            gender,
            phone,
            email,
            language,
            emergency_contact,
            blood_group
        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            patient_data.get("name", ""),
            patient_data.get("age"),
            patient_data.get("gender", ""),
            patient_data.get("phone", ""),
            patient_data.get("email", ""),
            patient_data.get("language", "English"),
            patient_data.get("emergency_contact", ""),
            patient_data.get("blood_group", "")
        )
    )

    patient_id = cursor.lastrowid

    connection.commit()

    cursor.close()
    connection.close()

    return patient_id


# ============================================================
# SAVE CASE
# ============================================================

def save_case(patient_id, case_record):

    connection = get_connection()

    cursor = connection.cursor()

    symptoms = case_record.get(
        "symptoms",
        []
    )

    adaptive_answers = case_record.get(
        "adaptive_answers",
        {}
    )

    red_flags = case_record.get(
        "red_flags",
        []
    )

    ai_summary = case_record.get(
        "ai_summary",
        {}
    )

    cursor.execute(
        """
        INSERT INTO patient_cases
        (
            patient_id,
            visit_number,
            visit_date,
            visit_time,
            visit_datetime,
            complaint,
            symptoms,
            duration,
            severity,
            previous_history,
            medications,
            adaptive_answers,
            language,
            ocr_text,
            red_flags,
            ai_summary
        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            patient_id,

            case_record.get(
                "visit_number",
                1
            ),

            case_record.get(
                "visit_date",
                ""
            ),

            case_record.get(
                "visit_time",
                ""
            ),

            case_record.get(
                "visit_datetime",
                ""
            ),

            case_record.get(
                "complaint",
                ""
            ),

            json.dumps(
                symptoms,
                ensure_ascii=False
            ),

            case_record.get(
                "duration",
                ""
            ),

            int(
                case_record.get(
                    "severity",
                    0
                )
            ),

            case_record.get(
                "previous_history",
                ""
            ),

            case_record.get(
                "medications",
                ""
            ),

            json.dumps(
                adaptive_answers,
                ensure_ascii=False
            ),

            case_record.get(
                "language",
                "English"
            ),

            case_record.get(
                "ocr_text",
                ""
            ),

            json.dumps(
                red_flags,
                ensure_ascii=False
            ),

            json.dumps(
                ai_summary,
                ensure_ascii=False
            )
        )
    )

    case_id = cursor.lastrowid

    connection.commit()

    cursor.close()
    connection.close()

    return case_id


# ============================================================
# GET PATIENT
# ============================================================

def get_patient(patient_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM patients
        WHERE id = ?
        """,
        (patient_id,)
    )

    row = cursor.fetchone()

    cursor.close()
    connection.close()

    if row:

        return dict(row)

    return None


# ============================================================
# GET ALL PATIENTS
# ============================================================

def get_all_patients():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM patients
        ORDER BY created_at DESC
        """
    )

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    return [
        dict(row)
        for row in rows
    ]


# ============================================================
# GET PATIENT CASES
# ============================================================

def get_patient_cases(patient_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM patient_cases

        WHERE patient_id = ?

        ORDER BY id DESC
        """,
        (patient_id,)
    )

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    cases = []

    for row in rows:

        case = dict(row)

        try:
            case["symptoms"] = json.loads(
                case["symptoms"]
            )
        except:
            case["symptoms"] = []

        try:
            case["adaptive_answers"] = json.loads(
                case["adaptive_answers"]
            )
        except:
            case["adaptive_answers"] = {}

        try:
            case["red_flags"] = json.loads(
                case["red_flags"]
            )
        except:
            case["red_flags"] = []

        try:
            case["ai_summary"] = json.loads(
                case["ai_summary"]
            )
        except:
            case["ai_summary"] = {}

        cases.append(case)

    return cases


# ============================================================
# GET ALL CASES
# ============================================================

def get_all_cases():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            patient_cases.*,
            patients.name AS patient_name

        FROM patient_cases

        INNER JOIN patients
        ON patient_cases.patient_id = patients.id

        ORDER BY patient_cases.id DESC
        """
    )

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    cases = []

    for row in rows:

        case = dict(row)

        try:
            case["symptoms"] = json.loads(
                case["symptoms"]
            )
        except:
            case["symptoms"] = []

        try:
            case["adaptive_answers"] = json.loads(
                case["adaptive_answers"]
            )
        except:
            case["adaptive_answers"] = {}

        try:
            case["red_flags"] = json.loads(
                case["red_flags"]
            )
        except:
            case["red_flags"] = []

        try:
            case["ai_summary"] = json.loads(
                case["ai_summary"]
            )
        except:
            case["ai_summary"] = {}

        cases.append(case)

    return cases


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def initialize_database():

    try:

        create_tables()

        return True

    except Exception as e:

        print(
            "Database initialization error:",
            e
        )

        return False