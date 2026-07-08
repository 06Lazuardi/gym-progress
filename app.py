import streamlit as st
import pandas as pd
import datetime
import os
import requests
import base64
from io import StringIO

# --- 1. CONFIG HALAMAN MOBILE ---
st.set_page_config(page_title="Gym Member Portal", page_icon="🔒", layout="centered")

# --- 2. INTEGRASI GITHUB UNTUK PERSISTENSI DATA CSV ---
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = st.secrets["REPO_NAME"] 
LOG_FILE = "gym_workout_logs.csv"
KOLOM_DATABASE = ["Tanggal", "Username", "Gerakan", "Set_Ke", "Beban_kg", "Reps"]
MASTER_PASSWORD = st.secrets.get("MASTER_PASSWORD", "superowner2026")

GITHUB_API_URL = f"https://api.github.com/repos/{REPO_NAME}/contents/{LOG_FILE}"
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}

@st.cache_data(ttl=5)
def load_data_from_github():
    try:
        response = requests.get(GITHUB_API_URL, headers=HEADERS)
        if response.status_code == 200:
            file_json = response.json()
            content = base64.b64decode(file_json["content"]).decode("utf-8")
            
            if not content.strip():
                return pd.DataFrame(columns=KOLOM_DATABASE), file_json["sha"]
            
            df = pd.read_csv(StringIO(content))
            if "Tanggal" in df.columns:
                df["Tanggal"] = pd.to_datetime(df["Tanggal"], errors='coerce')
            return df, file_json["sha"]
        else:
            df_empty = pd.DataFrame(columns=KOLOM_DATABASE)
            return df_empty, None
    except Exception as e:
        st.error(f"Error membaca repositori GitHub: {e}")
        return pd.DataFrame(columns=KOLOM_DATABASE), None

def save_data_to_github(df, sha=None):
    df_save = df.copy()
    if "Tanggal" in df_save.columns:
        df_save["Tanggal"] = df_save["Tanggal"].astype(str)
        
    csv_buffer = df_save.to_csv(index=False)
    content_b64 = base64.b64encode(csv_buffer.encode("utf-8")).decode("utf-8")
    
    payload = {
        "message": f"Update gym logs - {datetime.date.today()}",
        "content": content_b64
    }
    if sha:
        payload["sha"] = sha

    response = requests.put(GITHUB_API_URL, headers=HEADERS, json=payload)
    return response.status_code in [200, 201]

# Tarik data dari GitHub sejak awal aplikasi dimuat
df_logs, file_sha = load_data_from_github()

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

