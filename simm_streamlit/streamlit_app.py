import streamlit as st
import re
import time
import json
import os
import pandas as pd

# --- CONFIG HALAMAN ---
st.set_page_config(page_title="MyUnpam - Academic System", page_icon="🎓", layout="wide")

# ==========================================
# 🎨 REPLIKASI DETAIL VISUAL (CSS INJECTION)
# ==========================================
style_exact_unpam = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');

/* Reset & Font Global */
* {
    font-family: 'Poppins', sans-serif;
}

/* Latar Belakang Gradasi Biru Solid */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #3B82F6 0%, #1D4ED8 100%) !important;
    background-attachment: fixed;
}
[data-testid="stHeader"] { background: rgba(0,0,0,0); }

/* --- 🔐 INTERFACE LOGIN (Replikasi Foto 1) --- */
.login-container {
    background-color: #FFFFFF;
    border-radius: 20px;
    padding: 35px;
    box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.15);
    max-width: 420px;
    margin: 60px auto 10px auto;
    text-align: center;
}
.login-logos {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}
.logo-placeholder {
    width: 50px;
    height: 50px;
    background-color: #F1F5F9;
    border-radius: 50%;
    font-size: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #94A3B8;
}
.login-title {
    font-size: 24px;
    font-weight: 600;
    color: #1E293B;
}
.input-label {
    text-align: left;
    color: #475569;
    font-size: 13px;
    font-weight: 500;
    margin-top: 15px;
    margin-bottom: 5px;
}
.error-banner-unpam {
    background-color: #991B1B;
    color: #FFFFFF !important;
    text-align: center;
    padding: 12px;
    border-radius: 8px;
    font-weight: 500;
    font-size: 14px;
    max-width: 420px;
    margin: 15px auto;
}

/* --- 📊 INTERFACE DASHBOARD (Replikasi Foto 2) --- */
/* Top Header Ungu Pastel */
.top-header-purple {
    background-color: #818CF8;
    padding: 12px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: -10px -50px 20px -50px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}
.top-header-title {
    color: white;
    font-size: 14px;
    font-weight: 500;
}

/* Sapaan Pengguna */
.user-greeting-box {
    color: #FFFFFF;
    margin-bottom: 20px;
}
.user-name { font-size: 24px; font-weight: 600; }
.user-sub { font-size: 13px; opacity: 0.9; }

