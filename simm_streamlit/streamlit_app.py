"""
SIMM - Sistem Informasi Manajemen Mahasiswa
Universitas Pamulang

Aplikasi ini mengimplementasikan:
- CRUD Operations
- OOP (Encapsulation, Inheritance, Polymorphism)
- Searching Algorithms (Linear, Binary, Sequential)
- Sorting Algorithms (Bubble, Insertion, Selection, Merge, Shell)
- File I/O dengan SQLite
- Validasi dengan Regex
- Exception Handling
- Dokumentasi Time Complexity
"""

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import re
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from abc import ABC, abstractmethod

# ============================================================================
# KONFIGURASI DAN KONSTANTA
# ============================================================================

class AppConfig:
    """Konfigurasi aplikasi"""
    DB_NAME = 'database.db'
    PAGE_TITLE = "SIMM - Sistem Informasi Mahasiswa"
    PAGE_ICON = "🎓"
    LAYOUT = "wide"
    THEME = "dark"
    
    # Regex patterns untuk validasi
    NIM_PATTERN = r'^[0-9]{10,12}$'
    NAMA_PATTERN = r'^[A-Za-z\s]{2,50}$'
    IPK_PATTERN = r'^[0-4](\.\d{1,2})?$'
    USERNAME_PATTERN = r'^[A-Za-z0-9_]{3,20}$'
    PASSWORD_PATTERN = r'^.{3,}$'
    
    # Daftar program studi
    PRODI_LIST = [
        "Teknik Informatika", "Sistem Informasi", "Manajemen Informatika",
        "Teknik Komputer", "Akuntansi", "Manajemen", "Hukum", "Psikologi"
    ]
    
    STATUS_LIST = ["Aktif", "Pasif", "Cuti"]

# ============================================================================
# CUSTOM EXCEPTION
# ============================================================================

class ValidationError(Exception):
    """Exception untuk error validasi"""
    pass

class DatabaseError(Exception):
    """Exception untuk error database"""
    pass

class NotFoundError(Exception):
    """Exception untuk data tidak ditemukan"""
    pass

# ============================================================================
# CLASS MAHASISWA (OOP - Encapsulation)
# ============================================================================

class Mahasiswa:
    """
    Class Mahasiswa dengan implementasi Encapsulation
    
    Time Complexity: O(1) untuk semua operasi dasar
    Space Complexity: O(1)
    """
    
    def __init__(self, nim: str, nama: str, prodi: str, ipk: float, status: str = "Aktif"):
        """
        Constructor Mahasiswa
        Time Complexity: O(1)
        Space Complexity: O(1)
        """
        self.__nim = nim          # Private attribute (Encapsulation)
        self.__nama = nama
        self.__prodi = prodi
        self.__ipk = ipk
        self.__status = status
        self.__created_at = datetime.now()
    
    # ========== GETTER METHODS ==========
    def get_nim(self) -> str:
        """Getter untuk NIM - Time Complexity: O(1)"""
        return self.__nim
    
    def get_nama(self) -> str:
        """Getter untuk Nama - Time Complexity: O(1)"""
        return self.__nama
    
    def get_prodi(self) -> str:
        """Getter untuk Program Studi - Time Complexity: O(1)"""
        return self.__prodi
    
    def get_ipk(self) -> float:
        """Getter untuk IPK - Time Complexity: O(1)"""
        return self.__ipk
    
    def get_status(self) -> str:
        """Getter untuk Status - Time Complexity: O(1)"""
        return self.__status
    
    def get_created_at(self) -> datetime:
        """Getter untuk Created At - Time Complexity: O(1)"""
        return self.__created_at
    
    # ========== SETTER METHODS ==========
    def set_nama(self, nama: str) -> None:
        """Setter untuk Nama dengan validasi - Time Complexity: O(1)"""
        if not self._validate_nama(nama):
            raise ValidationError("Format nama tidak valid!")
        self.__nama = nama
    
    def set_prodi(self, prodi: str) -> None:
        """Setter untuk Program Studi - Time Complexity: O(1)"""
        if prodi not in AppConfig.PRODI_LIST:
            raise ValidationError("Program studi tidak valid!")
        self.__prodi = prodi
    
    def set_ipk(self, ipk: float) -> None:
        """Setter untuk IPK dengan validasi - Time Complexity: O(1)"""
        if not 0.0 <= ipk <= 4.0:
            raise ValidationError("IPK harus antara 0.00 - 4.00!")
        self.__ipk = ipk
    
    def set_status(self, status: str) -> None:
        """Setter untuk Status - Time Complexity: O(1)"""
        if status not in AppConfig.STATUS_LIST:
            raise ValidationError("Status tidak valid!")
        self.__status = status
    
    # ========== VALIDATION METHODS ==========
    @staticmethod
    def _validate_nama(nama: str) -> bool:
        """Validasi nama dengan Regex - Time Complexity: O(n)"""
        return bool(re.match(AppConfig.NAMA_PATTERN, nama))
    
    @staticmethod
    def validate_nim(nim: str) -> bool:
        """Validasi NIM dengan Regex - Time Complexity: O(n)"""
        return bool(re.match(AppConfig.NIM_PATTERN, nim))
    
    @staticmethod
    def validate_ipk(ipk: float) -> bool:
        """Validasi IPK dengan Regex - Time Complexity: O(1)"""
        return bool(re.match(AppConfig.IPK_PATTERN, str(ipk)))
    
    # ========== TO DICT METHOD ==========
    def to_dict(self) -> Dict[str, Any]:
        """
        Konversi objek ke dictionary
        Time Complexity: O(1)
        """
        return {
            'nim': self.__nim,
            'nama': self.__nama,
            'prodi': self.__prodi,
            'ipk': self.__ipk,
            'status': self.__status
        }
    
    # ========== STRING REPRESENTATION ==========
    def __str__(self) -> str:
        """String representation - Time Complexity: O(1)"""
        return f"{self.__nama} ({self.__nim}) - {self.__prodi} - IPK: {self.__ipk}"