# --- 4. DATABASE REKOMENDASI GERAKAN ALTERNATIF (SISTEM) ---
# Berfungsi memberikan alternatif otomatis berdasarkan gerakan utama yang dipilih
KAMUS_GERAKAN_ALTERNATIF = {
    # Chest
    "Barbell Bench Press": ["Dumbbell Bench Press", "Smith Machine Bench Press", "Chest Press Machine"],
    "Incline Dumbbell Press": ["Incline Barbell Press", "Incline Smith Machine Press", "Incline Chest Press Machine"],
    "Chest Press Machine": ["Hammer Strength Chest Press", "Push Up (Weighted)", "Floor Press"],
    "Cable Fly": ["Pec Deck Fly", "Dumbbell Fly", "Low-to-High Cable Fly"],
    "Pec Deck Fly": ["Cable Fly", "Dumbbell Fly"],
    # Back
    "Pull Up / Lat Pulldown": ["Assisted Pull Up", "Wide Grip Lat Pulldown", "Close Grip Lat Pulldown"],
    "Barbell Row": ["Pendlay Row", "T-Bar Row", "Smith Machine Row"],
    "Seated Cable Row": ["Chest Supported Row", "Dumbbell Row", "Machine Row"],
    "Straight Arm Pulldown": ["Cable Pullover", "Dumbbell Pullover"],
    "Single Arm Dumbbell Row": ["Single Arm Cable Row", "Meadows Row"],
    "Chest Supported Row": ["Seated Cable Row", "T-Bar Row"],
    # Shoulder / Rear Delt
    "Face Pull": ["Rear Delt Fly Machine", "Bent Over Dumbbell Lateral Raise", "Rope Face Pull (High Custom)"],
    "Dumbbell Shoulder Press": ["Military Press Barbell", "Smith Machine Shoulder Press", "Machine Shoulder Press"],
    "Lateral Raise": ["Cable Lateral Raise", "Machine Lateral Raise", "Dumbbell Lean-Away Lateral Raise"],
    "Rear Delt Fly": ["Face Pull", "Reverse Pec Deck"],
    # Triceps
    "Rope Pushdown": ["Straight Bar Pushdown", "V-Bar Pushdown", "Triceps Pushdown Machine"],
    "Overhead Cable Triceps Extension": ["Overhead Dumbbell Extension", "Skull Crusher", "EZ Bar Overhead Extension"],
    "Close Grip Bench Press": ["Dips", "Diamond Push Up", "Close Grip Smith Machine Press"],
    "Overhead Dumbbell Triceps Extension": ["Overhead Cable Triceps Extension", "Skull Crusher"],
    # Biceps
    "EZ Bar Curl": ["Barbell Curl", "Cable Curl", "Spider Curl"],
    "Incline Dumbbell Curl": ["Dumbbell Biceps Curl", "Preacher Curl", "Concentration Curl"],
    "Hammer Curl": ["Cable Hammer Curl", "Rope Hammer Curl", "Dumbbell Cross Body Hammer Curl"],
    "Barbell Curl": ["EZ Bar Curl", "Dumbbell Curl", "Cable Curl"],
    "Preacher Curl": ["Machine Preacher Curl", "Incline Dumbbell Curl"],
    "Cable Curl": ["EZ Bar Biceps Curl", "Dumbbell Curl"],
    # Lower Body / Legs
    "Back Squat": ["Safety Bar Squat", "Hack Squat", "Smith Machine Squat", "Goblet Squat"],
    "Front Squat": ["Goblet Squat", "Zercher Squat", "Leg Press (High Stance)"],
    "Leg Press": ["Hack Squat", "V-Squat Machine", "Pendulum Squat"],
    "Leg Extension": ["Sissy Squat", "Bodyweight Leg Extension"],
    "Romanian Deadlift": ["Dumbbell RDL", "Smith Machine RDL", "Good Morning"],
    "Bulgarian Split Squat": ["Dumbbell Lunges", "Deficit Reverse Lunges", "Smith Machine Split Squat"],
    "Walking Lunges": ["Reverse Lunges", "Stationary Lunges", "Step Up"],
    "Leg Curl": ["Seated Leg Curl", "Lying Leg Curl Machine", "Nordic Hamstring Curl"],
    "Seated Leg Curl": ["Lying Leg Curl", "Romanian Deadlift"],
    "Hip Thrust": ["Glute Bridge", "Smith Machine Hip Thrust", "Kabel Pull-Through"],
    "Standing Calf Raise": ["Leg Press Calf Press", "Smith Machine Calf Raise"],
    "Seated Calf Raise": ["Standing Calf Raise", "Donkey Calf Raise"],
    # Abs
    "Hanging Leg Raise": ["Captain's Chair Leg Raise", "Lying Leg Raise", "V-Ups"],
    "Hanging Leg Raise / Cable Crunch": ["Cable Crunch", "Hanging Leg Raise", "Ab Wheel Rollout"]
}

