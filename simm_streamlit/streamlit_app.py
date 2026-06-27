import streamlit as st
import re
import time
import json
import os
import pandas as pd  # Memastikan pandas terimport dengan benar

# --- KONFIGURASI HALAMAN & THEME ---
st.set_page_config(page_title="Sistem Manajemen Mahasiswa Super", page_icon="🎓", layout="wide")

# Custom CSS untuk background menarik dan layout clean bagi Admin
background_url = "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?q=80&w=1920"
st.markdown(f"""
<style>
[data-testid="stAppViewContainer"] {{
    background-image: linear-gradient(rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0.75)), url("{background_url}");
    background-size: cover; background-position: center; background-attachment: fixed;
}}
[data-testid="stSidebar"] {{ background-color: rgba(255, 255, 255, 0.95); }}
.stForm, .stAlert, [data-testid="stDataFrameFormColumns"] {{ 
    background-color: rgba(255, 255, 255, 0.95) !important; 
    border-radius: 10px; padding: 20px; box-shadow: 0px 4px 12px rgba(0,0,0,0.3);
}}
h1, h2, h3, p {{ color: white !important; }}
.stMarkdown p {{ color: white !important; }}
.complexity-box {{
    background-color: #1E1E1E; color: #00FF00; padding: 10px; 
    border-radius: 5px; font-family: monospace; margin-bottom: 15px;
}}
/* Menjaga keterbacaan komponen metrik */
[data-testid="stMetric"] {{
    background-color: white !important;
    padding: 15px;
    border-radius: 8px;
    box-shadow: 0px 2px 5px rgba(0,0,0,0.1);
}}
[data-testid="stMetricValue"] {{ color: #1E88E5 !important; }}
[data-testid="stMetricLabel"] {{ color: #444444 !important; }}
</style>
""", unsafe_allow_html=True)

# --- 1. PENERAPAN KONSEP OOP (Class, Enkapsulasi, Pewarisan, Polimorfisme) ---
class Orang:
    def __init__(self, nama: str):
        self._nama = nama  # Protected attribute
        
    def get_info(self):
        return f"Nama: {self._nama}"

class Mahasiswa(Orang):
    def __init__(self, nim: str, nama: str, jurusan: str, angkatan: int):
        super().__init__(nama)
        self.__nim = nim          # Private attribute
        self.jurusan = jurusan    
        self.angkatan = angkatan  
        
    def get_nim(self):
        return self.__nim
    
    def get_nama(self):
        return self._nama
    
    def set_nama(self, nama_baru):
        self._nama = nama_baru

    def get_info(self):
        return f"Mahasiswa: {self._nama} ({self.__nim}) - {self.jurusan}"

    def to_dict(self):
        return {
            "NIM": self.__nim,
            "Nama": self._nama,
            "Jurusan": self.jurusan,
            "Angkatan": self.angkatan
        }

# --- 2. PENYIMPANAN DATA (File I/O) ---
FILE_DATA = "data_mahasiswa.json"

def muat_dari_file():
    try:
        if os.path.exists(FILE_DATA):
            with open(FILE_DATA, "r") as f:
                data_list = json.load(f)
                return [Mahasiswa(d['NIM'], d['Nama'], d['Jurusan'], int(d['Angkatan'])) for d in data_list]
    except Exception as e:
        st.error(f"Gagal membaca file: {e}")
    return []

def simpan_ke_file(daftar_mahasiswa):
    try:
        with open(FILE_DATA, "w") as f:
            json.dump([m.to_dict() for m in daftar_mahasiswa], f, indent=4)
    except Exception as e:
        st.error(f"Gagal menulis ke penyimpanan: {e}")

# Inisialisasi Array Utama di Session State
if 'database_mhs' not in st.session_state:
    st.session_state['database_mhs'] = muat_dari_file()

# --- 3. ALGORITMA PENCARIAN (Linear & Binary Search) ---
def linear_search(daftar, kata_kunci):
    hasil = []
    for mhs in daftar:
        if kata_kunci.lower() in mhs.get_nim().lower() or kata_kunci.lower() in mhs.get_nama().lower():
            hasil.append(mhs)
    return hasil

def binary_search(daftar, nim_kunci):
    daftar_terurut = sorted(daftar, key=lambda x: x.get_nim())
    low = 0
    high = len(daftar_terurut) - 1
    
    while low <= high:
        mid = (low + high) // 2
        if daftar_terurut[mid].get_nim() == nim_kunci:
            return [daftar_terurut[mid]]
        elif daftar_terurut[mid].get_nim() < nim_kunci:
            low = mid + 1
        else:
            high = mid - 1
    return []

