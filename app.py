import streamlit as st
import pandas as pd
import datetime

# --- KONFIGURASI HALAMAN MOBILE-FRIENDLY ---
st.set_page_config(page_title="My Gym Schedule", page_icon="💪", layout="centered")

st.title("🏋️‍♂️ Personalized Gym Tracker")
st.write("Jadwal Rutin 5 Hari Kerja (Sabtu & Minggu Libur)")

# --- DATABASE JADWAL & GERAKAN SESUAI PERMINTAAN ---
JADWAL_ROUTINE = {
    "Hari 1: Chest (Heavy) & Triceps": [
        {"nama": "Barbell Bench Press", "target": "4 × 8"},
        {"nama": "Incline Dumbbell Press", "target": "4 × 10"},
        {"nama": "Chest Press Machine", "target": "3 × 12"},
        {"nama": "Chest Dips", "target": "3 × 10"},
        {"nama": "Cable Fly (Sejajar)", "target": "3 × 12"},
        {"nama": "Skull Crusher", "target": "3 × 12"},
        {"nama": "Rope Pushdown", "target": "3 × 15"}
    ],
    "Hari 2: Legs (Quad Dominant) & Calves": [
        {"nama": "Back Squat", "target": "4 × 8"},
        {"nama": "Romanian Deadlift", "target": "4 × 8"},
        {"nama": "Leg Press", "target": "3 × 10"},
        {"nama": "Bulgarian Split Squat", "target": "3 × 10/kaki"},
        {"nama": "Leg Extension", "target": "3 × 12"},
        {"nama": "Standing Calf Raise", "target": "4 × 15"}
    ],
    "Hari 3: Back & Biceps": [
        {"nama": "Lat Pulldown", "target": "4 × 10"},
        {"nama": "Barbell Row", "target": "4 × 8"},
        {"nama": "Seated Cable Row", "target": "3 × 10"},
        {"nama": "Single Arm Dumbbell Row", "target": "3 × 10"},
        {"nama": "Face Pull", "target": "3 × 15"},
        {"nama": "Bar Curl", "target": "3 × 10"},
        {"nama": "Incline Dumbbell Curl", "target": "3 × 12"},
        {"nama": "Hammer Curl", "target": "3 × 12"}
    ],
    "Hari 4: Chest (Volume) & Shoulders": [
        {"nama": "Incline Smith Press", "target": "4 × 10"},
        {"nama": "Dumbbell Bench Press", "target": "3 × 12"},
        {"nama": "Pec Deck Fly", "target": "4 × 15"},
        {"nama": "Cable Fly (High to Low)", "target": "3 × 15"},
        {"nama": "Dumbbell Shoulder Press", "target": "3 × 10"},
        {"nama": "Lateral Raise", "target": "4 × 15"},
        {"nama": "Rear Delt Fly", "target": "3 × 15"}
    ],
    "Hari 5: Legs (Posterior Focus) & Abs": [
        {"nama": "Front Squat", "target": "4 × 10"},
        {"nama": "Hip Thrust", "target": "4 × 10"},
        {"nama": "Walking Lunges", "target": "3 × 12"},
        {"nama": "Leg Curl", "target": "4 × 12"},
        {"nama": "Leg Extension", "target": "4 × 15"},
        {"nama": "Seated Calf Raise", "target": "4 × 20"},
        {"nama": "Hanging Leg Raise", "target": "3 × 15"},
        {"nama": "Cable Crunch", "target": "3 × 15"},
        {"nama": "Plank", "target": "3 × 1 menit"}
    ]
}

# --- LOGIKA OTOMATIS HARI ---
hari_ini = datetime.datetime.now().weekday() # 0=Senin, 4=Jumat, 5=Sabtu, 6=Minggu
nama_hari = datetime.datetime.now().strftime("%A")

