import streamlit as st
import pandas as pd
import datetime
import os
import requests
import base64
import random
import time  # Ditambahkan untuk pelacakan durasi login otomatis 12 jam
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

# --- 6. INITIALIZE STATUS LOGIN & FITUR EXPIRATION (12 JAM) ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.user_role = None
    st.session_state.user_nama = None
    st.session_state.login_timestamp = None
    st.session_state.tetap_login = False

# Sistem Cek Durasi Otomatis (Jika opsi "Tetap Login" dicentang)
# 12 Jam = 12 * 3600 detik = 43200 detik
if st.session_state.logged_in and st.session_state.tetap_login:
    waktu_sekarang = time.time()
    durasi_aktif = waktu_sekarang - st.session_state.login_timestamp
    if durasi_aktif > 43200:  
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.user_role = None
        st.session_state.user_nama = None
        st.session_state.login_timestamp = None
        st.session_state.tetap_login = False
        st.warning("⚠️ Sesi login 12 jam Anda telah berakhir. Silakan masuk kembali.")

# --- 7. INTERFACE SEBELUM LOGIN & LAMAN RESET PASSWORD ---
if not st.session_state.logged_in:
    st.title("🏋️‍♂️ Gym Private Member Portal")
    
    # KONDISI 1: HALAMAN LOGIN UTAMA
    if st.session_state.halaman_akses == "login":
        username_input = st.text_input("Username").strip()
        password_input = st.text_input("Password", type="password").strip()
        
        # Penambahan opsi "Tetap login di perangkat ini"
        tetap_login_checkbox = st.checkbox("Tetap login di perangkat ini (Maks. 12 Jam)")
        
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
                    st.session_state.login_timestamp = time.time()  # Simpan waktu masuk
                    st.session_state.tetap_login = tetap_login_checkbox # Simpan preferensi pengguna
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
                    # Buat kode acak 6 digit dan amankan data password baru sementara
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
        
        # Mengecek status otorisasi real-time
        if username_reset in st.session_state.reset_requests:
            req_data = st.session_state.reset_requests[username_reset]
            if req_data["approved"]:
                # Eksekusi pembaruan database jika admin telah menyetujui
                st.session_state.user_database[username_reset]["password"] = req_data["new_password"]
                del st.session_state.reset_requests[username_reset] # bersihkan antrean
                st.success("🎉 Otorisasi Admin Berhasil! Password Anda telah diperbarui.")
                
                # Alihkan kembali ke laman login utama secara otomatis
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
    
    # Tampilkan info durasi sisa waktu jika opsi "tetap login" aktif
    if st.session_state.tetap_login:
        sisa_waktu_detik = 43200 - (time.time() - st.session_state.login_timestamp)
        sisa_jam = int(sisa_waktu_detik // 3600)
        sisa_menit = int((sisa_waktu_detik % 3600) // 60)
        st.caption(f"⏳ Sesi simpan login aktif. Anda akan log out otomatis dalam: `{sisa_jam} jam {sisa_menit} menit`.")
        
    st.write("---")

    # === PANEL SIDEBAR KIRI ===
    st.sidebar.markdown(f"👤 **Pengguna:** {st.session_state.user_nama}")
    st.sidebar.markdown(f"🔰 **Akses:** `{st.session_state.user_role.upper()}`")
    
    # KONDISI KHUSUS ADMIN: MELIHAT DAFTAR SELURUH MEMBER BESERTA PASSWORD MEREKA
    if st.session_state.user_role == "admin":
        st.sidebar.write("---")
        st.sidebar.markdown("👥 **Daftar Seluruh Member & Password:**")
        for usr_id, detail in st.session_state.user_database.items():
            role_badge = "👑 Admin" if detail["role"] == "admin" else "🏃 Member"
            st.sidebar.text(f"• {detail['nama']} ({usr_id})\n  🔑 Pass: {detail['password']}\n  [{role_badge}]")
            
        # OTORISASI PERMINTAAN RESET PASSWORD YANG DIAJUKAN MEMBER
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

    # MENU GANTI PASSWORD MANDIRI UNTUK SEMUA USER (MEMBER & ADMIN)
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
        st.session_state.tetap_login = False
        st.rerun()

    tab_input, tab_progress = st.tabs(["🏋️ Latihan Hari Ini", "📊 Progress Latihan"])

    # ==================== TAB 1: INPUT LATIHAN ====================
    with tab_input:
        hari_index = datetime.datetime.now().weekday()
        nama_hari_indonesia = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"][hari_index]
        st.subheader(f"📆 Hari Ini: {nama_hari_indonesia}")

        is_rest_day = False
        if nama_hari_indonesia == "Selasa":
            hari_rara = "Hari 2 – Back + Biceps"; hari_admin = "Hari 2 – Back + Biceps"; hari_member_umum = "Hari 1 – Back + Biceps"
        elif nama_hari_indonesia == "Rabu":
            hari_rara = "Hari 3 – Leg"; hari_admin = "REST"; hari_member_umum = "Hari 2 – Chest + Triceps"
            if st.session_state.user_role == "admin": 
                is_rest_day = True
        else:
            hari_rara = "Hari 1 – Chest + Leg + Triceps"; hari_admin = "Hari 1 – Chest + Triceps"; hari_member_umum = "Hari 2 – Chest + Triceps"

        if is_rest_day:
            st.success("🧘‍♂️ Hari ini jadwalnya **REST/Istirahat**! Pulihkan otot Anda dengan baik.")
        else:
            if st.session_state.user_id == "Rara":
                jadwal_aktif = st.session_state.jadwal_gym_rara
                pilihan_menu = st.selectbox("Jadwal Latihan Anda Hari Ini:", [hari_rara], disabled=True)
            elif st.session_state.user_role == "admin":
                jadwal_aktif = st.session_state.jadwal_gym_admin
                pilihan_menu = st.selectbox("Jadwal Latihan Admin Hari Ini:", [hari_admin], disabled=True)
            else:
                jadwal_aktif = st.session_state.jadwal_gym_member_umum
                pilihan_menu = st.selectbox("Jadwal Latihan Anda Hari Ini:", [hari_member_umum], disabled=True)

            daftar_gerakan_default = [g["nama"] for g in jadwal_aktif[pilihan_menu]]
            
            variasi_minggu_lalu = {}
            if not df_logs.empty:
                tgl_7_hari_lalu = datetime.date.today() - datetime.timedelta(days=7)
                df_minggu_lalu = df_logs[(df_logs["Username"] == st.session_state.user_id) & (df_logs["Tanggal"].dt.date >= tgl_7_hari_lalu) & (df_logs["Tanggal"].dt.date < datetime.date.today())]
                if not df_minggu_lalu.empty:
                    for g in df_minggu_lalu["Gerakan"].unique():
                        if g in KAMUS_INDUK: 
                            variasi_minggu_lalu[KAMUS_INDUK[g]] = g

            gerakan_utama_dipilih = st.selectbox("Pilih Slot Gerakan Utama:", daftar_gerakan_default)
            target_bawaan = next(g["target"] for g in jadwal_aktif[pilihan_menu] if g["nama"] == gerakan_utama_dipilih)

            gerakan_pilihan_final = gerakan_utama_dipilih
            opsi_rekomendasi_sistem = KAMUS_GERAKAN_ALTERNATIF.get(gerakan_utama_dipilih, [])
            ada_variasi_minggu_lalu = gerakan_utama_dipilih in variasi_minggu_lalu
            
            if opsi_rekomendasi_sistem:
                label_checkbox = "🔄 Gunakan Rekomendasi Gerakan Alternatif"
                if ada_variasi_minggu_lalu: 
                    label_checkbox += " *(Otomatis aktif dari minggu lalu)*"
                gunakan_variasi = st.checkbox(label_checkbox, value=ada_variasi_minggu_lalu)
                if gunakan_variasi:
                    var_default = variasi_minggu_lalu.get(gerakan_utama_dipilih, opsi_rekomendasi_sistem[0])
                    idx_default = opsi_rekomendasi_sistem.index(var_default) if var_default in opsi_rekomendasi_sistem else 0
                    gerakan_pilihan_final = st.selectbox("Rekomendasi Alternatif (Target Otot Sama):", opsi_rekomendasi_sistem, index=idx_default)
                    target_bawaan = f"{target_bawaan.split(' ')[0]} × 10-12 (Variasi)"

            st.success(f"🎯 Gerakan Aktif: **{gerakan_pilihan_final}** | Target Panduan: **{target_bawaan}**")

            beban_set_sebelumnya_hari_ini = 0.0
            set_terakhir_tersimpan = 0
            if not df_logs.empty:
                df_hari_ini_user = df_logs[(df_logs["Username"] == st.session_state.user_id) & (df_logs["Tanggal"].dt.date == datetime.date.today()) & (df_logs["Gerakan"] == gerakan_pilihan_final)]
                if not df_hari_ini_user.empty:
                    set_terakhir_tersimpan = df_hari_ini_user["Set_Ke"].max()
                    beban_set_sebelumnya_hari_ini = df_hari_ini_user[df_hari_ini_user["Set_Ke"] == set_terakhir_tersimpan]["Beban_kg"].values[0]

            set_berikutnya = set_terakhir_tersimpan + 1

            with st.form("log_latihan_form"):
                st.markdown(f"#### 📝 Mengisi Data **Set Ke-{set_berikutnya}**")
                if set_berikutnya == 1:
                    st.caption("💡 Ini adalah Set Pertama Anda hari ini. Tentukan berat awal bebas.")
                    berat = st.number_input("Beban Latihan Realisasi (kg)", min_value=0.0, value=10.0, step=2.5)
                else:
                    st.warning(f"⚠️ **Overload Aktif**: Set {set_berikutnya} **WAJIB LEBIH BESAR** dari Set {set_terakhir_tersimpan} ({beban_set_sebelumnya_hari_ini} kg)!")
                    berat = st.number_input(f"Beban Latihan (Minimal {beban_set_sebelumnya_hari_ini + 2.5} kg)", min_value=0.0, value=float(beban_set_sebelumnya_hari_ini + 2.5), step=2.5)
                
                reps = st.number_input("Repetisi Berhasil", min_value=1, value=10, step=1)
                submit_log = st.form_submit_button(f"💾 Simpan Set {set_berikutnya}")
                
                if submit_log:
                    if set_berikutnya > 1 and berat <= beban_set_sebelumnya_hari_ini:
                        st.error(f"❌ Gagal! Beban wajib naik dibandingkan set sebelumnya ({beban_set_sebelumnya_hari_ini} kg)!")
                    else:
                        new_log = pd.DataFrame([{"Tanggal": pd.to_datetime(datetime.date.today()), "Username": st.session_state.user_id, "Gerakan": gerakan_pilihan_final, "Set_Ke": int(set_berikutnya), "Beban_kg": float(berat), "Reps": int(reps)}])
                        df_updated = pd.concat([df_logs, new_log], ignore_index=True)
                        if save_data_to_github(df_updated, file_sha):
                            st.success(f"Set {set_berikutnya} disimpan!")
                            st.cache_data.clear()
                            st.rerun()
                        else: 
                            st.error("Gagal menyimpan ke database cloud.")

        st.write("---")
        st.subheader("📋 Catatan Latihan Anda Hari Ini")
        df_hari_ini = pd.DataFrame()
        if not df_logs.empty:
            df_hari_ini = df_logs[(df_logs["Username"] == st.session_state.user_id) & (df_logs["Tanggal"].dt.date == datetime.date.today())]
        if not df_hari_ini.empty:
            st.dataframe(df_hari_ini[["Gerakan", "Set_Ke", "Beban_kg", "Reps"]].reset_index(drop=True), use_container_width=True)
        else: 
            st.caption("Belum ada set yang disimpan hari ini.")

    # ==================== TAB 2: PROGRESS LATIHAN ====================
    with tab_progress:
        st.subheader("📊 Analisis & Riwayat Progress Latihan")
        
        if st.session_state.user_role == "admin":
            st.info("🛠️ **Mode Admin**: Anda berhak meninjau info & seluruh data riwayat member.")
            daftar_member = list(st.session_state.user_database.keys())
            member_dipilih = st.selectbox("Pilih Member yang Ingin Dilihat Progresnya:", daftar_member, index=daftar_member.index(st.session_state.user_id))
            nama_tampilan = st.session_state.user_database[member_dipilih]["nama"]
            st.markdown(f"### 📈 Menampilkan Data Manajemen: **{nama_tampilan}** (`{member_dipilih}`)")
        else:
            member_dipilih = st.session_state.user_id
        
        df_user_all = pd.DataFrame()
        if not df_logs.empty:
            df_user_all = df_logs[df_logs["Username"] == member_dipilih].copy()
        
        if df_user_all.empty:
            st.warning("Belum ada riwayat latihan yang tercatat untuk pengguna ini.")
        else:
            df_user_all["Bulan"] = df_user_all["Tanggal"].dt.strftime("%Y-%m (%B)")
            df_user_all["Tanggal_Saja"] = df_user_all["Tanggal"].dt.date
            
            total_hari_latihan = df_user_all["Tanggal_Saja"].nunique()
            total_set_diangkat = len(df_user_all)
            
            col1, col2 = st.columns(2)
            col1.metric("📆 Total Hari Latihan", f"{total_hari_latihan} Hari")
            col2.metric("🏋️ Total Set Diselesaikan", f"{total_set_diangkat} Set")
            
            st.write("---")
            mode_view = st.radio("Pilih Mode Riwayat:", ["Per Bulan", "Per Hari Spesifik", "Grafik Tren Beban (Overload)", "Tabel Semua Data Mentah"], horizontal=True)
            
            if mode_view == "Per Bulan":
                st.markdown("### 📅 Riwayat Latihan Bulanan")
                pilihan_bulan = st.selectbox("Pilih Bulan Latihan:", df_user_all["Bulan"].unique())
                df_bulanan = df_user_all[df_user_all["Bulan"] == pilihan_bulan]
                df_summary_bulan = df_bulanan.groupby(["Tanggal_Saja", "Gerakan"]).agg(Total_Set=("Set_Ke", "count"), Beban_Maksimal_kg=("Beban_kg", "max"), Reps_Maksimal=("Reps", "max")).reset_index()
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
                st.line_chart(df_chart.set_index("Tanggal"), y="Beban Maksimal (kg)")
                
            elif mode_view == "Tabel Semua Data Mentah":
                st.markdown("### 📋 Log Seluruh Aktivitas Latihan")
                st.dataframe(df_user_all[["Tanggal_Saja", "Gerakan", "Set_Ke", "Beban_kg", "Reps"]].sort_values("Tanggal_Saja", ascending=False).reset_index(drop=True), use_container_width=True)
