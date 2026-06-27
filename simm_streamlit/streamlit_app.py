"""
SIMM - Sistem Informasi Manajemen Mahasiswa
Universitas Pamulang

Aplikasi dengan tampilan clean dan terstruktur untuk admin
"""

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import re
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
from abc import ABC, abstractmethod

# ============================================================================
# KONFIGURASI APLIKASI
# ============================================================================

class Config:
    """Konfigurasi aplikasi"""
    DB_NAME = 'database.db'
    PAGE_TITLE = "SIMM - Sistem Informasi Mahasiswa"
    PAGE_ICON = "🎓"
    
    # Regex Patterns
    NIM_PATTERN = r'^[0-9]{10,12}$'
    NAMA_PATTERN = r'^[A-Za-z\s]{2,50}$'
    IPK_PATTERN = r'^[0-4](\.\d{1,2})?$'
    
    PRODI_LIST = [
        "Teknik Informatika", "Sistem Informasi", "Manajemen Informatika",
        "Teknik Komputer", "Akuntansi", "Manajemen", "Hukum", "Psikologi"
    ]
    
    STATUS_LIST = ["Aktif", "Pasif", "Cuti"]

# ============================================================================
# CUSTOM EXCEPTION
# ============================================================================

class ValidationError(Exception):
    pass

class DatabaseError(Exception):
    pass

# ============================================================================
# CLASS MAHASISWA (OOP)
# ============================================================================

class Mahasiswa:
    """Class Mahasiswa dengan Encapsulation"""
    
    def __init__(self, nim: str, nama: str, prodi: str, ipk: float, status: str = "Aktif"):
        self.__nim = nim
        self.__nama = nama
        self.__prodi = prodi
        self.__ipk = ipk
        self.__status = status
    
    # GETTERS
    def get_nim(self) -> str:
        return self.__nim
    
    def get_nama(self) -> str:
        return self.__nama
    
    def get_prodi(self) -> str:
        return self.__prodi
    
    def get_ipk(self) -> float:
        return self.__ipk
    
    def get_status(self) -> str:
        return self.__status
    
    # SETTERS dengan Validasi
    def set_nama(self, nama: str) -> None:
        if not re.match(Config.NAMA_PATTERN, nama):
            raise ValidationError("Nama hanya boleh huruf dan spasi (2-50 karakter)!")
        self.__nama = nama
    
    def set_ipk(self, ipk: float) -> None:
        if not 0.0 <= ipk <= 4.0:
            raise ValidationError("IPK harus antara 0.00 - 4.00!")
        self.__ipk = ipk
    
    def to_dict(self) -> Dict:
        return {
            'nim': self.__nim,
            'nama': self.__nama,
            'prodi': self.__prodi,
            'ipk': self.__ipk,
            'status': self.__status
        }
    
    @staticmethod
    def validate_nim(nim: str) -> bool:
        return bool(re.match(Config.NIM_PATTERN, nim))

# ============================================================================
# CLASS MAHASISWA AKTIF (Inheritance)
# ============================================================================

class MahasiswaAktif(Mahasiswa):
    def __init__(self, nim: str, nama: str, prodi: str, ipk: float):
        super().__init__(nim, nama, prodi, ipk, "Aktif")
        self.__semester = 1
    
    def get_semester(self) -> int:
        return self.__semester
    
    def set_semester(self, semester: int) -> None:
        if semester < 1:
            raise ValidationError("Semester minimal 1!")
        self.__semester = semester

# ============================================================================
# CLASS DATABASE MANAGER
# ============================================================================

class DatabaseManager:
    """Manajemen database"""
    
    def __init__(self):
        self.__db_name = Config.DB_NAME
        self._init_database()
    
    def _get_connection(self):
        return sqlite3.connect(self.__db_name)
    
    def _init_database(self):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Tabel users
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT NOT NULL
                )
            ''')
            
            # Tabel mahasiswa
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mahasiswa (
                    nim TEXT PRIMARY KEY,
                    nama TEXT NOT NULL,
                    prodi TEXT NOT NULL,
                    ipk REAL NOT NULL,
                    status TEXT NOT NULL
                )
            ''')
            
            # Default user
            cursor.execute(
                "INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)",
                ('admin', 'admin123')
            )
            
            conn.commit()
            conn.close()
        except Exception as e:
            raise DatabaseError(f"Gagal inisialisasi database: {str(e)}")
    
    def execute_query(self, query: str, params: tuple = ()) -> List[tuple]:
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchall()
            conn.close()
            return result
        except Exception as e:
            raise DatabaseError(f"Error query: {str(e)}")
    
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
            raise DatabaseError(f"Error update: {str(e)}")

