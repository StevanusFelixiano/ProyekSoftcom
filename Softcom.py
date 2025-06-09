import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Major Finder: Rekomendasi Major & Minor Mahasiswa", layout="centered")

# Styling
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    .stSlider > div { padding: 0.2rem 0.5rem; }
    hr { border-top: 1px solid #bbb; }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/React-icon.svg/512px-React-icon.svg.png", width=80)
    st.markdown("## Major Finder")
    st.markdown("Sistem Rekomendasi Berdasarkan\n")
    st.markdown("- Minat\n- Nilai Akademik\n- Tujuan Karier")
    st.caption("Metode: Fuzzy Logic + AHP")

# Judul
st.title("🎓 Major Finder: Rekomendasi Major & Minor Mahasiswa")
st.markdown("🔎 Metode: **Fuzzy Logic + AHP** _(berdasarkan survei preferensi)_")
st.info("Isi data berikut untuk mendapatkan rekomendasi peminatan akademik terbaik untuk Anda.")

# Input: Minat
st.subheader("💡 Input Penilaian Mahasiswa")
minat = {}
col1, col2 = st.columns(2)
minat['Artificial Intelligence'] = col1.slider("Minat terhadap Artificial Intelligence", 0, 10, 5)
minat['Sistem Informasi'] = col2.slider("Minat terhadap Sistem Informasi", 0, 10, 5)
_, col3 = st.columns([1, 1])
minat['Jaringan Komputer'] = col3.slider("Minat terhadap Jaringan Komputer", 0, 10, 5)

# Input: Nilai
st.markdown("### 📚 Nilai Akademik")
nilai = {}
nilai['AI'] = st.number_input("Nilai Matkul Artificial Intelligence", 0, 100, 80)
nilai['SI'] = st.number_input("Nilai Matkul Sistem Informasi", 0, 100, 80)
nilai['Jaringan'] = st.number_input("Nilai Matkul Jaringan Komputer", 0, 100, 80)

# Input: Karier
st.markdown("### 🎯 Kesesuaian Karier")
karir = {}
col4, col5 = st.columns(2)
karir['Artificial Intelligence'] = col4.slider("Kesesuaian AI dengan karier", 0, 10, 5)
karir['Sistem Informasi'] = col5.slider("Kesesuaian SI dengan karier", 0, 10, 5)
_, col6 = st.columns([1, 1])
karir['Jaringan Komputer'] = col6.slider("Kesesuaian Jaringan dengan karier", 0, 10, 5)

# Fungsi bantu
def nilai_to_score(n):
    return 1.0 if n >= 80 else 0.8 if n >= 69 else 0.6 if n >= 57 else 0.4 if n >= 45 else 0.2
def fuzzy_normalize(x): return x / 10.0

# AHP weights
ahp_matrix = np.array([
    [1,   6,   5],
    [1/6, 1,   4],
    [1/5, 1/4, 1]
])
normalized = ahp_matrix / ahp_matrix.sum(axis=0)
weights_ahp = normalized.mean(axis=1)
weights = {'Minat': weights_ahp[0], 'Nilai': weights_ahp[1], 'Karier': weights_ahp[2]}

# Rekomendasi
if st.button("🚀 Rekomendasikan Major & Minor"):
    bidang_kode_map = {
        'Artificial Intelligence': 'AI',
        'Sistem Informasi': 'SI',
        'Jaringan Komputer': 'Jaringan'
    }

    skor_bidang = {}
    for bidang in bidang_kode_map:
        kode = bidang_kode_map[bidang]
        m = fuzzy_normalize(minat[bidang])
        n = nilai_to_score(nilai[kode])
        k = fuzzy_normalize(karir[bidang])
        total = weights['Minat']*m + weights['Nilai']*n + weights['Karier']*k
        skor_bidang[bidang] = total

    # Tie-break logic: skor → nilai → karier → minat → alfabet
    def skor_with_tiebreak(bidang):
        kode = bidang_kode_map[bidang]
        return (
            round(skor_bidang[bidang], 4),
            nilai[kode],
            fuzzy_normalize(karir[bidang]),
            minat[bidang],
            bidang
        )

    sorted_skor = sorted(skor_bidang.items(), key=lambda x: skor_with_tiebreak(x[0]), reverse=True)
    major = sorted_skor[0][0]
    minor = sorted_skor[1][0]
    major_kode = bidang_kode_map[major]
    minor_kode = bidang_kode_map[minor]

    # Deteksi jika semuanya sama
    all_same = len(set([round(skor_bidang[b], 4) for b in skor_bidang])) == 1 \
        and len(set([nilai[bidang_kode_map[b]] for b in skor_bidang])) == 1 \
        and len(set([karir[b] for b in skor_bidang])) == 1 \
        and len(set([minat[b] for b in skor_bidang])) == 1

    if all_same:
        st.caption("⚠️ Semua skor, nilai, karier, dan minat sama. Sistem memilih Major & Minor berdasarkan urutan dictionary.")

    # Mata kuliah minor berdasarkan kombinasi Major–Minor
    matkul_minor = {
        'AI': ['Grafika Komputer', 'Robotika'],
        'SI': ['Decision Support System', 'Kriptografi'],
        'Jaringan': ['Sistem Keamanan Jaringan', 'Sistem Terdistribusi']
    }

    if major_kode == "AI" and minor_kode == "SI":
        chosen_minor_course = "Decision Support System"
    elif major_kode == "Jaringan" and minor_kode == "SI":
        chosen_minor_course = "Kriptografi"
    elif major_kode == "AI" and minor_kode == "Jaringan":
        chosen_minor_course = "Sistem Keamanan Jaringan"
    elif major_kode == "Jaringan" and minor_kode == "AI":
        chosen_minor_course = "Robotika"
    elif major_kode == "SI" and minor_kode == "AI":
        chosen_minor_course = "Grafika Komputer"
    elif major_kode == "SI" and minor_kode == "Jaringan":
        chosen_minor_course = "Sistem Terdistribusi"
    else:
        chosen_minor_course = matkul_minor[minor_kode][0]

    # Output
    st.success("🎉 Rekomendasi Anda")
    st.markdown(f"### 🎓 Major: **{major}**")
    st.markdown(f"### 📘 Minor: **{minor}**")
    st.markdown(f"#### 📚 Mata kuliah minor yang direkomendasikan: **{chosen_minor_course}**")

    st.subheader("📊 Detail Skor Semua Peminatan")
    df_skor = pd.DataFrame(sorted_skor, columns=['Bidang', 'Skor'])
    st.table(df_skor)

    fig = px.bar(df_skor, x='Bidang', y='Skor', title="Skor Peminatan", color='Bidang', text_auto=True)
    st.plotly_chart(fig)

    st.subheader("📥 Ekspor Hasil")
    hasil_csv = df_skor.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", data=hasil_csv, file_name="hasil_rekomendasi.csv", mime="text/csv")

# Footer
st.markdown("""
<hr style="margin-top:50px">
<center><small>© 2025 Rekomendasi Major & Minor Mahasiswa | Dibangun dengan ❤️ oleh Jonatan, Stevanus dan Louis</small></center>
""", unsafe_allow_html=True)