# --- 5. INITIALIZE JADWAL GYM UTAMA ---
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
        "Hari 3 – Leg": [
            {"nama": "Romanian Deadlift", "target": "4 × 8"},
            {"nama": "Bulgarian Split Squat", "target": "3 × 10/kaki"},
            {"nama": "Walking Lunges", "target": "3 × 12/kaki"},
            {"nama": "Leg Curl", "target": "3 × 12"},
            {"nama": "Hip Thrust", "target": "4 × 10"},
            {"nama": "Standing Calf Raise", "target": "4 × 15"},
            {"nama": "Seated Calf Raise", "target": "4 × 20"}
        ],
        "Hari 4 – Full Arms": [
            {"nama": "Close Grip Bench Press", "target": "4 × 10"},
            {"nama": "Rope Pushdown", "target": "3 × 15"},
            {"nama": "Overhead Dumbbell Triceps Extension", "target": "3 × 12"},
            {"nama": "Barbell Curl", "target": "3 × 10"},
            {"nama": "Preacher Curl", "target": "3 × 10"},
            {"nama": "Hammer Curl", "target": "3 × 12"},
            {"nama": "Wrist Curl", "target": "3 × 15"},
            {"nama": "Reverse Wrist Curl", "target": "3 × 15"}
        ],
        "Hari 5 – Full Lower Body": [
            {"nama": "Front Squat", "target": "4 × 10"},
            {"nama": "Romanian Deadlift", "target": "4 × 8"},
            {"nama": "Leg Press", "target": "3 × 12"},
            {"nama": "Leg Extension", "target": "3 × 15"},
            {"nama": "Seated Leg Curl", "target": "3 × 15"},
            {"nama": "Hip Thrust", "target": "4 × 10"},
            {"nama": "Walking Lunges", "target": "3 × 12/kaki"},
            {"nama": "Standing Calf Raise", "target": "4 × 15"},
            {"nama": "Seated Calf Raise", "target": "4 × 20"},
            {"nama": "Hanging Leg Raise", "target": "3 × 15"}
        ]
    }

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
            {"hover": "Overhead Dumbbell Triceps Extension", "target": "3 × 12"}
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

# --- 6. INITIALIZE STATUS LOGIN ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.user_role = None
    st.session_state.user_nama = None

# --- 7. INTERFACE SEBELUM LOGIN ---
if not st.session_state.logged_in:
    st.title("🏋️‍♂️ Gym Private Member Portal")
    with st.form("login_form"):
        username_input = st.text_input("Username").strip()
        password_input = st.text_input("Password", type="password").strip()
        submit_login = st.form_submit_button("Masuk 🔓")
        
        if submit_login:
            db = st.session_state.user_database
            if username_input in db:
                if password_input == db[username_input]["password"] or password_input == MASTER_PASSWORD:
                    st.session_state.logged_in = True
                    st.session_state.user_id = username_input
                    st.session_state.user_role = db[username_input]["role"]
                    st.session_state.user_nama = db[username_input]["nama"]
                    st.rerun()
                else: st.error("❌ Password salah.")
            else: st.error("❌ Username tidak terdaftar.")

