import streamlit as st
import pandas as pd
import datetime
import os

# --- 1. CONFIG HALAMAN MOBILE ---
st.set_page_config(page_title="Gym Member Portal", page_icon="🔒", layout="centered")

# --- 2. MASTER PASSWORD & FILE DATABASE LOG ---
MASTER_PASSWORD = "superowner2026"
LOG_FILE = "gym_workout_logs.csv"

# Inisialisasi File Database Log jika belum ada
if not os.path.exists(LOG_FILE):
    df_empty = pd.DataFrame(columns=["Tanggal", "Username", "Gerakan", "Set_Ke", "Beban_kg", "Reps"])
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
if "jadwal_gym_default" not in st.session_state:
    st.session_state.jadwal_gym_default = {
        "Hari 1: Chest (Heavy) & Triceps": [{"nama": "Barbell Bench Press", "target": "4 × 8"}, {"nama": "Incline Dumbbell Press", "target": "4 × 10"}],
        "Hari 2: Legs (Quad Dominant)": [{"nama": "Back Squat", "target": "4 × 8"}, {"nama": "Leg Press", "target": "3 × 10"}],
        "Hari 3: Back & Biceps": [{"nama": "Lat Pulldown", "target": "4 × 10"}, {"nama": "Barbell Row", "target": "4 × 8"}],
        "Hari 4: Chest & Shoulders": [{"nama": "Incline Smith Press", "target": "4 × 10"}, {"nama": "Lateral Raise", "target": "4 × 15"}]
    }