# ============================================================================
# CLASS MAHASISWA AKTIF (OOP - Inheritance & Polymorphism)
# ============================================================================

class MahasiswaAktif(Mahasiswa):
    """
    Class turunan dari Mahasiswa untuk status Aktif
    Implementasi Inheritance dan Polymorphism
    """
    
    def __init__(self, nim: str, nama: str, prodi: str, ipk: float):
        """
        Constructor MahasiswaAktif
        Time Complexity: O(1)
        """
        super().__init__(nim, nama, prodi, ipk, "Aktif")
        self.__semester = 1  # Additional attribute
    
    def get_semester(self) -> int:
        """Getter untuk Semester"""
        return self.__semester
    
    def set_semester(self, semester: int) -> None:
        """Setter untuk Semester"""
        if semester < 1:
            raise ValidationError("Semester minimal 1!")
        self.__semester = semester
    
    # Polymorphism - Override method
    def to_dict(self) -> Dict[str, Any]:
        """Override method to_dict"""
        data = super().to_dict()
        data['semester'] = self.__semester
        return data
    
    def __str__(self) -> str:
        """Override string representation"""
        return f"{super().__str__()} - Semester {self.__semester}"

# ============================================================================
# CLASS MAHASISWA CUTI (OOP - Inheritance)
# ============================================================================

class MahasiswaCuti(Mahasiswa):
    """
    Class turunan dari Mahasiswa untuk status Cuti
    Implementasi Inheritance
    """
    
    def __init__(self, nim: str, nama: str, prodi: str, ipk: float):
        super().__init__(nim, nama, prodi, ipk, "Cuti")
        self.__alasan_cuti = ""  # Additional attribute
    
    def get_alasan_cuti(self) -> str:
        """Getter untuk Alasan Cuti"""
        return self.__alasan_cuti
    
    def set_alasan_cuti(self, alasan: str) -> None:
        """Setter untuk Alasan Cuti"""
        self.__alasan_cuti = alasan
    
    def __str__(self) -> str:
        """Override string representation"""
        base = super().__str__()
        return f"{base} - Alasan: {self.__alasan_cuti if self.__alasan_cuti else 'Tidak ada alasan'}"

# ============================================================================
# CLASS DATABASE MANAGER (OOP - Encapsulation)
# ============================================================================

