# ============================================
# SCPK PEMILIHAN MOBIL TERBAIK
# Streamlit UI - Metode Fuzzy Mamdani
# ============================================
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time

from database import Database
from fuzzy_logic import FuzzyMobil

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="SPK Mobil Terbaik",
    page_icon="🚗",
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
    st.title("SPK Mobil Terbaik")
    st.markdown("*Metode Fuzzy Mamdani*")
    
    if st.session_state.dataset_loaded and st.session_state.df_mobil is not None:
        st.success(f"Dataset: {len(st.session_state.df_mobil)} data siap")
    else:
        st.warning("Dataset belum diupload")
    
    st.markdown("---")
    
    menu = st.radio(
        "Menu",
        ["Upload Dataset", "Rekomendasi", "Histori"]
    )
    
    st.markdown("---")
    st.caption("(c) 2024 SCPK Fuzzy Mobil")

# ============================================
# 1. UPLOAD DATASET
# ============================================
if menu == "Upload Dataset":
    st.title("Upload Dataset CSV")
    st.markdown("Upload file CSV dataset mobil untuk diproses.")
    
    if st.session_state.dataset_loaded and st.session_state.df_mobil is not None:
        st.info(f"Dataset sudah terload: **{len(st.session_state.df_mobil)}** mobil")
        st.markdown("---")
        st.markdown("### Upload Ulang (Opsional)")
    
    uploaded = st.file_uploader("Pilih file CSV", type="csv", key="upload_csv")
    
    if uploaded:
        df = pd.read_csv(uploaded)
        st.session_state.df_mobil = df
        st.session_state.dataset_loaded = True
        st.session_state.hasil_rekomendasi = None
        
        st.success(f"Berhasil load {len(df)} data mobil!")
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
            st.success(f"Dataset tersedia: **{len(df)}** mobil")
            st.markdown("### Preview Dataset")
            st.dataframe(df.head(20), use_container_width=True)
        else:
            st.info("Silakan upload file CSV untuk memulai.")

