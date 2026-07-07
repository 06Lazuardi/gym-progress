import streamlit as st
import pandas as pd
import datetime
import os

# --- 1. CONFIG HALAMAN MOBILE ---
st.set_page_config(page_title="Gym Member Portal", page_icon="🔒", layout="centered")

# --- 2. MASTER PASSWORD & FILE DATABASE LOG (DENGAN PROTEKSI TABEL CSV) ---
MASTER_PASSWORD = "superowner2026"  
LOG_FILE = "gym_workout_logs.csv"
KOLOM_DATABASE = ["Tanggal", "Username", "Gerakan", "Set_Ke", "Beban_kg", "Reps"]

# Jika file tidak ada ATAU file ada tapi kosong (0 bytes), buat baru dengan format tabel lengkap
if not os.path.exists(LOG_FILE) or os.path.getsize(LOG_FILE) == 0:
    df_empty = pd.DataFrame(columns=KOLOM_DATABASE)
    df_empty.to_csv(LOG_FILE, index=False)

# --- 3. DATABASE USER ---
if "user_database" not in st.session_state:
    st.session_state.user_database = {
        "06_Lazuardi": {"password": "superpassword2026", "role": "admin", "nama": "Owner Gym (Ardi)"},
        "Artha": {"password": "Artha123", "role": "member", "nama": "Juniartha"},
        "Rara": {"password": "Rara123", "role": "member", "nama": "Rara"},
        "Yuni": {"password": "Yuni123", "role": "member", "nama": "Yuni"},
        "Meli": {"password": "Meli123", "role": "member", "nama": "Meli"},
        "Yana": {"password": "Yana123", "role": "member", "nama": "Yana"},
        "Ayu": {"password": "Ayu123", "role": "member", "nama": "Ayu"},
        "Sefitri": {"password": "Cepi123", "role": "member", "nama": "Sefitri"}
    }

# --- 4. INITIALIZE JADWAL GYM ---
# Jadwal 4 Hari untuk Admin
if "jadwal_gym_admin" not in st.session_state:
    st.session_state.jadwal_gym_admin = {
        "Hari 1 – Chest + Triceps": [
            {"nama": "Barbell Bench Press", "target": "4 × 8"},
            {"nama": "Incline Dumbbell Press", "target": "4 × 10"},
            {"nama": "Chest Press Machine", "target": "3 × 12"},
            {"nama": "Cable Fly", "target": "3 × 12"},
            {"nama": "Pec Deck Fly", "target": "3 × 15"},
            {"nama": "Rope Pushdown", "target": "3 × 15"},
            {"nama": "Overhead Cable Triceps Extension", "target": "3 × 12"},
            {"nama": "Dips / Assisted Dips", "target": "3 × Max"}
        ],
        "Hari 2 – Back + Biceps": [
            {"nama": "Pull Up / Lat Pulldown", "target": "4 × 10"},
            {"nama": "Barbell Row", "target": "4 × 8"},
            {"nama": "Seated Cable Row", "target": "3 × 10"},
            {"nama": "Single Arm Dumbbell Row", "target": "3 × 10"},
            {"nama": "Face Pull", "target": "3 × 15"},
            {"nama": "EZ Bar Curl", "target": "3 × 10"},
            {"nama": "Incline Dumbbell Curl", "target": "3 × 12"},
            {"nama": "Hammer Curl", "target": "3 × 12"}
        ],
        "Hari 3 – Upper Body + Arms": [
            {"nama": "Incline Smith Machine Press", "target": "4 × 10"},
            {"nama": "Chest Supported Row", "target": "4 × 10"},
            {"nama": "Dumbbell Shoulder Press", "target": "3 × 10"},
            {"nama": "Lateral Raise", "target": "4 × 15"},
            {"nama": "Rear Delt Fly", "target": "3 × 15"},
            {"nama": "Cable Fly", "target": "3 × 12"},
            {"nama": "Close Grip Bench Press", "target": "4 × 10"},
            {"nama": "Preacher Curl", "target": "3 × 10"},
            {"nama": "Rope Pushdown", "target": "3 × 15"},
            {"nama": "Cable Curl", "target": "3 × 12"}
        ],
        "Hari 4 – Full Lower Body": [
            {"nama": "Back Squat", "target": "4 × 8"},
            {"nama": "Romanian Deadlift", "target": "4 × 8"},
            {"nama": "Leg Press", "target": "3 × 12"},
            {"nama": "Walking Lunges", "target": "3 × 12/kaki"},
            {"nama": "Leg Extension", "target": "3 × 15"},
            {"nama": "Seated Leg Curl", "target": "3 × 15"},
            {"nama": "Hip Thrust", "target": "4 × 10"},
            {"nama": "Standing Calf Raise", "target": "4 × 15"},
            {"nama": "Seated Calf Raise", "target": "4 × 20"},
            {"nama": "Hanging Leg Raise / Cable Crunch", "target": "3 × 15"}
        ]
    }

