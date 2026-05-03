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
    file_path = "market_price.xlsx"  # <- ใช้ path นี้ตาม repo คุณ

    if not os.path.exists(file_path):
        st.error(f"❌ ไม่พบไฟล์: {file_path}")
        st.stop()

    df = pd.read_excel(file_path, sheet_name="Use_Data", engine="openpyxl")

    # lowercase column
    df.columns = df.columns.str.lower()

    # clean numeric columns
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

search = st.sidebar.text_input("ค้นหาชื่อพืช")

plants = df["plant_name"].dropna().unique() if "plant_name" in df.columns else []
selected_plants = st.sidebar.multiselect("เลือกพืช", plants)

account = df["account_type"].dropna().unique() if "account_type" in df.columns else []
account = st.sidebar.multiselect("ประเภทบัญชี", account)

size = df["size"].dropna().unique() if "size" in df.columns else []
size = st.sidebar.multiselect("ขนาด", size)

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

def safe_mean(series):
    if series is not None and len(series.dropna()) > 0:
        return round(series.mean(), 2)
    return None

# KPI
if "market_price_min" in filtered.columns:
    val = safe_mean(filtered["market_price_min"])
    col1.metric("ราคาต่ำสุดเฉลี่ย", f"{val:,.2f}" if val else "ไม่มีข้อมูล")

if "market_price_max" in filtered.columns:
    val = safe_mean(filtered["market_price_max"])
    col2.metric("ราคาสูงสุดเฉลี่ย", f"{val:,.2f}" if val else "ไม่มีข้อมูล")

if "est_price" in filtered.columns:
    val = safe_mean(filtered["est_price"])
    col3.metric("ราคาประเมินเฉลี่ย", f"{val:,.2f}" if val else "ไม่มีข้อมูล")

# -----------------------
# HISTOGRAM MIN
# -----------------------
st.subheader("📈 การกระจายราคาต่ำสุด")

if "market_price_min" in filtered.columns:
    fig_min = px.histogram(
        filtered,
        x="market_price_min",
        nbins=30,
        title="Distribution of Minimum Price"
    )
    st.plotly_chart(fig_min, use_container_width=True)

# -----------------------
# HISTOGRAM MAX
# -----------------------
st.subheader("📈 การกระจายราคาสูงสุด")

if "market_price_max" in filtered.columns:
    fig_max = px.histogram(
        filtered,
        x="market_price_max",
        nbins=30,
        title="Distribution of Maximum Price"
    )
    st.plotly_chart(fig_max, use_container_width=True)

# -----------------------
# OVERLAY MIN VS MAX
# -----------------------
st.subheader("📊 เปรียบเทียบการกระจาย Min vs Max")

if "market_price_min" in filtered.columns and "market_price_max" in filtered.columns:
    df_melt = filtered.melt(
        value_vars=["market_price_min", "market_price_max"],
        var_name="type",
        value_name="price"
    )

    fig_overlay = px.histogram(
        df_melt,
        x="price",
        color="type",
        nbins=30,
        barmode="overlay",
        title="Min vs Max Price Distribution"
    )

    st.plotly_chart(fig_overlay, use_container_width=True)

# -----------------------
# SCATTER MIN VS MAX
# -----------------------
st.subheader("📍 ความสัมพันธ์ระหว่างราคาต่ำสุดและสูงสุด")

if "market_price_min" in filtered.columns and "market_price_max" in filtered.columns:
    fig_scatter = px.scatter(
        filtered,
        x="market_price_min",
        y="market_price_max",
        hover_data=["plant_name"] if "plant_name" in filtered.columns else None,
        title="Min vs Max Price Scatter"
    )

    st.plotly_chart(fig_scatter, use_container_width=True)

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