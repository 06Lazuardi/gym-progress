import streamlit as st
import pandas as pd
import datetime
import os
import requests
import base64
import random
import time
import json
from io import StringIO

# --- 1. CONFIG HALAMAN MOBILE ---
st.set_page_config(page_title="Gym Member Portal", page_icon="🔒", layout="centered")

# --- 2. INTEGRASI GITHUB UNTUK PERSISTENSI DATA CSV ---
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = st.secrets["REPO_NAME"] 
LOG_FILE = "gym_workout_logs.csv"
USER_FILE = "users.json" # [TAMBAHAN: File untuk simpan user]
KOLOM_DATABASE = ["Tanggal", "Username", "Gerakan", "Set_Ke", "Beban_kg", "Reps"]
MASTER_PASSWORD = st.secrets.get("MASTER_PASSWORD", "superowner2026")

GITHUB_API_URL = f"https://api.github.com/repos/{REPO_NAME}/contents/{LOG_FILE}"
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}

@st.cache_data(ttl=5)
def load_data_from_github():
    try:
        # Load Logs
        resp_logs = requests.get(f"https://api.github.com/repos/{REPO_NAME}/contents/{LOG_FILE}", headers=HEADERS)
        df = pd.DataFrame(columns=KOLOM_DATABASE)
        sha_logs = None
        if resp_logs.status_code == 200:
            file_json = resp_logs.json()
            sha_logs = file_json["sha"]
            content = base64.b64decode(file_json["content"]).decode("utf-8")
            if content.strip():
                df = pd.read_csv(StringIO(content))
                df["Tanggal"] = pd.to_datetime(df["Tanggal"], errors='coerce')
        
        # Load Users
        resp_users = requests.get(f"https://api.github.com/repos/{REPO_NAME}/contents/{USER_FILE}", headers=HEADERS)
        users = None
        sha_users = None
        if resp_users.status_code == 200:
            file_json = resp_users.json()
            sha_users = file_json["sha"]
            users = json.loads(base64.b64decode(file_json["content"]).decode("utf-8"))
            
        return df, sha_logs, users, sha_users
    except Exception as e:
        return pd.DataFrame(columns=KOLOM_DATABASE), None, None, None

def save_to_github(file_path, content_str, sha=None, message="Update data"):
    content_b64 = base64.b64encode(content_str.encode("utf-8")).decode("utf-8")
    payload = {"message": message, "content": content_b64}
    if sha: payload["sha"] = sha
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{file_path}"
    response = requests.put(url, headers=HEADERS, json=payload)
    return response.status_code in [200, 201]

# Tarik data awal
df_logs, sha_logs, user_db_github, sha_users = load_data_from_github()

# --- FUNGSI TAMBAHAN: TRACKER HARI ---
def hitung_hari_latihan(tgl_mulai_str):
    try:
        tgl_mulai = datetime.datetime.strptime(tgl_mulai_str, "%Y-%m-%d").date()
        return (datetime.date.today() - tgl_mulai).days + 1
    except:
        return 1

# --- 3. DATABASE USER ---
if "user_database" not in st.session_state:
    st.session_state.user_database = user_db_github if user_db_github else {
        "06_Lazuardi": {"password": "superpassword2026", "role": "admin", "nama": "Ardi", "tanggal_mulai": "2026-07-07"},
        "Artha": {"password": "Artha123", "role": "member", "nama": "Juniartha", "tanggal_mulai": "2026-07-06"},
        "Rara": {"password": "Rara123", "role": "member", "nama": "Rara", "tanggal_mulai": "2026-07-06"},
        "Yuni": {"password": "Yuni123", "role": "member", "nama": "Yuni", "tanggal_mulai": "2026-07-07"},
        "Meli": {"password": "Meli123", "role": "member", "nama": "Meli", "tanggal_mulai": "2026-07-07"},
        "Yana": {"password": "Yana123", "role": "member", "nama": "Yana", "tanggal_mulai": "2026-07-07"},
        "Ayu": {"password": "Ayu123", "role": "member", "nama": "Ayu", "tanggal_mulai": "2026-07-07"},
        "Sefitri": {"password": "Cepi123", "role": "member", "nama": "Sefitri", "tanggal_mulai": "2026-07-07"}
    }
