import streamlit as st
import re
import time
import json
import os
import pandas as pd

# ==========================================
# 🎓 1. KONFIGURASI HALAMAN & THEME (GUI)
# ==========================================
st.set_page_config(page_title="Sistem Akademik Kampus", page_icon="🎓", layout="wide")

# CSS Kustom untuk Replikasi Total UI MyUnpam (Halaman Login & Dashboard)
style_unpam_premium = """
<style>
/* Background Utama Gradasi Biru-Ungu Kampus */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #1E40AF 0%, #0284C7 50%, #818CF8 100%) !important;
    background-attachment: fixed;
}
[data-testid="stHeader"] { background: rgba(0,0,0,0); }
[data-testid="stSidebar"] { background-color: rgba(255,255,255,0.95) !important; }

/* Wrapper Form Login & Registrasi (Card Putih Tengah) */
.unpam-login-card {
    background-color: #FFFFFF !important;
    border-radius: 16px;
    padding: 35px 40px;
    box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.25);
    max-width: 450px;
    margin: 60px auto 20px auto;
    text-align: center;
}
.unpam-login-card label, .unpam-login-card p { 
    color: #334155 !important; 
    font-weight: 600; 
    text-align: left;
}

/* Banner Pesan Error Merah di Bagian Bawah Form */
.error-banner-unpam {
    background-color: #DC2626; 
    color: white !important; 
    text-align: center;
    padding: 12px; 
    border-radius: 8px; 
    font-weight: bold; 
    font-size: 14px;
    max-width: 450px; 
    margin: 15px auto 0 auto; 
    box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
}

/* Kotak Sapaan Profil Admin */
.profile-greeting-box {
    background-color: rgba(255, 255, 255, 0.15);
    padding: 22px;
    border-radius: 16px;
    margin-bottom: 25px;
    border: 1px solid rgba(255, 255, 255, 0.25);
}

/* Kontainer Ringkasan Akademik Pastel */
.summary-academic-box {
    background: linear-gradient(90deg, #CFFAFE 0%, #E0F2FE 100%);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 30px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
}

/* Kartu Putih Kontainer Fitur Utama */
.main-feature-card {
    background-color: rgba(255, 255, 255, 0.95);
    border-radius: 20px;
    padding: 30px;
    box-shadow: 0px 10px 25px rgba(0, 0, 0, 0.08);
}

/* Terminal Log untuk Kompleksitas Algoritma */
.terminal-complexity {
    background-color: #0F172A; 
    color: #38BDF8; 
    padding: 12px 16px; 
    border-left: 4px solid #38BDF8; 
    border-radius: 6px; 
    font-family: 'Fira Code', monospace; 
    font-size: 13px; 
    margin-bottom: 20px;
}

/* Pengaturan Tombol Modifikasi */
div.stButton > button {
    border-radius: 8px !important;
    font-weight: bold !important;
}
</style>
"""
st.markdown(style_unpam_premium, unsafe_allow_html=True)


# ==========================================
# 🏛️ 2. BACKEND ENGINE: OOP & FILE I/O
# ==========================================
class Orang:
    """Class Induk (Konsep Pewarisan)"""
    def __init__(self, nama: str):
        self._nama = nama  # Protected Attribute (Enkapsulasi)
        
    def get_info(self):
        return f"Nama: {self._nama}"

class Mahasiswa(Orang):
    """Class Anak (Konsep Pewarisan)"""
    def __init__(self, nim: str, nama: str, jurusan: str, angkatan: int):
        super().__init__(nama)
        self.__nim = nim          # Private Attribute (Enkapsulasi Ketat)
        self.jurusan = jurusan    
        self.angkatan = angkatan  
        
    # Fungsi Getter & Setter
    def get_nim(self): return self.__nim
    def get_nama(self): return self._nama
    def set_nama(self, nama_baru): self._nama = nama_baru

    def get_info(self):
        """Override Method (Polimorfisme)"""
        return f"Mahasiswa: {self._nama} ({self.__nim}) - {self.jurusan}"

    def to_dict(self):
        return {"NIM": self.__nim, "Nama": self._nama, "Jurusan": self.jurusan, "Angkatan": self.angkatan}

FILE_DATA = "data_mahasiswa.json"
FILE_USERS = "data_users.json"

def muat_data_json(file_name):
    if os.path.exists(file_name):
        try:
            with open(file_name, "r") as f: return json.load(f)
        except: return []
    return []

