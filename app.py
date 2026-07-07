import streamlit as st
import pandas as pd
import datetime
import os

# Konfigurasi Halaman
st.set_page_config(page_title="Gym Goal Tracker", layout="wide")
st.title("🏋️‍♂️ Gym Goal Tracker & Variance Analysis")
st.write("Lacak target latihan Anda dan analisis efisiensinya secara berkala.")

# File Database Lokal
DB_FILE = "gym_data.csv"

# Load atau Inisialisasi Data
if os.path.exists(DB_FILE):
    df = pd.read_csv(DB_FILE)
else:
    df = pd.DataFrame(columns=[
        "Tanggal", "Jenis Latihan", "Target Berat (kg)", "Realisasi Berat (kg)", 
        "Target Raps", "Realisasi Raps", "Status"
    ])

# --- SIDEBAR: INPUT DATA ---
st.sidebar.header("📥 Input Log Latihan")
with st.sidebar.form("gym_form", clear_on_submit=True):
    tanggal = st.date_input("Tanggal", datetime.date.today())
    jenis_latihan = st.selectbox("Jenis Gerakan/Latihan", ["Bench Press", "Squat", "Deadlift", "Overhead Press", "Pull Up", "Lainnya"])
    
    col1, col2 = st.columns(2)
    with col1:
        t_berat = st.number_input("Target Berat (kg)", min_value=0.0, step=2.5)
        t_raps = st.number_input("Target Repetisi", min_value=0, step=1)
    with col2:
        r_berat = st.number_input("Realisasi Berat (kg)", min_value=0.0, step=2.5)
        r_raps = st.number_input("Realisasi Repetisi", min_value=0, step=1)
        
    submitted = st.form_submit_button("Simpan Data")

if submitted:
    # Evaluasi status pencapaian target
    status = "Target Tercapai" if (r_berat >= t_berat and r_raps >= t_raps) else "Di Bawah Target"
    
    # Tambah data baru
    new_data = pd.DataFrame([{
        "Tanggal": str(tanggal),
        "Jenis Latihan": jenis_latihan,
        "Target Berat (kg)": t_berat,
        "Realisasi Berat (kg)": r_berat,
        "Target Raps": t_raps,
        "Realisasi Raps": r_raps,
        "Status": status
    }])
    
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv(DB_FILE, index=False)
    st.sidebar.success("Data berhasil disimpan!")

# --- HALAMAN UTAMA: DASHBOARD ---
if not df.empty:
    # 1. Ringkasan Metrik (KPI)
    total_sesi = len(df)
    tercapai = len(df[df["Status"] == "Target Tercapai"])
    rate_keberhasilan = (tercapai / total_sesi) * 100 if total_sesi > 0 else 0
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Latihan Dicatat", f"{total_sesi} Kali")
    m2.metric("Sesi Target Tercapai", f"{tercapai} Kali")
    m3.metric("Efisiensi Keberhasilan", f"{rate_keberhasilan:.1f}%")
    
    st.markdown("---")
    
    # 2. Analisis Varians (Selisih Target vs Realisasi)
    st.subheader("📊 Analisis Progres & Varians")
    
    # Hitung selisih untuk analisis performa
    df_analisis = df.copy()
    df_analisis["Selisih Berat (kg)"] = df_analisis["Realisasi Berat (kg)"] - df_analisis["Target Berat (kg)"]
    df_analisis["Selisih Repetisi"] = df_analisis["Realisasi Raps"] - df_analisis["Target Raps"]
    
    # Pilih gerakan untuk grafik
    gerakan_pilihan = st.selectbox("Pilih Gerakan untuk Dilihat Progresnya:", df["Jenis Latihan"].unique())
    df_filtered = df_analisis[df_analisis["Jenis Latihan"] == gerakan_pilihan]
    
    if not df_filtered.empty:
        # Grafik Garis Progres Berat Angkatan
        st.line_chart(df_filtered.set_index("Tanggal")[["Target Berat (kg)", "Realisasi Berat (kg)"]])
    else:
        st.info("Belum ada data progres untuk gerakan ini.")
        
    st.markdown("---")
    
    # 3. Tabel Data Historis
    st.subheader("📋 Jurnal Latihan Historis")
    st.dataframe(df_analisis, use_container_width=True)
    
    # Tombol Reset Data jika diperlukan
    if st.button("Hapus Semua Riwayat"):
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
        st.rerun()
else:
    st.info("👋 Selamat Datang! Silakan masukkan target dan realisasi latihan pertama Anda pada menu di sebelah kiri.")