def sync_users():
    content = json.dumps(st.session_state.user_database, indent=4)
    save_to_github(USER_FILE, content, sha=sha_users, message="Update User Credentials")

# Tempat penyimpanan alur pengajuan reset password
if "reset_requests" not in st.session_state:
    st.session_state.reset_requests = {}

# State navigasi untuk memisahkan halaman login dan halaman reset password
if "halaman_akses" not in st.session_state:
    st.session_state.halaman_akses = "login"

# --- 4. DATABASE REKOMENDASI GERAKAN ALTERNATIF (SISTEM) ---
KAMUS_GERAKAN_ALTERNATIF = {
    # BACK (Punggung)
    "Pull Up": ["Chin Up", "Assisted Pull Up", "Lat Pulldown"],
    "Lat Pulldown": ["Close Grip Lat Pulldown", "Reverse Grip Lat Pulldown", "Straight Arm Pulldown"],
    "Barbell Row": ["Pendlay Row", "T-Bar Row", "Chest Supported Row", "Machine Row"],
    "Seated Cable Row": ["Chest Supported Row", "Machine Row", "Inverted Row"],
    "Single Arm Dumbbell Row": ["Dumbbell Row", "Meadows Row"],
    "Face Pull": ["Reverse Pec Deck", "Rear Delt Fly", "Cable Rear Delt Fly"],
    "Barbell Shrug": ["Dumbbell Shrug", "Machine Shrug"],

    # CHEST (Dada)
    "Barbell Bench Press": ["Dumbbell Bench Press", "Smith Machine Bench Press", "Chest Press Machine"],
    "Incline Barbell Bench Press": ["Incline Dumbbell Bench Press", "Incline Chest Press Machine"],
    "Cable Fly": ["High to Low Cable Fly", "Low to High Cable Fly", "Pec Deck Fly", "Dumbbell Fly"],
    "Push Up": ["Incline Push Up", "Decline Push Up", "Diamond Push Up"],
    "Dips": ["Bench Dip", "Parallel Bar Dip"],

    # CORE (Perut)
    "Cable Crunch": ["Crunch", "Reverse Crunch", "Decline Sit Up"],
    "Hanging Leg Raise": ["Hanging Knee Raise", "Toes to Bar"],
    "Plank": ["Side Plank", "Ab Wheel Rollout"],
    "Russian Twist": ["Bicycle Crunch", "Mountain Climber", "Cable Wood Chop"],
    "Dead Bug": ["Bird Dog", "Pallof Press"],

    # ARMS (Lengan)
    "Barbell Curl": ["EZ Bar Curl", "Dumbbell Curl", "Cable Curl", "Preacher Curl"],
    "Hammer Curl": ["Cross Body Hammer Curl", "Reverse Curl"],
    "Rope Pushdown": ["Straight Bar Pushdown", "V-Bar Pushdown", "Single Arm Cable Pushdown"],
    "Overhead Cable Extension": ["Overhead Dumbbell Extension", "Skull Crusher"],
    "Close Grip Bench Press": ["JM Press", "Bench Dip"],

    # LOWER BODY (Kaki)
    "Back Squat": ["Front Squat", "Hack Squat", "Goblet Squat", "Smith Squat"],
    "Leg Press": ["Sumo Squat", "Hack Squat"],
    "Bulgarian Split Squat": ["Walking Lunges", "Reverse Lunges", "Forward Lunges", "Step Up"],
    "Romanian Deadlift (RDL)": ["Conventional Deadlift", "Stiff Leg Deadlift", "Sumo Deadlift"],
    "Lying Leg Curl": ["Seated Leg Curl", "Nordic Curl", "Glute Ham Raise"],
    "Hip Thrust": ["Glute Bridge", "Cable Kickback"],
    "Standing Calf Raise": ["Seated Calf Raise", "Donkey Calf Raise", "Leg Press Calf Raise", "Single Leg Calf Raise"]
}

