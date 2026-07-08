import streamlit as st
import pandas as pd
import datetime
import os
import requests
import base64
import random
import time  # Melacak durasi login otomatis 12 jam di latar belakang
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

# Tempat penyimpanan alur pengajuan reset password
if "reset_requests" not in st.session_state:
    st.session_state.reset_requests = {}

# State navigasi untuk memisahkan halaman login dan halaman reset password
if "halaman_akses" not in st.session_state:
    st.session_state.halaman_akses = "login"

# --- 4. DATABASE REKOMENDASI GERAKAN ALTERNATIF (SISTEM) ---
KAMUS_GERAKAN_ALTERNATIF = {
    "Barbell Bench Press": ["Dumbbell Bench Press", "Smith Machine Bench Press", "Chest Press Machine"],
    "Incline Dumbbell Press": ["Incline Barbell Press", "Incline Smith Machine Press", "Incline Chest Press Machine"],
    "Chest Press Machine": ["Hammer Strength Chest Press", "Push Up (Weighted)", "Floor Press"],
    "Cable Fly": ["Pec Deck Fly", "Dumbbell Fly", "Low-to-High Cable Fly"],
    "Pec Deck Fly": ["Cable Fly", "Dumbbell Fly"],
    "Pull Up / Lat Pulldown": ["Assisted Pull Up", "Wide Grip Lat Pulldown", "Close Grip Lat Pulldown"],
    "Barbell Row": ["Pendlay Row", "T-Bar Row", "Smith Machine Row"],
    "Seated Cable Row": ["Chest Supported Row", "Dumbbell Row", "Machine Row"],
    "Straight Arm Pulldown": ["Cable Pullover", "Dumbbell Pullover"],
    "Single Arm Dumbbell Row": ["Single Arm Cable Row", "Meadows Row"],
    "Chest Supported Row": ["Seated Cable Row", "T-Bar Row"],
    "Face Pull": ["Rear Delt Fly Machine", "Bent Over Dumbbell Lateral Raise", "Rope Face Pull (High Custom)"],
    "Dumbbell Shoulder Press": ["Military Press Barbell", "Smith Machine Shoulder Press", "Machine Shoulder Press"],
    "Lateral Raise": ["Cable Lateral Raise", "Machine Lateral Raise", "Dumbbell Lean-Away Lateral Raise"],
    "Rear Delt Fly": ["Face Pull", "Reverse Pec Deck"],
    "Rope Pushdown": ["Straight Bar Pushdown", "V-Bar Pushdown", "Triceps Pushdown Machine"],
    "Overhead Cable Triceps Extension": ["Overhead Dumbbell Extension", "Skull Crusher", "EZ Bar Overhead Extension"],
    "Close Grip Bench Press": ["Dips", "Diamond Push Up", "Close Grip Smith Machine Press"],
    "Overhead Dumbbell Triceps Extension": ["Overhead Cable Triceps Extension", "Skull Crusher"],
    "EZ Bar Curl": ["Barbell Curl", "Cable Curl", "Spider Curl"],
    "Incline Dumbbell Curl": ["Dumbbell Biceps Curl", "Preacher Curl", "Concentration Curl"],
    "Hammer Curl": ["Cable Hammer Curl", "Rope Hammer Curl", "Dumbbell Cross Body Hammer Curl"],
    "Barbell Curl": ["EZ Bar Curl", "Dumbbell Curl", "Cable Curl"],
    "Preacher Curl": ["Machine Preacher Curl", "Incline Dumbbell Curl"],
    "Cable Curl": ["EZ Bar Biceps Curl", "Dumbbell Curl"],
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
    "Hanging Leg Raise": ["Captain's Chair Leg Raise", "Lying Leg Raise", "V-Ups"],
    "Hanging Leg Raise / Cable Crunch": ["Cable Crunch", "Hanging Leg Raise", "Ab Wheel Rollout"]
}

KAMUS_INDUK = {v: induk for induk, variasi_list in KAMUS_GERAKAN_ALTERNATIF.items() for v in variasi_list}

