import streamlit as st
import pandas as pd
import plotly.express as px

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
    df = pd.read_excel("ฐานข้อมูลราคาตลาดและราคาประเมินต้นไม้_รวม_3.05.2026.xlsx")
    return df

df = load_data()

# -----------------------
# CLEAN DATA (เผื่อ)
# -----------------------
df.columns = df.columns.str.lower()

# -----------------------
# SIDEBAR FILTER
# -----------------------
st.sidebar.header("🔎 ตัวกรองข้อมูล")

# search
search = st.sidebar.text_input("ค้นหาชื่อพืช")

# plant filter
plants = df["plant_name"].dropna().unique()
selected_plants = st.sidebar.multiselect("เลือกพืช", plants)

# account type
if "account_type" in df.columns:
    account = st.sidebar.multiselect("ประเภทบัญชี", df["account_type"].unique())

# size
if "size" in df.columns:
    size = st.sidebar.multiselect("ขนาด", df["size"].dropna().unique())

# -----------------------
# FILTER LOGIC
# -----------------------
filtered = df.copy()

if search:
    filtered = filtered[filtered["plant_name"].str.contains(search, case=False, na=False)]

if selected_plants:
    filtered = filtered[filtered["plant_name"].isin(selected_plants)]

if "account_type" in df.columns and account:
    filtered = filtered[filtered["account_type"].isin(account)]

if "size" in df.columns and size:
    filtered = filtered[filtered["size"].isin(size)]

# -----------------------
# KPI
# -----------------------
st.subheader("📊 ภาพรวม")

col1, col2, col3 = st.columns(3)

if "market_price_min" in filtered.columns:
    col1.metric("ราคาต่ำสุดเฉลี่ย", round(filtered["market_price_min"].mean(),2))

if "market_price_max" in filtered.columns:
    col2.metric("ราคาสูงสุดเฉลี่ย", round(filtered["market_price_max"].mean(),2))

if "est_price" in filtered.columns:
    col3.metric("ราคาประเมินเฉลี่ย", round(filtered["est_price"].mean(),2))

# -----------------------
# CHART
# -----------------------
st.subheader("📈 การกระจายราคา")

if "market_price_min" in filtered.columns:
    fig = px.histogram(filtered, x="market_price_min", nbins=30, title="Distribution of Min Price")
    st.plotly_chart(fig, use_container_width=True)

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
    filtered.to_csv(index=False),
    file_name="filtered_data.csv"
)