class DatabaseManager:
    """
    Manajemen database dengan SQLite
    Implementasi Encapsulation untuk operasi database
    
    Time Complexity: O(1) untuk koneksi, O(n) untuk operasi data
    """
    
    def __init__(self, db_name: str = AppConfig.DB_NAME):
        """
        Constructor DatabaseManager
        Time Complexity: O(1)
        """
        self.__db_name = db_name
        self.__connection = None
        self._init_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        """
        Mendapatkan koneksi database
        Time Complexity: O(1)
        """
        if self.__connection is None:
            self.__connection = sqlite3.connect(self.__db_name)
        return self.__connection
    
    def _close_connection(self) -> None:
        """
        Menutup koneksi database
        Time Complexity: O(1)
        """
        if self.__connection:
            self.__connection.close()
            self.__connection = None
    
    def _init_database(self) -> None:
        """
        Inisialisasi database dan tabel
        Time Complexity: O(1)
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Tabel users
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabel mahasiswa
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
            
            # Insert default user
            cursor.execute(
                "INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)",
                ('fitra', '12345')
            )
            
            conn.commit()
        except sqlite3.Error as e:
            raise DatabaseError(f"Gagal inisialisasi database: {str(e)}")
        finally:
            self._close_connection()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[tuple]:
        """
        Eksekusi query SELECT
        Time Complexity: O(n) dimana n = jumlah data
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
        except sqlite3.Error as e:
            raise DatabaseError(f"Gagal execute query: {str(e)}")
        finally:
            self._close_connection()
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """
        Eksekusi query INSERT/UPDATE/DELETE
        Time Complexity: O(1) untuk operasi dasar
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
        except sqlite3.Error as e:
            raise DatabaseError(f"Gagal execute update: {str(e)}")
        finally:
            self._close_connection()

# ============================================================================
# CLASS SEARCH ALGORITHMS (OOP - Polymorphism)
# ============================================================================

class SearchAlgorithms:
    """
    Implementasi berbagai algoritma pencarian
    """
    
    @staticmethod
    def linear_search(data: List[Dict], key: str, value: Any) -> Optional[Dict]:
        """
        Linear Search / Sequential Search
        
        Time Complexity: O(n)
        Space Complexity: O(1)
        
        Args:
            data: List of dictionaries
            key: Key to search
            value: Value to find
            
        Returns:
            First matching item or None
        """
        for item in data:
            if str(item.get(key, '')).lower() == str(value).lower():
                return item
        return None
    
    @staticmethod
    def linear_search_all(data: List[Dict], key: str, value: Any) -> List[Dict]:
        """
        Linear Search - Find all matches
        
        Time Complexity: O(n)
        Space Complexity: O(k) dimana k = jumlah hasil
        """
        results = []
        for item in data:
            if str(item.get(key, '')).lower() == str(value).lower():
                results.append(item)
        return results
    
    @staticmethod
    def binary_search(data: List[Dict], key: str, value: Any) -> Optional[Dict]:
        """
        Binary Search (data harus sudah terurut berdasarkan key)
        
        Time Complexity: O(log n)
        Space Complexity: O(1)
        
        Args:
            data: List of dictionaries (sorted by key)
            key: Key to search
            value: Value to find
            
        Returns:
            Matching item or None
        """
        if not data:
            return None
        
        # Sort data by key first
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
    def sequential_search(data: List[Dict], conditions: Dict[str, Any]) -> List[Dict]:
        """
        Sequential Search dengan multiple conditions
        
        Time Complexity: O(n)
        Space Complexity: O(k) dimana k = jumlah hasil
        
        Args:
            data: List of dictionaries
            conditions: Dictionary of key-value pairs to match
            
        Returns:
            List of matching items
        """
        results = []
        for item in data:
            match = True
            for key, value in conditions.items():
                if key in item:
                    item_value = str(item[key]).lower()
                    search_value = str(value).lower()
                    if search_value not in item_value:
                        match = False
                        break
            if match:
                results.append(item)
        return results

# ============================================================================
# CLASS SORTING ALGORITHMS (OOP)
# ============================================================================

class SortingAlgorithms:
    """
    Implementasi berbagai algoritma pengurutan
    """
    
    @staticmethod
    def bubble_sort(data: List[Dict], key: str, reverse: bool = False) -> List[Dict]:
        """
        Bubble Sort Algorithm
        
        Time Complexity: O(n²) - Worst Case, O(n) - Best Case
        Space Complexity: O(1)
        
        Args:
            data: List of dictionaries
            key: Key to sort by
            reverse: Sort descending if True
            
        Returns:
            Sorted list
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
        Insertion Sort Algorithm
        
        Time Complexity: O(n²) - Worst Case, O(n) - Best Case
        Space Complexity: O(1)
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
    def selection_sort(data: List[Dict], key: str, reverse: bool = False) -> List[Dict]:
        """
        Selection Sort Algorithm
        
        Time Complexity: O(n²) - All Cases
        Space Complexity: O(1)
        """
        arr = data.copy()
        n = len(arr)
        
        for i in range(n):
            min_idx = i
            for j in range(i + 1, n):
                val1 = str(arr[j].get(key, '')).lower()
                val2 = str(arr[min_idx].get(key, '')).lower()
                
                if (val1 < val2 and not reverse) or (val1 > val2 and reverse):
                    min_idx = j
            
            if min_idx != i:
                arr[i], arr[min_idx] = arr[min_idx], arr[i]
        
        return arr
    
    @staticmethod
    def merge_sort(data: List[Dict], key: str, reverse: bool = False) -> List[Dict]:
        """
        Merge Sort Algorithm
        
        Time Complexity: O(n log n) - All Cases
        Space Complexity: O(n)
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
        """Helper untuk merge sort"""
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
        Shell Sort Algorithm
        
        Time Complexity: O(n log n) - Average, O(n²) - Worst Case
        Space Complexity: O(1)
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
# CLASS MAHASISWA MANAGER (Main Business Logic)
# ============================================================================

class MahasiswaManager:
    """
    Manajemen data mahasiswa dengan implementasi OOP
    Menggunakan Array (List) untuk menyimpan data
    """
    
    def __init__(self):
        """Constructor - Time Complexity: O(1)"""
        self.__db = DatabaseManager()
        self.__mahasiswa_list: List[Dict] = []
        self._load_data()
    
    def _load_data(self) -> None:
        """
        Load data dari database ke dalam array (List)
        Time Complexity: O(n) dimana n = jumlah data
        """
        try:
            data = self.__db.execute_query("SELECT * FROM mahasiswa")
            self.__mahasiswa_list = [
                {
                    'nim': row[0],
                    'nama': row[1],
                    'prodi': row[2],
                    'ipk': row[3],
                    'status': row[4]
                }
                for row in data
            ]
        except DatabaseError:
            self.__mahasiswa_list = []
    
    def get_all(self) -> List[Dict]:
        """
        Mendapatkan semua data mahasiswa
        
        Time Complexity: O(1) - Returns reference
        """
        return self.__mahasiswa_list
    
    def get_by_nim(self, nim: str) -> Optional[Dict]:
        """
        Mencari mahasiswa berdasarkan NIM menggunakan Linear Search
        
        Time Complexity: O(n)
        """
        return SearchAlgorithms.linear_search(self.__mahasiswa_list, 'nim', nim)
    
    def search(self, keyword: str, field: str = 'nama') -> List[Dict]:
        """
        Mencari mahasiswa dengan Sequential Search
        
        Time Complexity: O(n)
        """
        return SearchAlgorithms.sequential_search(
            self.__mahasiswa_list,
            {field: keyword}
        )
    
    def sort(self, key: str = 'nama', algorithm: str = 'bubble', reverse: bool = False) -> List[Dict]:
        """
        Mengurutkan data mahasiswa dengan berbagai algoritma
        
        Time Complexity: Bervariasi tergantung algoritma
        """
        algorithms = {
            'bubble': SortingAlgorithms.bubble_sort,
            'insertion': SortingAlgorithms.insertion_sort,
            'selection': SortingAlgorithms.selection_sort,
            'merge': SortingAlgorithms.merge_sort,
            'shell': SortingAlgorithms.shell_sort
        }
        
        if algorithm not in algorithms:
            raise ValidationError(f"Algoritma '{algorithm}' tidak dikenal!")
        
        return algorithms[algorithm](self.__mahasiswa_list, key, reverse)
    
    def tambah(self, nim: str, nama: str, prodi: str, ipk: float, status: str = "Aktif") -> Tuple[bool, str]:
        """
        Menambahkan data mahasiswa baru
        
        Time Complexity: O(1)
        """
        try:
            # Validasi dengan Regex
            if not Mahasiswa.validate_nim(nim):
                raise ValidationError("NIM harus 10-12 digit angka!")
            
            if not Mahasiswa._validate_nama(nama):
                raise ValidationError("Nama hanya boleh huruf dan spasi (2-50 karakter)!")
            
            if not Mahasiswa.validate_ipk(ipk):
                raise ValidationError("IPK harus antara 0.00 - 4.00!")
            
            # Cek duplikat
            if self.get_by_nim(nim):
                raise ValidationError("NIM sudah terdaftar!")
            
            # Buat objek Mahasiswa
            if status == "Aktif":
                mahasiswa = MahasiswaAktif(nim, nama, prodi, ipk)
            elif status == "Cuti":
                mahasiswa = MahasiswaCuti(nim, nama, prodi, ipk)
            else:
                mahasiswa = Mahasiswa(nim, nama, prodi, ipk, status)
            
            # Simpan ke database
            data = mahasiswa.to_dict()
            query = """
                INSERT INTO mahasiswa (nim, nama, prodi, ipk, status)
                VALUES (?, ?, ?, ?, ?)
            """
            self.__db.execute_update(query, (
                data['nim'], data['nama'], data['prodi'],
                data['ipk'], data['status']
            ))
            
            # Update array
            self.__mahasiswa_list.append(data)
            
            return True, "Data berhasil ditambahkan!"
            
        except (ValidationError, DatabaseError) as e:
            return False, str(e)
        except Exception as e:
            return False, f"Terjadi kesalahan: {str(e)}"
    
    def update(self, nim: str, nama: str, prodi: str, ipk: float, status: str) -> Tuple[bool, str]:
        """
        Mengupdate data mahasiswa
        
        Time Complexity: O(n) - Linear search untuk cari data
        """
        try:
            # Validasi
            if not Mahasiswa._validate_nama(nama):
                raise ValidationError("Nama hanya boleh huruf dan spasi (2-50 karakter)!")
            
            if not Mahasiswa.validate_ipk(ipk):
                raise ValidationError("IPK harus antara 0.00 - 4.00!")
            
            # Cari data
            existing = self.get_by_nim(nim)
            if not existing:
                raise NotFoundError("Mahasiswa dengan NIM tersebut tidak ditemukan!")
            
            # Update database
            query = """
                UPDATE mahasiswa 
                SET nama=?, prodi=?, ipk=?, status=?
                WHERE nim=?
            """
            self.__db.execute_update(query, (nama, prodi, float(ipk), status, nim))
            
            # Update array
            for i, item in enumerate(self.__mahasiswa_list):
                if item['nim'] == nim:
                    self.__mahasiswa_list[i] = {
                        'nim': nim, 'nama': nama,
                        'prodi': prodi, 'ipk': ipk, 'status': status
                    }
                    break
            
            return True, "Data berhasil diupdate!"
            
        except (ValidationError, NotFoundError, DatabaseError) as e:
            return False, str(e)
        except Exception as e:
            return False, f"Terjadi kesalahan: {str(e)}"
    
    def hapus(self, nim: str) -> Tuple[bool, str]:
        """
        Menghapus data mahasiswa
        
        Time Complexity: O(n) - Linear search untuk cari data
        """
        try:
            # Cek data exists
            if not self.get_by_nim(nim):
                raise NotFoundError("Mahasiswa dengan NIM tersebut tidak ditemukan!")
            
            # Hapus dari database
            query = "DELETE FROM mahasiswa WHERE nim = ?"
            self.__db.execute_update(query, (nim,))
            
            # Hapus dari array
            self.__mahasiswa_list = [
                item for item in self.__mahasiswa_list
                if item['nim'] != nim
            ]
            
            return True, "Data berhasil dihapus!"
            
        except (NotFoundError, DatabaseError) as e:
            return False, str(e)
        except Exception as e:
            return False, f"Terjadi kesalahan: {str(e)}"
    
    def generate_contoh(self) -> Tuple[bool, str]:
        """
        Generate data contoh
        
        Time Complexity: O(n) dimana n = jumlah data contoh
        """
        sample_data = [
            ("2010114001", "Fajar Dian Taufani", "Teknik Informatika", 3.85, "Aktif"),
            ("2010114005", "Siti Aminah", "Sistem Informasi", 3.40, "Aktif"),
            ("2010114002", "Andi Wijaya", "Teknik Informatika", 2.90, "Cuti"),
            ("2010114012", "Riska Amelia", "Manajemen", 4.00, "Aktif"),
            ("2010114009", "Budi Santoso", "Akuntansi", 3.15, "Pasif")
        ]
        
        added = 0
        for data in sample_data:
            success, _ = self.tambah(*data)
            if success:
                added += 1
        
        return True, f"{added} data contoh berhasil ditambahkan!"
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Mendapatkan statistik data
        
        Time Complexity: O(n)
        """
        if not self.__mahasiswa_list:
            return {
                'total': 0,
                'aktif': 0,
                'avg_ipk': 0.0,
                'max_ipk': 0.0,
                'min_ipk': 0.0,
                'prodi_counts': {}
            }
        
        ipk_values = [item['ipk'] for item in self.__mahasiswa_list]
        status_counts = {}
        prodi_counts = {}
        
        for item in self.__mahasiswa_list:
            status_counts[item['status']] = status_counts.get(item['status'], 0) + 1
            prodi_counts[item['prodi']] = prodi_counts.get(item['prodi'], 0) + 1
        
        return {
            'total': len(self.__mahasiswa_list),
            'aktif': status_counts.get('Aktif', 0),
            'avg_ipk': sum(ipk_values) / len(ipk_values),
            'max_ipk': max(ipk_values),
            'min_ipk': min(ipk_values),
            'status_counts': status_counts,
            'prodi_counts': prodi_counts
        }