# --- 5. INITIALIZE JADWAL GYM ---
if "jadwal_gym_admin" not in st.session_state:
    st.session_state.jadwal_gym_admin = {
        "Hari 1 – Chest + Triceps": [{"nama": "Barbell Bench Press", "target": "4 × 8"}, {"nama": "Incline Dumbbell Press", "target": "4 × 10"}, {"nama": "Chest Press Machine", "target": "3 × 12"}, {"nama": "Cable Fly", "target": "3 × 12"}, {"nama": "Pec Deck Fly", "target": "3 × 15"}, {"nama": "Rope Pushdown", "target": "3 × 15"}, {"nama": "Overhead Cable Triceps Extension", "target": "3 × 12"}, {"nama": "Dips / Assisted Dips", "target": "3 × Max"}],
        "Hari 2 – Back + Biceps": [{"nama": "Pull Up / Lat Pulldown", "target": "4 × 10"}, {"nama": "Barbell Row", "target": "4 × 8"}, {"nama": "Seated Cable Row", "target": "3 × 10"}, {"nama": "Single Arm Dumbbell Row", "target": "3 × 10"}, {"nama": "Face Pull", "target": "3 × 15"}, {"nama": "EZ Bar Curl", "target": "3 × 10"}, {"nama": "Incline Dumbbell Curl", "target": "3 × 12"}, {"nama": "Hammer Curl", "target": "3 × 12"}],
        "Hari 3 – Upper Body + Arms": [{"nama": "Incline Smith Machine Press", "target": "4 × 10"}, {"nama": "Chest Supported Row", "target": "4 × 10"}, {"nama": "Dumbbell Shoulder Press", "target": "3 × 10"}, {"nama": "Lateral Raise", "target": "4 × 15"}, {"nama": "Rear Delt Fly", "target": "3 × 15"}, {"nama": "Cable Fly", "target": "3 × 12"}, {"nama": "Close Grip Bench Press", "target": "4 × 10"}, {"nama": "Preacher Curl", "target": "3 × 10"}, {"nama": "Rope Pushdown", "target": "3 × 15"}, {"nama": "Cable Curl", "target": "3 × 12"}],
        "Hari 4 – Full Lower Body": [{"nama": "Back Squat", "target": "4 × 8"}, {"nama": "Romanian Deadlift", "target": "4 × 8"}, {"nama": "Leg Press", "target": "3 × 12"}, {"nama": "Walking Lunges", "target": "3 × 12/kaki"}, {"nama": "Leg Extension", "target": "3 × 15"}, {"nama": "Seated Leg Curl", "target": "3 × 15"}, {"nama": "Hip Thrust", "target": "4 × 10"}, {"nama": "Standing Calf Raise", "target": "4 × 15"}, {"nama": "Seated Calf Raise", "target": "4 × 20"}, {"nama": "Hanging Leg Raise / Cable Crunch", "target": "3 × 15"}]
    }