# Jadwal 5 Hari untuk Rara
if "jadwal_gym_rara" not in st.session_state:
    st.session_state.jadwal_gym_rara = {
        "Hari 1 – Chest + Leg + Triceps": [
            {"nama": "Barbell Bench Press", "target": "4 × 8"},
            {"nama": "Incline Dumbbell Press", "target": "4 × 10"},
            {"nama": "Chest Press Machine", "target": "3 × 12"},
            {"nama": "Cable Fly", "target": "3 × 12"},
            {"nama": "Back Squat", "target": "4 × 8"},
            {"nama": "Leg Press", "target": "3 × 10"},
            {"nama": "Leg Extension", "target": "3 × 12"},
            {"nama": "Rope Pushdown", "target": "3 × 15"},
            {"nama": "Overhead Cable Triceps Extension", "target": "3 × 12"}
        ],
        "Hari 2 – Back + Biceps": [
            {"nama": "Pull Up / Lat Pulldown", "target": "4 × 10"},
            {"nama": "Barbell Row", "target": "4 × 8"},
            {"nama": "Seated Cable Row", "target": "3 × 10"},
            {"nama": "Straight Arm Pulldown", "target": "3 × 12"},
            {"nama": "Face Pull", "target": "3 × 15"},
            {"nama": "EZ Bar Curl", "target": "3 × 10"},
            {"nama": "Incline Dumbbell Curl", "target": "3 × 12"},
            {"nama": "Hammer Curl", "target": "3 × 12"}
        ],
        "Hari 3 – Upper Body + Leg": [
            {"nama": "Incline Smith Machine Press", "target": "4 × 10"},
            {"nama": "Pec Deck Fly", "target": "3 × 15"},
            {"nama": "Chest Supported Row", "target": "4 × 10"},
            {"nama": "Dumbbell Shoulder Press", "target": "3 × 10"},
            {"nama": "Lateral Raise", "target": "4 × 15"},
            {"nama": "Romanian Deadlift", "target": "4 × 8"},
            {"nama": "Walking Lunges", "target": "3 × 12/kaki"},
            {"nama": "Leg Curl", "target": "3 × 12"},
            {"nama": "Standing Calf Raise", "target": "4 × 15"}
        ],
        "Hari 4 – Full Arms": [
            {"nama": "Close Grip Bench Press", "target": "4 × 10"},
            {"nama": "Barbell Curl", "target": "3 × 10"},
            {"nama": "Preacher Curl", "target": "3 × 10"},
            {"nama": "Hammer Curl", "target": "3 × 12"},
            {"nama": "Rope Pushdown", "target": "3 × 15"},
            {"nama": "Overhead Dumbbell Triceps Extension", "target": "3 × 12"},
            {"nama": "Wrist Curl", "target": "3 × 15"},
            {"nama": "Reverse Wrist Curl", "target": "3 × 15"}
        ],
        "Hari 5 – Lower Body Full": [
            {"nama": "Front Squat / Hack Squat", "target": "4 × 10"},
            {"nama": "Romanian Deadlift", "target": "4 × 8"},
            {"nama": "Leg Press", "target": "3 × 12"},
            {"nama": "Leg Extension", "target": "3 × 15"},
            {"nama": "Seated Leg Curl", "target": "3 × 15"},
            {"nama": "Hip Thrust", "target": "4 × 10"},
            {"nama": "Seated Calf Raise", "target": "4 × 20"},
            {"nama": "Hanging Leg Raise", "target": "3 × 15"},
            {"nama": "Cable Crunch", "target": "3 × 15"}
        ]
    }