# ============================================================================
# CLASS SEARCH ALGORITHMS
# ============================================================================

class SearchAlgorithms:
    """Algoritma Pencarian"""
    
    @staticmethod
    def linear_search(data: List[Dict], key: str, value: Any) -> Optional[Dict]:
        """
        Linear Search - O(n)
        Mencari data satu per satu dari awal sampai ketemu
        """
        for item in data:
            if str(item.get(key, '')).lower() == str(value).lower():
                return item
        return None
    
    @staticmethod
    def linear_search_all(data: List[Dict], key: str, value: Any) -> List[Dict]:
        """
        Linear Search All - O(n)
        Mencari semua data yang cocok
        """
        results = []
        for item in data:
            if str(item.get(key, '')).lower() == str(value).lower():
                results.append(item)
        return results
    
    @staticmethod
    def binary_search(data: List[Dict], key: str, value: Any) -> Optional[Dict]:
        """
        Binary Search - O(log n)
        Mencari data dengan membagi array menjadi 2 bagian (data harus terurut)
        """
        if not data:
            return None
        
        # Sort data by key
        sorted_data = sorted(data, key=lambda x: str(x.get(key, '')).lower())
        
        low, high = 0, len(sorted_data) - 1
        search_value = str(value).lower()
        
        while low <= high:
            mid = (low + high) // 2
            mid_value = str(sorted_data[mid].get(key, '')).lower()
            
            if mid_value == search_value:
                return sorted_data[mid]
            elif mid_value < search_value:
                low = mid + 1
            else:
                high = mid - 1
        
        return None
    
    @staticmethod
    def sequential_search(data: List[Dict], keyword: str) -> List[Dict]:
        """
        Sequential Search - O(n)
        Mencari data dengan keyword di semua field
        """
        results = []
        keyword_lower = keyword.lower()
        
        for item in data:
            for value in item.values():
                if keyword_lower in str(value).lower():
                    results.append(item)
                    break
        
        return results

# ============================================================================
# CLASS SORTING ALGORITHMS
# ============================================================================

class SortingAlgorithms:
    """Algoritma Pengurutan"""
    
    @staticmethod
    def bubble_sort(data: List[Dict], key: str, reverse: bool = False) -> List[Dict]:
        """
        Bubble Sort - O(n²)
        Membandingkan elemen bersebelahan dan menukar jika tidak sesuai
        """
        arr = data.copy()
        n = len(arr)
        
        for i in range(n):
            swapped = False
            for j in range(0, n - i - 1):
                val1 = str(arr[j].get(key, '')).lower()
                val2 = str(arr[j + 1].get(key, '')).lower()
                
                if (val1 > val2 and not reverse) or (val1 < val2 and reverse):
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    swapped = True
            
            if not swapped:
                break
        
        return arr
    
    @staticmethod
    def insertion_sort(data: List[Dict], key: str, reverse: bool = False) -> List[Dict]:
        """
        Insertion Sort - O(n²)
        Membangun array terurut satu per satu
        """
        arr = data.copy()
        
        for i in range(1, len(arr)):
            key_item = arr[i]
            j = i - 1
            
            while j >= 0:
                val1 = str(arr[j].get(key, '')).lower()
                val2 = str(key_item.get(key, '')).lower()
                
                if (val1 > val2 and not reverse) or (val1 < val2 and reverse):
                    arr[j + 1] = arr[j]
                    j -= 1
                else:
                    break
            
            arr[j + 1] = key_item
        
        return arr
    
    @staticmethod
    def merge_sort(data: List[Dict], key: str, reverse: bool = False) -> List[Dict]:
        """
        Merge Sort - O(n log n)
        Membagi array menjadi 2 bagian, urutkan, lalu gabungkan
        """
        arr = data.copy()
        
        if len(arr) <= 1:
            return arr
        
        mid = len(arr) // 2
        left = SortingAlgorithms.merge_sort(arr[:mid], key, reverse)
        right = SortingAlgorithms.merge_sort(arr[mid:], key, reverse)
        
        return SortingAlgorithms._merge(left, right, key, reverse)
    
    @staticmethod
    def _merge(left: List[Dict], right: List[Dict], key: str, reverse: bool) -> List[Dict]:
        result = []
        i = j = 0
        
        while i < len(left) and j < len(right):
            val1 = str(left[i].get(key, '')).lower()
            val2 = str(right[j].get(key, '')).lower()
            
            if (val1 <= val2 and not reverse) or (val1 >= val2 and reverse):
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        
        result.extend(left[i:])
        result.extend(right[j:])
        return result
    
    @staticmethod
    def shell_sort(data: List[Dict], key: str, reverse: bool = False) -> List[Dict]:
        """
        Shell Sort - O(n log n)
        Versi perbaikan dari insertion sort dengan gap
        """
        arr = data.copy()
        n = len(arr)
        gap = n // 2
        
        while gap > 0:
            for i in range(gap, n):
                temp = arr[i]
                j = i
                
                while j >= gap:
                    val1 = str(arr[j - gap].get(key, '')).lower()
                    val2 = str(temp.get(key, '')).lower()
                    
                    if (val1 > val2 and not reverse) or (val1 < val2 and reverse):
                        arr[j] = arr[j - gap]
                        j -= gap
                    else:
                        break
                
                arr[j] = temp
            
            gap //= 2
        
        return arr