if "jadwal_gym_rara" not in st.session_state:
    st.session_state.jadwal_gym_rara = {
        "Hari 1 – Chest + Leg + Triceps": [{"nama": "Barbell Bench Press", "target": "4 × 8"}, {"nama": "Incline Dumbbell Press", "target": "4 × 10"}, {"nama": "Chest Press Machine", "target": "3 × 12"}, {"nama": "Cable Fly", "target": "3 × 12"}, {"nama": "Back Squat", "target": "4 × 8"}, {"nama": "Leg Press", "target": "3 × 10"}, {"nama": "Leg Extension", "target": "3 × 12"}, {"nama": "Rope Pushdown", "target": "3 × 15"}, {"nama": "Overhead Cable Triceps Extension", "target": "3 × 12"}],
        "Hari 2 – Back + Biceps": [{"nama": "Pull Up / Lat Pulldown", "target": "4 × 10"}, {"nama": "Barbell Row", "target": "4 × 8"}, {"nama": "Seated Cable Row", "target": "3 × 10"}, {"nama": "Straight Arm Pulldown", "target": "3 × 12"}, {"nama": "Face Pull", "target": "3 × 15"}, {"nama": "EZ Bar Curl", "target": "3 × 10"}, {"nama": "Incline Dumbbell Curl", "target": "3 × 12"}, {"nama": "Hammer Curl", "target": "3 × 12"}],
        "Hari 3 – Leg": [{"nama": "Romanian Deadlift", "target": "4 × 8"}, {"nama": "Bulgarian Split Squat", "target": "3 × 10/kaki"}, {"nama": "Walking Lunges", "target": "3 × 12/kaki"}, {"nama": "Leg Curl", "target": "3 × 12"}, {"nama": "Hip Thrust", "target": "4 × 10"}, {"nama": "Standing Calf Raise", "target": "4 × 15"}, {"nama": "Seated Calf Raise", "target": "4 × 20"}],
        "Hari 4 – Full Arms": [{"nama": "Close Grip Bench Press", "target": "4 × 10"}, {"nama": "Rope Pushdown", "target": "3 × 15"}, {"nama": "Overhead Dumbbell Triceps Extension", "target": "3 × 12"}, {"nama": "Barbell Curl", "target": "3 × 10"}, {"nama": "Preacher Curl", "target": "3 × 10"}, {"nama": "Hammer Curl", "target": "3 × 12"}, {"nama": "Wrist Curl", "target": "3 × 15"}, {"nama": "Reverse Wrist Curl", "target": "3 × 15"}],
        "Hari 5 – Full Lower Body": [{"nama": "Front Squat", "target": "4 × 10"}, {"nama": "Romanian Deadlift", "target": "4 × 8"}, {"nama": "Leg Press", "target": "3 × 12"}, {"nama": "Leg Extension", "target": "3 × 15"}, {"nama": "Seated Leg Curl", "target": "3 × 15"}, {"nama": "Hip Thrust", "target": "4 × 10"}, {"nama": "Walking Lunges", "target": "3 × 12/kaki"}, {"nama": "Standing Calf Raise", "target": "4 × 15"}, {"nama": "Seated Calf Raise", "target": "4 × 20"}, {"nama": "Hanging Leg Raise", "target": "3 × 15"}]
    }

if "jadwal_gym_member_umum" not in st.session_state:
    st.session_state.jadwal_gym_member_umum = {
        "Hari 1 – Back + Biceps": [{"nama": "Pull Up / Lat Pulldown", "target": "4 × 10"}, {"nama": "Barbell Row", "target": "4 × 8"}, {"nama": "Chest Supported Row", "target": "3 × 10"}, {"nama": "Seated Cable Row", "target": "3 × 12"}, {"nama": "Straight Arm Pulldown", "target": "3 × 12"}, {"nama": "Face Pull", "target": "3 × 15"}, {"nama": "EZ Bar Curl", "target": "3 × 10"}, {"nama": "Incline Dumbbell Curl", "target": "3 × 12"}, {"nama": "Hammer Curl", "target": "3 × 12"}],
        "Hari 2 – Chest + Triceps": [{"nama": "Barbell Bench Press", "target": "4 × 8"}, {"nama": "Incline Dumbbell Press", "target": "4 × 10"}, {"nama": "Chest Press Machine", "target": "3 × 12"}, {"nama": "Pec Deck Fly", "target": "3 × 15"}, {"nama": "Cable Fly", "target": "3 × 12"}, {"nama": "Dips / Assisted Dips", "target": "3 × Max"}, {"nama": "Rope Pushdown", "target": "3 × 15"}, {"nama": "Overhead Cable Triceps Extension", "target": "3 × 12"}],
        "Hari 3 – Upper Body + Arms": [{"nama": "Incline Smith Machine Press", "target": "4 × 10"}, {"nama": "Chest Supported Row", "target": "4 × 10"}, {"nama": "Dumbbell Shoulder Press", "target": "3 × 10"}, {"nama": "Lateral Raise", "target": "4 × 15"}, {"nama": "Rear Delt Fly", "target": "3 × 15"}, {"nama": "Close Grip Bench Press", "target": "4 × 10"}, {"nama": "Cable Curl", "target": "3 × 12"}, {"nama": "Preacher Curl", "target": "3 × 10"}, {"nama": "Rope Pushdown", "target": "3 × 15"}, {"nama": "Overhead Dumbbell Triceps Extension", "target": "3 × 12"}],
        "Hari 4 – Full Lower Body": [{"nama": "Back Squat", "target": "4 × 8"}, {"nama": "Romanian Deadlift", "target": "4 × 8"}, {"nama": "Leg Press", "target": "3 × 12"}, {"nama": "Bulgarian Split Squat", "target": "3 × 10/kaki"}, {"nama": "Leg Extension", "target": "3 × 15"}, {"nama": "Seated Leg Curl", "target": "3 × 15"}, {"nama": "Hip Thrust", "target": "4 × 10"}, {"nama": "Standing Calf Raise", "target": "4 × 15"}, {"nama": "Seated Calf Raise", "target": "4 × 20"}, {"nama": "Hanging Leg Raise / Cable Crunch", "target": "3 × 15"}]
    }