# --- 4. ALGORITMA PENGURUTAN (Bubble & Insertion Sort) ---
def bubble_sort(daftar, kriteria):
    n = len(daftar)
    arr = list(daftar)
    for i in range(n):
        for j in range(0, n-i-1):
            val_j = arr[j].get_nama() if kriteria == "Nama" else arr[j].get_nim()
            val_j1 = arr[j+1].get_nama() if kriteria == "Nama" else arr[j+1].get_nim()
            if val_j > val_j1:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

def insertion_sort(daftar, kriteria):
    arr = list(daftar)
    for i in range(1, len(arr)):
        key_obj = arr[i]
        key_val = key_obj.get_nama() if kriteria == "Nama" else key_obj.get_nim()
        j = i-1
        while j >= 0 and (arr[j].get_nama() if kriteria == "Nama" else arr[j].get_nim()) > key_val:
            arr[j+1] = arr[j]
            j -= 1
        arr[j+1] = key_obj
    return arr


# --- ANTARMUKA UTAMA (ADMIN PANEL) ---
st.title("🎓 Admin Panel - Manajemen Mahasiswa Berbasis Algoritma & OOP")

# Sidebar Navigasi
menu = ["📊 Dasbor & Pengurutan", "🔍 Pencarian Data", "➕ Tambah Mahasiswa", "🔄 Edit Data", "❌ Hapus Data"]
pilihan = st.sidebar.selectbox("Menu Utama Admin", menu)

# --- MENU 1: DASBOR & SORTING ---
if pilihan == "📊 Dasbor & Pengurutan":
    st.subheader("📊 Dasbor Utama & Fitur Pengurutan (Sorting)")
    daftar_mhs = st.session_state['database_mhs']
    
    if daftar_mhs:
        col_sort1, col_sort2 = st.columns(2)
        with col_sort1:
            metode = st.selectbox("Pilih Algoritma Sorting", ["Bubble Sort", "Insertion Sort"])
        with col_sort2:
            kriteria = st.selectbox("Urutkan Berdasarkan", ["NIM", "Nama"])
            
        start_time = time.time()
        if metode == "Bubble Sort":
            data_tampil = bubble_sort(daftar_mhs, kriteria)
            complexity_msg = "🔴 Bubble Sort Time Complexity: Best O(n), Worst/Average O(n²)"
        else:
            data_tampil = insertion_sort(daftar_mhs, kriteria)
            complexity_msg = "🟡 Insertion Sort Time Complexity: Best O(n), Worst/Average O(n²)"
        end_time = time.time()
        
        st.markdown(f'<div class="complexity-box">{complexity_msg} | Waktu Eksekusi: {(end_time - start_time)*1000:.4f} ms</div>', unsafe_allow_html=True)
        
        # Konversi objek array ke bentuk tabular DataFrame Pandas dengan aman
        raw_data = [m.to_dict() for m in data_tampil]
        df_tampil = pd.DataFrame(raw_data)
        
        # Tampilkan statistik sederhana di atas tabel
        c1, c2 = st.columns(2)
        c1.metric("Total Mahasiswa", len(df_tampil))
        c2.metric("Total Jurusan", df_tampil["Jurusan"].nunique())
        
        st.markdown("### Tabel Data")
        st.dataframe(df_tampil, use_container_width=True)
    else:
        st.info("Belum ada data mahasiswa dalam sistem.")

# --- MENU 2: PENCARIAN DATA (SEARCHING) ---
elif pilihan == "🔍 Pencarian Data":
    st.subheader("🔍 Fitur Pencarian Data")
    
    col_sch1, col_sch2 = st.columns([2, 1])
    with col_sch1:
        kata_kunci = st.text_input("Masukkan NIM atau Nama yang dicari:")
    with col_sch2:
        metode_search = st.selectbox("Pilih Algoritma Search", ["Linear Search", "Binary Search (Spesifik NIM)"])
        
    if kata_kunci:
        start_time = time.time()
        if metode_search == "Linear Search":
            hasil = linear_search(st.session_state['database_mhs'], kata_kunci)
            complexity_msg = "🔵 Linear Search Time Complexity: O(n)"
        else:
            hasil = binary_search(st.session_state['database_mhs'], kata_kunci)
            complexity_msg = "🟢 Binary Search Time Complexity: O(log n)"
        end_time = time.time()
        
        st.markdown(f'<div class="complexity-box">{complexity_msg} | Waktu Eksekusi: {(end_time - start_time)*1000:.4f} ms</div>', unsafe_allow_html=True)
        
        if hasil:
            st.success(f"Ditemukan {len(hasil)} data mahasiswa:")
            raw_hasil = [h.to_dict() for h in hasil]
            st.dataframe(pd.DataFrame(raw_hasil), use_container_width=True)
            for h in hasil:
                st.caption(f"ℹ️ [Output Polimorfisme] {h.get_info()}")
        else:
            st.error("Data tidak ditemukan.")

