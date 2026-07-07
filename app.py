import streamlit as st
import pandas as pd
import datetime
import os

# --- 1. CONFIG HALAMAN MOBILE ---
st.set_page_config(page_title="Gym Member Portal", page_icon="🔒", layout="centered")

# --- 2. MASTER PASSWORD & FILE DATABASE LOG ---
MASTER_PASSWORD = "superowner2026"  
LOG_FILE = "gym_workout_logs.csv"

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

# --- 7. INTERFACE SETELAH LOGIN ---
else:
    st.title("🏋️‍♂️ Universal Gym Tracker Portal")
    
    # --- SALAM PEMBUKA KUSTOM ---
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

    # --- FITUR UBAH PASSWORD MANDIRI ---
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

    # --- CONTROL PANEL ADMIN ---
    if st.session_state.user_role == "admin":
        st.sidebar.markdown("---")
        st.sidebar.subheader("🛠️ Admin Panel")
        with st.sidebar.expander("📋 Lihat Data Password Member"):
            st.json(st.session_state.user_database)

    # --- PEMBAGIAN MENU TAB (INPUT VS PROGRESS) ---
    tab_input, tab_progress = st.tabs(["🏋️ Latihan Hari Ini", "📊 Progress Latihan"])

    # Load DB log di awal untuk kedua tab
    df_logs = pd.read_csv(LOG_FILE)
    df_logs["Tanggal"] = pd.to_datetime(df_logs["Tanggal"], errors='coerce')

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
