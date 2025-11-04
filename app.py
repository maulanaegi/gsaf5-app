import streamlit as st
import pandas as pd
import plotly.express as px

# === URL dataset di GitHub ===
# Contoh: raw URL GitHub
DATA_URL = "https://raw.githubusercontent.com/<username>/<repo>/main/GSAF5.xlsx"
# Ganti <username>, <repo>, dan nama file sesuai repo kamu

# === Fungsi untuk memuat dan membersihkan data ===
@st.cache_data
def load_and_clean_data(url):
    try:
        # Baca file Excel langsung dari GitHub
        df = pd.read_excel(url, engine='openpyxl')
    except Exception as e:
        st.error(f"Gagal membaca dataset: {e}")
        st.stop()

    # Bersihkan nama kolom
    df.columns = df.columns.str.strip().str.replace(' ', '_').str.replace(':', '_')

    # Pilih kolom yang tersedia
    expected_cols = [
        'Case_Number', 'Date', 'Year', 'Type', 'Country', 'State', 'Location',
        'Activity', 'Name', 'Sex', 'Age', 'Injury', 'Time', 'Species', 'Source'
    ]
    available_cols = [c for c in expected_cols if c in df.columns]
    df = df[available_cols]

    # Konversi tipe data
    if 'Year' in df.columns:
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
    if 'Age' in df.columns:
        df['Age'] = pd.to_numeric(df['Age'], errors='coerce')
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    # Bersihkan teks
    for col in ['Country', 'Activity', 'Species']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.lower()

    # Hapus duplikat dan baris kosong
    if 'Case_Number' in df.columns:
        df = df.drop_duplicates(subset=['Case_Number'])
    if {'Year', 'Country'}.issubset(df.columns):
        df = df.dropna(subset=['Year', 'Country'], how='any')

    # Filter tahun valid
    if 'Year' in df.columns:
        df = df[df['Year'] >= 1900]

    return df

# === Judul aplikasi ===
st.set_page_config(page_title="Visualisasi Serangan Hiu Global", layout="wide")
st.title("🦈 Visualisasi Interaktif Dataset Serangan Hiu Global (GSAF)")
st.write("Dataset diambil langsung dari GitHub. Filter dan visualisasi tersedia secara interaktif.")

# === Muat data dari GitHub ===
df = load_and_clean_data(DATA_URL)

# === Sidebar Filter ===
st.sidebar.header("🔍 Filter Data")

selected_countries = st.sidebar.multiselect(
    "Pilih Negara", options=sorted(df['Country'].dropna().unique()), default=[]
)

if 'Year' in df.columns:
    min_year, max_year = int(df['Year'].min()), int(df['Year'].max())
    selected_years = st.sidebar.slider("Rentang Tahun", min_year, max_year, (2000, max_year))
else:
    selected_years = (2000, 2020)

selected_activities = st.sidebar.multiselect(
    "Pilih Aktivitas", options=sorted(df['Activity'].dropna().unique()), default=[]
)

# === Terapkan Filter ===
filtered_df = df.copy()
if selected_countries:
    filtered_df = filtered_df[filtered_df['Country'].isin(selected_countries)]
if 'Year' in filtered_df.columns:
    filtered_df = filtered_df[
        (filtered_df['Year'] >= selected_years[0]) & (filtered_df['Year'] <= selected_years[1])
    ]
if selected_activities:
    filtered_df = filtered_df[filtered_df['Activity'].isin(selected_activities)]

# === Visualisasi ===
if not filtered_df.empty:
    # 1️⃣ Tren Serangan per Tahun
    if 'Year' in filtered_df.columns:
        st.subheader("📈 Tren Serangan Hiu per Tahun")
        yearly_counts = filtered_df.groupby('Year').size().reset_index(name='Jumlah')
        line_fig = px.line(yearly_counts, x='Year', y='Jumlah', title='Tren Tahunan Serangan Hiu')
        st.plotly_chart(line_fig, use_container_width=True)

    # 2️⃣ Peta Interaktif
    if 'Country' in filtered_df.columns:
        st.subheader("🌍 Distribusi Geografis Serangan Hiu")
        country_counts = filtered_df.groupby('Country').size().reset_index(name='Jumlah')
        map_fig = px.choropleth(
            country_counts,
            locations='Country',
            locationmode='country names',
            color='Jumlah',
            color_continuous_scale='Reds',
            title='Serangan Hiu per Negara'
        )
        st.plotly_chart(map_fig, use_container_width=True)

    # 3️⃣ Aktivitas Saat Serangan
    if 'Activity' in filtered_df.columns:
        st.subheader("🏄 Aktivitas Umum Saat Serangan")
        activity_counts = filtered_df['Activity'].value_counts().reset_index(name='Jumlah').head(10)
        bar_fig = px.bar(activity_counts, x='Activity', y='Jumlah', title='Top 10 Aktivitas Saat Serangan')
        st.plotly_chart(bar_fig, use_container_width=True)

    # 4️⃣ Distribusi Usia
    if 'Age' in filtered_df.columns:
        st.subheader("👥 Distribusi Usia Korban")
        hist_fig = px.histogram(filtered_df, x='Age', nbins=20, title='Histogram Usia Korban')
        st.plotly_chart(hist_fig, use_container_width=True)

    # 5️⃣ Sampel Data
    st.subheader("📋 Sampel Data")
    st.dataframe(filtered_df.head(10))
else:
    st.warning("Tidak ada data yang cocok dengan filter yang dipilih.")

# === Footer ===
st.markdown("---")
st.caption("Dibuat dengan ❤️ menggunakan Streamlit & Plotly | © 2025")
