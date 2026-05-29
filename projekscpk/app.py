# ============================================
# SCPK PEMILIHAN MOBIL TERBAIK
# Streamlit UI - Metode Fuzzy Mamdani
# ============================================
import streamlit as st
import pandas as pd
import numpy as np
import time

from database import Database
from fuzzy_logic import FuzzyMobil

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="SPK Mobil Terbaik",
    # page_icon="",
    layout="wide"
)

# ============================================
# INIT FUZZY ENGINE
# ============================================
@st.cache_resource
def init_fuzzy():
    return FuzzyMobil()

fuzzy_engine = init_fuzzy()

# ============================================
# SESSION STATE
# ============================================
if 'df_mobil' not in st.session_state:
    st.session_state.df_mobil = None

if 'dataset_loaded' not in st.session_state:
    st.session_state.dataset_loaded = False

if 'hasil_rekomendasi' not in st.session_state:
    st.session_state.hasil_rekomendasi = None

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.title(" SPK Mobil Terbaik")
    st.markdown("*Metode Fuzzy Mamdani*")
    
    if st.session_state.dataset_loaded and st.session_state.df_mobil is not None:
        st.success(f" {len(st.session_state.df_mobil)} data siap")
    else:
        st.warning(" Dataset belum diupload")
    
    st.markdown("---")
    
    menu = st.radio(
        "Menu",
        [" Upload Dataset", " Rekomendasi", " Histori"]
    )
    
    st.markdown("---")
    st.caption("© 2024 SCPK Fuzzy Mobil")

# ============================================
# 1. UPLOAD DATASET
# ============================================
if menu == " Upload Dataset":
    st.title(" Upload Dataset CSV")
    st.markdown("Upload file CSV dataset mobil untuk diproses.")
    
    if st.session_state.dataset_loaded and st.session_state.df_mobil is not None:
        st.info(f" Dataset sudah terload: **{len(st.session_state.df_mobil)}** mobil")
        st.markdown("---")
        st.markdown("### Upload Ulang (Opsional)")
    
    uploaded = st.file_uploader("Pilih file CSV", type="csv", key="upload_csv")
    
    if uploaded:
        df = pd.read_csv(uploaded)
        st.session_state.df_mobil = df
        st.session_state.dataset_loaded = True
        st.session_state.hasil_rekomendasi = None
        
        st.success(f" Berhasil load {len(df)} data mobil!")
        st.markdown("### Preview Dataset")
        st.dataframe(df.head(20), use_container_width=True)
        
        st.markdown("### Info Dataset")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Data", len(df))
        col2.metric("Mobil Unik", df['Car_Name'].nunique())
        col3.metric("Tahun", f"{df['Year'].min()} - {df['Year'].max()}")
    
    else:
        if st.session_state.dataset_loaded and st.session_state.df_mobil is not None:
            df = st.session_state.df_mobil
            st.success(f" Dataset tersedia: **{len(df)}** mobil")
            st.markdown("### Preview Dataset")
            st.dataframe(df.head(20), use_container_width=True)
        else:
            st.info(" Silakan upload file CSV untuk memulai.")

