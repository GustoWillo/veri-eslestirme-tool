# Streamlit tabanlı demo: Veri Temizleme Aracı

import streamlit as st
import pandas as pd
import datetime
import pytesseract
from PIL import Image
import io
import re

# Fonksiyon: Görselden veri çıkar ve tüm metni serbest sütunlara böler
def extract_from_image_dynamic(file):
    image = Image.open(file)
    text = pytesseract.image_to_string(image, lang='tur')
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    data = {f"alan_{i+1}": line for i, line in enumerate(lines)}
    data["metin"] = text.replace("\n", " ")[:500]
    return pd.DataFrame([data])

# Arayüz
st.title("Veri Temizleme Demo Tool")
st.write("Excel ya da fiş fotoğrafı yükleyin. Sistem içeriği otomatik analiz edip yapılandırılmış hale getirir.")

uploaded_file = st.file_uploader("Excel ya da görsel dosya yükleyin", type=["xlsx", "jpg", "jpeg", "png"])

if uploaded_file:
    if uploaded_file.type in ["image/jpeg", "image/png", "image/jpg"]:
        df = extract_from_image_dynamic(uploaded_file)
        st.write("Görselden çıkarılan satır bazlı veri:")
        st.dataframe(df)
    else:
        df = pd.read_excel(uploaded_file)
        st.write("Yüklenen orijinal Excel verisi:")
        st.dataframe(df.head())

        st.success("Veri yüklendi. Kolonlar korunarak gösteriliyor.")
        st.dataframe(df)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Temizlenmiş Veriyi İndir", csv, "temiz_veri.csv", "text/csv")