# Mapping otomatis hari kerja ke target menu gym
if hari_ini == 0: default_index = 0   # Senin -> Hari 1
elif hari_ini == 1: default_index = 1 # Selasa -> Hari 2
elif hari_ini == 2: default_index = 2 # Rabu -> Hari 3
elif hari_ini == 3: default_index = 3 # Kamis -> Hari 4
elif hari_ini == 4: default_index = 4 # Jumat -> Hari 5
else: default_index = 5               # Sabtu/Minggu -> Rest Day

# --- UI DETEKSI HARI LIBUR ---
if default_index == 5:
    st.info(f"📆 Hari Ini: {nama_hari} (Weekend)")
    st.success("🧘‍♂️ Jadwal Hari Ini: LIBUR / REST DAY. Selamat beristirahat untuk pertumbuhan otot optimal!")
    st.markdown("---")
    st.write("💡 *Ingin mencatat latihan yang tertunda? Silakan pilih menu latihan secara manual di bawah ini:*")

# Dropdown pilihan menu latihan (Otomatis terpilih sesuai hari asli)
pilihan_menu = st.selectbox(
    "Pilih Menu Latihan:", 
    list(JADWAL_ROUTINE.keys()) + ["Manually Log / Rest Day"],
    index=default_index if default_index < 5 else 5
)

# --- ENGINE FORM LOG INPUT ---
if pilihan_menu != "Manually Log / Rest Day":
    st.subheader(f"📋 Menu: {pilihan_menu}")
    
    # Pilih gerakan spesifik dari jadwal hari yang dipilih
    daftar_gerakan = [g["nama"] for g in JADWAL_ROUTINE[pilihan_menu]]
    gerakan_pilihan = st.selectbox("Pilih Gerakan yang Sedang Dilakukan:", daftar_gerakan)
    
    # Mencari tahu target set & reps bawaan untuk gerakan tersebut
    target_bawaan = next(g["target"] for g in JADWAL_ROUTINE[pilihan_menu] if g["nama"] == gerakan_pilihan)
    st.info(f"🎯 Target Bawaan: **{target_bawaan}**")

    # Form Input Angka Realisasi
    with st.form("gym_routine_form", clear_on_submit=True):
        tanggal_log = st.date_input("Tanggal", datetime.date.today())
        
        col1, col2 = st.columns(2)
        with col1:
            berat_input = st.number_input("Beban Realisasi (kg)", min_value=0.0, step=2.5)
        with col2:
            reps_input = st.number_input("Repetisi Berhasil", min_value=0, step=1)
            
        submit = st.form_submit_button("💾 Simpan Log Set")

    # Simulasi Penyimpanan Data Lokal
    if submit:
        try:
            df_history = pd.read_csv("gym_routine_history.csv")
        except:
            df_history = pd.DataFrame(columns=["Tanggal", "Menu", "Gerakan", "Target", "Beban (kg)", "Reps"])
            
        new_log = pd.DataFrame([{
            "Tanggal": str(tanggal_log),
            "Menu": pilihan_menu,
            "Gerakan": gerakan_pilihan,
            "Target": target_bawaan,
            "Beban (kg)": berat_input,
            "Reps": reps_input
        }])
        
        df_history = pd.concat([df_history, new_log], ignore_index=True)
        df_history.to_csv("gym_routine_history.csv", index=False)
        st.success(f"Berhasil mencatat log untuk {gerakan_pilihan}!")
        st.rerun()

st.markdown("---")

# --- DATABASE VIEW / RIWAYAT ---
st.subheader("📊 Jurnal Latihan Anda")
try:
    df_show = pd.read_csv("gym_routine_history.csv")
    st.dataframe(df_show, use_container_width=True)
    
    # Fitur download excel/csv ringkas dari HP
    csv = df_show.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Semua Data (CSV)", csv, "gym_history.csv", "text/csv")
except:
    st.info("Belum ada data latihan yang terekam. Log latihan Anda akan muncul di sini.")
