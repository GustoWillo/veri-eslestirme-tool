# Streamlit tabanlı demo: Veri Eşleştirme & Temizleme Aracı

import streamlit as st
import pandas as pd
import datetime

# Belirli isimleri içeren örnek liste (ileri aşamada dinamik yapılabilir)
KNOWN_NAMES = ["Ali Veli", "Ayşe Kaya", "Mehmet Yılmaz"]

# Fonksiyon: Kuralları uygula
def check_rules(row):
    description_col = row.get("description_col", "")
    amount_col = row.get("amount_col", "")
    date_col = row.get("date_col", "")

    has_contract = any(word.isdigit() and len(word) == 8 for word in str(description_col).split())
    has_tckn = any(word.isdigit() and len(word) == 11 for word in str(description_col).split())
    has_name = any(name in str(description_col) for name in KNOWN_NAMES)

    try:
        parsed_amount = float(amount_col)
        is_valid_amount = parsed_amount > 0
    except:
        is_valid_amount = False

    try:
        if isinstance(date_col, str):
            parsed_date = pd.to_datetime(date_col, dayfirst=True)
        else:
            parsed_date = date_col
        is_valid_date = parsed_date <= datetime.datetime.now()
    except:
        is_valid_date = False

    if not has_contract:
        return "❌ Sözleşme No Eksik"
    elif not has_tckn:
        return "⚠️ TCKN Eksik"
    elif not has_name:
        return "⚠️ İsim Eksik veya Eşleşmiyor"
    elif not is_valid_amount:
        return "❌ Geçersiz Tutar"
    elif not is_valid_date:
        return "❌ Geçersiz Tarih"
    else:
        return "✅ Eşleşti"

# Arayüz
st.title("Veri Eşleştirme & Temizleme Demo Tool")
st.write("Yüklediğiniz veride açıklama, tarih ve tutar sütunlarını otomatik tanımaya çalışıyoruz. İsterseniz elle de seçebilirsiniz.")

uploaded_file = st.file_uploader("Excel dosyasını yükleyin", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("Yüklenen veri:")
    st.dataframe(df.head())

    column_options = df.columns.tolist()

    # Otomatik tahmin + kullanıcı seçimi
    default_desc = next((col for col in column_options if "açıklama" in col.lower() or "desc" in col.lower()), column_options[0])
    default_amount = next((col for col in column_options if "tutar" in col.lower() or "amount" in col.lower()), column_options[0])
    default_date = next((col for col in column_options if "tarih" in col.lower() or "date" in col.lower()), column_options[0])

    desc_col = st.selectbox("Açıklama sütunu", options=column_options, index=column_options.index(default_desc))
    amount_col = st.selectbox("Tutar sütunu", options=column_options, index=column_options.index(default_amount))
    date_col = st.selectbox("Tarih sütunu", options=column_options, index=column_options.index(default_date))

    df["description_col"] = df[desc_col]
    df["amount_col"] = df[amount_col]
    df["date_col"] = df[date_col]

    df["Durum"] = df.apply(check_rules, axis=1)
    st.success("Veri işlendi. Aşağıda eşleşme durumlarını görebilirsiniz.")
    st.dataframe(df[[desc_col, amount_col, date_col, "Durum"]])

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("İşlenmiş Veriyi İndir", csv, "eslesme_sonuclari.csv", "text/csv")