def simpan_data_json(data, file_name):
    with open(file_name, "w") as f: json.dump(data, f, indent=4)

# Inisialisasi State Basis Data ke Array Sistem (Session State)
if 'users_db' not in st.session_state: st.session_state['users_db'] = muat_data_json(FILE_USERS)
if 'mahasiswa_db' not in st.session_state: st.session_state['mahasiswa_db'] = muat_data_json(FILE_DATA)
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'username' not in st.session_state: st.session_state['username'] = ""
if 'error_msg' not in st.session_state: st.session_state['error_msg'] = ""
if 'current_menu' not in st.session_state: st.session_state['current_menu'] = "Ringkasan"


# ==========================================
# 🔀 3. ALGORITMA CORE ENGINE (SORT & SEARCH)
# ==========================================
def bubble_sort_mhs(daftar, kriteria):
    arr = list(daftar)
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            val_j = arr[j]['Nama'] if kriteria == "Nama" else arr[j]['NIM']
            val_j1 = arr[j+1]['Nama'] if kriteria == "Nama" else arr[j+1]['NIM']
            if val_j > val_j1:
                arr[j], arr[j+1] = arr[j+1], arr[j]
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

def linear_search_mhs(daftar, kunci):
    return [d for d in daftar if kunci.lower() in d['NIM'].lower() or kunci.lower() in d['Nama'].lower()]


# ==========================================
# 🔐 4. INTERFACE AUTENTIKASI (LOGIN & REGISTER)
# ==========================================
if not st.session_state['logged_in']:
    _, center_col, _ = st.columns([1, 1.4, 1])
    with center_col:
        st.markdown("<h1 style='text-align: center; color: white; margin-top:40px; font-weight:800;'>Learning Activities Digital System</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: white; font-size: 16px; opacity:0.85;'>Universitas Pamulang Portal</p>", unsafe_allow_html=True)
        
        auth_choice = st.radio("Akses Otentikasi", ["MASUK (LOGIN)", "DAFTAR AKUN BARU"], horizontal=True)
        st.markdown('<div class="unpam-login-card">', unsafe_allow_html=True)
        
        if auth_choice == "MASUK (LOGIN)":
            st.markdown("<h2 style='color: #1E293B; margin-bottom: 25px; font-weight:700;'>LOGIN</h2>", unsafe_allow_html=True)
            u_login = st.text_input("Username / NIM *", placeholder="Masukkan Kredensial")
            p_login = st.text_input("Password *", type="password", placeholder="••••••••••••")
            
            if st.button("LOGIN", use_container_width=True, type="primary"):
                found = next((u for u in st.session_state['users_db'] if u['username'] == u_login), None)
                if found and found['password'] == p_login:
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = u_login
                    st.session_state['error_msg'] = ""
                    st.rerun()
                else:
                    st.session_state['error_msg'] = "Akun anda sudah tidak terdaftar atau password salah"
                    st.rerun()

        elif auth_choice == "DAFTAR AKUN BARU":
            st.markdown("<h2 style='color: #1E293B; margin-bottom: 25px; font-weight:700;'>REGISTRASI ADMIN</h2>", unsafe_allow_html=True)
            u_reg = st.text_input("Username Admin Baru *", placeholder="Contoh: admin_informatika")
            p_reg = st.text_input("Password Baru *", type="password")
            p_conf = st.text_input("Konfirmasi Password *", type="password")
            
            if st.button("DAFTAR", use_container_width=True, type="primary"):
                if u_reg and p_reg:
                    if p_reg == p_conf:
                        if any(u['username'] == u_reg for u in st.session_state['users_db']):
                            st.session_state['error_msg'] = "Username sudah terpakai!"
                            st.rerun()
                        else:
                            st.session_state['users_db'].append({"username": u_reg, "password": p_reg})
                            simpan_data_json(st.session_state['users_db'], FILE_USERS)
                            st.session_state['error_msg'] = ""
                            st.success("Akun terdaftar! Silakan pindah ke tab LOGIN.")
                    else:
                        st.session_state['error_msg'] = "Konfirmasi password tidak cocok!"
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.session_state['error_msg']:
            st.markdown(f'<div class="error-banner-unpam">{st.session_state["error_msg"]}</div>', unsafe_allow_html=True)