# ============================================
# 2. REKOMENDASI
# ============================================
elif menu == "Rekomendasi":
    st.title("Rekomendasi Mobil")
    
    if not st.session_state.dataset_loaded or st.session_state.df_mobil is None:
        st.warning("Upload dataset terlebih dahulu di menu Upload Dataset!")
    else:
        st.markdown("### Filter Kriteria")
        
        col1, col2 = st.columns(2)
        
        with col1:
            harga = st.slider("Harga Maksimal (Lakh)", 0.0, 40.0, 15.0, 0.5)
            umur = st.slider("Umur Maksimal (Tahun)", 0, 25, 8)
            pemilik = st.slider("Maks. Pemilik Sebelumnya", 0, 5, 2)
        
        with col2:
            km = st.slider("KM Maksimal", 0, 250000, 80000, 5000)
            rasio = st.slider("Rasio Harga Maksimal", 0.0, 1.2, 0.8, 0.05)
        
        if st.button("Hitung Rekomendasi", use_container_width=True):
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
                    st.warning("Tidak ada mobil yang sesuai. Longgarkan filter.")
    
    # Tampilkan hasil
    if st.session_state.hasil_rekomendasi is not None:
        results = st.session_state.hasil_rekomendasi
        
        st.markdown("---")
        st.success(f"Ditemukan {len(results)} mobil yang sesuai!")
        
        # ============================================
        # PROSES SPK
        # ============================================
        st.markdown("## Proses SPK (Fuzzy Mamdani)")
        
        pilihan = st.selectbox(
            "Pilih mobil untuk melihat proses fuzzy:",
            options=range(len(results)),
            format_func=lambda x: f"Rank #{x+1} - {results[x]['Nama Mobil']} (Skor: {results[x]['Skor Fuzzy']})"
        )
        mobil_terpilih = results[pilihan]
        
        st.info(f"Menampilkan proses fuzzy untuk: **{mobil_terpilih['Nama Mobil']}**")
        
        derajat = fuzzy_engine.get_derajat_keanggotaan(
            mobil_terpilih['Harga (Lakh)'],
            mobil_terpilih['Umur'],
            mobil_terpilih['KM'],
            mobil_terpilih['Rasio Harga'],
            mobil_terpilih['Pemilik']
        )
        
        # --- TABEL DERAJAT KEANGGOTAAN ---
        st.markdown("### Tabel Derajat Keanggotaan (Fuzzifikasi)")
        
        data_fuzzifikasi = []
        var_labels = {
            "harga": ("Harga Jual", f"{mobil_terpilih['Harga (Lakh)']} Lakh"),
            "umur": ("Umur Mobil", f"{mobil_terpilih['Umur']} Tahun"),
            "km": ("Jarak Tempuh", f"{mobil_terpilih['KM']} KM"),
            "rasio_harga": ("Rasio Harga", f"{mobil_terpilih['Rasio Harga']}"),
            "pemilik": ("Riwayat Pemilik", f"{mobil_terpilih['Pemilik']}"),
        }
        
        for var_key, (var_name, var_value) in var_labels.items():
            row = {
                "Variabel": var_name,
                "Nilai Input": var_value,
            }
            for set_name, mu in derajat[var_key].items():
                row[set_name.capitalize()] = f"{mu:.3f}"
            data_fuzzifikasi.append(row)
        
        df_fuzzifikasi = pd.DataFrame(data_fuzzifikasi)
        st.dataframe(df_fuzzifikasi, use_container_width=True, hide_index=True)
        
        # --- GRAFIK 1: KURVA KEANGGOTAAN ---
        st.markdown("### Grafik 1: Kurva Keanggotaan (Membership Function)")
        
        fig1, axes = plt.subplots(2, 3, figsize=(15, 10))
        axes = axes.flatten()
        var_keys = list(var_labels.keys())
        
        for idx, var_key in enumerate(var_keys):
            ax = axes[idx]
            var_info = fuzzy_engine.variables[var_key]
            x_range = np.linspace(var_info['range'][0], var_info['range'][1], 500)
            
            colors = ['#E63946', '#3498db', '#2ecc71']
            
            for j, (set_name, params) in enumerate(var_info['sets'].items()):
                y = [fuzzy_engine._fuzzify(x, params) for x in x_range]
                ax.plot(x_range, y, color=colors[j], linewidth=2, label=set_name.capitalize())
                ax.fill_between(x_range, 0, y, color=colors[j], alpha=0.1)
            
            if var_key == "harga":
                input_val = mobil_terpilih['Harga (Lakh)']
            elif var_key == "umur":
                input_val = mobil_terpilih['Umur']
            elif var_key == "km":
                input_val = mobil_terpilih['KM']
            elif var_key == "rasio_harga":
                input_val = mobil_terpilih['Rasio Harga']
            else:
                input_val = mobil_terpilih['Pemilik']
            
            ax.axvline(x=input_val, color='yellow', linestyle='--', linewidth=2, label=f'Input: {input_val}')
            ax.set_title(var_labels[var_key][0], fontweight='bold', fontsize=12)
            ax.set_xlabel('Nilai')
            ax.set_ylabel('Derajat Keanggotaan')
            ax.legend(loc='best', fontsize=8)
            ax.grid(True, alpha=0.3)
            ax.set_ylim(0, 1.1)
        
        axes[5].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig1)
        plt.close()
        
        # --- TABEL DEFUZZIFIKASI ---
        st.markdown("### Tabel Proses Defuzzifikasi")
        
        derajat_input = {
            "harga": derajat["harga"],
            "umur": derajat["umur"],
            "km": derajat["km"],
            "rasio_harga": derajat["rasio_harga"],
            "pemilik": derajat["pemilik"],
        }
        aggregated, _ = fuzzy_engine._inferensi(derajat_input)
        
        centroids = {
            "Tidak Direkomendasikan": 0.20,
            "Cukup": 0.50,
            "Direkomendasikan": 0.80,
        }
        
        data_defuzz = []
        numerator_total = 0
        denominator_total = 0
        
        for name, mu_val in aggregated.items():
            label_map = {
                "tidak_direkomendasikan": "Tidak Direkomendasikan",
                "cukup": "Cukup",
                "direkomendasikan": "Direkomendasikan",
            }
            label = label_map[name]
            centroid = centroids[label]
            hasil_kali = mu_val * centroid
            
            data_defuzz.append({
                "Kategori Output": label,
                "Derajat": f"{mu_val:.3f}",
                "Titik Tengah": centroid,
                "Derajat x Titik Tengah": f"{hasil_kali:.3f}",
            })
            
            numerator_total += hasil_kali
            denominator_total += mu_val
        
        data_defuzz.append({
            "Kategori Output": "TOTAL",
            "Derajat": f"{denominator_total:.3f}",
            "Titik Tengah": "",
            "Derajat x Titik Tengah": f"{numerator_total:.3f}",
        })
        
        df_defuzz = pd.DataFrame(data_defuzz)
        st.dataframe(df_defuzz, use_container_width=True, hide_index=True)
        
        skor_akhir = mobil_terpilih['Skor Fuzzy']
        
        st.markdown(f"""
        <div style="background-color:#1a1f2e; padding:15px; border-radius:10px; border:1px solid #30363d;">
        <h4>Rumus Defuzzifikasi (Weighted Average)</h4>
        <p style="font-size:1.1rem;">
        <b>Skor = SUM(Derajat x Titik Tengah) / SUM(Derajat)</b><br>
        <b>Skor = {numerator_total:.3f} / {denominator_total:.3f} = <span style="color:#2ecc71; font-size:1.3rem;">{skor_akhir:.3f}</span></b><br>
        <b>Status: {mobil_terpilih['Status']}</b>
        </p>
        </div>
        """, unsafe_allow_html=True)
        
        # --- GRAFIK 2: HASIL AKHIR ---
        st.markdown("### Grafik 2: Hasil Akhir Fuzzy (Defuzzifikasi)")
        
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        
        x_out = np.linspace(0, 1, 200)
        
        y_tidak = [fuzzy_engine._fuzzify(x, [0, 0, 0.4]) for x in x_out]
        ax2.plot(x_out, y_tidak, 'r-', linewidth=2, label='Tidak Direkomendasikan')
        ax2.fill_between(x_out, 0, y_tidak, color='red', alpha=0.05)
        
        y_cukup = [fuzzy_engine._fuzzify(x, [0.3, 0.5, 0.7]) for x in x_out]
        ax2.plot(x_out, y_cukup, 'orange', linewidth=2, label='Cukup')
        ax2.fill_between(x_out, 0, y_cukup, color='orange', alpha=0.05)
        
        y_dir = [fuzzy_engine._fuzzify(x, [0.6, 1, 1]) for x in x_out]
        ax2.plot(x_out, y_dir, 'g-', linewidth=2, label='Direkomendasikan')
        ax2.fill_between(x_out, 0, y_dir, color='green', alpha=0.05)
        
        for name, mu_val in aggregated.items():
            if mu_val > 0:
                if name == "tidak_direkomendasikan":
                    color = 'red'
                elif name == "cukup":
                    color = 'orange'
                else:
                    color = 'green'
                ax2.axhline(y=mu_val, color=color, linestyle='--', alpha=0.7, linewidth=1.5)
                ax2.text(0.02, mu_val + 0.02, f'{name}: {mu_val:.3f}', fontsize=9, color=color)
        
        ax2.axvline(x=skor_akhir, color='blue', linestyle='-', linewidth=3, 
                    label=f'Skor Akhir: {skor_akhir:.3f} ({mobil_terpilih["Status"]})')
        
        ax2.set_xlabel('Skor', fontsize=12)
        ax2.set_ylabel('Derajat Keanggotaan', fontsize=12)
        ax2.set_title(f'Hasil Defuzzifikasi - {mobil_terpilih["Nama Mobil"]}', fontweight='bold', fontsize=14)
        ax2.legend(loc='upper center', fontsize=9)
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(0, 1.1)
        
        st.pyplot(fig2)
        plt.close()
        
        # ============================================
        # TABEL HASIL REKOMENDASI
        # ============================================
        st.markdown("---")
        st.markdown("## Hasil Rekomendasi")
        st.caption("Diurutkan dari skor tertinggi ke terendah")
        
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
        
        for i, row in enumerate(results):
            cols = st.columns([0.4, 1.8, 0.6, 0.8, 0.8, 0.6, 0.8, 1.2, 0.8])
            
            cols[0].markdown(f"**{row['No']}**")
            cols[1].markdown(f"**{row['Nama Mobil']}**")
            cols[2].markdown(f"{row['Tahun']}")
            cols[3].markdown(f"Rs. {row['Harga (Lakh)']}")
            cols[4].markdown(f"{row['KM']}")
            cols[5].markdown(f"{row['BBM']}")
            cols[6].markdown(f"{row['Transmisi']}")
            
            skor_val = row['Skor Fuzzy']
            if skor_val >= 0.7:
                skor_color = "#27ae60"
            elif skor_val >= 0.4:
                skor_color = "#f39c12"
            else:
                skor_color = "#e74c3c"
            
            cols[7].markdown(f"<span style='color:{skor_color}; font-weight:bold;'>Skor: {skor_val}</span><br><small>{row['Status']}</small>", unsafe_allow_html=True)
            
            if row['disimpan']:
                cols[8].markdown("**Tersimpan**")
            else:
                if cols[8].button("Simpan", key=f"save_{i}"):
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
elif menu == "Histori":
    st.title("Histori Rekomendasi")
    
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
            
            for i, (_, row) in enumerate(df_hist.iterrows()):
                cols = st.columns([0.4, 1.8, 0.6, 0.8, 0.8, 0.6, 0.8, 1.2, 0.8])
                
                cols[0].markdown(f"**{i+1}**")
                cols[1].markdown(f"**{row['car_name']}**")
                cols[2].markdown(f"{row['year']}")
                cols[3].markdown(f"Rs. {row['selling_price']}")
                cols[4].markdown(f"{row['kms_driven']}")
                cols[5].markdown(f"{row['fuel_type']}")
                
                skor_val = row['skor_fuzzy']
                if skor_val >= 0.7:
                    skor_color = "#27ae60"
                elif skor_val >= 0.4:
                    skor_color = "#f39c12"
                else:
                    skor_color = "#e74c3c"
                
                cols[6].markdown(f"<span style='color:{skor_color}; font-weight:bold;'>Skor: {skor_val}</span>", unsafe_allow_html=True)
                
                if row['status_rekomendasi'] == 'Direkomendasikan':
                    cols[7].markdown("**Direkomendasikan**")
                elif row['status_rekomendasi'] == 'Cukup':
                    cols[7].markdown("**Cukup**")
                else:
                    cols[7].markdown("**Tidak Direkomendasikan**")
                
                if cols[8].button("Hapus", key=f"del_{row['id']}"):
                    db2 = Database()
                    if db2.connect():
                        db2.delete_rekomendasi_by_id(row['id'])
                        db2.disconnect()
                        st.rerun()
                
                st.divider()
            
            csv = df_hist.to_csv(index=False)
            st.download_button("Download CSV", csv, "histori.csv", "text/csv")
    else:
        st.error("Gagal konek database. Pastikan Laragon MySQL menyala.")