import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Page Config
st.set_page_config(page_title="Tree Compensation Dashboard V2", layout="wide", page_icon="🌳")

DATA_PATH = 'data.csv'

# 2. Data Engine (ล้างข้อมูลอัตโนมัติ)
@st.cache_data
def load_data():
    if not os.path.exists(DATA_PATH):
        return pd.DataFrame()
    
    df = pd.read_csv(DATA_PATH)
    df.columns = df.columns.str.strip() # ลบช่องว่างที่ชื่อคอลัมน์
    
    # Clean Price Column
    if 'compensation_price' in df.columns:
        df['compensation_price'] = df['compensation_price'].astype(str).str.replace(',', '', regex=False)
        df['compensation_price'] = pd.to_numeric(df['compensation_price'], errors='coerce')
    
    # Clean Year Column
    if 'year' in df.columns:
        df['year'] = pd.to_numeric(df['year'], errors='coerce')
        
    return df

# Initialize Data
if 'df' not in st.session_state:
    st.session_state.df = load_data()

# --- HEADER ---
st.title("🌳 ระบบจัดการข้อมูลราคาค่าทดแทนพืชผล")
st.markdown("---")

# --- TOP NAVIGATION / FILTERS ---
# ใช้ columns เพื่อสร้างแถบกรองข้อมูลด้านบน (แทน Sidebar ที่ใช้งานยาก)
c1, c2, c3, c4 = st.columns([3, 2, 2, 2])

with c1:
    search_q = st.text_input("🔍 ค้นหาชื่อพืช", placeholder="พิมพ์ชื่อเพื่อค้นหาทันที...")

with c2:
    available_years = sorted(st.session_state.df['year'].dropna().unique().astype(int))
    selected_year = st.selectbox("📅 เลือกปี พ.ศ.", options=available_years[::-1])

with c3:
    all_conds = st.session_state.df['plant_condition'].unique().tolist()
    selected_conds = st.multiselect("🍃 สภาพพืช", options=all_conds, default=all_conds)

with c4:
    # ปุ่มสลับหน้าแบบใช้ง่าย
    mode = st.radio("🎮 โหมดการใช้งาน", ["ดูข้อมูล", "เพิ่มข้อมูล"], horizontal=True)

# --- PROCESSING ---
mask = (st.session_state.df['year'] == selected_year) & \
       (st.session_state.df['plant_condition'].isin(selected_conds))

if search_q:
    mask &= (st.session_state.df['plant_name'].str.contains(search_q, na=False))

df_view = st.session_state.df[mask]

# --- MAIN CONTENT ---
if mode == "ดูข้อมูล":
    # สรุปตัวเลขสำคัญ
    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        st.metric("รายการที่พบ", f"{len(df_view)} รายการ")
    with kpi2:
        st.metric("ราคาสูงสุด (ปีนี้)", f"{df_view['compensation_price'].max():,.0f} ฿")
    with kpi3:
        st.metric("ราคาเฉลี่ย (ปีนี้)", f"{df_view['compensation_price'].mean():,.0f} ฿")

    st.markdown("---")

    # กราฟวิเคราะห์
    g1, g2 = st.columns([7, 3])
    with g1:
        st.subheader("📊 การกระจายราคาตามหมวดหมู่ (ก-ฮ)")
        fig_box = px.box(df_view, x='category', y='compensation_price', color='plant_condition',
                         points="all", hover_data=['plant_name'], template="plotly_white")
        st.plotly_chart(fig_box, use_container_width=True)
    
    with g2:
        st.subheader("📌 Top 5 พืชราคาสูง")
        top_5 = df_view.nlargest(5, 'compensation_price')
        fig_bar = px.bar(top_5, x='compensation_price', y='plant_name', orientation='h',
                         color='compensation_price', color_continuous_scale='Greens')
        st.plotly_chart(fig_bar, use_container_width=True)

    # ตารางข้อมูล
    st.subheader("📑 รายละเอียดข้อมูล")
    st.dataframe(df_view.sort_values('compensation_price', ascending=False), use_container_width=True)

else:
    # หน้าเพิ่มข้อมูล (Add Data)
    st.subheader("➕ เพิ่มรายการพืชใหม่")
    with st.form("add_form", clear_on_submit=True):
        f1, f2, f3 = st.columns(3)
        p_id = f1.text_input("รหัสพืช (ID)")
        p_name = f2.text_input("ชื่อพืช")
        p_price = f3.number_input("ราคา (บาท)", min_value=0.0)
        
        f4, f5, f6 = st.columns(3)
        p_cat = f4.text_input("หมวด (ก-ฮ)")
        p_cond = f5.selectbox("สภาพพืช", all_conds)
        p_year = f6.number_input("ปี พ.ศ.", value=selected_year)
        
        if st.form_submit_button("💾 บันทึกข้อมูลเข้าฐานข้อมูล"):
            if p_id and p_name:
                new_row = {
                    'plant_id': p_id, 'plant_name': p_name, 'compensation_price': p_price,
                    'category': p_cat, 'plant_condition': p_cond, 'year': p_year,
                    'account_type': 'A' if 'A' in p_id else 'B'
                }
                st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
                st.session_state.df.to_csv(DATA_PATH, index=False, encoding='utf-8-sig')
                st.success("บันทึกสำเร็จ!")
                st.balloons()
            else:
                st.error("กรุณากรอก ID และชื่อพืช")