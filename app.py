import streamlit as st
import pandas as pd

DATA_URL = "https://raw.githubusercontent.com/<username>/<repo>/main/GSAF5.xls"

@st.cache_data
def load_and_clean_data(url):
    try:
        # Untuk file .xls gunakan engine 'xlrd'
        if url.endswith('.xls'):
            df = pd.read_excel(url, engine='xlrd')
        else:
            df = pd.read_excel(url, engine='openpyxl')
    except Exception as e:
        st.error(f"Gagal membaca dataset: {e}")
        st.stop()
    return df

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