# ==========================================
# 📊 5. INTERFACE DASHBOARD UTAMA ADMIN
# ==========================================
else:
    # --- HEADER Sapaan Personal ---
    st.markdown(f"""
    <div class="profile-greeting-box">
        <span style="font-size: 26px; font-weight: 700; color: white;">Hai, {st.session_state['username']} 👋</span><br>
        <span style="font-size: 14px; color: white; opacity: 0.9;">Sistem Aktivitas Pembelajaran Digital Universitas Pamulang</span><br>
        <span style="font-size: 12px; color: #6EE7B7; font-weight: bold;">🟢 Role: Administrator Sistem</span>
    </div>
    """, unsafe_allow_html=True)

    db_mhs = st.session_state['mahasiswa_db']
    df_mhs = pd.DataFrame(db_mhs) if db_mhs else pd.DataFrame(columns=["NIM", "Nama", "Jurusan", "Angkatan"])

    # --- WIDGET RINGKASAN AKADEMIK ---
    st.markdown('<div class="summary-academic-box"><b style="color:#0369A1; font-size:15px;">📋 Ringkasan Akademik Global</b>', unsafe_allow_html=True)
    mc1, mc2, mc3 = st.columns(3)
    mc1.metric("Total Mahasiswa Terdaftar", len(df_mhs))
    mc2.metric("Total Program Studi Aktif", df_mhs["Jurusan"].nunique() if db_mhs else 0)
    mc3.metric("Rata-rata Angkatan", int(df_mhs["Angkatan"].mean()) if db_mhs else 0)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- NAVIGASI GRID MENU UTAMA ---
    st.markdown("<h4 style='color: white; margin-bottom: 12px;'>📂 Navigasi Menu Utama</h4>", unsafe_allow_html=True)
    gc1, gc2, gc3 = st.columns(3)
    with gc1:
        if st.button("📊 Tampilkan & Urutkan Data", use_container_width=True): st.session_state['current_menu'] = "Ringkasan"
        if st.button("➕ Tambah Mahasiswa Baru", use_container_width=True): st.session_state['current_menu'] = "Tambah"
    with gc2:
        if st.button("🔍 Pencarian Cepat Algoritma", use_container_width=True): st.session_state['current_menu'] = "Cari"
        if st.button("🔄 Edit Informasi Data", use_container_width=True): st.session_state['current_menu'] = "Edit"
    with gc3:
        if st.button("❌ Hapus Data Permanen", use_container_width=True): st.session_state['current_menu'] = "Hapus"
        if st.button("🚪 Keluar (Logout System)", type="primary", use_container_width=True):
            st.session_state['logged_in'] = False
            st.session_state['username'] = ""
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # --- KONTAINER AKSI DINAMIS ---
    st.markdown('<div class="main-feature-card">', unsafe_allow_html=True)

    # A. MENU: RINGKASAN & SORTING
    if st.session_state['current_menu'] == "Ringkasan":
        st.markdown("<h3 style='color:#1E293B !important;'>📋 Daftar Seluruh Mahasiswa</h3>", unsafe_allow_html=True)
        if db_mhs:
            sc1, sc2 = st.columns(2)
            with sc1: v_alg = st.selectbox("Pilih Algoritma Sorting", ["Bubble Sort", "Insertion Sort"])
            with sc2: v_crit = st.selectbox("Urutkan Berdasarkan Kriteria", ["NIM", "Nama"])
            
            t_start = time.time()
            data_terurut = bubble_sort_mhs(db_mhs, v_crit) if v_alg == "Bubble Sort" else insertion_sort_mhs(db_mhs, v_crit)
            t_end = time.time()
            
            st.markdown(f'<div class="terminal-complexity">⚙️ {v_alg} Berhasil | Time Complexity: O(n²) | Waktu Eksekusi: {(t_end - t_start)*1000:.4f} ms</div>', unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(data_terurut), use_container_width=True)
        else:
            st.info("Sistem kosong. Silakan gunakan menu tambah data.")

    # B. MENU: CARI DATA
    elif st.session_state['current_menu'] == "Cari":
        st.markdown("<h3 style='color:#1E293B !important;'>🔍 Pencarian Data Mahasiswa</h3>", unsafe_allow_html=True)
        q_search = st.text_input("Ketik Kata Kunci (Nama / NIM):")
        m_search = st.selectbox("Pilih Algoritma Pencarian", ["Linear Search", "Binary Search (Spesifik NIM)"])
        
        if q_search:
            t_start = time.time()
            if m_search == "Linear Search":
                hasil = linear_search_mhs(db_mhs, q_search)
                c_msg = "🔵 Linear Search Complexity: O(n)"
            else:
                # Simulasi Binary Search internal
                db_sorted = sorted(db_mhs, key=lambda x: x['NIM'])
                hasil = [d for d in db_sorted if d['NIM'] == q_search]
                c_msg = "🟢 Binary Search Complexity: O(log n)"
            t_end = time.time()
            
            st.markdown(f'<div class="terminal-complexity">{c_msg} | Waktu Eksekusi: {(t_end - t_start)*1000:.4f} ms</div>', unsafe_allow_html=True)
            if hasil: st.dataframe(pd.DataFrame(hasil), use_container_width=True)
            else: st.error("Data tidak ditemukan.")

    # C. MENU: TAMBAH DATA (Try-Catch & Regex)
    elif st.session_state['current_menu'] == "Tambah":
        st.markdown("<h3 style='color:#1E293B !important;'>➕ Input Mahasiswa Baru</h3>", unsafe_allow_html=True)
        with st.form("f_add"):
            i_nim = st.text_input("NIM Mahasiswa (Wajib 8 Digit Angka)")
            i_nama = st.text_input("Nama Lengkap")
            i_jur = st.selectbox("Program Studi", ["Teknik Informatika", "Sistem Informasi", "Sistem Komputer"])
            i_ang = st.number_input("Angkatan", min_value=2020, max_value=2026, value=2024)
            
            if st.form_submit_button("Simpan Permanen"):
                try:
                    if not re.match(r"^\d{8}$", i_nim):
                        raise ValueError("Format Gagal! NIM wajib berisi tepat 8 digit angka.")
                    if any(d['NIM'] == i_nim for d in db_mhs):
                        raise KeyError("NIM sudah terdaftar di dalam sistem!")
                        
                    # Menggunakan konsep instansiasi OOP Mahasiswa
                    obj_mhs = Mahasiswa(i_nim, i_nama, i_jur, int(i_ang))
                    st.session_state['mahasiswa_db'].append(obj_mhs.to_dict())
                    simpan_data_json(st.session_state['mahasiswa_db'], FILE_DATA)
                    st.success(f"Sukses! Data {obj_mhs.get_nama()} tersimpan di array memori dan file JSON.")
                    time.sleep(1); st.rerun()
                except (ValueError, KeyError) as e:
                    st.error(f"❌ Terjadi Penolakan: {e}")

    # D. MENU: EDIT DATA
    elif st.session_state['current_menu'] == "Edit":
        st.markdown("<h3 style='color:#1E293B !important;'>🔄 Perbarui Data Mahasiswa</h3>", unsafe_allow_html=True)
        if db_mhs:
            nim_edit = st.selectbox("Pilih NIM Target", [d['NIM'] for d in db_mhs])
            idx = next(i for i, d in enumerate(db_mhs) if d['NIM'] == nim_edit)
            
            with st.form("f_edit"):
                u_nama = st.text_input("Nama Baru", value=db_mhs[idx]['Nama'])
                u_jur = st.selectbox("Jurusan Baru", ["Teknik Informatika", "Sistem Informasi", "Sistem Komputer"], 
                                     index=["Teknik Informatika", "Sistem Informasi", "Sistem Komputer"].index(db_mhs[idx]['Jurusan']))
                
                if st.form_submit_button("Simpan Perubahan"):
                    st.session_state['mahasiswa_db'][idx]['Nama'] = u_nama
                    st.session_state['mahasiswa_db'][idx]['Jurusan'] = u_jur
                    simpan_data_json(st.session_state['mahasiswa_db'], FILE_DATA)
                    st.success("Data berhasil dimodifikasi!")
                    time.sleep(1); st.rerun()

    # E. MENU: HAPUS DATA
    elif st.session_state['current_menu'] == "Hapus":
        st.markdown("<h3 style='color:#1E293B !important;'>❌ Hapus Data Permanen</h3>", unsafe_allow_html=True)
        if db_mhs:
            nim_del = st.selectbox("Pilih NIM yang akan Dihapus", [d['NIM'] for d in db_mhs])
            if st.button("HAPUS DARI JALUR MEMORI & FILE", type="primary"):
                st.session_state['mahasiswa_db'] = [d for d in db_mhs if d['NIM'] != nim_del]
                simpan_data_json(st.session_state['mahasiswa_db'], FILE_DATA)
                st.success("Data sukses dieliminasi dari sistem.")
                time.sleep(1); st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