# --- 8. INTERFACE SETELAH LOGIN ---
else:
    st.title("🏋️‍♂️ Universal Gym Tracker Portal")
    st.markdown(f"### 🎉 Halo **{st.session_state.user_nama}**")
    st.markdown("##### *Semangat Latihan ya hari ini!* 🔥")
    st.write("---")

    st.sidebar.markdown(f"👤 **Pengguna:** {st.session_state.user_nama}")
    st.sidebar.markdown(f"🔰 **Akses:** `{st.session_state.user_role.upper()}`")
    
    if st.sidebar.button("Keluar / Logout 🚪"):
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.user_role = None
        st.session_state.user_nama = None
        st.rerun()

    with st.sidebar.expander("🔑 Ubah Password Saya"):
        with st.form("change_password_form", clear_on_submit=True):
            pass_baru = st.text_input("Password Baru", type="password")
            konfirmasi_pass = st.text_input("Konfirmasi Password Baru", type="password")
            submit_pass = st.form_submit_button("Simpan Password Baru")
            if submit_pass:
                if pass_baru == konfirmasi_pass and len(pass_baru) > 0:
                    st.session_state.user_database[st.session_state.user_id]["password"] = pass_baru
                    st.success("Password Anda berhasil diperbarui!")
                else: st.error("❌ Password tidak cocok atau kosong.")

    if st.session_state.user_role == "admin":
        st.sidebar.markdown("---")
        st.sidebar.subheader("🛠️ Admin Panel")
        with st.sidebar.expander("📋 Lihat Data Password Member"):
            st.json(st.session_state.user_database)

    # PEMBAGIAN MENU TAB
    tab_input, tab_progress = st.tabs(["🏋️ Latihan Hari Ini", "📊 Progress Latihan"])

    # ==================== TAB 1: INPUT LATIHAN ====================
    with tab_input:
        hari_index = datetime.datetime.now().weekday()
        nama_hari_indonesia = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"][hari_index]
        st.subheader(f"📆 Hari Ini: {nama_hari_indonesia}")

        is_rest_day = False
        
        if nama_hari_indonesia == "Selasa":
            hari_rara = "Hari 2 – Back + Biceps"
            hari_admin = "Hari 2 – Back + Biceps"  
            hari_member_umum = "Hari 1 – Back + Biceps"
            info_rara = "📌 **Hari Selasa:** Jadwal Anda **Hari 2 (Back + Biceps)**."
            info_admin = "📌 **Hari Selasa:** Jadwal Admin **Hari 2 (Back + Biceps)**."
            info_umum = "📌 **Hari Selasa:** Jadwal Member **Hari 1 (Back + Biceps)**."
        elif nama_hari_indonesia == "Rabu":
            hari_rara = "Hari 3 – Leg"
            hari_admin = "REST"
            hari_member_umum = "Hari 2 – Chest + Triceps"
            info_rara = "📌 **Hari Rabu:** Jadwal Anda **Hari 3 (Leg)**."
            info_admin = "📌 **Hari Rabu:** Jadwal Anda hari ini adalah **REST / Istirahat**."
            info_umum = "📌 **Hari Rabu:** Jadwal Member **Hari 2 (Chest + Triceps)**."
            if st.session_state.user_role == "admin":
                is_rest_day = True
        else:
            hari_rara = "Hari 1 – Chest + Leg + Triceps"
            hari_admin = "Hari 1 – Chest + Triceps"
            hari_member_umum = "Hari 2 – Chest + Triceps"
            info_rara = f"📌 **Hari {nama_hari_indonesia}:** Menggunakan pengaturan jadwal harian reguler."
            info_admin = f"📌 **Hari {nama_hari_indonesia}:** Menggunakan pengaturan jadwal harian reguler."
            info_umum = f"📌 **Hari {nama_hari_indonesia}:** Menggunakan pengaturan jadwal harian reguler."

        if is_rest_day:
            st.info(info_admin)
            st.success("🧘‍♂️ Hari ini jadwalnya **REST/Istirahat**! Pulihkan otot Anda dengan baik.")
        else:
            if st.session_state.user_id == "Rara":
                st.info(info_rara)
                jadwal_aktif = st.session_state.jadwal_gym_rara
                pilihan_menu = st.selectbox("Jadwal Latihan Anda Hari Ini:", [hari_rara], disabled=True)
            elif st.session_state.user_role == "admin":
                st.info(info_admin)
                jadwal_aktif = st.session_state.jadwal_gym_admin
                pilihan_menu = st.selectbox("Jadwal Latihan Admin Hari Ini:", [hari_admin], disabled=True)
            else:
                st.info(info_umum)
                jadwal_aktif = st.session_state.jadwal_gym_member_umum
                pilihan_menu = st.selectbox("Jadwal Latihan Anda Hari Ini:", [hari_member_umum], disabled=True)

            # 1. Pilih Gerakan Utama dari Jadwal yang Sudah Ditentukan
            daftar_gerakan_default = [g["nama"] for g in jadwal_aktif[pilihan_menu]]
            gerakan_utama_dipilih = st.selectbox("Pilih Gerakan Target Utama:", daftar_gerakan_default)
            
            # Ambil target bawaan (set x reps) gerakan utama
            target_bawaan = next(g["target"] for g in jadwal_aktif[pilihan_menu] if g["nama"] == gerakan_utama_dipilih)

            # 2. SISTEM REKOMENDASI GERAKAN ALTERNATIF OTOMATIS
            # Cari apakah gerakan utama tersebut memiliki variasi di kamus sistem
            opsi_rekomendasi_sistem = KAMUS_GERAKAN_ALTERNATIF.get(gerakan_utama_dipilih, [])
            
            gerakan_pilihan_final = gerakan_utama_dipilih
            
            if opsi_rekomendasi_sistem:
                gunakan_variasi = st.checkbox("🔄 Gunakan Rekomendasi Gerakan Alternatif (Alat Penuh / Bosan)")
                if gunakan_variasi:
                    # Sistem menyajikan pilihan alternatif khusus untuk melatih otot yang sama
                    gerakan_pilihan_final = st.selectbox(
                        "Sistem merekomendasikan gerakan alternatif berikut (Target Otot Sama):",
                        opsi_rekomendasi_sistem
                    )
                    target_bawaan = f"{target_bawaan.split(' ')[0]} × 10-12 (Variasi Otot)"

            st.success(f"🎯 Gerakan Aktif: **{gerakan_pilihan_final}** | Target Panduan: **{target_bawaan}**")

            # --- ENGINE PROGRESSIVE OVERLOAD ---
            beban_dasar_minggu_ini = 0.0
            info_progres = "Sesi pertama untuk gerakan ini. Mulai dengan beban yang aman."
            
            if not df_logs.empty:
                user_logs = df_logs[(df_logs["Username"] == st.session_state.user_id) & (df_logs["Gerakan"] == gerakan_pilihan_final)].copy()
                if not user_logs.empty:
                    hari_ini_tgl = datetime.date.today()
                    logs_sesi_lalu = user_logs[user_logs["Tanggal"].dt.date < hari_ini_tgl]
                    if not logs_sesi_lalu.empty:
                        tgl_terakhir = logs_sesi_lalu["Tanggal"].max()
                        sesi_terakhir = logs_sesi_lalu[logs_sesi_lalu["Tanggal"] == tgl_terakhir]
                        beban_maks_minggu_lalu = sesi_terakhir["Beban_kg"].max()
                        beban_dasar_minggu_ini = beban_maks_minggu_lalu + 2.5
                        info_progres = f"📈 Progres: Target beban dasar naik: **{beban_dasar_minggu_ini}kg** (+2.5kg dari beban tertinggi sesi sebelumnya)."
                    else:
                        beban_dasar_minggu_ini = user_logs["Beban_kg"].min()
                        info_progres = "Melanjutkan sesi latihan hari ini."

            st.markdown(f"💡 *{info_progres}*")

            # --- FORM ENTRI INPUT SET ---
            with st.form("log_latihan_form"):
                set_ke = st.number_input("Set Ke-", min_value=1, max_value=6, step=1)
                rekomendasi_beban = beban_dasar_minggu_ini + ((set_ke - 1) * 2.5)
                
                berat = st.number_input("Beban Latihan Realisasi (kg)", min_value=0.0, value=float(rekomendasi_beban), step=2.5)
                reps = st.number_input("Repetisi Berhasil", min_value=0, step=1)
                submit_log = st.form_submit_button("💾 Simpan Set Ini")
                
                if submit_log:
                    new_log = pd.DataFrame([{
                        "Tanggal": pd.to_datetime(datetime.date.today()),
                        "Username": st.session_state.user_id,
                        "Gerakan": gerakan_pilihan_final,
                        "Set_Ke": int(set_ke),
                        "Beban_kg": float(berat),
                        "Reps": int(reps)
                    }])
                    df_updated = pd.concat([df_logs, new_log], ignore_index=True)
                    
                    if save_data_to_github(df_updated, file_sha):
                        st.success(f"Set {set_ke} untuk gerakan '{gerakan_pilihan_final}' berhasil disimpan!")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("Gagal menyimpan ke database Cloud. Cek koneksi internet Anda.")

        # --- MONITORING CATATAN HARI INI ---
        st.write("---")
        st.subheader("📋 Catatan Latihan Anda Hari Ini")
        df_hari_ini = pd.DataFrame()
        if not df_logs.empty:
            df_hari_ini = df_logs[(df_logs["Username"] == st.session_state.user_id) & (df_logs["Tanggal"].dt.date == datetime.date.today())]
        
        if not df_hari_ini.empty:
            st.dataframe(df_hari_ini[["Gerakan", "Set_Ke", "Beban_kg", "Reps"]].reset_index(drop=True), use_container_width=True)
            st.balloons()
            st.success("🎉 **YEAY! LATIHAN SELESAI!** 💪")
        else:
            st.caption("Belum ada set yang disimpan hari ini.")

    # ==================== TAB 2: PROGRESS LATIHAN ====================
    with tab_progress:
        st.subheader("📊 Analisis & Riwayat Progress")
        df_user_all = pd.DataFrame()
        if not df_logs.empty:
            df_user_all = df_logs[df_logs["Username"] == st.session_state.user_id].copy()
        
        if df_user_all.empty:
            st.info("Belum ada riwayat latihan.")
        else:
            df_user_all["Bulan"] = df_user_all["Tanggal"].dt.strftime("%Y-%m (%B)")
            df_user_all["Tanggal_Saja"] = df_user_all["Tanggal"].dt.date
            
            total_hari_latihan = df_user_all["Tanggal_Saja"].nunique()
            total_set_diangkat = len(df_user_all)
            
            col1, col2 = st.columns(2)
            col1.metric("📆 Total Hari Latihan", f"{total_hari_latihan} Hari")
            col2.metric("🏋️ Total Set Diselesaikan", f"{total_set_diangkat} Set")
            
            st.write("---")
            mode_view = st.radio("Pilih Mode Riwayat:", ["Per Bulan", "Per Hari Spesifik", "Grafik Tren Beban (Overload)"], horizontal=True)
            
            if mode_view == "Per Bulan":
                st.markdown("### 📅 Riwayat Latihan Bulanan")
                pilihan_bulan = st.selectbox("Pilih Bulan Latihan:", df_user_all["Bulan"].unique())
                df_bulanan = df_user_all[df_user_all["Bulan"] == pilihan_bulan]
                df_summary_bulan = df_bulanan.groupby(["Tanggal_Saja", "Gerakan"]).agg(
                    Total_Set=("Set_Ke", "count"),
                    Beban_Maksimal_kg=("Beban_kg", "max"),
                    Reps_Maksimal=("Reps", "max")
                ).reset_index()
                df_summary_bulan.columns = ["Tanggal", "Nama Gerakan", "Jumlah Set", "Beban Tertinggi (kg)", "Reps Tertinggi"]
                st.dataframe(df_summary_bulan.sort_values(by="Tanggal", ascending=False), use_container_width=True)
                
            elif mode_view == "Per Hari Spesifik":
                st.markdown("### 📆 Riwayat Detil Harian")
                daftar_tanggal = sorted(df_user_all["Tanggal_Saja"].unique(), reverse=True)
                pilihan_tanggal = st.selectbox("Pilih Tanggal Latihan:", daftar_tanggal)
                df_harian = df_user_all[df_user_all["Tanggal_Saja"] == pilihan_tanggal]
                st.dataframe(df_harian[["Gerakan", "Set_Ke", "Beban_kg", "Reps"]].reset_index(drop=True), use_container_width=True)
                
            elif mode_view == "Grafik Tren Beban (Overload)":
                st.markdown("### 📈 Grafik Kenaikan Beban (*Progressive Overload*)")
                daftar_gerakan_user = df_user_all["Gerakan"].unique()
                gerakan_dipilih = st.selectbox("Pilih Gerakan yang Ingin Dilihat Trennya:", daftar_gerakan_user)
                
                df_tren = df_user_all[df_user_all["Gerakan"] == gerakan_dipilih]
                df_chart = df_tren.groupby("Tanggal_Saja")["Beban_kg"].max().reset_index()
                df_chart.columns = ["Tanggal", "Beban Maksimal (kg)"]
                df_chart = df_chart.set_index("Tanggal")
                
                st.line_chart(df_chart, y="Beban Maksimal (kg)")
