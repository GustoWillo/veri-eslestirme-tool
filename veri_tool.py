# Streamlit tabanlı demo: Genel Amaçlı Veri Temizleme Aracı (Şık Minimalist Stil)

import streamlit as st
import pandas as pd
import requests
import re
from PIL import Image
import io
from datetime import datetime

st.set_page_config(page_title="Veri Temizleyici", page_icon="🧹", layout="centered")
st.markdown("""
    <style>
    .main {background-color: #f9f9f9;}
    div[data-testid="stSidebar"] {background-color: #ffffff;}
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        padding: 0.5em 1em;
        border: none;
    }
    .stDownloadButton>button {
        background-color: #3B82F6;
        color: white;
        border-radius: 8px;
        padding: 0.5em 1em;
        border: none;
    }
    </style>
""", unsafe_allow_html=True)

# OCR: Görselden metin çıkar

def ocr_space_image(file, language='tur'):
    api_key = 'helloworld'
    url = 'https://api.ocr.space/parse/image'
    payload = {'isOverlayRequired': False, 'apikey': api_key, 'language': language}
    files = {'file': file.getvalue()}
    response = requests.post(url, files=files, data=payload)
    result = response.json()
    if result['IsErroredOnProcessing']:
        return "OCR Hatası"
    return result['ParsedResults'][0]['ParsedText']

def extract_from_image_dynamic(file):
    text = ocr_space_image(file)
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    data = {f"alan_{i+1}": line for i, line in enumerate(lines)}
    data["tam_metin"] = text.replace("\n", " ")[:500]
    return pd.DataFrame([data])

def clean_generic_data(df, etiket_map):
    df = df.copy()
    issues = []
    for col in df.columns:
        null_count = df[col].isnull().sum()
        empty_count = (df[col] == '').sum()
        numeric_check = pd.to_numeric(df[col], errors='coerce')
        zero_or_negative = ((numeric_check <= 0) & numeric_check.notnull()).sum()
        issue = []
        if null_count > 0:
            issue.append(f"🔴 {null_count} boş hücre")
        if empty_count > 0:
            issue.append(f"🔴 {empty_count} boş string")
        if zero_or_negative > 0:
            issue.append(f"🟠 {zero_or_negative} sıfır/negatif değer")
        if etiket_map.get(col) == "E-posta":
            invalid = df[col].apply(lambda x: not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", str(x)) if pd.notnull(x) else False).sum()
            if invalid > 0:
                issue.append(f"⚠️ {invalid} geçersiz e-posta")
        if etiket_map.get(col) == "Telefon":
            invalid = df[col].apply(lambda x: not re.match(r"^(\+\d{1,3}[- ]?)?\d{10,15}$", str(x)) if pd.notnull(x) else False).sum()
            if invalid > 0:
                issue.append(f"⚠️ {invalid} geçersiz telefon")
        if etiket_map.get(col) == "Kimlik":
            invalid = df[col].apply(lambda x: not (str(x).isdigit() and len(str(x)) == 11 and str(x)[0] != "0") if pd.notnull(x) else False).sum()
            if invalid > 0:
                issue.append(f"⚠️ {invalid} geçersiz TCKN")
        if etiket_map.get(col) == "Tarih":
            def is_valid_date(val):
                for fmt in ("%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y"):
                    try:
                        datetime.strptime(str(val), fmt)
                        return True
                    except:
                        continue
                return False
            invalid = df[col].apply(lambda x: not is_valid_date(x) if pd.notnull(x) else False).sum()
            if invalid > 0:
                issue.append(f"⚠️ {invalid} geçersiz tarih formatı")
        issues.append("; ".join(issue) if issue else "✅ Temiz")
    return df, pd.DataFrame({'Kolon': df.columns, 'Durum': issues})

def manual_column_tagging(df):
    st.subheader("🔧 Kolonları Etiketleyin")
    tipler = ["Belirtilmedi", "Tarih", "Tutar", "Açıklama", "Kimlik", "Kategori", "E-posta", "Telefon"]
    return {col: st.selectbox(f"'{col}' tipi:", tipler, key=col) for col in df.columns}

st.title("🧹 Veri Temizleyici")
st.caption("Verinizi yükleyin, sistem otomatik analiz edip olası sorunları göstersin.")

uploaded_file = st.file_uploader("📎 Excel veya görsel dosya yükleyin", type=["xlsx", "jpg", "jpeg", "png"])

if uploaded_file:
    if uploaded_file.type.startswith("image"):
        df = extract_from_image_dynamic(uploaded_file)
        st.write("📸 Görselden çıkarılan veri:")
        st.dataframe(df)
    else:
        df = pd.read_excel(uploaded_file)
        st.write("📄 Excel'den gelen veri:")
        st.dataframe(df.head())
        etiketler = manual_column_tagging(df)
        cleaned_df, issues_df = clean_generic_data(df, etiketler)
        st.success("Analiz tamamlandı. Aşağıda kolon bazlı durum yer alır:")
        st.dataframe(issues_df)
        csv = cleaned_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Temizlenmiş Veriyi İndir", csv, "temiz_veri.csv", "text/csv")