# Jadwal 4 Hari untuk Member Umum
if "jadwal_gym_member_umum" not in st.session_state:
    st.session_state.jadwal_gym_member_umum = {
        "Hari 1 – Back + Biceps": [
            {"nama": "Pull Up / Lat Pulldown", "target": "4 × 10"},
            {"nama": "Barbell Row", "target": "4 × 8"},
            {"nama": "Chest Supported Row", "target": "3 × 10"},
            {"nama": "Seated Cable Row", "target": "3 × 12"},
            {"nama": "Straight Arm Pulldown", "target": "3 × 12"},
            {"nama": "Face Pull", "target": "3 × 15"},
            {"nama": "EZ Bar Curl", "target": "3 × 10"},
            {"nama": "Incline Dumbbell Curl", "target": "3 × 12"},
            {"nama": "Hammer Curl", "target": "3 × 12"}
        ],
        "Hari 2 – Chest + Triceps": [
            {"nama": "Barbell Bench Press", "target": "4 × 8"},
            {"nama": "Incline Dumbbell Press", "target": "4 × 10"},
            {"nama": "Chest Press Machine", "target": "3 × 12"},
            {"nama": "Pec Deck Fly", "target": "3 × 15"},
            {"nama": "Cable Fly", "target": "3 × 12"},
            {"nama": "Dips / Assisted Dips", "target": "3 × Max"},
            {"nama": "Rope Pushdown", "target": "3 × 15"},
            {"nama": "Overhead Cable Triceps Extension", "target": "3 × 12"}
        ],
        "Hari 3 – Upper Body + Arms": [
            {"nama": "Incline Smith Machine Press", "target": "4 × 10"},
            {"nama": "Chest Supported Row", "target": "4 × 10"},
            {"nama": "Dumbbell Shoulder Press", "target": "3 × 10"},
            {"nama": "Lateral Raise", "target": "4 × 15"},
            {"nama": "Rear Delt Fly", "target": "3 × 15"},
            {"nama": "Close Grip Bench Press", "target": "4 × 10"},
            {"nama": "Cable Curl", "target": "3 × 12"},
            {"nama": "Preacher Curl", "target": "3 × 10"},
            {"nama": "Rope Pushdown", "target": "3 × 15"},
            {"nama": "Overhead Dumbbell Triceps Extension", "target": "3 × 12"}
        ],
        "Hari 4 – Full Lower Body": [
            {"nama": "Back Squat", "target": "4 × 8"},
            {"nama": "Romanian Deadlift", "target": "4 × 8"},
            {"nama": "Leg Press", "target": "3 × 12"},
            {"nama": "Bulgarian Split Squat", "target": "3 × 10/kaki"},
            {"nama": "Leg Extension", "target": "3 × 15"},
            {"nama": "Seated Leg Curl", "target": "3 × 15"},
            {"nama": "Hip Thrust", "target": "4 × 10"},
            {"nama": "Standing Calf Raise", "target": "4 × 15"},
            {"nama": "Seated Calf Raise", "target": "4 × 20"},
            {"nama": "Hanging Leg Raise / Cable Crunch", "target": "3 × 15"}
        ]
    }

# --- 5. INITIALIZE STATUS LOGIN ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.user_role = None
    st.session_state.user_nama = None

# --- 6. INTERFACE SEBELUM LOGIN ---
if not st.session_state.logged_in:
    st.title("🏋️‍♂️ Gym Private Member Portal")
    with st.form("login_form"):
        username_input = st.text_input("Username").strip()
        password_input = st.text_input("Password", type="password").strip()
        submit_login = st.form_submit_button("Masuk 🔓")
        
        if submit_login:
            db = st.session_state.
