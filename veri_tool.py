# Streamlit tabanlı demo: Veri Temizleme Aracı

st.caption("✅ Kod gerçekten güncellenmişse bu yazı görünür.")

import streamlit as st
import pandas as pd
import requests
import re
from PIL import Image
import io

# OCR.space API entegrasyonu (ücretsiz)
def ocr_space_image(file, language='tur'):
    api_key = 'helloworld'  # Ücretsiz demo anahtarı (kısıtlı)
    url = 'https://api.ocr.space/parse/image'
    payload = {
        'isOverlayRequired': False,
        'apikey': api_key,
        'language': language,
    }
    files = {'file': file.getvalue()}
    response = requests.post(url, files=files, data=payload)
    result = response.json()
    if result['IsErroredOnProcessing']:
        return "OCR Hatası: " + result.get('ErrorMessage', [''])[0]
    return result['ParsedResults'][0]['ParsedText']

# Fonksiyon: OCR metni satırlara böl ve sütun oluştur
def extract_from_image_dynamic(file):
    text = ocr_space_image(file)
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    data = {f"alan_{i+1}": line for i, line in enumerate(lines)}
    data["metin"] = text.replace("\n", " ")[:500]
    return pd.DataFrame([data])

# Fonksiyon: Excel başlıklarını tanımla ve gösterim için hazırla
def analyze_excel_headers(df):
    df = df.copy()
    header_suggestions = {}

    for col in df.columns:
        sample_vals = df[col].astype(str).head(10).tolist()
        col_lower = col.lower()

        if "tarih" in col_lower:
            header_suggestions[col] = "📅 Tarih (başlıktan algılandı)"
        elif "tutar" in col_lower or "ücret" in col_lower:
            header_suggestions[col] = "💰 Tutar (başlıktan algılandı)"
        elif "açıklama" in col_lower or "detay" in col_lower:
            header_suggestions[col] = "📝 Açıklama (başlıktan algılandı)"
        elif any(re.search(r"\d{2}[./-]\d{2}[./-]\d{4}", val) for val in sample_vals):
            header_suggestions[col] = "📅 Tarih (veriden algılandı)"
        elif any(re.search(r"\d+[.,]\d{2}", val) for val in sample_vals):
            header_suggestions[col] = "💰 Tutar (veriden algılandı)"
        elif any(len(val.split()) > 3 for val in sample_vals):
            header_suggestions[col] = "📝 Açıklama (veriden algılandı)"
        else:
            header_suggestions[col] = "🔹 Diğer (başlık & içerik analizine göre sınıflandırılamadı)"

    return df, header_suggestions

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

        df, detected_headers = analyze_excel_headers(df)

        st.success("Kolonlar analiz edildi. Tahmini türleri aşağıda listelenmiştir:")
        for col, meaning in detected_headers.items():
            st.markdown(f"**{col}** → {meaning}")

        st.dataframe(df)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Temizlenmiş Veriyi İndir", csv, "temiz_veri.csv", "text/csv")