# ============================================================================
# CLASS MAHASISWA MANAGER
# ============================================================================

class MahasiswaManager:
    """Manager untuk operasi CRUD Mahasiswa"""
    
    def __init__(self):
        self.__db = DatabaseManager()
        self.__data: List[Dict] = []
        self._load_data()
    
    def _load_data(self):
        """Load data dari database"""
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
        """Mendapatkan semua data - O(1)"""
        return self.__data
    
    def get_by_nim(self, nim: str) -> Optional[Dict]:
        """Cari berdasarkan NIM - O(n)"""
        return SearchAlgorithms.linear_search(self.__data, 'nim', nim)
    
    def tambah(self, nim: str, nama: str, prodi: str, ipk: float, status: str) -> Tuple[bool, str]:
        """Tambah data - O(1)"""
        try:
            # Validasi
            if not Mahasiswa.validate_nim(nim):
                raise ValidationError("NIM harus 10-12 digit angka!")
            
            if not re.match(Config.NAMA_PATTERN, nama):
                raise ValidationError("Nama hanya boleh huruf dan spasi!")
            
            if not 0.0 <= ipk <= 4.0:
                raise ValidationError("IPK harus 0.00 - 4.00!")
            
            if self.get_by_nim(nim):
                raise ValidationError("NIM sudah terdaftar!")
            
            # Simpan
            query = "INSERT INTO mahasiswa (nim, nama, prodi, ipk, status) VALUES (?, ?, ?, ?, ?)"
            self.__db.execute_update(query, (nim, nama, prodi, ipk, status))
            
            # Update cache
            self.__data.append({'nim': nim, 'nama': nama, 'prodi': prodi, 'ipk': ipk, 'status': status})
            
            return True, "✅ Data berhasil ditambahkan!"
            
        except (ValidationError, DatabaseError) as e:
            return False, f"❌ {str(e)}"
        except Exception as e:
            return False, f"❌ Terjadi kesalahan: {str(e)}"
    
    def update(self, nim: str, nama: str, prodi: str, ipk: float, status: str) -> Tuple[bool, str]:
        """Update data - O(n)"""
        try:
            if not self.get_by_nim(nim):
                raise ValidationError("NIM tidak ditemukan!")
            
            if not re.match(Config.NAMA_PATTERN, nama):
                raise ValidationError("Nama hanya boleh huruf dan spasi!")
            
            if not 0.0 <= ipk <= 4.0:
                raise ValidationError("IPK harus 0.00 - 4.00!")
            
            query = "UPDATE mahasiswa SET nama=?, prodi=?, ipk=?, status=? WHERE nim=?"
            self.__db.execute_update(query, (nama, prodi, ipk, status, nim))
            
            # Update cache
            for item in self.__data:
                if item['nim'] == nim:
                    item.update({'nama': nama, 'prodi': prodi, 'ipk': ipk, 'status': status})
                    break
            
            return True, "✅ Data berhasil diupdate!"
            
        except (ValidationError, DatabaseError) as e:
            return False, f"❌ {str(e)}"
        except Exception as e:
            return False, f"❌ Terjadi kesalahan: {str(e)}"
    
    def hapus(self, nim: str) -> Tuple[bool, str]:
        """Hapus data - O(n)"""
        try:
            if not self.get_by_nim(nim):
                raise ValidationError("NIM tidak ditemukan!")
            
            query = "DELETE FROM mahasiswa WHERE nim = ?"
            self.__db.execute_update(query, (nim,))
            
            # Update cache
            self.__data = [item for item in self.__data if item['nim'] != nim]
            
            return True, "✅ Data berhasil dihapus!"
            
        except (ValidationError, DatabaseError) as e:
            return False, f"❌ {str(e)}"
        except Exception as e:
            return False, f"❌ Terjadi kesalahan: {str(e)}"
    
    def generate_contoh(self) -> Tuple[bool, str]:
        """Generate data contoh"""
        sample_data = [
            ("2010114001", "Fajar Dian Taufani", "Teknik Informatika", 3.85, "Aktif"),
            ("2010114005", "Siti Aminah", "Sistem Informasi", 3.40, "Aktif"),
            ("2010114002", "Andi Wijaya", "Teknik Informatika", 2.90, "Cuti"),
            ("2010114012", "Riska Amelia", "Manajemen", 4.00, "Aktif"),
            ("2010114009", "Budi Santoso", "Akuntansi", 3.15, "Pasif"),
            ("2010114015", "Dewi Lestari", "Teknik Informatika", 3.60, "Aktif"),
            ("2010114020", "Rahmat Hidayat", "Sistem Informasi", 2.75, "Aktif")
        ]
        
        added = 0
        for data in sample_data:
            success, _ = self.tambah(*data)
            if success:
                added += 1
        
        return True, f"✅ {added} data contoh berhasil ditambahkan!"

