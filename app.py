import streamlit as st
import datetime

# --- 1. CONFIG HALAMAN MOBILE ---
st.set_page_config(page_title="Gym Member Portal", page_icon="🔒", layout="centered")

# --- 2. DATABASE USER & PASSWORD (DIKELOLA OLEH ANDA) ---
USER_DATABASE = {
    "admin_gym": {"password": "superpassword2026", "role": "admin", "nama": "Owner Gym (Anda)"},
    "budi_member": {"password": "budi123", "role": "member", "nama": "Budi Santoso"},
    "siti_member": {"password": "siti456", "role": "member", "nama": "Siti Rahma"},
    "member_baru": {"password": "gym789", "role": "member", "nama": "Andi Wijaya"}
}

# --- 3. INITIALIZE JADWAL GYM (SESSION STATE) ---
if "jadwal_gym" not in st.session_state:
    st.session_state.jadwal_gym = {
        "Hari 1: Chest (Heavy) & Triceps": [
            {"nama": "Barbell Bench Press", "target": "4 × 8"},
            {"nama": "Incline Dumbbell Press", "target": "4 × 10"},
            {"nama": "Skull Crusher", "target": "3 × 12"}
        ],
        "Hari 2: Legs (Quad Dominant)": [
            {"nama": "Back Squat", "target": "4 × 8"},
            {"nama": "Romanian Deadlift", "target": "4 × 8"},
            {"nama": "Leg Press", "target": "3 × 10"}
        ],
        "Hari 3: Back & Biceps": [
            {"nama": "Lat Pulldown", "target": "4 × 10"},
            {"nama": "Barbell Row", "target": "4 × 8"},
            {"nama": "Bar Curl", "target": "3 × 10"}
        ],
        "Hari 4: Chest & Shoulders": [
            {"nama": "Incline Smith Press", "target": "4 × 10"},
            {"nama": "Dumbbell Shoulder Press", "target": "3 × 10"},
            {"nama": "Lateral Raise", "target": "4 × 15"}
        ],
        "Hari 5: Legs & Abs": [
            {"nama": "Front Squat", "target": "4 × 10"},
            {"nama": "Leg Curl", "target": "4 × 12"},
            {"nama": "Plank", "target": "3 × 1 menit"}
        ]
    }

# --- 4. SISTEM LOGIN ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.user_nama = None

if not st.session_state.logged_in:
    st.title("🏋️‍♂️ Gym Private Member Login")
    st.write("Silakan masukkan akun yang telah diberikan oleh pengelola gym.")
    
    with st.form("login_form"):
        username_input = st.text_input("Username").strip()
        password_input = st.text_input("Password", type="password").strip()
        submit_login = st.form_submit_button("Masuk 🔓")
        
        if submit_login:
            if username_input in USER_DATABASE and USER_DATABASE[username_input]["password"] == password_input:
                st.session_state.logged_in = True
                st.session_state.user_role = USER_DATABASE[username_input]["role"]
                st.session_state.user_nama = USER_DATABASE[username_input]["nama"]
                st.success(f"Selamat datang {st.session_state.user_nama}!")
                st.rerun()
            else:
                st.error("❌ Username atau Password salah. Hubungi Owner Gym.")

# --- 5. HALAMAN SETELAH BERHASIL LOGIN ---
else:
    st.title("🏋️‍♂️ Universal Gym Tracker Portal")
    st.sidebar.markdown(f"👤 **Pengguna:** {st.session_state.user_nama}")
    st.sidebar.markdown(f"🔰 **Akses:** `{st.session_state.user_role.upper()}`")
    
    if st.sidebar.button("Keluar / Logout 🚪"):
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.user_nama = None
        st.rerun()

    # CONTROL PANEL ADMIN
    if st.session_state.user_role == "admin":
        st.sidebar.markdown("---")
        st.sidebar.subheader("🛠️ Admin Panel (Hanya Anda)")
        
        with st.sidebar.expander("📝 Edit Jadwal Gym"):
            hari_diedit = st.selectbox("Pilih Hari Latihan:", list(st.session_state.jadwal_gym.keys()))
            gerakan_list = st.session_state.jadwal_gym[hari_diedit]
            
            teks_jadwal_baru = ""
            for g in gerakan_list:
                teks_jadwal_baru += f"{g['nama']} | {g['target']}\n"
                
            area_edit = st.text_area("Format: Nama Gerakan | Set x Reps", value=teks_jadwal_baru, height=150)
            
            if st.button("💾 Perbarui Jadwal Member"):
                baris = area_edit.strip().split("\n")
                jadwal_diperbarui = []
                for b in baris:
                    if "|" in b:
                        nama_g, t_g = b.split("|")
                        jadwal_diperbarui.append({"nama": nama_g.strip(), "target": t_g.strip()})
                
                st.session_state.jadwal_gym[hari_diedit] = jadwal_diperbarui
                st.sidebar.success("Jadwal sukses di-update untuk semua member!")
                st.rerun()

    # INTERFACE MEMBER
    st.header("💪 Menu Latihan Hari Ini")
    pilihan_menu = st.selectbox("Pilih Jadwal:", list(st.session_state.jadwal_gym.keys()))
    
    daftar_gerakan = [g["nama"] for g in st.session_state.jadwal_gym[pilihan_menu]]
    gerakan_pilihan = st.selectbox("Pilih Gerakan:", daftar_gerakan)
    
    target_bawaan = next(g["target"] for g in st.session_state.jadwal_gym[pilihan_menu] if g["nama"] == gerakan_pilihan)
    st.info(f"🎯 Target Panduan: **{target_bawaan}**")
    
    with st.form("log_latihan_form"):
        berat = st.number_input("Beban Latihan (kg)", min_value=0.0, step=2.5)
        reps = st.number_input("Repetisi Berhasil", min_value=0, step=1)
        submit_log = st.form_submit_button("💾 Simpan Hasil Latihan")
        
        if submit_log:
            st.success(f"Berhasil mencatat {gerakan_pilihan} - {berat}kg x {reps} Reps!")