# --- 6. INITIALIZE STATUS LOGIN & FITUR EXPIRATION (OTOMATIS 12 JAM) ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.user_role = None
    st.session_state.user_nama = None
    st.session_state.login_timestamp = None

# Proteksi Otomatis: 12 Jam = 12 * 3600 detik = 43200 detik
if st.session_state.logged_in:
    waktu_sekarang = time.time()
    durasi_aktif = waktu_sekarang - st.session_state.login_timestamp
    if durasi_aktif > 43200:  
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.user_role = None
        st.session_state.user_nama = None
        st.session_state.login_timestamp = None
        st.warning("⚠️ Sesi login 12 jam Anda telah berakhir demi keamanan. Silakan masuk kembali.")

# --- 7. INTERFACE SEBELUM LOGIN & LAMAN RESET PASSWORD ---
if not st.session_state.logged_in:
    st.title("🏋️‍♂️ Gym Private Member Portal")
    
    # KONDISI 1: HALAMAN LOGIN UTAMA
    if st.session_state.halaman_akses == "login":
        username_input = st.text_input("Username").strip()
        password_input = st.text_input("Password", type="password").strip()
        
        # Penataan Tombol Masuk & Tombol Lupa Password Berdampingan
        col_btn1, col_btn2 = st.columns([1, 4])
        with col_btn1:
            submit_login = st.button("Masuk 🔓")
        with col_btn2:
            go_to_reset = st.button("Lupa Password? 🔐")
            
        if submit_login:
            db = st.session_state.user_database
            if username_input in db:
                if password_input == db[username_input]["password"] or password_input == MASTER_PASSWORD:
                    st.session_state.logged_in = True
                    st.session_state.user_id = username_input
                    st.session_state.user_role = db[username_input]["role"]
                    st.session_state.user_nama = db[username_input]["nama"]
                    st.session_state.login_timestamp = time.time()  # Waktu mulai login dicatat otomatis
                    st.rerun()
                else: 
                    st.error("❌ Password salah.")
            else: 
                st.error("❌ Username tidak terdaftar.")
            
        if go_to_reset:
            st.session_state.halaman_akses = "reset_page"
            st.rerun()
            
    # KONDISI 2: DIALIHKAN KE LAMAN RESET PASSWORD
    elif st.session_state.halaman_akses == "reset_page":
        st.markdown("### 🔑 Laman Reset Password Member")
        st.caption("Silakan isi password baru Anda terlebih dahulu, kemudian kirimkan kode verifikasi pengajuan ke Admin.")
        
        username_reset = st.text_input("Masukkan Username Anda:").strip()
        password_baru = st.text_input("Masukkan Password Baru:", type="password")
        
        if st.button("🔴 Ajukan Perubahan & Kirim Kode ke Admin"):
            if username_reset in st.session_state.user_database:
                if password_baru.strip() == "":
                    st.error("❌ Password baru tidak boleh kosong.")
                else:
                    kode_acak = str(random.randint(100000, 999999))
                    st.session_state.reset_requests[username_reset] = {
                        "code": kode_acak,
                        "new_password": password_baru,
                        "approved": False
                    }
                    st.success(f"✅ Password baru tersimpan sementara! Kode Otorisasi `{kode_acak}` telah dikirimkan ke Admin. Silakan hubungi Owner Gym (Ardi) untuk menyetujui.")
            else:
                st.error("❌ Username tidak ditemukan.")
                
        st.write("---")
        
        if username_reset in st.session_state.reset_requests:
            req_data = st.session_state.reset_requests[username_reset]
            if req_data["approved"]:
                st.session_state.user_database[username_reset]["password"] = req_data["new_password"]
                del st.session_state.reset_requests[username_reset] 
                st.success("🎉 Otorisasi Admin Berhasil! Password Anda telah diperbarui.")
                st.session_state.halaman_akses = "login"
                st.info("Kembali ke halaman login...")
                st.button("Klik untuk Masuk Kembali")
                st.rerun()
            else:
                st.info("⏳ Menunggu Otorisasi Admin... Tekan tombol di bawah untuk menyegarkan status jika Admin sudah klik setuju.")
                if st.button("🔄 Cek Status Otorisasi"):
                    st.rerun()
                    
        if st.button("⬅️ Batalkan & Kembali ke Login"):
            st.session_state.halaman_akses = "login"
            st.rerun()