# Mapping otomatis untuk sistem pencarian progress
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
        "Hari 4 – Upper Body + Arms": [{"nama": "Incline Smith Machine Press", "target": "4 × 10"}, {"nama": "Chest Supported Row", "target": "4 × 10"}, {"nama": "Dumbbell Shoulder Press", "target": "3 × 10"}, {"nama": "Lateral Raise", "target": "4 × 15"}, {"nama": "Rear Delt Fly", "target": "3 × 15"}, {"nama": "Cable Fly", "target": "3 × 12"}, {"nama": "Close Grip Bench Press", "target": "4 × 10"}, {"nama": "Preacher Curl", "target": "3 × 10"}, {"nama": "Rope Pushdown", "target": "3 × 15"}, {"nama": "Cable Curl", "target": "3 × 12"}],
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
        st.warning("⚠️ Sesi login 12 jam Anda telah berakhir. Silakan masuk kembali.")

# --- 7. INTERFACE SEBELUM LOGIN & LAMAN RESET PASSWORD ---
if not st.session_state.logged_in:
    st.title("🏋️‍♂️ Aplikasi Gymnya Anak SC")
    
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
                sync_users() # <-- [TAMBAHAN] Simpan perubahan ke GitHub
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
    st.title("🏋️‍♂️ Aplikasi Gymnya Anak SC")
    st.markdown(f"### 🎉 Halo **{st.session_state.user_nama}**")
    
    # [FITUR TAMBAHAN]: Menampilkan Hari ke-berapa
    user_info = st.session_state.user_database.get(st.session_state.user_id, {})
    tgl_mulai_user = user_info.get("tanggal_mulai", "2026-07-06")
    hari_ke = hitung_hari_latihan(tgl_mulai_user)
    
    st.markdown("##### *Semangat Latihan ya hari ini!* 🔥")
        
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
                    sync_users() # <-- [TAMBAHAN] Simpan perubahan ke GitHub
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

    tab_input, tab_progress = st.tabs(["🏋️ Latihan Hari Ini", "📊 Progress Latihan"])