# ============================================
# 2. REKOMENDASI
# ============================================
elif menu == " Rekomendasi":
    st.title(" Rekomendasi Mobil")
    
    if not st.session_state.dataset_loaded or st.session_state.df_mobil is None:
        st.warning(" Upload dataset terlebih dahulu di menu **Upload Dataset**!")
    else:
        st.markdown("### Filter Kriteria")
        
        col1, col2 = st.columns(2)
        
        with col1:
            harga = st.slider("Harga Maksimal", 0.0, 40.0, 15.0, 0.5)
            umur = st.slider("Umur Maksimal (Tahun)", 0, 25, 8)
            pemilik = st.slider("Maks. Pemilik Sebelumnya", 0, 5, 2)
        
        with col2:
            km = st.slider("KM Maksimal", 0, 250000, 80000, 5000)
            rasio = st.slider("Rasio Harga Maksimal", 0.0, 1.2, 0.8, 0.05)
        
        if st.button("🔍 Hitung Rekomendasi", use_container_width=True):
            with st.spinner("Memproses..."):
                df = st.session_state.df_mobil
                results = []
                
                progress = st.progress(0)
                total = len(df)
                
                for i, (_, row) in enumerate(df.iterrows()):
                    mobil_umur = 2024 - row['Year']
                    mobil_rasio = row['Selling_Price'] / row['Present_Price'] if row['Present_Price'] > 0 else 1
                    
                    if (row['Selling_Price'] <= harga and 
                        mobil_umur <= umur and
                        row['Kms_Driven'] <= km and
                        mobil_rasio <= rasio and
                        row['Owner'] <= pemilik):
                        
                        skor, status = fuzzy_engine.hitung(
                            row['Selling_Price'], mobil_umur, row['Kms_Driven'],
                            mobil_rasio, row['Owner']
                        )
                        
                        results.append({
                            'No': 0,
                            'Nama Mobil': row['Car_Name'],
                            'Tahun': row['Year'],
                            'Harga (Lakh)': row['Selling_Price'],
                            'Umur': mobil_umur,
                            'KM': row['Kms_Driven'],
                            'Rasio Harga': round(mobil_rasio, 2),
                            'Pemilik': row['Owner'],
                            'BBM': row['Fuel_Type'],
                            'Transmisi': row['Transmission'],
                            'Skor Fuzzy': round(skor, 3),
                            'Status': status,
                            'disimpan': False
                        })
                    
                    progress.progress((i + 1) / total)
                
                progress.empty()
                
                if results:
                    results = sorted(results, key=lambda x: x['Skor Fuzzy'], reverse=True)
                    for i, r in enumerate(results):
                        r['No'] = i + 1
                    st.session_state.hasil_rekomendasi = results
                else:
                    st.session_state.hasil_rekomendasi = None
                    st.warning(" Tidak ada mobil yang sesuai. Longgarkan filter.")
    
    # Tampilkan hasil
    if st.session_state.hasil_rekomendasi is not None:
        results = st.session_state.hasil_rekomendasi
        
        st.markdown("---")
        st.success(f" Ditemukan {len(results)} mobil yang sesuai!")
        st.markdown("###  Hasil Rekomendasi")
        st.caption("⬆ Diurutkan dari skor tertinggi ke terendah")
        
        # Header
        hdr = st.columns([0.4, 1.8, 0.6, 0.8, 0.8, 0.6, 0.8, 1.2, 0.8])
        hdr[0].markdown("**No**")
        hdr[1].markdown("**Nama Mobil**")
        hdr[2].markdown("**Tahun**")
        hdr[3].markdown("**Harga**")
        hdr[4].markdown("**KM**")
        hdr[5].markdown("**BBM**")
        hdr[6].markdown("**Transmisi**")
        hdr[7].markdown("**Skor**")
        hdr[8].markdown("**Aksi**")
        st.divider()
        
        # Tampilkan per baris
        for i, row in enumerate(results):
            cols = st.columns([0.4, 1.8, 0.6, 0.8, 0.8, 0.6, 0.8, 1.2, 0.8])
            
            cols[0].markdown(f"**{row['No']}**")
            cols[1].markdown(f"**{row['Nama Mobil']}**")
            cols[2].markdown(f" {row['Tahun']}")
            cols[3].markdown(f" {row['Harga (Lakh)']}")
            cols[4].markdown(f" {row['KM']}")
            cols[5].markdown(f" {row['BBM']}")
            cols[6].markdown(f" {row['Transmisi']}")
            
            # Skor
            skor_val = row['Skor Fuzzy']
            if skor_val >= 0.7:
                skor_color = "#27ae60"
            elif skor_val >= 0.4:
                skor_color = "#f39c12"
            else:
                skor_color = "#e74c3c"
            
            if row['Status'] == 'Direkomendasikan':
                status_text = " Direkomendasikan"
            elif row['Status'] == 'Cukup':
                status_text = " Cukup"
            else:
                status_text = " Tidak"
            
            cols[7].markdown(f"<span style='color:{skor_color}; font-weight:bold;'> {skor_val}</span><br><small>{status_text}</small>", unsafe_allow_html=True)
            
            # Tombol simpan
            if row['disimpan']:
                cols[8].markdown(" **Tersimpan**")
            else:
                if cols[8].button(" Simpan", key=f"save_{i}"):
                    db = Database()
                    if db.connect():
                        db.create_tables()
                        db.save_rekomendasi(
                            row['Nama Mobil'], row['Tahun'], row['Harga (Lakh)'],
                            row['Umur'], row['KM'], row['Rasio Harga'],
                            row['Pemilik'], row['BBM'], row['Transmisi'],
                            row['Skor Fuzzy'], row['Status']
                        )
                        db.disconnect()
                        st.session_state.hasil_rekomendasi[i]['disimpan'] = True
                        st.rerun()
                    else:
                        st.error("Gagal konek database!")
            
            st.divider()