# --- 8. INTERFACE SETELAH LOGIN ---
else:
    st.title("🏋️‍♂️ Universal Gym Tracker Portal")
    st.markdown(f"### 🎉 Halo **{st.session_state.user_nama}**")
    st.markdown("##### *Semangat Latihan ya hari ini!* 🔥")
    
    # [Perubahan]: Teks keterangan sisa waktu masa sesi aktif di sini telah dihapus sesuai request
        
    st.write("---")

    # === PANEL SIDEBAR KIRI ===
    st.sidebar.markdown(f"👤 **Pengguna:** {st.session_state.user_nama}")
    st.sidebar.markdown(f"🔰 **Akses:** `{st.session_state.user_role.upper()}`")
    
    if st.session_state.user_role == "admin":
        st.sidebar.write("---")
        st.sidebar.markdown("👥 **Daftar Seluruh Member & Password:**")
        for usr_id, detail in st.session_state.user_database.items():
            role_badge = "👑 Admin" if detail["role"] == "admin" else "🏃 Member"
            st.sidebar.text(f"• {detail['nama']} ({usr_id})\n  🔑 Pass: {detail['password']}\n  [{role_badge}]")
            
        if st.session_state.reset_requests:
            st.sidebar.write("---")
            st.sidebar.warning("🚨 **Otorisasi Reset Password:**")
            for u_target, data_r in list(st.session_state.reset_requests.items()):
                if not data_r["approved"]:
                    st.sidebar.write(f"Member: **{u_target}**")
                    st.sidebar.info(f"Kode Pengajuan: `{data_r['code']}`")
                    if st.sidebar.button(f"Selesaikan Otorisasi {u_target}"):
                        st.session_state.reset_requests[u_target]["approved"] = True
                        st.sidebar.success(f"Akses diberikan untuk {u_target}!")
                        st.rerun()

    st.sidebar.write("---")
    with st.sidebar.expander("🔐 Ganti Password Mandiri"):
        with st.form("change_password_form"):
            pass_lama = st.text_input("Password Lama", type="password")
            pass_baru_self = st.text_input("Password Baru", type="password")
            submit_ganti = st.form_submit_button("Simpan Password")
            
            if submit_ganti:
                real_pass = st.session_state.user_database[st.session_state.user_id]["password"]
                if pass_lama == real_pass:
                    st.session_state.user_database[st.session_state.user_id]["password"] = pass_baru_self
                    st.success("✅ Password berhasil diubah!")
                else:
                    st.error("❌ Password lama salah.")
                    
    st.sidebar.write("---")
    if st.sidebar.button("Keluar / Logout 🚪"):
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.user_role = None
        st.session_state.user_nama = None
        st.session_state.login_timestamp = None
        st.rerun()

    tab_input, tab_progress = st.tabs(
