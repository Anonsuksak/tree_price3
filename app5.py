import streamlit as st
import pandas as pd
import plotly.express as px
import os

# -----------------------
# CONFIG
# -----------------------
st.set_page_config(page_title="Tree Price Dashboard", layout="wide")
st.title("🌳 ระบบฐานข้อมูลราคาต้นไม้และพืชผล")

# -----------------------
# LOAD DATA
# -----------------------
@st.cache_data
def load_data():
    file_path = os.path.join("data", "market_price.xlsx")

    if not os.path.exists(file_path):
        st.error(f"❌ ไม่พบไฟล์: {file_path}")
        st.stop()

    df = pd.read_excel(file_path, engine="openpyxl")

    # ทำชื่อ column เป็น lowercase
    df.columns = df.columns.str.lower()

    # -----------------------
    # CLEAN NUMERIC COLUMNS
    # -----------------------
    numeric_cols = ["market_price_min", "market_price_max", "est_price"]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(",", "")
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


df = load_data()

# -----------------------
# SIDEBAR FILTER
# -----------------------
st.sidebar.header("🔎 ตัวกรองข้อมูล")

# search
search = st.sidebar.text_input("ค้นหาชื่อพืช")

# plant filter
if "plant_name" in df.columns:
    plants = df["plant_name"].dropna().unique()
    selected_plants = st.sidebar.multiselect("เลือกพืช", plants)
else:
    selected_plants = []

# account type
if "account_type" in df.columns:
    account = st.sidebar.multiselect("ประเภทบัญชี", df["account_type"].dropna().unique())
else:
    account = []

# size
if "size" in df.columns:
    size = st.sidebar.multiselect("ขนาด", df["size"].dropna().unique())
else:
    size = []

# -----------------------
# FILTER LOGIC
# -----------------------
filtered = df.copy()

if search and "plant_name" in filtered.columns:
    filtered = filtered[filtered["plant_name"].str.contains(search, case=False, na=False)]

if selected_plants:
    filtered = filtered[filtered["plant_name"].isin(selected_plants)]

if account:
    filtered = filtered[filtered["account_type"].isin(account)]

if size:
    filtered = filtered[filtered["size"].isin(size)]

# -----------------------
# KPI
# -----------------------
st.subheader("📊 ภาพรวม")

col1, col2, col3 = st.columns(3)

# safe mean function
def safe_mean(series):
    if series is not None and len(series.dropna()) > 0:
        return round(series.mean(), 2)
    return None

# KPI 1
if "market_price_min" in filtered.columns:
    val = safe_mean(filtered["market_price_min"])
    col1.metric("ราคาต่ำสุดเฉลี่ย", f"{val:,.2f}" if val else "ไม่มีข้อมูล")

# KPI 2
if "market_price_max" in filtered.columns:
    val = safe_mean(filtered["market_price_max"])
    col2.metric("ราคาสูงสุดเฉลี่ย", f"{val:,.2f}" if val else "ไม่มีข้อมูล")

# KPI 3
if "est_price" in filtered.columns:
    val = safe_mean(filtered["est_price"])
    col3.metric("ราคาประเมินเฉลี่ย", f"{val:,.2f}" if val else "ไม่มีข้อมูล")

# -----------------------
# CHART
# -----------------------
st.subheader("📈 การกระจายราคา")

if "market_price_min" in filtered.columns:
    fig = px.histogram(
        filtered,
        x="market_price_min",
        nbins=30,
        title="Distribution of Minimum Price"
    )
    st.plotly_chart(fig, use_container_width=True)

# -----------------------
# SCATTER (MIN-MAX)
# -----------------------
if "market_price_min" in filtered.columns and "market_price_max" in filtered.columns:
    st.subheader("📊 เปรียบเทียบช่วงราคา (Min-Max)")

    fig2 = px.scatter(
        filtered,
        x="market_price_min",
        y="market_price_max",
        hover_data=["plant_name"] if "plant_name" in filtered.columns else None
    )
    st.plotly_chart(fig2, use_container_width=True)

# -----------------------
# TABLE
# -----------------------
st.subheader("📋 ตารางข้อมูล")

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