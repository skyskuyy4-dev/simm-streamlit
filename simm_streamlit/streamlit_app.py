import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ========== KONFIGURASI HALAMAN ==========
st.set_page_config(
    page_title="SIMM - Sistem Informasi Mahasiswa",
    page_icon="🎓",
    layout="wide"
)

# ========== DARK MODE CSS ==========
def apply_theme():
    if st.session_state.theme == "dark":
        st.markdown("""
            <style>
                .stApp { background-color: #0f111a; }
                .stApp, .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp label { color: white !important; }
                .stButton > button { background: linear-gradient(135deg, #3b82f6, #2563eb); color: white; border-radius: 10px; font-weight: bold; }
                .stButton > button:hover { background: linear-gradient(135deg, #2563eb, #1d4ed8); }
                .stTextInput > div > div > input { 
                    background-color: #1e1e2e; 
                    color: white; 
                    border: 1px solid #3b82f6;
                    border-radius: 10px;
                    padding: 12px;
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
                .card-stat { background: linear-gradient(135deg, #1e1e2e, #16162a); border-radius: 15px; padding: 20px; text-align: center; }
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
            </style>
        """, unsafe_allow_html=True)

# ========== DATABASE ==========
def get_db():
    conn = sqlite3.connect('database.db')
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mahasiswa (
            nim TEXT PRIMARY KEY,
            nama TEXT NOT NULL,
            prodi TEXT NOT NULL,
            ipk REAL NOT NULL,
            status TEXT NOT NULL
        )
    ''')
    
    cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES ('fitra', '12345')")
    conn.commit()
    conn.close()

def register_user(username, password):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True, "Registrasi berhasil! Silakan login."
    except sqlite3.IntegrityError:
        return False, "Username sudah terdaftar!"
    finally:
        conn.close()

def get_all_mahasiswa():
    conn = get_db()
    df = pd.read_sql_query("SELECT * FROM mahasiswa", conn)
    conn.close()
    return df

def tambah_mahasiswa(nim, nama, prodi, ipk, status):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO mahasiswa (nim, nama, prodi, ipk, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (nim, nama, prodi, float(ipk), status))
        conn.commit()
        return True, "Data berhasil ditambahkan!"
    except sqlite3.IntegrityError:
        return False, "NIM sudah terdaftar!"
    finally:
        conn.close()

def hapus_mahasiswa(nim):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM mahasiswa WHERE nim = ?", (nim,))
    conn.commit()
    conn.close()
    return True, "Data berhasil dihapus!"

def update_mahasiswa(nim, nama, prodi, ipk, status):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE mahasiswa SET nama=?, prodi=?, ipk=?, status=? WHERE nim=?
    ''', (nama, prodi, float(ipk), status, nim))
    conn.commit()
    conn.close()
    return True, "Data berhasil diupdate!"

def generate_contoh():
    sample_data = [
        ("2010114001", "Fajar Dian Taufani", "Teknik Informatika", 3.85, "Aktif"),
        ("2010114005", "Siti Aminah", "Sistem Informasi", 3.40, "Aktif"),
        ("2010114002", "Andi Wijaya", "Teknik Informatika", 2.90, "Cuti"),
        ("2010114012", "Riska Amelia", "Manajemen", 4.00, "Aktif"),
        ("2010114009", "Budi Santoso", "Akuntansi", 3.15, "Pasif")
    ]
    conn = get_db()
    cursor = conn.cursor()
    for data in sample_data:
        cursor.execute("INSERT OR IGNORE INTO mahasiswa VALUES (?, ?, ?, ?, ?)", data)
    conn.commit()
    conn.close()
    return True, "5 data contoh berhasil ditambahkan!"

# ========== INIT DATABASE ==========
init_db()

# ========== SESSION STATE ==========
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.theme = "dark"

# ========== APPLY THEME ==========
apply_theme()

# ========== HEADER ==========
st.markdown("""
    <div class="main-header">
        <h1>🎓 SIMM - Sistem Informasi Manajemen Mahasiswa</h1>
        <p>Universitas Pamulang</p>
    </div>
""", unsafe_allow_html=True)

# ========== SIDEBAR ==========
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.username if st.session_state.logged_in else 'Guest'}")
    st.markdown("---")
    
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

# ========== HALAMAN LOGIN ==========
if not st.session_state.logged_in:
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
                    conn = get_db()
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
                    user = cursor.fetchone()
                    conn.close()
                    
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.rerun()
                    else:
                        st.error("❌ Username atau password salah!")
    
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
                    if not new_username or not new_password:
                        st.error("⚠️ Username dan password harus diisi!")
                    elif new_password != confirm_password:
                        st.error("❌ Password tidak cocok!")
                    elif len(new_password) < 3:
                        st.error("⚠️ Password minimal 3 karakter!")
                    else:
                        success, msg = register_user(new_username, new_password)
                        if success:
                            st.success("✅ " + msg)
                        else:
                            st.error("❌ " + msg)
    
        st.stop()

# ========== MENU UTAMA ==========
menu = st.sidebar.radio(
    "📋 Menu Utama",
    ["🏠 Dashboard", "➕ Tambah Mahasiswa", "📋 Data Mahasiswa", "📈 Statistik", "✏️ Edit Data"]
)

