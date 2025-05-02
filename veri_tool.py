import streamlit as st
import pandas as pd
import datetime

def check_rules(row):
    description = row.get("Açıklama", "")
    amount = row.get("Tutar", "")
    date = row.get("Tarih", "")

    has_contract = any(word.isdigit() and len(word) == 8 for word in str(description).split())
    has_tckn = any(word.isdigit() and len(word) == 11 for word in str(description).split())
    has_name = any(name in description for name in ["Ali Veli", "Ayşe Kaya", "Mehmet Yılmaz"])

    try:
        parsed_amount = float(amount)
        is_valid_amount = parsed_amount > 0
    except:
        is_valid_amount = False

    try:
        if isinstance(date, str):
            parsed_date = pd.to_datetime(date, dayfirst=True)
        else:
            parsed_date = date
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

st.title("Veri Eşleştirme & Temizleme Demo Tool")
st.write("Yüklediğiniz veriye göre eşleşme durumları aşağıda listelenecektir.")

uploaded_file = st.file_uploader("Excel dosyasını yükleyin", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df["Durum"] = df.apply(check_rules, axis=1)
    st.success("Veri işlendi. Aşağıda eşleşme durumlarını görebilirsiniz.")
    st.dataframe(df)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("İşlenmiş Veriyi İndir", csv, "eslesme_sonuclari.csv", "text/csv")