# ============================================
# 3. HISTORI
# ============================================
elif menu == " Histori":
    st.title(" Histori Rekomendasi")
    
    db = Database()
    if db.connect():
        df_hist = db.get_all_rekomendasi()
        db.disconnect()
        
        if df_hist.empty:
            st.info("Belum ada rekomendasi tersimpan.")
        else:
            col1, col2, col3 = st.columns(3)
            col1.metric("Total", len(df_hist))
            col2.metric("Rata-rata Skor", f"{df_hist['skor_fuzzy'].mean():.3f}")
            
            direkom = len(df_hist[df_hist['status_rekomendasi'] == 'Direkomendasikan'])
            col3.metric("Direkomendasikan", direkom)
            
            st.markdown("---")
            
            # Header
            hdr = st.columns([0.4, 1.8, 0.6, 0.8, 0.8, 0.6, 0.8, 1.2, 0.8])
            hdr[0].markdown("**No**")
            hdr[1].markdown("**Nama Mobil**")
            hdr[2].markdown("**Tahun**")
            hdr[3].markdown("**Harga**")
            hdr[4].markdown("**KM**")
            hdr[5].markdown("**BBM**")
            hdr[6].markdown("**Skor**")
            hdr[7].markdown("**Status**")
            hdr[8].markdown("**Aksi**")
            st.divider()
            
            # Tampilkan per baris
            for i, (_, row) in enumerate(df_hist.iterrows()):
                cols = st.columns([0.4, 1.8, 0.6, 0.8, 0.8, 0.6, 0.8, 1.2, 0.8])
                
                cols[0].markdown(f"**{i+1}**")
                cols[1].markdown(f"**{row['car_name']}**")
                cols[2].markdown(f" {row['year']}")
                cols[3].markdown(f" {row['selling_price']}")
                cols[4].markdown(f" {row['kms_driven']}")
                cols[5].markdown(f" {row['fuel_type']}")
                
                skor_val = row['skor_fuzzy']
                if skor_val >= 0.7:
                    skor_color = "#27ae60"
                elif skor_val >= 0.4:
                    skor_color = "#f39c12"
                else:
                    skor_color = "#e74c3c"
                
                cols[6].markdown(f"<span style='color:{skor_color}; font-weight:bold;'> {skor_val}</span>", unsafe_allow_html=True)
                
                if row['status_rekomendasi'] == 'Direkomendasikan':
                    cols[7].markdown(" **Direkomendasikan**")
                elif row['status_rekomendasi'] == 'Cukup':
                    cols[7].markdown(" **Cukup**")
                else:
                    cols[7].markdown(" **Tidak**")
                
                if cols[8].button(" Hapus", key=f"del_{row['id']}"):
                    db2 = Database()
                    if db2.connect():
                        db2.delete_rekomendasi_by_id(row['id'])
                        db2.disconnect()
                        st.rerun()
                
                st.divider()
            
            # Download
            csv = df_hist.to_csv(index=False)
            st.download_button(" Download CSV", csv, "histori.csv", "text/csv")
    else:
        st.error("Gagal konek database. Pastikan Laragon MySQL menyala.")