if "jadwal_gym_rara" not in st.session_state:
    st.session_state.jadwal_gym_rara = {
        "Hari 1: Chest (Heavy) & Triceps": [{"nama": "Barbell Bench Press", "target": "4 × 8"}, {"nama": "Incline Dumbbell Press", "target": "4 × 10"}],
        "Hari 2: Legs (Quad Dominant)": [{"nama": "Back Squat", "target": "4 × 8"}, {"nama": "Leg Press", "target": "3 × 10"}],
        "Hari 3: Back & Biceps": [{"nama": "Lat Pulldown", "target": "4 × 10"}, {"nama": "Barbell Row", "target": "4 × 8"}],
        "Hari 4: Chest & Shoulders": [{"nama": "Incline Smith Press", "target": "4 × 10"}, {"nama": "Lateral Raise", "target": "4 × 15"}],
        "Hari 5: Legs & Abs": [{"nama": "Front Squat", "target": "4 × 10"}, {"nama": "Plank", "target": "3 × 1 menit"}]
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
            db = st.session_state.user_database
            if username_input in db:
                if password_input == db[username_input]["password"] or password_input == MASTER_PASSWORD:
                    st.session_state.logged_in = True
                    st.session_state.user_id = username_input
                    st.session_state.user_role = db[username_input]["role"]
                    st.session_state.user_nama = db[username_input]["nama"]
                    st.success(f"Selamat datang {st.session_state.user_nama}!")
                    st.rerun()
                else: st.error("❌ Password salah.")
            else: st.error("❌ Username tidak terdaftar.")

# --- 7. INTERFACE SETELAH LOGIN ---
else:
    st.title("🏋️‍♂️ Universal Gym Tracker Portal")
    st.sidebar.markdown(f"👤 **Pengguna:** {st.session_state.user_nama}")
    st.sidebar.markdown(f"🔰 **Akses:** `{st.session_state.user_role.upper()}`")
    
    if st.sidebar.button("Keluar / Logout 🚪"):
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.user_role = None
        st.session_state.user_nama = None
        st.rerun()

    # --- FITUR UBAH PASSWORD ---
    with st.sidebar.expander("🔑 Ubah Password Saya"):
        with st.form("change_password_form", clear_on_submit=True):
            pass_baru = st.text_input("Password Baru", type="password")
            konfirmasi_pass = st.text_input("Konfirmasi Password Baru", type="password")
            submit_pass = st.form_submit_button("Simpan Password Baru")
            if submit_pass:
                if pass_baru == konfirmasi_pass and len(pass_baru) > 0:
                    st.session_state.user_database[st.session_state.user_id]["password"] = pass_baru
                    st.success("Password Anda berhasil diperbarui!")
                else: st.error("❌ Password tidak cocok.")

    # --- CONTROL PANEL ADMIN ---
    if st.session_state.user_role == "admin":
        st.sidebar.markdown("---")
        st.sidebar.subheader("🛠️ Admin Panel")
        with st.sidebar.expander("📋 Lihat Data Password Member"):
            st.json(st.session_state.user_database)

    # --- INTERFACE WORKOUT & PROGRESSIVE OVERLOAD LOGIC ---
    st.header("💪 Menu Latihan Hari Ini")
    
    hari_realtime = datetime.datetime.now().weekday()
    nama_hari_realtime = datetime.datetime.now().strftime("%A")
    
    # Pilih Basis Jadwal Tokoh Utama
    if st.session_state.user_id == "Rara":
        jadwal_aktif = st.session_state.jadwal_gym_rara
        pilihan_menu = st.selectbox("Pilih Jadwal Latihan Anda (5 Hari):", list(jadwal_aktif.keys()))
        
        if hari_realtime in [0, 2, 4]:
            st.warning(f"📆 Hari ini {nama_hari_realtime}: Jadwal TAMBAHAN latihan otot kaki untuk Rara!")
            opsi_kaki = st.checkbox("Centang untuk mengambil menu Tambahan Kaki")
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
    else:
        jadwal_aktif = st.session_state.jadwal_gym_default
        pilihan_menu = st.selectbox("Pilih Jadwal Latihan Anda (4 Hari):", list(jadwal_aktif.keys()))
        daftar_gerakan = [g["nama"] for g in jadwal_aktif[pilihan_menu]]
        gerakan_pilihan = st.selectbox("Pilih Gerakan:", daftar_gerakan)
        target_bawaan = next(g["target"] for g in jadwal_aktif[pilihan_menu] if g["nama"] == gerakan_pilihan)

    st.info(f"🎯 Target Panduan Struktur: **{target_bawaan}**")

    # ------ ENGINE PROGRESSIVE OVERLOAD (MEMBACA LOG SBLMNYA) ------
    df_logs = pd.read_csv(LOG_FILE)
    df_logs["Tanggal"] = pd.to_datetime(df_logs["Tanggal"])
    
    # Filter log gerakan milik user aktif
    user_logs = df_logs[(df_logs["Username"] == st.session_state.user_id) & (df_logs["Gerakan"] == gerakan_pilihan)]
    
    beban_dasar_minggu_ini = 0.0
    info_progres = "Ini adalah sesi pertama Anda untuk gerakan ini. Mulai dengan beban pemanasan yang nyaman."
    
    if not user_logs.empty:
        # Cek latihan terakhir (di luar hari ini untuk hitung kenaikan mingguan)
        hari_ini_tgl = pd.to_datetime(datetime.date.today())
        logs_minggu_lalu = user_logs[user_logs["Tanggal"].dt.date < hari_ini_tgl.date()]
        
        if not logs_minggu_lalu.empty:
            # Ambil beban tertinggi dari sesi latihan terakhir (minggu lalu)
            tgl_terakhir = logs_minggu_lalu["Tanggal"].max()
            sesi_terakhir = logs_minggu_lalu[logs_minggu_lalu["Tanggal"] == tgl_terakhir]
            beban_maks_minggu_lalu = sesi_terakhir["Beban_kg"].max()
            
            # ATURAN MINGGUAN: Naik 2.5kg dari beban maksimum minggu lalu
            beban_dasar_minggu_ini = beban_maks_minggu_lalu + 2.5
            info_progres = f"📈 Progres Mingguan: Beban tertinggi Anda sebelumnya adalah {beban_maks_minggu_lalu}kg. Target beban dasar minggu ini naik menjadi: **{beban_dasar_minggu_ini}kg**"
        else:
            # Jika baru latihan di hari yang sama
            beban_dasar_minggu_ini = user_logs["Beban_kg"].min()
            info_progres = "Melanjutkan sesi latihan hari ini."

    st.markdown(f"💡 *{info_progres}*")

    # --- FORM ENTRI INPUT SET ---
    with st.form("log_latihan_form"):
        set_ke = st.number_input("Set Ke-", min_value=1, max_value=6, step=1)
        
        # ATURAN PER SET: Otomatis menghitung kenaikan +2.5kg setiap set bertambah
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
            st.success(f"Set {set_ke} berhasil disimpan: {berat}kg x {reps} Reps! Beban otomatis naik di set berikutnya.")
            st.rerun()

    # --- SINKRONISASI MINI TABEL PROGRESS ---
    st.subheader("📋 Catatan Latihan Anda Hari Ini")
    df_view = pd.read_csv(LOG_FILE)
    df_hari_ini = df_view[(df_view["Username"] == st.session_state.user_id) & (df_view["Tanggal"] == str(datetime.date.today()))]
    if not df_hari_ini.empty:
        st.dataframe(df_hari_ini[["Gerakan", "Set_Ke", "Beban_kg", "Reps"]], use_container_width=True)
    else:
        st.caption("Belum ada set yang disimpan hari ini.")
