"""
SIMM - Sistem Informasi Manajemen Mahasiswa
Universitas Pamulang
"""

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import re
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime

# ============================================================================
# KONFIGURASI
# ============================================================================

class Config:
    DB_NAME = 'database.db'
    PAGE_TITLE = "SIMM - Sistem Informasi Mahasiswa"
    PAGE_ICON = "🎓"
    
    NIM_PATTERN = r'^[0-9]{10,12}$'
    NAMA_PATTERN = r'^[A-Za-z\s]{2,50}$'
    USERNAME_PATTERN = r'^[A-Za-z0-9_]{3,20}$'
    PASSWORD_PATTERN = r'^.{4,}$'
    
    PRODI_LIST = [
        "Teknik Informatika", "Sistem Informasi", "Manajemen Informatika",
        "Teknik Komputer", "Akuntansi", "Manajemen", "Hukum", "Psikologi"
    ]
    
    STATUS_LIST = ["Aktif", "Pasif", "Cuti"]

# ============================================================================
# DATABASE MANAGER
# ============================================================================

class DatabaseManager:
    def __init__(self):
        self._init_database()
    
    def _get_connection(self):
        return sqlite3.connect(Config.DB_NAME)
    
    def _init_database(self):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT NOT NULL,
                    nama_lengkap TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mahasiswa (
                    nim TEXT PRIMARY KEY,
                    nama TEXT NOT NULL,
                    prodi TEXT NOT NULL,
                    ipk REAL NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            st.error(f"Error database: {str(e)}")
    
    def execute_query(self, query: str, params: tuple = ()) -> List[tuple]:
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchall()
            conn.close()
            return result
        except Exception as e:
            st.error(f"Error query: {str(e)}")
            return []
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            affected = cursor.rowcount
            conn.close()
            return affected
        except Exception as e:
            st.error(f"Error update: {str(e)}")
            return 0

# ============================================================================
# ALGORITMA PENCARIAN
# ============================================================================

class SimpleSearch:
    @staticmethod
    def linear_search(data: List[Dict], keyword: str) -> List[Dict]:
        results = []
        keyword_lower = keyword.lower()
        
        for item in data:
            if (keyword_lower in str(item['nim']).lower() or
                keyword_lower in str(item['nama']).lower() or
                keyword_lower in str(item['prodi']).lower() or
                keyword_lower in str(item['status']).lower()):
                results.append(item)
        
        return results
    
    @staticmethod
    def binary_search(data: List[Dict], keyword: str, search_by: str = 'nim') -> List[Dict]:
        if not data:
            return []
        
        sorted_data = sorted(data, key=lambda x: str(x[search_by]).lower())
        low, high = 0, len(sorted_data) - 1
        keyword_lower = keyword.lower()
        results = []
        
        while low <= high:
            mid = (low + high) // 2
            mid_value = str(sorted_data[mid][search_by]).lower()
            
            if keyword_lower == mid_value:
                results.append(sorted_data[mid])
                left = mid - 1
                while left >= 0 and str(sorted_data[left][search_by]).lower() == keyword_lower:
                    results.append(sorted_data[left])
                    left -= 1
                right = mid + 1
                while right < len(sorted_data) and str(sorted_data[right][search_by]).lower() == keyword_lower:
                    results.append(sorted_data[right])
                    right += 1
                break
            elif keyword_lower < mid_value:
                high = mid - 1
            else:
                low = mid + 1
        
        return results
    
    @staticmethod
    def search_all_fields(data: List[Dict], keyword: str) -> List[Dict]:
        results = []
        keyword_lower = keyword.lower()
        
        for item in data:
            for value in item.values():
                if keyword_lower in str(value).lower():
                    results.append(item)
                    break
        
        return results

# ============================================================================
# MAHASISWA MANAGER
# ============================================================================

class MahasiswaManager:
    def __init__(self):
        self.__db = DatabaseManager()
        self.__data: List[Dict] = []
        self._load_data()
    
    def _load_data(self):
        try:
            result = self.__db.execute_query("SELECT * FROM mahasiswa")
            self.__data = [
                {'nim': row[0], 'nama': row[1], 'prodi': row[2], 
                 'ipk': row[3], 'status': row[4]}
                for row in result
            ]
        except:
            self.__data = []
    
    def get_all(self) -> List[Dict]:
        return self.__data
    
    def search(self, keyword: str, method: str = 'auto') -> Tuple[List[Dict], str, str]:
        if not keyword or not keyword.strip():
            return self.__data, "Tidak ada pencarian", "-"
        
        keyword = keyword.strip()
        
        if method == 'auto':
            if re.match(r'^[0-9]{10,12}$', keyword):
                results = SimpleSearch.binary_search(self.__data, keyword, 'nim')
                return results, "Binary Search (NIM)", "O(log n) - Sangat Cepat"
            else:
                results = SimpleSearch.search_all_fields(self.__data, keyword)
                return results, "Sequential Search (Fleksibel)", "O(n) - Cukup Cepat"
        
        elif method == 'linear':
            results = SimpleSearch.linear_search(self.__data, keyword)
            return results, "Linear Search", "O(n) - Cukup Cepat"
        
        elif method == 'binary':
            results = SimpleSearch.binary_search(self.__data, keyword, 'nim')
            if not results:
                results = SimpleSearch.binary_search(self.__data, keyword, 'nama')
            return results, "Binary Search", "O(log n) - Sangat Cepat"
        
        else:
            results = SimpleSearch.search_all_fields(self.__data, keyword)
            return results, "Sequential Search", "O(n) - Cukup Cepat"
    
    def tambah(self, nim: str, nama: str, prodi: str, ipk: float, status: str) -> Tuple[bool, str]:
        try:
            if not re.match(Config.NIM_PATTERN, nim):
                return False, "NIM harus 10-12 digit angka!"
            
            if not re.match(Config.NAMA_PATTERN, nama):
                return False, "Nama hanya boleh huruf dan spasi (2-50 karakter)!"
            
            if not 0.0 <= ipk <= 4.0:
                return False, "IPK harus 0.00 - 4.00!"
            
            for item in self.__data:
                if item['nim'] == nim:
                    return False, "NIM sudah terdaftar!"
            
            query = "INSERT INTO mahasiswa (nim, nama, prodi, ipk, status) VALUES (?, ?, ?, ?, ?)"
            self.__db.execute_update(query, (nim, nama, prodi, ipk, status))
            
            self.__data.append({'nim': nim, 'nama': nama, 'prodi': prodi, 'ipk': ipk, 'status': status})
            
            return True, "Data berhasil ditambahkan!"
            
        except Exception as e:
            return False, f"Terjadi kesalahan: {str(e)}"
    
    def update(self, nim: str, nama: str, prodi: str, ipk: float, status: str) -> Tuple[bool, str]:
        try:
            found = False
            for item in self.__data:
                if item['nim'] == nim:
                    found = True
                    break
            
            if not found:
                return False, "NIM tidak ditemukan!"
            
            if not re.match(Config.NAMA_PATTERN, nama):
                return False, "Nama hanya boleh huruf dan spasi (2-50 karakter)!"
            
            if not 0.0 <= ipk <= 4.0:
                return False, "IPK harus 0.00 - 4.00!"
            
            query = "UPDATE mahasiswa SET nama=?, prodi=?, ipk=?, status=? WHERE nim=?"
            self.__db.execute_update(query, (nama, prodi, ipk, status, nim))
            
            for item in self.__data:
                if item['nim'] == nim:
                    item.update({'nama': nama, 'prodi': prodi, 'ipk': ipk, 'status': status})
                    break
            
            return True, "Data berhasil diupdate!"
            
        except Exception as e:
            return False, f"Terjadi kesalahan: {str(e)}"
    
    def hapus(self, nim: str) -> Tuple[bool, str]:
        try:
            found = False
            for item in self.__data:
                if item['nim'] == nim:
                    found = True
                    break
            
            if not found:
                return False, "NIM tidak ditemukan!"
            
            query = "DELETE FROM mahasiswa WHERE nim = ?"
            self.__db.execute_update(query, (nim,))
            
            self.__data = [item for item in self.__data if item['nim'] != nim]
            
            return True, "Data berhasil dihapus!"
            
        except Exception as e:
            return False, f"Terjadi kesalahan: {str(e)}"
    
    def generate_contoh(self) -> Tuple[bool, str]:
        sample_data = [
            ("2010114001", "Fajar Dian Taufani", "Teknik Informatika", 3.85, "Aktif"),
            ("2010114005", "Siti Aminah", "Sistem Informasi", 3.40, "Aktif"),
            ("2010114002", "Andi Wijaya", "Teknik Informatika", 2.90, "Cuti"),
            ("2010114012", "Riska Amelia", "Manajemen", 4.00, "Aktif"),
            ("2010114009", "Budi Santoso", "Akuntansi", 3.15, "Pasif"),
            ("2010114015", "Dewi Lestari", "Teknik Informatika", 3.60, "Aktif"),
            ("2010114020", "Rahmat Hidayat", "Sistem Informasi", 2.75, "Aktif"),
            ("2010114025", "Putri Wulandari", "Manajemen", 3.90, "Aktif"),
            ("2010114030", "Ahmad Rizki", "Teknik Komputer", 3.45, "Pasif"),
        ]
        
        added = 0
        for data in sample_data:
            success, _ = self.tambah(*data)
            if success:
                added += 1
        
        return True, f"{added} data contoh berhasil ditambahkan!"

# ============================================================================
# AUTH MANAGER
# ============================================================================

class AuthManager:
    def __init__(self):
        self.__db = DatabaseManager()
    
    def login(self, username: str, password: str) -> Tuple[bool, str]:
        try:
            query = "SELECT * FROM users WHERE username = ? AND password = ?"
            result = self.__db.execute_query(query, (username, password))
            
            if result:
                return True, f"Selamat datang, {result[0][2] or username}!"
            return False, "Username atau password salah!"
            
        except Exception as e:
            return False, f"Terjadi kesalahan: {str(e)}"
    
    def register(self, username: str, password: str, confirm_password: str, 
                 nama_lengkap: str = "") -> Tuple[bool, str]:
        try:
            if not username or not username.strip():
                return False, "Username harus diisi!"
            
            if not re.match(Config.USERNAME_PATTERN, username):
                return False, "Username harus 3-20 karakter (huruf, angka, underscore)!"
            
            if not password or not password.strip():
                return False, "Password harus diisi!"
            
            if not re.match(Config.PASSWORD_PATTERN, password):
                return False, "Password minimal 4 karakter!"
            
            if password != confirm_password:
                return False, "Password tidak cocok!"
            
            check_query = "SELECT * FROM users WHERE username = ?"
            existing = self.__db.execute_query(check_query, (username,))
            if existing:
                return False, "Username sudah terdaftar!"
            
            if nama_lengkap and not re.match(Config.NAMA_PATTERN, nama_lengkap):
                return False, "Nama lengkap hanya boleh huruf dan spasi!"
            
            insert_query = """
                INSERT INTO users (username, password, nama_lengkap) 
                VALUES (?, ?, ?)
            """
            self.__db.execute_update(
                insert_query, 
                (username, password, nama_lengkap if nama_lengkap else username)
            )
            
            return True, "Registrasi berhasil! Silakan login."
            
        except Exception as e:
            return False, f"Terjadi kesalahan: {str(e)}"
    
    def get_user_info(self, username: str) -> Optional[Dict]:
        try:
            query = "SELECT * FROM users WHERE username = ?"
            result = self.__db.execute_query(query, (username,))
            if result:
                return {
                    'username': result[0][0],
                    'nama_lengkap': result[0][2],
                    'created_at': result[0][3]
                }
            return None
        except:
            return None

# ============================================================================
# STREAMLIT UI
# ============================================================================

class StreamlitUI:
    def __init__(self):
        self.mahasiswa = MahasiswaManager()
        self.auth = AuthManager()
        self._init_session()
        self._setup_page()
    
    def _init_session(self):
        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.show_register = False
    
    def _setup_page(self):
        st.set_page_config(
            page_title=Config.PAGE_TITLE,
            page_icon=Config.PAGE_ICON,
            layout="wide"
        )
        
        st.markdown("""
            <style>
                .main-header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 20px;
                    border-radius: 15px;
                    margin-bottom: 30px;
                    text-align: center;
                    color: white;
                }
                .main-header h1 {
                    margin: 0;
                    font-size: 2.5rem;
                }
                .main-header p {
                    margin: 5px 0 0 0;
                    opacity: 0.9;
                }
                
                .login-container {
                    background: white;
                    padding: 40px;
                    border-radius: 20px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                    max-width: 500px;
                    margin: 0 auto;
                }
                
                .register-container {
                    background: white;
                    padding: 40px;
                    border-radius: 20px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                    max-width: 500px;
                    margin: 0 auto;
                }
                
                .search-box {
                    background: white;
                    padding: 30px;
                    border-radius: 15px;
                    box-shadow: 0 2px 15px rgba(0,0,0,0.1);
                    margin-bottom: 20px;
                }
                
                .badge {
                    display: inline-block;
                    padding: 5px 15px;
                    border-radius: 20px;
                    font-size: 0.85rem;
                    margin: 3px;
                }
                
                .badge-blue {
                    background: #667eea;
                    color: white;
                }
                
                .badge-green {
                    background: #10b981;
                    color: white;
                }
                
                .badge-orange {
                    background: #f59e0b;
                    color: white;
                }
                
                .badge-red {
                    background: #ef4444;
                    color: white;
                }
                
                .complexity-info {
                    background: #f1f5f9;
                    padding: 15px;
                    border-radius: 10px;
                    border-left: 4px solid #3b82f6;
                    margin: 10px 0;
                }
                
                .user-info {
                    background: #f1f5f9;
                    padding: 10px 20px;
                    border-radius: 10px;
                    display: inline-block;
                    margin: 5px 0;
                }
                
                .tab-active {
                    text-align: center;
                    padding: 10px;
                    background: #667eea;
                    border-radius: 10px;
                    color: white;
                    font-weight: bold;
                }
            </style>
        """, unsafe_allow_html=True)
    
    def _render_login_register(self):
        st.markdown("""
            <div style="text-align: center; margin-bottom: 30px;">
                <h2>Selamat Datang</h2>
                <p style="color: #6b7280;">Silakan login atau daftar untuk melanjutkan</p>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if not st.session_state.get('show_register', False):
                st.markdown("""
                    <div class="tab-active">
                        LOGIN
                    </div>
                """, unsafe_allow_html=True)
            else:
                if st.button("Login", use_container_width=True):
                    st.session_state.show_register = False
                    st.rerun()
        
        with col2:
            if st.session_state.get('show_register', False):
                st.markdown("""
                    <div class="tab-active">
                        REGISTER
                    </div>
                """, unsafe_allow_html=True)
            else:
                if st.button("Register", use_container_width=True):
                    st.session_state.show_register = True
                    st.rerun()
        
        st.markdown("---")
        
        if st.session_state.get('show_register', False):
            self._render_register_form()
        else:
            self._render_login_form()
    
    def _render_login_form(self):
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown("<h2>Login</h2>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input(
                "Username",
                placeholder="Masukkan username Anda"
            )
            
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Masukkan password Anda"
            )
            
            submitted = st.form_submit_button("Login", use_container_width=True, type="primary")
            
            if submitted:
                if not username or not password:
                    st.error("Username dan password harus diisi!")
                else:
                    success, msg = self.auth.login(username, password)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
        
        st.markdown("""
            <div style="text-align: center; margin-top: 15px;">
                <p style="color: #6b7280; font-size: 0.9rem;">
                    Belum punya akun? 
                    <span style="color: #667eea; font-weight: bold; cursor: pointer;">
                        Daftar di sini
                    </span>
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def _render_register_form(self):
        st.markdown('<div class="register-container">', unsafe_allow_html=True)
        st.markdown("<h2>Daftar Akun Baru</h2>", unsafe_allow_html=True)
        
        with st.form("register_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                username = st.text_input(
                    "Username *",
                    placeholder="Contoh: johndoe",
                    help="3-20 karakter (huruf, angka, underscore)"
                )
                
                password = st.text_input(
                    "Password *",
                    type="password",
                    placeholder="Minimal 4 karakter",
                    help="Minimal 4 karakter"
                )
            
            with col2:
                nama_lengkap = st.text_input(
                    "Nama Lengkap",
                    placeholder="Contoh: John Doe",
                    help="Opsional, hanya huruf dan spasi"
                )
                
                confirm_password = st.text_input(
                    "Konfirmasi Password *",
                    type="password",
                    placeholder="Ulangi password Anda"
                )
            
            st.markdown("""
                <div style="background: #f1f5f9; padding: 10px; border-radius: 10px; margin: 10px 0; font-size: 0.85rem;">
                    <p style="margin: 0; color: #64748b;">
                        <strong>Aturan:</strong><br>
                        • Username: 3-20 karakter (huruf, angka, underscore)<br>
                        • Password: Minimal 4 karakter<br>
                        • Nama: Hanya huruf dan spasi (opsional)
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            submitted = st.form_submit_button("Daftar Sekarang", use_container_width=True, type="primary")
            
            if submitted:
                if not username or not password or not confirm_password:
                    st.error("Field yang bertanda * harus diisi!")
                else:
                    success, msg = self.auth.register(
                        username, password, confirm_password, nama_lengkap
                    )
                    if success:
                        st.success(msg)
                        st.balloons()
                        st.session_state.show_register = False
                        st.rerun()
                    else:
                        st.error(msg)
        
        if st.button("Kembali ke Login", use_container_width=True):
            st.session_state.show_register = False
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def _render_sidebar(self):
        with st.sidebar:
            user_info = self.auth.get_user_info(st.session_state.username)
            nama_display = user_info['nama_lengkap'] if user_info else st.session_state.username
            
            st.markdown(f"""
                <div style="text-align: center; padding: 15px;">
                    <div style="font-size: 3rem;">👤</div>
                    <h3>{nama_display}</h3>
                    <div class="user-info">
                        <small>@{st.session_state.username}</small>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            menu = st.radio(
                "Menu",
                [
                    "Dashboard",
                    "Tambah Data",
                    "Data Mahasiswa",
                    "Cari Mahasiswa",
                    "Statistik"
                ],
                index=0
            )
            
            st.markdown("---")
            
            if st.button("Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.username = ""
                st.rerun()
            
            return menu
    
    def _render_dashboard(self):
        st.markdown("""
            <div class="main-header">
                <h1>Dashboard</h1>
                <p>Ringkasan data mahasiswa</p>
            </div>
        """, unsafe_allow_html=True)
        
        data = self.mahasiswa.get_all()
        
        col1, col2, col3, col4 = st.columns(4)
        
        total = len(data)
        aktif = len([d for d in data if d['status'] == 'Aktif'])
        avg_ipk = sum(d['ipk'] for d in data) / total if total > 0 else 0
        max_ipk = max([d['ipk'] for d in data]) if data else 0
        
        with col1:
            st.metric("Total Mahasiswa", total)
        with col2:
            st.metric("Mahasiswa Aktif", aktif)
        with col3:
            st.metric("Rata-rata IPK", f"{avg_ipk:.2f}")
        with col4:
            st.metric("IPK Tertinggi", f"{max_ipk:.2f}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Generate Contoh Data", use_container_width=True):
                success, msg = self.mahasiswa.generate_contoh()
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
        
        st.markdown("---")
        st.subheader("Data Terbaru")
        
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df.head(10), use_container_width=True)
        else:
            st.info("Belum ada data. Klik 'Generate Contoh Data' untuk menambahkan.")
    
    def _render_tambah(self):
        st.markdown("""
            <div class="main-header">
                <h1>Tambah Mahasiswa</h1>
                <p>Masukkan data mahasiswa baru</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("tambah_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                nim = st.text_input("NIM (10-12 digit)", placeholder="Contoh: 2010114001")
                nama = st.text_input("Nama Lengkap", placeholder="Masukkan nama lengkap")
                prodi = st.selectbox("Program Studi", Config.PRODI_LIST)
            
            with col2:
                ipk = st.number_input("IPK (0.00 - 4.00)", min_value=0.0, max_value=4.0, step=0.01, format="%.2f")
                status = st.selectbox("Status", Config.STATUS_LIST)
            
            submitted = st.form_submit_button("Simpan Data", use_container_width=True)
            
            if submitted:
                if not nim or not nama:
                    st.error("NIM dan Nama harus diisi!")
                else:
                    success, msg = self.mahasiswa.tambah(nim, nama, prodi, ipk, status)
                    if success:
                        st.success(msg)
                        st.balloons()
                    else:
                        st.error(msg)
    
    def _render_data(self):
        st.markdown("""
            <div class="main-header">
                <h1>Data Mahasiswa</h1>
                <p>Kelola data mahasiswa</p>
            </div>
        """, unsafe_allow_html=True)
        
        data = self.mahasiswa.get_all()
        
        if not data:
            st.info("Belum ada data. Generate contoh data terlebih dahulu.")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            search = st.text_input("Cari", placeholder="Ketik NIM atau Nama...")
        with col2:
            filter_status = st.selectbox("Filter Status", ["Semua"] + Config.STATUS_LIST)
        
        filtered = data.copy()
        
        if search:
            search_lower = search.lower()
            filtered = [
                item for item in filtered
                if search_lower in item['nim'].lower() or 
                   search_lower in item['nama'].lower()
            ]
        
        if filter_status != "Semua":
            filtered = [item for item in filtered if item['status'] == filter_status]
        
        if filtered:
            df = pd.DataFrame(filtered)
            st.dataframe(df, use_container_width=True)
            
            st.markdown("---")
            st.subheader("Hapus Data")
            
            col1, col2 = st.columns([2, 1])
            with col1:
                nim_to_delete = st.selectbox(
                    "Pilih NIM untuk dihapus",
                    [item['nim'] for item in filtered]
                )
            with col2:
                if st.button("Hapus", type="secondary", use_container_width=True):
                    success, msg = self.mahasiswa.hapus(nim_to_delete)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
        else:
            st.warning("Tidak ada data yang cocok.")
    
    def _render_search(self):
        st.markdown("""
            <div class="main-header">
                <h1>Cari Mahasiswa</h1>
                <p>Cukup ketik apapun yang ingin dicari</p>
            </div>
        """, unsafe_allow_html=True)
        
        data = self.mahasiswa.get_all()
        
        if not data:
            st.info("Belum ada data. Generate contoh data terlebih dahulu.")
            return
        
        st.markdown('<div class="search-box">', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            keyword = st.text_input(
                "Masukkan kata kunci",
                placeholder="Contoh: 2010114001, Fajar, Informatika, Aktif..."
            )
        
        with col2:
            method = st.selectbox(
                "Metode",
                [
                    "Otomatis (Rekomendasi)",
                    "Cepat - Binary Search",
                    "Fleksibel - Sequential Search",
                    "Sederhana - Linear Search"
                ]
            )
        
        if st.button("Cari Sekarang", use_container_width=True, type="primary"):
            if not keyword or not keyword.strip():
                st.warning("Silakan masukkan kata kunci terlebih dahulu!")
            else:
                method_map = {
                    "Otomatis (Rekomendasi)": "auto",
                    "Cepat - Binary Search": "binary",
                    "Fleksibel - Sequential Search": "sequential",
                    "Sederhana - Linear Search": "linear"
                }
                
                with st.spinner("Sedang mencari..."):
                    selected_method = method_map[method]
                    results, method_used, complexity = self.mahasiswa.search(
                        keyword, selected_method
                    )
                
                st.markdown("---")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Ditemukan", f"{len(results)} data")
                
                with col2:
                    st.markdown(f"""
                        <div style="background: #f1f5f9; padding: 15px; border-radius: 10px; text-align: center;">
                            <small style="color: #64748b;">Metode</small><br>
                            <strong>{method_used}</strong>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                        <div style="background: #f1f5f9; padding: 15px; border-radius: 10px; text-align: center;">
                            <small style="color: #64748b;">Kompleksitas</small><br>
                            <strong>{complexity}</strong>
                        </div>
                    """, unsafe_allow_html=True)
                
                if results:
                    st.success(f"Menampilkan {len(results)} hasil pencarian untuk '{keyword}'")
                    df = pd.DataFrame(results)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.warning(f"Tidak ditemukan data untuk '{keyword}'")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        with st.expander("Penjelasan Metode Pencarian", expanded=False):
            st.markdown("""
                <div class="complexity-info">
                    <h4>3 Metode Pencarian</h4>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin-top: 15px;">
                        
                        <div style="background: white; padding: 15px; border-radius: 10px; border-left: 4px solid #667eea;">
                            <h5>Otomatis <span class="badge badge-green">Rekomendasi</span></h5>
                            <p style="margin: 5px 0; font-size: 0.9rem;">
                                Sistem pilih metode terbaik:
                            </p>
                            <ul style="font-size: 0.85rem;">
                                <li><strong>NIM</strong> -> Binary Search</li>
                                <li><strong>Nama/Prodi</strong> -> Sequential Search</li>
                            </ul>
                            <small style="color: #64748b;">Paling mudah</small>
                        </div>
                        
                        <div style="background: white; padding: 15px; border-radius: 10px; border-left: 4px solid #10b981;">
                            <h5>Cepat <span class="badge badge-blue">Binary</span></h5>
                            <p style="margin: 5px 0; font-size: 0.9rem;">
                                Mencari dengan membagi data.
                            </p>
                            <ul style="font-size: 0.85rem;">
                                <li><strong>Kecepatan:</strong> Sangat Cepat</li>
                                <li><strong>Kompleksitas:</strong> O(log n)</li>
                                <li><strong>Cocok:</strong> Data > 100</li>
                            </ul>
                        </div>
                        
                        <div style="background: white; padding: 15px; border-radius: 10px; border-left: 4px solid #f59e0b;">
                            <h5>Fleksibel <span class="badge badge-orange">Sequential</span></h5>
                            <p style="margin: 5px 0; font-size: 0.9rem;">
                                Mencari di semua field.
                            </p>
                            <ul style="font-size: 0.85rem;">
                                <li><strong>Kecepatan:</strong> Cukup Cepat</li>
                                <li><strong>Kompleksitas:</strong> O(n)</li>
                                <li><strong>Cocok:</strong> Pencarian fleksibel</li>
                            </ul>
                        </div>
                        
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        with st.expander("Contoh Pencarian", expanded=False):
            st.markdown("""
                <div style="background: #f1f5f9; padding: 15px; border-radius: 10px;">
                    <h4>Coba cari dengan kata kunci berikut:</h4>
                    <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px;">
                        <span class="badge badge-blue">2010114001</span>
                        <span class="badge badge-blue">Fajar</span>
                        <span class="badge badge-blue">Informatika</span>
                        <span class="badge badge-blue">Aktif</span>
                        <span class="badge badge-blue">Siti</span>
                        <span class="badge badge-blue">Manajemen</