# --- MENU 3: TAMBAH DATA ---
elif pilihan == "➕ Tambah Mahasiswa":
    st.subheader("➕ Tambah Mahasiswa Baru")
    
    with st.form("form_tambah_mhs"):
        input_nim = st.text_input("NIM (Harus 8 Digit Angka)")
        input_nama = st.text_input("Nama Lengkap")
        input_jurusan = st.selectbox("Jurusan", ["Teknik Informatika", "Sistem Informasi", "Data Science"])
        input_angkatan = st.number_input("Angkatan", min_value=2020, max_value=2026, value=2024)
        
        tombol_simpan = st.form_submit_button("Simpan ke Array & File")
        
        if tombol_simpan:
            regex_nim = r"^\d{8}$"
            try:
                if not re.match(regex_nim, input_nim):
                    raise ValueError("Format NIM Salah! NIM wajib berupa 8 digit angka murni.")
                if not input_nama.strip():
                    raise ValueError("Nama lengkap tidak boleh kosong!")
                
                for m in st.session_state['database_mhs']:
                    if m.get_nim() == input_nim:
                        raise KeyError("NIM tersebut sudah terdaftar di sistem!")
                
                mhs_baru = Mahasiswa(input_nim, input_nama, input_jurusan, int(input_angkatan))
                st.session_state['database_mhs'].append(mhs_baru)
                simpan_ke_file(st.session_state['database_mhs'])
                st.success(f"Berhasil menyimpan data: {mhs_baru.get_nama()}")
                
            except (ValueError, KeyError) as err_kustom:
                st.error(f"❌ Kesalahan Validasi: {err_kustom}")
            except Exception as e:
                st.error(f"💥 Terjadi Error Tak Terduga: {e}")

# --- MENU 4: EDIT DATA ---
elif pilihan == "🔄 Edit Data":
    st.subheader("🔄 Modifikasi Data Mahasiswa")
    daftar = st.session_state['database_mhs']
    
    if daftar:
        list_nim = [m.get_nim() for m in daftar]
        nim_pilihan = st.selectbox("Pilih NIM Mahasiswa yang akan diubah", list_nim)
        
        index_target = -1
        for i in range(len(daftar)):
            if daftar[i].get_nim() == nim_pilihan:
                index_target = i
                break
                
        if index_target != -1:
            mhs_target = daftar[index_target]
            
            with st.form("form_edit"):
                nama_baru = st.text_input("Ubah Nama Lengkap", value=mhs_target.get_nama())
                jurusan_baru = st.selectbox("Ubah Jurusan", ["Teknik Informatika", "Sistem Informasi", "Data Science"], 
                                            index=["Teknik Informatika", "Sistem Informasi", "Data Science"].index(mhs_target.jurusan))
                angkatan_baru = st.number_input("Ubah Angkatan", min_value=2020, max_value=2026, value=int(mhs_target.angkatan))
                
                tombol_edit = st.form_submit_button("Perbarui Data")
                
                if tombol_edit:
                    try:
                        if not nama_baru.strip(): raise ValueError("Nama tidak boleh kosong.")
                        mhs_target.set_nama(nama_baru)
                        mhs_target.jurusan = jurusan_baru
                        mhs_target.angkatan = int(angkatan_baru)
                        
                        simpan_ke_file(daftar)
                        st.success("Data berhasil diperbarui!")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal memperbarui: {e}")
    else:
        st.info("Belum ada data mahasiswa.")

# --- MENU 5: HAPUS DATA ---
elif pilihan == "❌ Hapus Data":
    st.subheader("❌ Hapus Data dari Array & File")
    daftar = st.session_state['database_mhs']
    
    if daftar:
        list_display = [f"{m.get_nim()} - {m.get_nama()}" for m in daftar]
        pilihan_hapus = st.selectbox("Pilih Mahasiswa yang akan dihapus permanen", list_display)
        nim_hapus = pilihan_hapus.split(" - ")[0]
        
        if st.button("Hapus Secara Permanen", type="primary"):
            try:
                st.session_state['database_mhs'] = [m for m in daftar if m.get_nim() != nim_hapus]
                simpan_ke_file(st.session_state['database_mhs'])
                st.success(f"Data dengan NIM {nim_hapus} berhasil dihapus.")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Gagal menghapus: {e}")
    else:
        st.info("Tidak ada data untuk dihapus.")