/* Ringkasan Akademik Kotak Transparan */
.academic-box {
    background-color: rgba(255, 255, 255, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 16px;
    padding: 15px;
    margin-bottom: 25px;
}
.academic-box-title {
    color: #FFFFFF;
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 12px;
}

/* Modifikasi Metric Streamlit biar Mirip Kotak Putih di Foto */
[data-testid="stMetric"] {
    background-color: #FFFFFF !important;
    border-radius: 12px !important;
    padding: 10px 15px !important;
    box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.05) !important;
}
[data-testid="stMetricValue"] { color: #22C55E !important; font-weight: 700 !important; font-size: 20px !important; }
[data-testid="stMetricLabel"] { color: #475569 !important; font-size: 12px !important; font-weight: 600 !important; }

/* TAB PUTIH RAKSASA MENU UTAMA (Lekukan Atas Sesuai Foto) */
.menu-white-sheet {
    background-color: #F8FAFC !important;
    border-radius: 35px 35px 0px 0px;
    padding: 30px;
    margin: 25px -50px -50px -50px;
    min-height: 700px;
    box-shadow: 0px -10px 25px rgba(0, 0, 0, 0.05);
}
.menu-sheet-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 25px;
}
.menu-sheet-title { font-size: 20px; font-weight: 700; color: #1E293B; font-style: italic; }
.menu-sheet-link { font-size: 14px; color: #64748B; font-style: italic; }

/* Tombol Menu Grid Kustom (Menggantikan Button Bawaan) */
div.stButton > button {
    width: 100% !important;
    border-radius: 16px !important;
    padding: 20px 15px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    border: none !important;
    text-align: left !important;
    display: flex !important;
    align-items: center !important;
    box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.04) !important;
}
div.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0px 6px 16px rgba(0, 0, 0, 0.08) !important;
}

/* Warna Grid Sesuai Foto */
.m-blue button { background-color: #E0F2FE !important; color: #0369A1 !important; }
.m-purple button { background-color: #F3E8FF !important; color: #6B21A8 !important; }
.m-slate button { background-color: #F1F5F9 !important; color: #334155 !important; }
.m-login button { background-color: #3B82F6 !important; color: white !important; text-align: center !important; justify-content: center !important;}

/* Kontainer Tempat Kerja Fitur (Di bawah Grid) */
.workspace-card {
    background-color: #FFFFFF;
    border-radius: 16px;
    padding: 25px;
    margin-top: 30px;
    border: 1px solid #E2E8F0;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.02);
}
.workspace-card h3 {
    color: #1E293B !important;
    margin-bottom: 15px;
}

/* Terminal Box */
.algo-terminal {
    background-color: #0F172A;
    color: #38BDF8;
    padding: 12px 16px;
    border-left: 4px solid #38BDF8;
    border-radius: 6px;
    font-family: monospace;
    font-size: 13px;
    margin-bottom: 15px;
}
</style>
"""

# ==========================================
# 💾 DATABASE & BACKEND SYSTEM (TETAP SAMA)
# ==========================================
FILE_DATA, FILE_USERS = "data_mahasiswa.json", "data_users.json"
def load_json(f):
    if os.path.exists(f):
        with open(f, "r") as file: return json.load(file)
    return []
def save_json(d, f):
    with open(f, "w") as file: json.dump(d, file, indent=4)

if 'users_db' not in st.session_state: st.session_state['users_db'] = load_json(FILE_USERS)
if 'mahasiswa_db' not in st.session_state: st.session_state['mahasiswa_db'] = load_json(FILE_DATA)
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'username' not in st.session_state: st.session_state['username'] = ""
if 'err_msg' not in st.session_state: st.session_state['err_msg'] = ""
if 'current_tab' not in st.session_state: st.session_state['current_tab'] = "Akademik"

# ==========================================
# 🔀 ALGORITMA CORE (TETAP SAMA)
# ==========================================
def bubble_sort_mhs(daftar, kriteria):
    arr = list(daftar)
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            val_j = arr[j]['Nama'] if kriteria == "Nama" else arr[j]['NIM']
            val_j1 = arr[j+1]['Nama'] if kriteria == "Nama" else arr[j+1]['NIM']
            if val_j > val_j1: arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

def insertion_sort_mhs(daftar, kriteria):
    arr = list(daftar)
    for i in range(1, len(arr)):
        key_obj = arr[i]
        key_val = key_obj['Nama'] if kriteria == "Nama" else key_obj['NIM']
        j = i-1
        while j >= 0 and (arr[j]['Nama'] if kriteria == "Nama" else arr[j]['NIM']) > key_val:
            arr[j+1] = arr[j]
            j -= 1
        arr[j+1] = key_obj
    return arr

# ==========================================
# 🔐 RENDER: LOGIN & REGISTER (FOTO 1)
# ==========================================
if not st.session_state['logged_in']:
    st.markdown(style_exact_unpam, unsafe_allow_html=True)
    _, center_col, _ = st.columns([1, 1.2, 1])
    
    with center_col:
        st.markdown('<div style="height:40px;"></div>', unsafe_allow_html=True)
        choice = st.radio("Akses", ["LOGIN", "REGISTRASI"], horizontal=True, label_visibility="collapsed")
        
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
    <img src="https://raw.githubusercontent.com/skyskuyy4-dev/simm-streamlit/refs/heads/main/login.png" style="max-width: 100%; height: auto; border-radius: 10px;">
</div>
        """, unsafe_allow_html=True)
        
        if choice == "LOGIN":
            st.markdown('<div class="input-label">Username *</div>', unsafe_allow_html=True)
            u_in = st.text_input("", key="u_log", label_visibility="collapsed", placeholder="Username / NIM")
            st.markdown('<div class="input-label">Password *</div>', unsafe_allow_html=True)
            p_in = st.text_input("", type="password", key="p_log", label_visibility="collapsed", placeholder="••••••••")
            
            st.markdown('<div class="m-login">', unsafe_allow_html=True)
            if st.button("LOGIN", key="btn_submit_l"):
                user = next((x for x in st.session_state['users_db'] if x['username'] == u_in), None)
                if user and user['password'] == p_in:
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = u_in
                    st.session_state['err_msg'] = ""
                    st.rerun()
                else:
                    st.session_state['err_msg'] = "Akun anda sudah tidak terdaftar atau password salah"
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="input-label">Username Baru *</div>', unsafe_allow_html=True)
            u_reg = st.text_input("", key="u_reg", label_visibility="collapsed")
            st.markdown('<div class="input-label">Password Baru *</div>', unsafe_allow_html=True)
            p_reg = st.text_input("", type="password", key="p_reg", label_visibility="collapsed")
            
            st.markdown('<div class="m-login">', unsafe_allow_html=True)
            if st.button("DAFTAR", key="btn_submit_r"):
                if u_reg and p_reg:
                    st.session_state['users_db'].append({"username": u_reg, "password": p_reg})
                    save_json(st.session_state['users_db'], FILE_USERS)
                    st.success("Berhasil didaftarkan! Silakan pindah ke tab LOGIN.")
            st.markdown('</div>', unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.session_state['err_msg']:
            st.markdown(f'<div class="error-banner-unpam">{st.session_state["err_msg"]}</div>', unsafe_allow_html=True)

# ==========================================
# 📊 RENDER: DASHBOARD REPLIKASI (FOTO 2)
# ==========================================
else:
    st.markdown(style_exact_unpam, unsafe_allow_html=True)
    
    # Top Purple Header
    st.markdown("""
    <div class="top-header-purple">
        <div class="top-header-title">🎓 Learning Activities through Digital System</div>
        <div style="color:white; font-size:16px;">🔔</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sapaan Profil
    st.markdown(f"""
    <div class="user-greeting-box">
        <div class="user-name">Hai, {st.session_state['username']} 🖐️</div>
        <div class="user-sub">Administrator Hub System</div>
        <div style="font-size:11px; color:#BCF5D4; font-weight:600; margin-top:3px;">🟢 Status: Active Session</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Mempersiapkan Data
    mhs_list = st.session_state['mahasiswa_db']
    df = pd.DataFrame(mhs_list) if mhs_list else pd.DataFrame(columns=["NIM", "Nama", "Jurusan", "Angkatan"])
    
    # Ringkasan Kontainer
    st.markdown('<div class="academic-box"><div class="academic-box-title">📋 Ringkasan Akademik</div>', unsafe_allow_html=True)
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("TOTAL MHS", len(df))
    col_m2.metric("PRODI AKTIF", df["Jurusan"].nunique() if mhs_list else 0)
    col_m3.metric("RATA2 ANGKATAN", int(df["Angkatan"].mean()) if mhs_list else 0)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # --- LEMBARAN PUTIH MENU UTAMA (TAB SHEET) ---
    st.markdown('<div class="menu-white-sheet">', unsafe_allow_html=True)
    st.markdown("""
    <div class="menu-sheet-header">
        <div class="menu-sheet-title">Menu Utama</div>
        <div class="menu-sheet-link">lihat semua &gt;</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Grid 6 Tombol Menu Sesuai Warna Asli Gambar
    g1, g2 = st.columns(2)
    with g1:
        st.markdown('<div class="m-blue">', unsafe_allow_html=True)
        if st.button("👨‍🎓 &nbsp; Akademik (Tabel & Sorting)", use_container_width=True, key="m1"): st.session_state['current_tab'] = "Akademik"
        st.markdown('</div><div class="m-purple">', unsafe_allow_html=True)
        if st.button("📝 &nbsp; Registrasi Mhs (Tambah Baru)", use_container_width=True, key="m3"): st.session_state['current_tab'] = "Tambah"
        st.markdown('</div><div class="m-slate">', unsafe_allow_html=True)
        if st.button("📋 &nbsp; Log Kompleksitas Algoritma", use_container_width=True, key="m5"): st.session_state['current_tab'] = "Log"
        st.markdown('</div>', unsafe_allow_html=True)
    with g2:
        st.markdown('<div class="m-blue">', unsafe_allow_html=True)
        if st.button("🔍 &nbsp; Pencarian Cepat (Search)", use_container_width=True, key="m2"): st.session_state['current_tab'] = "Cari"
        st.markdown('</div><div class="m-purple">', unsafe_allow_html=True)
        if st.button("🔄 &nbsp; Modifikasi Informasi (Edit)", use_container_width=True, key="m4"): st.session_state['current_tab'] = "Edit"
        st.markdown('</div><div class="m-slate">', unsafe_allow_html=True)
        if st.button("🗑️ &nbsp; Eliminasi Mahasiswa (Hapus)", use_container_width=True, key="m6"): st.session_state['current_tab'] = "Hapus"
        st.markdown('</div>', unsafe_allow_html=True)
        
    # --- WORKSPACE AKSI (DI BAWAH GRID) ---
    st.markdown('<div class="workspace-card">', unsafe_allow_html=True)
    
    if st.session_state['current_tab'] == "Akademik":
        st.markdown("### 📊 Database & Pengurutan Mahasiswa")
        if mhs_list:
            c1, c2 = st.columns(2)
            with c1: alg = st.selectbox("Pilih Algoritma", ["Bubble Sort", "Insertion Sort"])
            with c2: crit = st.selectbox("Kriteria Urut", ["NIM", "Nama"])
            
            t_start = time.time()
            data_terurut = bubble_sort_mhs(mhs_list, crit) if alg == "Bubble Sort" else insertion_sort_mhs(mhs_list, crit)
            t_end = time.time()
            
            st.markdown(f'<div class="algo-terminal">⚙️ {alg} Aktif | Waktu Proses: {(t_end - t_start)*1000:.4f} ms</div>', unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(data_terurut), use_container_width=True)
        else:
            st.info("Data kosong. Silakan tambah data terlebih dahulu melalui menu Registrasi.")
            
    elif st.session_state['current_tab'] == "Cari":
        st.markdown("### 🔍 Pencarian Mahasiswa")
        key = st.text_input("Masukkan Nama atau NIM Mahasiswa:")
        if key and mhs_list:
            hasil = [d for d in mhs_list if key.lower() in d['Nama'].lower() or key.lower() in d['NIM'].lower()]
            if hasil: st.dataframe(pd.DataFrame(hasil), use_container_width=True)
            else: st.error("Data tidak ditemukan.")
            
    elif st.session_state['current_tab'] == "Tambah":
        st.markdown("### ➕ Tambah Mahasiswa")
        with st.form("add_m"):
            nim_in = st.text_input("NIM (8 Angka)")
            nama_in = st.text_input("Nama Lengkap")
            jur_in = st.selectbox("Jurusan", ["Teknik Informatika", "Sistem Informasi"])
            ang_in = st.number_input("Angkatan", min_value=2020, value=2024)
            if st.form_submit_button("Simpan"):
                try:
                    if not re.match(r"^\d{8}$", nim_in): raise ValueError("NIM harus tepat 8 digit angka murni.")
                    if any(x['NIM'] == nim_in for x in mhs_list): raise KeyError("NIM sudah digunakan.")
                    st.session_state['mahasiswa_db'].append({"NIM": nim_in, "Nama": nama_in, "Jurusan": jur_in, "Angkatan": int(ang_in)})
                    save_json(st.session_state['mahasiswa_db'], FILE_DATA)
                    st.success("Data berhasil tersimpan!"); time.sleep(0.5); st.rerun()
                except Exception as e: st.error(f"Error: {e}")
                
    elif st.session_state['current_tab'] == "Edit":
        st.markdown("### 🔄 Modifikasi Data")
        if mhs_list:
            n_pilih = st.selectbox("Pilih NIM Target", [d['NIM'] for d in mhs_list])
            idx = next(i for i, d in enumerate(mhs_list) if d['NIM'] == n_pilih)
            with st.form("ed_f"):
                nm_baru = st.text_input("Nama Baru", value=mhs_list[idx]['Nama'])
                if st.form_submit_button("Perbarui"):
                    st.session_state['mahasiswa_db'][idx]['Nama'] = nm_baru
                    save_json(st.session_state['mahasiswa_db'], FILE_DATA)
                    st.success("Berhasil diubah!"); time.sleep(0.5); st.rerun()
                    
    elif st.session_state['current_tab'] == "Hapus":
        st.markdown("### ❌ Hapus Data")
        if mhs_list:
            n_del = st.selectbox("Pilih NIM yang akan dihapus", [d['NIM'] for d in mhs_list])
            if st.button("HAPUS PERMANEN", type="primary"):
                st.session_state['mahasiswa_db'] = [d for d in mhs_list if d['NIM'] != n_del]
                save_json(st.session_state['mahasiswa_db'], FILE_DATA)
                st.success("Terhapus!"); time.sleep(0.5); st.rerun()
                
    elif st.session_state['current_tab'] == "Log":
        st.markdown("### ⚙️ Analisis Kinerja Kompleksitas")
        st.markdown('<div class="algo-terminal">🔴 Bubble / Insertion Sort: Worst Case O(n²) | Best Case O(n)</div>', unsafe_allow_html=True)
        st.markdown('<div class="algo-terminal">🔵 Linear Search Complexity: O(n)</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True) # Tutup Workspace
    st.markdown('</div>', unsafe_allow_html=True) # Tutup Lembaran Putih Menu
    
    # Sidebar Minimalis untuk Logout
    if st.sidebar.button("Keluar (Logout)", type="primary"):
        st.session_state['logged_in'] = False
        st.rerun()