if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

# ========== HALAMAN DASHBOARD ==========
if menu == "🏠 Dashboard":
    st.markdown("### 🏠 Dashboard")
    
    df = get_all_mahasiswa()
    
    col1, col2, col3, col4 = st.columns(4)
    
    total = len(df)
    aktif = len(df[df['status'] == 'Aktif']) if not df.empty else 0
    avg_ipk = df['ipk'].mean() if not df.empty else 0
    max_ipk = df['ipk'].max() if not df.empty else 0
    
    with col1:
        st.metric("📊 Total Mahasiswa", total, delta=None)
    with col2:
        st.metric("✅ Mahasiswa Aktif", aktif, delta=None)
    with col3:
        st.metric("⭐ Rata-rata IPK", f"{avg_ipk:.2f}", delta=None)
    with col4:
        st.metric("🏆 IPK Tertinggi", f"{max_ipk:.2f}", delta=None)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📄 Generate Contoh Data", use_container_width=True):
            success, msg = generate_contoh()
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
    
    st.subheader("📋 Data Mahasiswa Terbaru")
    if not df.empty:
        st.dataframe(df.head(10), use_container_width=True)
    else:
        st.info("Belum ada data. Klik 'Generate Contoh Data' untuk mengisi.")

# ========== HALAMAN TAMBAH ==========
elif menu == "➕ Tambah Mahasiswa":
    st.markdown("### ➕ Tambah Mahasiswa Baru")
    
    with st.form("tambah_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            nim = st.text_input("NIM (10-12 digit)", placeholder="Contoh: 2010114001")
            nama = st.text_input("Nama Lengkap", placeholder="Contoh: Fajar Dian Taufani")
            prodi = st.selectbox("Program Studi", [
                "Teknik Informatika", "Sistem Informasi", "Manajemen Informatika",
                "Teknik Komputer", "Akuntansi", "Manajemen", "Hukum", "Psikologi"
            ])
        
        with col2:
            ipk = st.number_input("IPK (0.00 - 4.00)", min_value=0.0, max_value=4.0, step=0.01, format="%.2f")
            status = st.selectbox("Status", ["Aktif", "Pasif", "Cuti"])
        
        submitted = st.form_submit_button("💾 Simpan Mahasiswa", use_container_width=True)
        
        if submitted:
            if not nim or not nama:
                st.error("NIM dan Nama harus diisi!")
            elif len(nim) < 10 or len(nim) > 12:
                st.error("NIM harus 10-12 digit!")
            else:
                success, msg = tambah_mahasiswa(nim, nama, prodi, ipk, status)
                if success:
                    st.success(msg)
                    st.balloons()
                else:
                    st.error(msg)

# ========== HALAMAN DATA ==========
elif menu == "📋 Data Mahasiswa":
    st.markdown("### 📋 Data Mahasiswa")
    
    df = get_all_mahasiswa()
    
    col1, col2 = st.columns(2)
    with col1:
        search = st.text_input("🔍 Cari (NIM/Nama)", placeholder="Ketik NIM atau Nama...")
    with col2:
        status_filter = st.selectbox("Filter Status", ["Semua", "Aktif", "Pasif", "Cuti"])
    
    if not df.empty:
        filtered_df = df.copy()
        if search:
            filtered_df = filtered_df[
                filtered_df['nim'].str.contains(search, case=False) | 
                filtered_df['nama'].str.contains(search, case=False)
            ]
        if status_filter != "Semua":
            filtered_df = filtered_df[filtered_df['status'] == status_filter]
        
        st.dataframe(filtered_df, use_container_width=True)
        
        st.subheader("🗑️ Hapus Data")
        nim_to_delete = st.selectbox("Pilih NIM yang akan dihapus", filtered_df['nim'].tolist() if not filtered_df.empty else [])
        if st.button("Hapus Data", type="secondary"):
            success, msg = hapus_mahasiswa(nim_to_delete)
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
    else:
        st.info("Belum ada data. Klik 'Generate Contoh Data' di menu Dashboard.")

# ========== HALAMAN EDIT ==========
elif menu == "✏️ Edit Data":
    st.markdown("### ✏️ Edit Data Mahasiswa")
    
    df = get_all_mahasiswa()
    
    if not df.empty:
        nim_list = df['nim'].tolist()
        selected_nim = st.selectbox("Pilih Mahasiswa yang akan diedit", nim_list)
        
        if selected_nim:
            selected_data = df[df['nim'] == selected_nim].iloc[0]
            
            with st.form("edit_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    nim = st.text_input("NIM", value=selected_data['nim'], disabled=True)
                    nama = st.text_input("Nama", value=selected_data['nama'])
                    prodi = st.selectbox("Program Studi", [
                        "Teknik Informatika", "Sistem Informasi", "Manajemen Informatika",
                        "Teknik Komputer", "Akuntansi", "Manajemen", "Hukum", "Psikologi"
                    ], index=["Teknik Informatika", "Sistem Informasi", "Manajemen Informatika",
                              "Teknik Komputer", "Akuntansi", "Manajemen", "Hukum", "Psikologi"].index(selected_data['prodi']) if selected_data['prodi'] in ["Teknik Informatika", "Sistem Informasi", "Manajemen Informatika",
                              "Teknik Komputer", "Akuntansi", "Manajemen", "Hukum", "Psikologi"] else 0)
                
                with col2:
                    ipk = st.number_input("IPK", min_value=0.0, max_value=4.0, step=0.01, format="%.2f", value=float(selected_data['ipk']))
                    status = st.selectbox("Status", ["Aktif", "Pasif", "Cuti"], index=["Aktif", "Pasif", "Cuti"].index(selected_data['status']))
                
                submitted = st.form_submit_button("💾 Update Data", use_container_width=True)
                
                if submitted:
                    if not nama:
                        st.error("Nama harus diisi!")
                    else:
                        success, msg = update_mahasiswa(selected_nim, nama, prodi, ipk, status)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
    else:
        st.info("Belum ada data. Generate contoh data terlebih dahulu.")

# ========== HALAMAN STATISTIK (DENGAN DIAGRAM LINGKARAN) ==========
elif menu == "📈 Statistik":
    st.markdown("### 📈 Statistik Mahasiswa")
    
    df = get_all_mahasiswa()
    
    if not df.empty:
        # Diagram Lingkaran Status
        st.subheader("📊 Status Mahasiswa")
        status_counts = df['status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Jumlah']
        
        fig_status = px.pie(status_counts, values='Jumlah', names='Status', 
                            title='Distribusi Status Mahasiswa',
                            color='Status',
                            color_discrete_map={'Aktif': '#10b981', 'Pasif': '#ef4444', 'Cuti': '#f59e0b'},
                            hole=0.3)
        fig_status.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
        fig_status.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_status, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        # Diagram Lingkaran Program Studi (Top 5)
        with col1:
            st.subheader("📚 Program Studi")
            prodi_counts = df['prodi'].value_counts().head(5).reset_index()
            prodi_counts.columns = ['Program Studi', 'Jumlah']
            
            fig_prodi = px.pie(prodi_counts, values='Jumlah', names='Program Studi', 
                               title='5 Program Studi Teratas',
                               hole=0.3)
            fig_prodi.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
            st.plotly_chart(fig_prodi, use_container_width=True)
        
        # Bar Chart IPK
        with col2:
            st.subheader("⭐ Distribusi IPK")
            fig_ipk = px.histogram(df, x='ipk', nbins=10, title='Histogram IPK Mahasiswa',
                                   color_discrete_sequence=['#3b82f6'])
            fig_ipk.update_layout(bargap=0.1)
            st.plotly_chart(fig_ipk, use_container_width=True)
        
        # Statistik IPK
        st.subheader("📊 Statistik IPK")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Rata-rata IPK", f"{df['ipk'].mean():.2f}")
        with col2:
            st.metric("IPK Tertinggi", f"{df['ipk'].max():.2f}")
        with col3:
            st.metric("IPK Terendah", f"{df['ipk'].min():.2f}")
        with col4:
            st.metric("Total Mahasiswa", len(df))
        
        # Bar Chart Program Studi
        st.subheader("📊 Jumlah Mahasiswa per Program Studi")
        prodi_counts_all = df['prodi'].value_counts().reset_index()
        prodi_counts_all.columns = ['Program Studi', 'Jumlah']
        
        fig_prodi_bar = px.bar(prodi_counts_all, x='Program Studi', y='Jumlah', 
                                title='Distribusi Program Studi',
                                color='Jumlah', color_continuous_scale='Blues')
        fig_prodi_bar.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_prodi_bar, use_container_width=True)
        
        # Tabel lengkap
        with st.expander("📋 Lihat Data Lengkap Mahasiswa"):
            st.dataframe(df, use_container_width=True)
    else:
        st.info("Belum ada data. Klik 'Generate Contoh Data' di menu Dashboard.")
SQLite format 3   @                                                                     .Š
ø 2 LÍ2                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              d ƒtablemahasiswamahasiswaCREATE TABLE mahasiswa (
            nim TEXT PRIMARY KEY,
            nama TEXT NOT NULL,
            prodi TEXT NOT NULL,
            ipk REAL NOT NULL,
            status TEXT NOT NULL
        )1E indexsqlite_autoindex_mahasiswa_1mahasiswa ]tableusersusersCREATE TABLE users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        ))= indexsqlite_autoindex_users_1users       
   ñ ñ                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
fitra12345
   ÷ ÷                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             	fitra
   ë Á‡Lë                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         2!% 2010114009Budi SantosoAkuntansi@	333333Pasif+!%2010114012Riska AmeliaManajemenAktif9!#1 2010114002Andi WijayaTeknik Informatika@ 333333Cuti8!#- 2010114005Siti AminahSistem Informasi@333333Aktif=!)1 2010114001Muhammad FitraTeknik Informatika@ÌÌÌÌÌÍAktif
   ¶ òÔã¶Å                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    !2010114009!2010114012!2010114002!2010114005
!	2010114001