# ============================================================================
# CLASS AUTH MANAGER
# ============================================================================

class AuthManager:
    """Manajemen autentikasi user"""
    
    def __init__(self):
        self.__db = DatabaseManager()
    
    def login(self, username: str, password: str) -> Tuple[bool, str]:
        """
        Login user
        
        Time Complexity: O(1)
        """
        try:
            query = "SELECT * FROM users WHERE username = ? AND password = ?"
            result = self.__db.execute_query(query, (username, password))
            
            if result:
                return True, "Login berhasil!"
            return False, "Username atau password salah!"
            
        except DatabaseError as e:
            return False, str(e)
    
    def register(self, username: str, password: str, confirm_password: str) -> Tuple[bool, str]:
        """
        Register user baru dengan validasi Regex
        
        Time Complexity: O(1)
        """
        try:
            # Validasi dengan Regex
            if not re.match(AppConfig.USERNAME_PATTERN, username):
                raise ValidationError("Username harus 3-20 karakter (huruf, angka, underscore)!")
            
            if not re.match(AppConfig.PASSWORD_PATTERN, password):
                raise ValidationError("Password minimal 3 karakter!")
            
            if password != confirm_password:
                raise ValidationError("Password tidak cocok!")
            
            # Cek username exists
            check_query = "SELECT * FROM users WHERE username = ?"
            if self.__db.execute_query(check_query, (username,)):
                raise ValidationError("Username sudah terdaftar!")
            
            # Insert user
            query = "INSERT INTO users (username, password) VALUES (?, ?)"
            self.__db.execute_update(query, (username, password))
            
            return True, "Registrasi berhasil! Silakan login."
            
        except (ValidationError, DatabaseError) as e:
            return False, str(e)
        except Exception as e:
            return False, f"Terjadi kesalahan: {str(e)}"