# ==================== TAB 1: INPUT LATIHAN ====================
    with tab_input:
        # --- DETEKSI HARI REAL-TIME & PEMETAAN HARI OTOMATIS ---
        hari_index = datetime.datetime.now().weekday()
        nama_hari_indonesia = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"][hari_index]
        
        st.subheader(f"📆 Hari Ini: {nama_hari_indonesia}")

        # Penyetelan Otomatis Hari Latihan (Kunci Khusus Hari Selasa)
        if nama_hari_indonesia == "Selasa":
            hari_rara = "Hari 2 – Back + Biceps"
            hari_admin = "Hari 2 – Back + Biceps"  
            hari_member_umum = "Hari 1 – Back + Biceps"
            info_hari_teks = "📌 **Hari Selasa:** Rara berada di **Hari 2**, Admin di **Hari 2**, Member Lain di **Hari 1 (Back + Biceps)**."
        else:
            hari_rara = "Hari 1 – Chest + Leg + Triceps"
            hari_admin = "Hari 1 – Chest + Triceps"
            hari_member_umum = "Hari 2 – Chest + Triceps"
            info_hari_teks = f"📌 **Hari {nama_hari_indonesia}:** Menggunakan pengaturan jadwal harian reguler."

        st.info(info_hari_teks)

        # --- PEMILIHAN DATA JADWAL SINKRON ---
        if st.session_state.user_id == "Rara":
            jadwal_aktif = st.session_state.jadwal_gym_rara
            pilihan_menu = st.selectbox("Jadwal Latihan Anda Hari Ini:", [hari_rara], disabled=True)
            
            if hari_index in [0, 2, 4]:
                st.warning("⚠️ Akun Rara terdeteksi memiliki jadwal TAMBAHAN latihan otot kaki!")
                opsi_kaki = st.checkbox("Ambil menu Tambahan Kaki")
                if opsi_kaki:
                    daftar_gerakan = ["Leg Extension (Kaki Rara)", "Seated Leg Curl (Kaki Rara)", "Calf Raises (Kaki Rara)"]
                    gerakan_pilihan = st.selectbox("Pilih Gerakan Tambahan:", daftar_gerakan)
                    target_bawaan = "3 × 12"
                else:
                    daftar_gerakan = [g["nama"] for g in jadwal_aktif[pilihan_menu]]
                    gerakan_pilihan = st.selectbox("Pilih Gerakan:", daftar_gerakan)
                    target_bawaan = next(g["target"] for g in jadwal_aktif[pilihan_menu] if g["nama"] == gerakan_pilihan)
            else:
                daftar_gerakan = [g["nama"] for g in jadwal_aktif[pilihan_menu]]
                gerakan_pilihan = st.selectbox("Pilih Gerakan:", daftar_gerakan)
                target_bawaan = next(g["target"] for g in jadwal_aktif[pilihan_menu] if g["nama"] == gerakan_pilihan)

        elif st.session_state.user_role == "admin":
            jadwal_aktif = st.session_state.jadwal_gym_admin
            pilihan_menu = st.selectbox("Jadwal Latihan Admin Hari Ini:", [hari_admin], disabled=True)
            daftar_gerakan = [g["nama"] for g in jadwal_aktif[pilihan_menu]]
            gerakan_pilihan = st.selectbox("Pilih Gerakan:", daftar_gerakan)
            target_bawaan = next(g["target"] for g in jadwal_aktif[pilihan_menu] if g["nama"] == gerakan_pilihan)

        else:
            jadwal_aktif = st.session_state.jadwal_gym_member_umum
            pilihan_menu = st.selectbox("Jadwal Latihan Anda Hari Ini:", [hari_member_umum], disabled=True)
            daftar_gerakan = [g["nama"] for g in jadwal_aktif[pilihan_menu]]
            gerakan_pilihan = st.selectbox("Pilih Gerakan:", daftar_gerakan)
            target_bawaan = next(g["target"] for g in jadwal_aktif[pilihan_menu] if g["nama"] == gerakan_pilihan)

        st.success(f"🎯 Target Panduan: **{target_bawaan}**")

        # ------ ENGINE PROGRESSIVE OVERLOAD ------
        df_clean_logs = df_logs.dropna(subset=["Tanggal"])
        user_logs = df_clean_logs[(df_clean_logs["Username"] == st.session_state.user_id) & (df_clean_logs["Gerakan"] == gerakan_pilihan)]
        beban_dasar_minggu_ini = 0.0
        info_progres = "Sesi pertama untuk gerakan ini. Mulai dengan beban yang aman."
        
        if not user_logs.empty:
            hari_ini_tgl = pd.to_datetime(datetime.date.today())
            logs_minggu_lalu = user_logs[user_logs["Tanggal"].dt.date < hari_ini_tgl.date()]
            
            if not logs_minggu_lalu.empty:
                tgl_terakhir = logs_minggu_lalu["Tanggal"].max()
                sesi_terakhir = logs_minggu_lalu[logs_minggu_lalu["Tanggal"] == tgl_terakhir]
                beban_maks_minggu_lalu = sesi_terakhir["Beban_kg"].max()
                beban_dasar_minggu_ini = beban_maks_minggu_lalu + 2.5
                info_progres = f"📈 Progres Mingguan: Target beban dasar naik menjadi: **{beban_dasar_minggu_ini}kg** (+2.5kg dari beban tertinggi minggu lalu)."
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
                    "Tanggal": str(datetime.date.today()),
                    "Username": st.session_state.user_id,
                    "Gerakan": gerakan_pilihan,
                    "Set_Ke": set_ke,
                    "Beban_kg": berat,
                    "Reps": reps
                }])
                df_updated = pd.concat([df_logs, new_log], ignore_index=True)
                df_updated.to_csv(LOG_FILE, index=False)
                st.success(f"Set {set_ke} berhasil disimpan!")
                st.rerun()

        # --- DATA VIEW MONITORING & KALIMAT PENUTUP ---
        st.write("---")
        st.subheader("📋 Catatan Latihan Anda Hari Ini")
        df_hari_ini = df_logs[(df_logs["Username"] == st.session_state.user_id) & (df_logs["Tanggal"].dt.date == datetime.date.today())]
        
        if not df_hari_ini.empty:
            st.dataframe(df_hari_ini[["Gerakan", "Set_Ke", "Beban_kg", "Reps"]], use_container_width=True)
            st.balloons()
            st.success("""
            🎉 **YEAY! LATIHAN SELESAI!** 💪 *Nikmati DOMS nya besok.* 🔥 **Jangan menyerah, ayo terus semangat latihannya!**
            """)
        else:
            st.caption("Belum ada set yang disimpan hari ini.")

    # ==================== TAB 2: PROGRESS LATIHAN ====================
    with tab_progress:
        st.subheader("📊 Analisis & Riwayat Progress")
        
        # Filter log khusus user yang sedang login
        df_user_all = df_logs[df_logs["Username"] == st.session_state.user_id].copy()
        
        if df_user_all.empty:
            st.info("Belum ada riwayat latihan yang tercatat untuk akun Anda. Silakan isi latihan terlebih dahulu!")
        else:
            # Tambah kolom pembantu untuk waktu
            df_user_all["Bulan"] = df_user_all["Tanggal"].dt.strftime("%Y-%m (%B)")
            df_user_all["Tanggal_Saja"] = df_user_all["Tanggal"].dt.date
            
            # --- RINGKASAN TOTAL AKUMULASI ---
            total_hari_latihan = df_user_all["Tanggal_Saja"].nunique()
            total_set_diangkat = len(df_user_all)
            
            col1, col2 = st.columns(2)
            col1.metric("📆 Total Hari Latihan", f"{total_hari_latihan} Hari")
            col2.metric("🏋️ Total Set Diselesaikan", f"{total_set_diangkat} Set")
            
            st.write("---")
            
            # --- FILTER PROGRESS ---
            mode_view = st.radio("Pilih Mode Riwayat:", ["Per Bulan", "Per Hari Spesifik", "Grafik Tren Beban (Overload)"], horizontal=True)
            
            if mode_view == "Per Bulan":
                st.markdown("### 📅 Riwayat Latihan Bulanan")
                pilihan_bulan = st.selectbox("Pilih Bulan Latihan:", df_user_all["Bulan"].unique())
                
                df_bulanan = df_user_all[df_user_all["Bulan"] == pilihan_bulan]
                # Mengelompokkan gerakan per bulan
                df_summary_bulan = df_bulanan.groupby(["Tanggal_Saja", "Gerakan"]).agg(
                    Total_Set=("Set_Ke", "count"),
                    Beban_Maksimal_kg=("Beban_kg", "max"),
                    Reps_Maksimal=("Reps", "max")
                ).reset_index()
                
                df_summary_bulan.columns = ["Tanggal", "Nama Gerakan", "Jumlah Set", "Beban Tertinggi (kg)", "Reps Tertinggi"]
                st.dataframe(df_summary_bulan.sort_values(by="Tanggal", ascending=False), use_container_width=True)
                
            elif mode_view == "Per Hari Spesifik":
                st.markdown("### 📆 Riwayat Detil Harian")
                # Mengurutkan tanggal terbaru di atas
                daftar_tanggal = sorted(df_user_all["Tanggal_Saja"].unique(), reverse=True)
                pilihan_tanggal = st.selectbox("Pilih Tanggal Latihan:", daftar_tanggal)
                
                df_harian = df_user_all[df_user_all["Tanggal_Saja"] == pilihan_tanggal]
                st.dataframe(df_harian[["Gerakan", "Set_Ke", "Beban_kg", "Reps"]].reset_index(drop=True), use_container_width=True)
                
            elif mode_view == "Grafik Tren Beban (Overload)":
                st.markdown("### 📈 Grafik Kenaikan Beban (*Progressive Overload*)")
                st.caption("Gunakan fitur ini untuk melihat apakah beban latihan Anda meningkat dari minggu ke minggu.")
                
                daftar_gerakan_user = df_user_all["Gerakan"].unique()
                gerakan_dipilih = st.selectbox("Pilih Gerakan yang Ingin Dilihat Trennya:", daftar_gerakan_user)
                
                # Filter data gerakan tersebut, lalu cari beban maksimum per tanggal latihan
                df_tren = df_user_all[df_user_all["Gerakan"] == gerakan_dipilih]
                df_chart = df_tren.groupby("Tanggal_Saja")["Beban_kg"].max().reset_index()
                df_chart.columns = ["Tanggal", "Beban Maksimal (kg)"]
                
                # Set index tanggal agar terbaca dengan baik oleh st.line_chart
                df_chart = df_chart.set_index("Tanggal")
                
                # Tampilkan grafik garis
                st.line_chart(df_chart, y="Beban Maksimal (kg)")
                
                # Tabel pendukung grafik
                with st.expander("Lihat Angka Detil Kenaikan"):
                    st.dataframe(df_chart.sort_index(ascending=False), use_container_width=True)
