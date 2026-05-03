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
# FILTER UI
# -----------------------
st.subheader("🔎 ค้นหาข้อมูล")

col1, col2, col3, col4 = st.columns(4)

search = col1.text_input("ค้นหาชื่อพืช")

plant_list = sorted(df["plant_name"].dropna().unique())
selected_plant = col2.selectbox("เลือกพืช", ["ทั้งหมด"] + plant_list)

account_list = sorted(df["account_type"].dropna().unique())
selected_account = col3.selectbox("ประเภทบัญชี", ["ทั้งหมด"] + account_list)

size_list = sorted(df["size"].dropna().unique())
selected_size = col4.selectbox("ขนาด", ["ทั้งหมด"] + size_list)

# -----------------------
# FILTER LOGIC
# -----------------------
filtered = df.copy()

if search:
    filtered = filtered[
        filtered["plant_name"].str.contains(search, case=False, na=False)
    ]

if selected_plant != "ทั้งหมด":
    filtered = filtered[filtered["plant_name"] == selected_plant]

if selected_account != "ทั้งหมด":
    filtered = filtered[filtered["account_type"] == selected_account]

if selected_size != "ทั้งหมด":
    filtered = filtered[filtered["size"] == selected_size]

# -----------------------
# RESULT COUNT
# -----------------------
st.markdown(f"📌 พบข้อมูลทั้งหมด **{len(filtered)} รายการ**")

# -----------------------
# SHOW LIMIT
# -----------------------
limit = st.selectbox("จำนวนที่แสดง", [10, 20, 50, 100], index=0)

display_df = filtered.head(limit)

# -----------------------
# TABLE (FAST)
# -----------------------
st.subheader("📋 ตารางข้อมูล")

st.dataframe(display_df, use_container_width=True)

# -----------------------
# DOWNLOAD
# -----------------------
st.download_button(
    "⬇️ ดาวน์โหลดข้อมูล",
    filtered.to_csv(index=False).encode("utf-8-sig"),
    file_name="filtered_data.csv",
    mime="text/csv"
)