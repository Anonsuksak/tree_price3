import streamlit as st
import pandas as pd
import os

# -----------------------
# CONFIG
# -----------------------
st.set_page_config(page_title="Market Price Search", layout="wide")
st.title("🌳 ระบบฐานข้อมูลราคาตลาดและราคาประเมินต้นไม้")

# -----------------------
# LOAD DATA
# -----------------------
@st.cache_data
def load_data():
    file_path = "market_price.xlsx"

    if not os.path.exists(file_path):
        st.error(f"❌ ไม่พบไฟล์: {file_path}")
        st.stop()

    df = pd.read_excel(file_path, sheet_name="Use_Data", engine="openpyxl")
    df.columns = df.columns.str.lower()

    # clean numeric
    for col in ["market_price_min", "market_price_max", "est_price"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(",", "")
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df

df = load_data()

# -----------------------
# SEARCH
# -----------------------
st.subheader("🔎 ค้นหาข้อมูล")

col1, col2 = st.columns(2)

# search text
search = col1.text_input("ค้นหาชื่อพืช")

# dropdown
plant_list = sorted(df["plant_name"].dropna().unique())
selected_plant = col2.selectbox("หรือเลือกจากรายการ", ["ทั้งหมด"] + plant_list)

# -----------------------
# FILTER
# -----------------------
filtered = df.copy()

if search:
    filtered = filtered[
        filtered["plant_name"].str.contains(search, case=False, na=False)
    ]

if selected_plant != "ทั้งหมด":
    filtered = filtered[filtered["plant_name"] == selected_plant]

# -----------------------
# RESULT COUNT
# -----------------------
st.markdown(f"📌 พบข้อมูลทั้งหมด **{len(filtered)} รายการ**")

# -----------------------
# DISPLAY (CARD STYLE)
# -----------------------
st.subheader("📊 รายละเอียดข้อมูล")

if len(filtered) == 0:
    st.warning("ไม่พบข้อมูล")
else:
    for _, row in filtered.iterrows():
        with st.container():
            st.markdown("----")
            col1, col2, col3 = st.columns(3)

            col1.markdown(f"**🌿 ชื่อพืช:** {row.get('plant_name','-')}")
            col1.markdown(f"ประเภทบัญชี: {row.get('account_type','-')}")
            col1.markdown(f"ขนาด: {row.get('size','-')}")

            col2.markdown(f"ราคาต่ำสุด: {row.get('market_price_min','-')}")
            col2.markdown(f"ราคาสูงสุด: {row.get('market_price_max','-')}")
            col2.markdown(f"ราคาประเมิน: {row.get('est_price','-')}")

            col3.markdown(f"หน่วย: {row.get('unit','-')}")
            col3.markdown(f"ปี: {row.get('year','-')}")
            col3.markdown(f"แหล่งที่มา: {row.get('source','-')}")

# -----------------------
# TABLE (OPTIONAL)
# -----------------------
with st.expander("📋 แสดงข้อมูลแบบตาราง"):
    st.dataframe(filtered, use_container_width=True)

# -----------------------
# DOWNLOAD
# -----------------------
st.download_button(
    "⬇️ ดาวน์โหลดข้อมูล",
    filtered.to_csv(index=False).encode("utf-8-sig"),
    file_name="filtered_data.csv",
    mime="text/csv"
)