# ============================================================================
# STREAMLIT UI CLASS
# ============================================================================

class StreamlitUI:
    """Class untuk mengelola tampilan Streamlit"""
    
    def __init__(self):
        self.mahasiswa_manager = MahasiswaManager()
        self.auth_manager = AuthManager()
        self._init_session_state()
        self._apply_theme()
        self._render_header()
    
    def _init_session_state(self) -> None:
        """Inisialisasi session state"""
        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.theme = "dark"
    
    def _apply_theme(self) -> None:
        """Apply theme CSS"""
        if st.session_state.theme == "dark":
            st.markdown("""
                <style>
                    .stApp { background-color: #0f111a; }
                    .stApp, .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp label { color: white !important; }
                    .stButton > button { background: linear-gradient(135deg, #3b82f6, #2563eb); color: white; border-radius: 10px; font-weight: bold; }
                    .stButton > button:hover { background: linear-gradient(135deg, #2563eb, #1d4ed8); }
                    .stTextInput > div > div > input { 
                        background-color: #1e1e2e; color: white; border: 1px solid #3b82f6; border-radius: 10px; padding: 12px;
                    }
                    .stSelectbox > div > div { background-color: #1e1e2e; color: white; }
                    .stMetric { background: linear-gradient(135deg, #1e1e2e, #16162a); padding: 20px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
                    .stMetric label { color: #9ca3af !important; }
                    .stMetric .stMetric-value { color: #3b82f6 !important; font-size: 2rem !important; }
                    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
                    .stTabs [data-baseweb="tab"] { background-color: #1e1e2e; border-radius: 10px; padding: 10px 25px; color: white; }
                    .stTabs [aria-selected="true"] { background: linear-gradient(135deg, #3b82f6, #2563eb) !important; }
                    .stDataFrame { background-color: #1e1e2e; border-radius: 10px; padding: 10px; }
                    .main-header { text-align: center; padding: 20px; background: linear-gradient(135deg, #3b82f6, #2563eb); border-radius: 20px; margin-bottom: 30px; }
                    .main-header h1 { color: white !important; margin: 0; }
                    .main-header p { color: rgba(255,255,255,0.9) !important; }
                    .complexity-badge { background: #1e1e2e; padding: 10px; border-radius: 10px; border-left: 4px solid #3b82f6; margin: 10px 0; }
                </style>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <style>
                    .stApp { background-color: #f0f2f5; }
                    .stButton > button { background: linear-gradient(135deg, #3b82f6, #2563eb); color: white; border-radius: 10px; font-weight: bold; }
                    .stMetric { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
                    .stMetric label { color: #6b7280 !important; }
                    .stMetric .stMetric-value { color: #3b82f6 !important; font-size: 2rem !important; }
                    .stTabs [data-baseweb="tab"] { background-color: #e0e0e0; border-radius: 10px; padding: 10px 25px; }
                    .stTabs [aria-selected="true"] { background: linear-gradient(135deg, #3b82f6, #2563eb) !important; color: white !important; }
                    .main-header { text-align: center; padding: 20px; background: linear-gradient(135deg, #3b82f6, #2563eb); border-radius: 20px; margin-bottom: 30px; }
                    .main-header h1 { color: white !important; margin: 0; }
                    .main-header p { color: rgba(255,255,255,0.9) !important; }
                    .stDataFrame { background-color: white; border-radius: 10px; padding: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                    .complexity-badge { background: white; padding: 10px; border-radius: 10px; border-left: 4px solid #3b82f6; margin: 10px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                </style>
            """, unsafe_allow_html=True)
    
    def _render_header(self) -> None:
        """Render header aplikasi"""
        st.markdown("""
            <div class="main-header">
                <h1>🎓 SIMM - Sistem Informasi Manajemen Mahasiswa</h1>
                <p>Universitas Pamulang</p>
            </div>
        """, unsafe_allow_html=True)
    
    def _render_sidebar(self) -> None:
        """Render sidebar"""
        with st.sidebar:
            st.markdown(f"### 👤 {st.session_state.username if st.session_state.logged_in else 'Guest'}")
            st.markdown("---")
            
            # Theme toggle
            theme_col1, theme_col2 = st.columns(2)
            with theme_col1:
                if st.button("🌙 Dark", use_container_width=True):
                    st.session_state.theme = "dark"
                    st.rerun()
            with theme_col2:
                if st.button("☀️ Light", use_container_width=True):
                    st.session_state.theme = "light"
                    st.rerun()
            st.markdown("---")
    
    def _render_login(self) -> None:
        """Render halaman login"""
        tab1, tab2 = st.tabs(["🔐 LOGIN", "📝 REGISTER"])
        
        with tab1:
            with st.form("login_form"):
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.markdown("### Masuk ke Akun Anda")
                    username = st.text_input("Username", placeholder="Masukkan username Anda")
                    password = st.text_input("Password", type="password", placeholder="Masukkan password Anda")
                    submitted = st.form_submit_button("🔐 Login", use_container_width=True)
                    
                    if submitted:
                        success, msg = self.auth_manager.login(username, password)
                        if success:
                            st.session_state.logged_in = True
                            st.session_state.username = username
                            st.rerun()
                        else:
                            st.error(f"❌ {msg}")
        
        with tab2:
            with st.form("register_form"):
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.markdown("### Daftar Akun Baru")
                    new_username = st.text_input("Username Baru", placeholder="Pilih username Anda")
                    new_password = st.text_input("Password Baru", type="password", placeholder="Buat password")
                    confirm_password = st.text_input("Konfirmasi Password", type="password", placeholder="Ulangi password Anda")
                    submitted_reg = st.form_submit_button("📝 Daftar", use_container_width=True)
                    
                    if submitted_reg:
                        success, msg = self.auth_manager.register(
                            new_username, new_password, confirm_password
                        )
                        if success:
                            st.success(f"✅ {msg}")
                        else:
                            st.error(f"❌ {msg}")
        
        st.stop()
    
    def _render_dashboard(self) -> None:
        """Render halaman dashboard"""
        st.markdown("### 🏠 Dashboard")
        
        data = self.mahasiswa_manager.get_all()
        stats = self.mahasiswa_manager.get_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Total Mahasiswa", stats['total'])
        with col2:
            st.metric("✅ Mahasiswa Aktif", stats['aktif'])
        with col3:
            st.metric("⭐ Rata-rata IPK", f"{stats['avg_ipk']:.2f}")
        with col4:
            st.metric("🏆 IPK Tertinggi", f"{stats['max_ipk']:.2f}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📄 Generate Contoh Data", use_container_width=True):
                success, msg = self.mahasiswa_manager.generate_contoh()
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
        
        # Complexity Information
        st.markdown("""
            <div class="complexity-badge">
                <b>⚡ Time Complexity Dashboard:</b><br>
                - get_all(): O(1) - Mengembalikan referensi array<br>
                - get_statistics(): O(n) - Iterasi semua data untuk menghitung statistik
            </div>
        """, unsafe_allow_html=True)
        
        st.subheader("📋 Data Mahasiswa Terbaru")
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df.head(10), use_container_width=True)
        else:
            st.info("Belum ada data. Klik 'Generate Contoh Data' untuk mengisi.")
    
    def _render_tambah(self) -> None:
        """Render halaman tambah mahasiswa"""
        st.markdown("### ➕ Tambah Mahasiswa Baru")
        
        with st.form("tambah_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                nim = st.text_input("NIM (10-12 digit)", placeholder="Contoh: 2010114001")
                nama = st.text_input("Nama Lengkap", placeholder="Masukkan nama lengkap")
                prodi = st.selectbox("Program Studi", AppConfig.PRODI_LIST)
            
            with col2:
                ipk = st.number_input("IPK (0.00 - 4.00)", min_value=0.0, max_value=4.0, step=0.01, format="%.2f")
                status = st.selectbox("Status", AppConfig.STATUS_LIST)
            
            # Complexity Info
            st.markdown("""
                <div class="complexity-badge">
                    <b>⚡ Time Complexity:</b><br>
                    - Validasi input: O(n) (Regex matching)<br>
                    - Cek duplikat: O(n) (Linear Search)<br>
                    - Insert ke database: O(1)<br>
                    - Update array: O(1)
                </div>
            """, unsafe_allow_html=True)
            
            submitted = st.form_submit_button("💾 Simpan Mahasiswa", use_container_width=True)
            
            if submitted:
                if not nim or not nama:
                    st.error("NIM dan Nama harus diisi!")
                else:
                    success, msg = self.mahasiswa_manager.tambah(nim, nama, prodi, ipk, status)
                    if success:
                        st.success(msg)
                        st.balloons()
                    else:
                        st.error(msg)
    
    def _render_data(self) -> None:
        """Render halaman data mahasiswa"""
        st.markdown("### 📋 Data Mahasiswa")
        
        data = self.mahasiswa_manager.get_all()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            search = st.text_input("🔍 Cari (NIM/Nama)", placeholder="Ketik NIM atau Nama...")
        with col2:
            status_filter = st.selectbox("Filter Status", ["Semua"] + AppConfig.STATUS_LIST)
        with col3:
            sort_by = st.selectbox("Urutkan Berdasarkan", ["NIM", "Nama", "IPK", "Status"])
        
        # Pilihan algoritma pencarian
        search_algo = st.radio(
            "Pilih Algoritma Pencarian",
            ["Linear Search (O(n))", "Binary Search (O(log n))", "Sequential Search (O(n))"],
            horizontal=True
        )
        
        # Complexity Info
        st.markdown("""
            <div class="complexity-badge">
                <b>⚡ Complexity:</b><br>
                - Linear/Sequential Search: O(n)<br>
                - Binary Search: O(log n) <i>(data harus terurut)</i>
            </div>
        """, unsafe_allow_html=True)
        
        if data:
            filtered_data = data.copy()
            
            # Apply search
            if search:
                if "Linear" in search_algo:
                    results = SearchAlgorithms.sequential_search(
                        filtered_data, {'nama': search}
                    )
                    if not results:
                        results = SearchAlgorithms.sequential_search(
                            filtered_data, {'nim': search}
                        )
                    filtered_data = results
                elif "Binary" in search_algo:
                    # Binary Search memerlukan data terurut
                    sorted_data = sorted(filtered_data, key=lambda x: x['nim'])
                    result = SearchAlgorithms.binary_search(sorted_data, 'nim', search)
                    filtered_data = [result] if result else []
                else:  # Sequential
                    filtered_data = SearchAlgorithms.sequential_search(
                        filtered_data, {'nama': search}
                    )
                    if not filtered_data:
                        filtered_data = SearchAlgorithms.sequential_search(
                            data, {'nim': search}
                        )
            
            # Apply status filter
            if status_filter != "Semua":
                filtered_data = [item for item in filtered_data if item['status'] == status_filter]
            
            # Apply sorting
            key_map = {
                "NIM": "nim",
                "Nama": "nama",
                "IPK": "ipk",
                "Status": "status"
            }
            if sort_by in key_map:
                filtered_data = sorted(filtered_data, key=lambda x: x[key_map[sort_by]])
            
            if filtered_data:
                df = pd.DataFrame(filtered_data)
                st.dataframe(df, use_container_width=True)
                
                # Hapus Data
                st.subheader("🗑️ Hapus Data")
                nim_to_delete = st.selectbox(
                    "Pilih NIM yang akan dihapus",
                    [item['nim'] for item in filtered_data]
                )
                if st.button("Hapus Data", type="secondary"):
                    success, msg = self.mahasiswa_manager.hapus(nim_to_delete)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
            else:
                st.info("Tidak ada data yang cocok dengan pencarian.")
        else:
            st.info("Belum ada data. Klik 'Generate Contoh Data' di menu Dashboard.")
    
    def _render_edit(self) -> None:
        """Render halaman edit mahasiswa"""
        st.markdown("### ✏️ Edit Data Mahasiswa")
        
        data = self.mahasiswa_manager.get_all()
        
        if data:
            nim_list = [item['nim'] for item in data]
            selected_nim = st.selectbox("Pilih Mahasiswa yang akan diedit", nim_list)
            
            if selected_nim:
                selected_data = self.mahasiswa_manager.get_by_nim(selected_nim)
                
                if selected_data:
                    with st.form("edit_form"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            nim = st.text_input("NIM", value=selected_data['nim'], disabled=True)
                            nama = st.text_input("Nama", value=selected_data['nama'])
                            prodi = st.selectbox(
                                "Program Studi",
                                AppConfig.PRODI_LIST,
                                index=AppConfig.PRODI_LIST.index(selected_data['prodi'])
                                if selected_data['prodi'] in AppConfig.PRODI_LIST else 0
                            )
                        
                        with col2:
                            ipk = st.number_input(
                                "IPK",
                                min_value=0.0,
                                max_value=4.0,
                                step=0.01,
                                format="%.2f",
                                value=float(selected_data['ipk'])
                            )
                            status = st.selectbox(
                                "Status",
                                AppConfig.STATUS_LIST,
                                index=AppConfig.STATUS_LIST.index(selected_data['status'])
                            )
                        
                        st.markdown("""
                            <div class="complexity-badge">
                                <b>⚡ Time Complexity:</b><br>
                                - Update database: O(1)<br>
                                - Update array: O(n) - Linear search untuk cari data
                            </div>
                        """, unsafe_allow_html=True)
                        
                        submitted = st.form_submit_button("💾 Update Data", use_container_width=True)
                        
                        if submitted:
                            if not nama:
                                st.error("Nama harus diisi!")
                            else:
                                success, msg = self.mahasiswa_manager.update(
                                    selected_nim, nama, prodi, ipk, status
                                )
                                if success:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)
        else:
            st.info("Belum ada data. Generate contoh data terlebih dahulu.")
    
    def _render_statistik(self) -> None:
        """Render halaman statistik"""
        st.markdown("### 📈 Statistik Mahasiswa")
        
        data = self.mahasiswa_manager.get_all()
        stats = self.mahasiswa_manager.get_statistics()
        
        if data:
            df = pd.DataFrame(data)
            
            # Status Distribution
            st.subheader("📊 Status Mahasiswa")
            status_counts = pd.DataFrame(
                list(stats['status_counts'].items()),
                columns=['Status', 'Jumlah']
            )
            
            fig_status = px.pie(
                status_counts,
                values='Jumlah',
                names='Status',
                title='Distribusi Status Mahasiswa',
                color='Status',
                color_discrete_map={'Aktif': '#10b981', 'Pasif': '#ef4444', 'Cuti': '#f59e0b'},
                hole=0.3
            )
            fig_status.update_layout(
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
            )
            fig_status.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_status, use_container_width=True)
            
            col1, col2 = st.columns(2)
            
            # Program Studi Distribution
            with col1:
                st.subheader("📚 Program Studi")
                prodi_counts = pd.DataFrame(
                    list(stats['prodi_counts'].items()),
                    columns=['Program Studi', 'Jumlah']
                ).head(5)
                
                fig_prodi = px.pie(
                    prodi_counts,
                    values='Jumlah',
                    names='Program Studi',
                    title='5 Program Studi Teratas',
                    hole=0.3
                )
                fig_prodi.update_layout(
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
                )
                st.plotly_chart(fig_prodi, use_container_width=True)
            
            # IPK Distribution
            with col2:
                st.subheader("⭐ Distribusi IPK")
                fig_ipk = px.histogram(
                    df,
                    x='ipk',
                    nbins=10,
                    title='Histogram IPK Mahasiswa',
                    color_discrete_sequence=['#3b82f6']
                )
                fig_ipk.update_layout(bargap=0.1)
                st.plotly_chart(fig_ipk, use_container_width=True)
            
            # IPK Statistics
            st.subheader("📊 Statistik IPK")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Rata-rata IPK", f"{stats['avg_ipk']:.2f}")
            with col2:
                st.metric("IPK Tertinggi", f"{stats['max_ipk']:.2f}")
            with col3:
                st.metric("IPK Terendah", f"{stats['min_ipk']:.2f}")
            with col4:
                st.metric("Total Mahasiswa", stats['total'])
            
            # Sorting Demo
            st.subheader("🔀 Demo Algoritma Sorting")
            sort_algorithm = st.selectbox(
                "Pilih Algoritma Sorting",
                ["Bubble Sort (O(n²))", "Insertion Sort (O(n²))", 
                 "Selection Sort (O(n²))", "Merge Sort (O(n log n))", 
                 "Shell Sort (O(n log n))"]
            )
            
            sort_key = st.selectbox("Sort Berdasarkan", ["NIM", "Nama", "IPK", "Status"])
            sort_reverse = st.checkbox("Urutkan Descending")
            
            if st.button("🔄 Jalankan Sorting", use_container_width=True):
                key_map = {
                    "NIM": "nim",
                    "Nama": "nama",
                    "IPK": "ipk",
                    "Status": "status"
                }
                
                algorithm_map = {
                    "Bubble Sort (O(n²))": "bubble",
                    "Insertion Sort (O(n²))": "insertion",
                    "Selection Sort (O(n²))": "selection",
                    "Merge Sort (O(n log n))": "merge",
                    "Shell Sort (O(n log n))": "shell"
                }
                
                sorted_data = self.mahasiswa_manager.sort(
                    key=key_map[sort_key],
                    algorithm=algorithm_map[sort_algorithm],
                    reverse=sort_reverse
                )
                
                st.dataframe(pd.DataFrame(sorted_data), use_container_width=True)
                st.success(f"✅ Data berhasil diurutkan dengan {sort_algorithm}")
            
            # Complexity Summary
            st.markdown("""
                <div class="complexity-badge">
                    <b>📊 Time Complexity Summary:</b><br>
                    - Linear/Sequential Search: O(n)<br>
                    - Binary Search: O(log n)<br>
                    - Bubble/Insertion/Selection Sort: O(n²)<br>
                    - Merge/Shell Sort: O(n log n)<br>
                    - Statistik (mean, min, max): O(n)<br>
                    - CRUD Operations: O(1) - O(n)
                </div>
            """, unsafe_allow_html=True)
            
            # Full data
            with st.expander("📋 Lihat Data Lengkap Mahasiswa"):
                st.dataframe(df, use_container_width=True)
        else:
            st.info("Belum ada data. Klik 'Generate Contoh Data' di menu Dashboard.")
    
    def run(self) -> None:
        """Main method untuk menjalankan aplikasi"""
        self._render_sidebar()
        
        # Check login
        if not st.session_state.logged_in:
            self._render_login()
            return
        
        # Menu
        menu = st.sidebar.radio(
            "📋 Menu Utama",
            ["🏠 Dashboard", "➕ Tambah Mahasiswa", "📋 Data Mahasiswa", 
             "✏️ Edit Data", "📈 Statistik"]
        )
        
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
        
        # Render menu
        if menu == "🏠 Dashboard":
            self._render_dashboard()
        elif menu == "➕ Tambah Mahasiswa":
            self._render_tambah()
        elif menu == "📋 Data Mahasiswa":
            self._render_data()
        elif menu == "✏️ Edit Data":
            self._render_edit()
        elif menu == "📈 Statistik":
            self._render_statistik()

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main entry point aplikasi"""
    st.set_page_config(
        page_title=AppConfig.PAGE_TITLE,
        page_icon=AppConfig.PAGE_ICON,
        layout=AppConfig.LAYOUT
    )
    
    app = StreamlitUI()
    app.run()

if __name__ == "__main__":
    main()