# ============================================================================
# CLASS AUTH MANAGER
# ============================================================================

class AuthManager:
    """Manajemen autentikasi"""
    
    def __init__(self):
        self.__db = DatabaseManager()
    
    def login(self, username: str, password: str) -> Tuple[bool, str]:
        try:
            query = "SELECT * FROM users WHERE username = ? AND password = ?"
            result = self.__db.execute_query(query, (username, password))
            
            if result:
                return True, "Login berhasil!"
            return False, "Username atau password salah!"
            
        except DatabaseError as e:
            return False, str(e)

# ============================================================================
# STREAMLIT UI - CLEAN & TERSTRUKTUR
# ============================================================================

class StreamlitUI:
    """UI Streamlit dengan tampilan clean"""
    
    def __init__(self):
        self.mahasiswa = MahasiswaManager()
        self.auth = AuthManager()
        self._init_session()
        self._setup_page()
    
    def _init_session(self):
        """Inisialisasi session state"""
        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False
            st.session_state.username = ""
    
    def _setup_page(self):
        """Setup halaman"""
        st.set_page_config(
            page_title=Config.PAGE_TITLE,
            page_icon=Config.PAGE_ICON,
            layout="wide"
        )
        
        # CSS Custom
        st.markdown("""
            <style>
                /* Header */
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
                
                /* Card */
                .card {
                    background: white;
                    padding: 20px;
                    border-radius: 15px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    margin-bottom: 20px;
                }
                
                /* Badge */
                .badge {
                    background: #667eea;
                    color: white;
                    padding: 5px 15px;
                    border-radius: 20px;
                    font-size: 0.8rem;
                    display: inline-block;
                    margin: 5px;
                }
                
                .badge-success {
                    background: #10b981;
                }
                
                .badge-warning {
                    background: #f59e0b;
                }
                
                .badge-danger {
                    background: #ef4444;
                }
                
                /* Complexity Info */
                .complexity-box {
                    background: #f3f4f6;
                    padding: 15px;
                    border-radius: 10px;
                    border-left: 4px solid #667eea;
                    margin: 15px 0;
                }
                
                .complexity-box code {
                    background: #e5e7eb;
                    padding: 2px 8px;
                    border-radius: 5px;
                }
            </style>
        """, unsafe_allow_html=True)
    
    def _render_login(self):
        """Halaman Login"""
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("""
                <div style="background: white; padding: 40px; border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
                    <h2 style="text-align: center; margin-bottom: 30px;">🔐 Login</h2>
            """, unsafe_allow_html=True)
            
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Masukkan username")
                password = st.text_input("Password", type="password", placeholder="Masukkan password")
                
                submitted = st.form_submit_button("Login", use_container_width=True)
                
                if submitted:
                    success, msg = self.auth.login(username, password)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.rerun()
                    else:
                        st.error(msg)
            
            st.markdown("""
                <div style="text-align: center; margin-top: 20px; padding: 15px; background: #f3f4f6; border-radius: 10px;">
                    <p style="margin: 0;">📝 Demo: <code>admin</code> / <code>admin123</code></p>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    def _render_sidebar(self):
        """Sidebar navigasi"""
        with st.sidebar:
            st.markdown(f"""
                <div style="text-align: center; padding: 10px;">
                    <h3>👤 {st.session_state.username}</h3>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Menu utama dengan ikon
            menu = st.radio(
                "📋 Menu",
                [
                    "🏠 Dashboard",
                    "➕ Tambah Data",
                    "📋 Data Mahasiswa",
                    "🔍 Pencarian",
                    "📊 Statistik"
                ],
                index=0
            )
            
            st.markdown("---")
            
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.rerun()
            
            return menu
    
    def _render_dashboard(self):
        """Dashboard"""
        st.markdown("""
            <div class="main-header">
                <h1>📊 Dashboard</h1>
                <p>Ringkasan data mahasiswa</p>
            </div>
        """, unsafe_allow_html=True)
        
        data = self.mahasiswa.get_all()
        
        # Statistik Cards
        col1, col2, col3, col4 = st.columns(4)
        
        total = len(data)
        aktif = len([d for d in data if d['status'] == 'Aktif'])
        avg_ipk = sum(d['ipk'] for d in data) / total if total > 0 else 0
        max_ipk = max([d['ipk'] for d in data]) if data else 0
        
        with col1:
            st.metric("📊 Total Mahasiswa", total)
        with col2:
            st.metric("✅ Aktif", aktif)
        with col3:
            st.metric("⭐ Rata-rata IPK", f"{avg_ipk:.2f}")
        with col4:
            st.metric("🏆 IPK Tertinggi", f"{max_ipk:.2f}")
        
        # Tombol Generate
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📄 Generate Contoh Data", use_container_width=True):
                success, msg = self.mahasiswa.generate_contoh()
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
        
        # Tabel data terbaru
        st.markdown("---")
        st.subheader("📋 Data Terbaru")
        
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df.head(10), use_container_width=True)
        else:
            st.info("Belum ada data. Klik 'Generate Contoh Data' untuk menambahkan.")
    
    def _render_tambah(self):
        """Halaman Tambah Data"""
        st.markdown("""
            <div class="main-header">
                <h1>➕ Tambah Mahasiswa</h1>
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
            
            st.markdown("""
                <div class="complexity-box">
                    <b>⚡ Kompleksitas:</b><br>
                    • Validasi: O(1)<br>
                    • Insert Data: O(1)<br>
                    • Update Cache: O(1)
                </div>
            """, unsafe_allow_html=True)
            
            submitted = st.form_submit_button("💾 Simpan Data", use_container_width=True)
            
            if submitted:
                if not nim or not nama:
                    st.error("❌ NIM dan Nama harus diisi!")
                else:
                    success, msg = self.mahasiswa.tambah(nim, nama, prodi, ipk, status)
                    if success:
                        st.success(msg)
                        st.balloons()
                    else:
                        st.error(msg)
    
    def _render_data(self):
        """Halaman Data Mahasiswa"""
        st.markdown("""
            <div class="main-header">
                <h1>📋 Data Mahasiswa</h1>
                <p>Kelola data mahasiswa</p>
            </div>
        """, unsafe_allow_html=True)
        
        data = self.mahasiswa.get_all()
        
        if not data:
            st.info("Belum ada data. Generate contoh data terlebih dahulu.")
            return
        
        # Filter dan Search
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search = st.text_input("🔍 Cari", placeholder="Ketik NIM atau Nama...")
        with col2:
            filter_status = st.selectbox("Filter Status", ["Semua"] + Config.STATUS_LIST)
        with col3:
            sort_by = st.selectbox("Urutkan", ["NIM", "Nama", "IPK", "Status"])
        
        # Filter data
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
        
        # Sorting
        key_map = {"NIM": "nim", "Nama": "nama", "IPK": "ipk", "Status": "status"}
        if sort_by in key_map:
            filtered = sorted(filtered, key=lambda x: x[key_map[sort_by]])
        
        # Tampilkan data
        if filtered:
            df = pd.DataFrame(filtered)
            st.dataframe(df, use_container_width=True)
            
            # Hapus Data
            st.markdown("---")
            st.subheader("🗑️ Hapus Data")
            
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
            st.warning("Tidak ada data yang cocok dengan filter.")
    
    def _render_search(self):
        """Halaman Pencarian dengan Algoritma"""
        st.markdown("""
            <div class="main-header">
                <h1>🔍 Pencarian Mahasiswa</h1>
                <p>Gunakan berbagai algoritma pencarian</p>
            </div>
        """, unsafe_allow_html=True)
        
        data = self.mahasiswa.get_all()
        
        if not data:
            st.info("Belum ada data. Generate contoh data terlebih dahulu.")
            return
        
        st.markdown("""
            <div class="card">
                <h4>📖 Pilih Algoritma Pencarian</h4>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            algorithm = st.selectbox(
                "Algoritma",
                [
                    "Linear Search - O(n)",
                    "Binary Search - O(log n)",
                    "Sequential Search - O(n)"
                ]
            )
        
        with col2:
            search_type = st.selectbox("Cari Berdasarkan", ["NIM", "Nama"])
            keyword = st.text_input("Kata Kunci", placeholder="Masukkan kata kunci...")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Complexity Info
        st.markdown("""
            <div class="complexity-box">
                <b>📊 Perbandingan Kompleksitas:</b><br>
                • <b>Linear Search</b>: O(n) - Mencari satu per satu dari awal<br>
                • <b>Binary Search</b>: O(log n) - Membagi data menjadi 2 bagian (data harus terurut)<br>
                • <b>Sequential Search</b>: O(n) - Mencari di semua field
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔍 Cari", use_container_width=True):
            if not keyword:
                st.warning("⚠️ Masukkan kata kunci terlebih dahulu!")
                return
            
            key = "nim" if search_type == "NIM" else "nama"
            results = []
            
            # Jalankan algoritma yang dipilih
            if "Linear" in algorithm:
                with st.spinner("Mencari dengan Linear Search..."):
                    result = SearchAlgorithms.linear_search(data, key, keyword)
                    if result:
                        results = [result]
                    st.info(f"✅ Linear Search selesai - O(n)")
            
            elif "Binary" in algorithm:
                with st.spinner("Mencari dengan Binary Search..."):
                    result = SearchAlgorithms.binary_search(data, key, keyword)
                    if result:
                        results = [result]
                    st.info(f"✅ Binary Search selesai - O(log n)")
            
            else:  # Sequential
                with st.spinner("Mencari dengan Sequential Search..."):
                    results = SearchAlgorithms.sequential_search(data, keyword)
                    st.info(f"✅ Sequential Search selesai - O(n)")
            
            # Tampilkan hasil
            if results:
                st.success(f"✅ Ditemukan {len(results)} data!")
                df = pd.DataFrame(results)
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("❌ Data tidak ditemukan!")
    
    def _render_statistik(self):
        """Halaman Statistik dengan Sorting"""
        st.markdown("""
            <div class="main-header">
                <h1>📊 Statistik & Sorting</h1>
                <p>Analisis data dan demo sorting</p>
            </div>
        """, unsafe_allow_html=True)
        
        data = self.mahasiswa.get_all()
        
        if not data:
            st.info("Belum ada data. Generate contoh data terlebih dahulu.")
            return
        
        # Statistik
        col1, col2, col3 = st.columns(3)
        
        total = len(data)
        aktif = len([d for d in data if d['status'] == 'Aktif'])
        avg_ipk = sum(d['ipk'] for d in data) / total
        
        with col1:
            st.metric("Total", total)
        with col2:
            st.metric("Aktif", aktif)
        with col3:
            st.metric("Rata-rata IPK", f"{avg_ipk:.2f}")
        
        # Grafik Status
        st.subheader("📊 Distribusi Status")
        status_counts = {}
        for item in data:
            status_counts[item['status']] = status_counts.get(item['status'], 0) + 1
        
        df_status = pd.DataFrame(list(status_counts.items()), columns=['Status', 'Jumlah'])
        fig = px.pie(df_status, values='Jumlah', names='Status', hole=0.3)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
        
        # Sorting Demo
        st.markdown("---")
        st.subheader("🔀 Demo Sorting")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            sort_algorithm = st.selectbox(
                "Algoritma",
                [
                    "Bubble Sort - O(n²)",
                    "Insertion Sort - O(n²)",
                    "Merge Sort - O(n log n)",
                    "Shell Sort - O(n log n)"
                ]
            )
        
        with col2:
            sort_key = st.selectbox("Sort Berdasarkan", ["NIM", "Nama", "IPK", "Status"])
        
        with col3:
            sort_reverse = st.checkbox("Descending")
        
        # Complexity Info
        st.markdown("""
            <div class="complexity-box">
                <b>📊 Perbandingan Kompleksitas Sorting:</b><br>
                • <b>Bubble Sort</b>: O(n²) - Membandingkan elemen bersebelahan<br>
                • <b>Insertion Sort</b>: O(n²) - Membangun array terurut satu per satu<br>
                • <b>Merge Sort</b>: O(n log n) - Membagi dan menggabungkan<br>
                • <b>Shell Sort</b>: O(n log n) - Perbaikan insertion sort dengan gap
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Jalankan Sorting", use_container_width=True):
            with st.spinner(f"Menjalankan {sort_algorithm}..."):
                key_map = {"NIM": "nim", "Nama": "nama", "IPK": "ipk", "Status": "status"}
                algo_map = {
                    "Bubble Sort - O(n²)": "bubble",
                    "Insertion Sort - O(n²)": "insertion",
                    "Merge Sort - O(n log n)": "merge",
                    "Shell Sort - O(n log n)": "shell"
                }
                
                algo_name = algo_map[sort_algorithm]
                key = key_map[sort_key]
                
                # Panggil algoritma sorting
                if algo_name == "bubble":
                    sorted_data = SortingAlgorithms.bubble_sort(data, key, sort_reverse)
                elif algo_name == "insertion":
                    sorted_data = SortingAlgorithms.insertion_sort(data, key, sort_reverse)
                elif algo_name == "merge":
                    sorted_data = SortingAlgorithms.merge_sort(data, key, sort_reverse)
                else:  # shell
                    sorted_data = SortingAlgorithms.shell_sort(data, key, sort_reverse)
                
                st.success(f"✅ Sorting selesai dengan {sort_algorithm}")
                df = pd.DataFrame(sorted_data)
                st.dataframe(df, use_container_width=True)
    
    def run(self):
        """Main run"""
        # Header
        st.markdown("""
            <div class="main-header">
                <h1>🎓 SIMM - Sistem Informasi Mahasiswa</h1>
                <p>Universitas Pamulang</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Cek login
        if not st.session_state.logged_in:
            self._render_login()
            return
        
        # Render sidebar dan dapatkan menu
        menu = self._render_sidebar()
        
        # Render menu
        if menu == "🏠 Dashboard":
            self._render_dashboard()
        elif menu == "➕ Tambah Data":
            self._render_tambah()
        elif menu == "📋 Data Mahasiswa":
            self._render_data()
        elif menu == "🔍 Pencarian":
            self._render_search()
        elif menu == "📊 Statistik":
            self._render_statistik()

# ============================================================================
# MAIN
# ============================================================================

def main():
    app = StreamlitUI()
    app.run()

if __name__ == "__main__":
    main()
