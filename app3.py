import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. ตั้งค่าหน้าจอแบบ Wide และธีมสีเขียวสะอาดตา
st.set_page_config(page_title="Tree Price Database 2026", layout="wide", page_icon="🌳")

DATA_PATH = 'data.csv'

# 2. ฟังก์ชันโหลดและคลีนข้อมูล
@st.cache_data
def load_data():
    if not os.path.exists(DATA_PATH):
        return pd.DataFrame()
    
    df = pd.read_csv(DATA_PATH)
    df.columns = df.columns.str.strip() # ลบช่องว่างที่ชื่อคอลัมน์
    
    # จัดการคอลัมน์ราคา: ลบคอมม่าและแปลงเป็นตัวเลข
    if 'compensation_price' in df.columns:
        df['compensation_price'] = df['compensation_price'].astype(str).str.replace(',', '', regex=False)
        df['compensation_price'] = pd.to_numeric(df['compensation_price'], errors='coerce')
    
    # คลีนข้อมูลตัวอักษร
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.strip()
            
    return df

# เริ่มต้นข้อมูล
if 'df' not in st.session_state:
    st.session_state.df = load_data()

# --- HEADER SECTION ---
st.title("🌳 ระบบฐานข้อมูลราคาค่าทดแทนพืชผล")
st.info(f"📅 ข้อมูลปัจจุบัน: บัญชีราคากลางปีล่าสุด | จำนวนทั้งหมด {len(st.session_state.df)} รายการ")

# --- NAVIGATION BAR (TOP) ---
# ปรับให้เมนูอยู่ด้านบนเพื่อให้ใช้งานง่าย
mode = st.segmented_control("เลือกโหมดการทำงาน", ["🔍 ค้นหาและวิเคราะห์", "➕ เพิ่มข้อมูลใหม่"], default="🔍 ค้นหาและวิเคราะห์")

st.markdown("---")

if mode == "🔍 ค้นหาและวิเคราะห์":
    # --- FILTERS ---
    col_f1, col_f2, col_f3 = st.columns([4, 3, 3])
    
    with col_f1:
        search_q = st.text_input("🔍 ค้นหาชื่อพืช", placeholder="พิมพ์ชื่อพืชที่ต้องการหา...")
    
    with col_f2:
        # ตัวเลือกสภาพพืช: มีผล vs ไม่มีผล
        cond_list = sorted(st.session_state.df['plant_condition'].unique().tolist())
        selected_conds = st.multiselect("🍃 สภาพพืช", options=cond_list, default=cond_list)
        
    with col_f3:
        # ตัวเลือกบัญชี A หรือ B
        acc_list = sorted(st.session_state.df['account_type'].unique().tolist())
        selected_acc = st.multiselect("📂 ประเภทบัญชี", options=acc_list, default=acc_list, 
                                     format_func=lambda x: "A: ไม้ยืนต้น" if x == 'A' else "B: พืชล้มลุก")

    # ประมวลผลการกรอง
    mask = (st.session_state.df['plant_condition'].isin(selected_conds)) & \
           (st.session_state.df['account_type'].isin(selected_acc))
    
    if search_q:
        mask &= (st.session_state.df['plant_name'].str.contains(search_q, na=False))
        
    df_filtered = st.session_state.df[mask]

    # --- KPI METRICS ---
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("รายการที่พบ", f"{len(df_filtered):,}")
    k2.metric("ราคาสูงสุด", f"{df_filtered['compensation_price'].max():,.0f} ฿")
    k3.metric("ราคาเฉลี่ย", f"{df_filtered['compensation_price'].mean():,.0f} ฿")
    k4.metric("งบประมาณรวม (Filter)", f"{df_filtered['compensation_price'].sum():,.0f} ฿")

    st.markdown("---")

    # --- CHARTS ---
    g1, g2 = st.columns([6, 4])
    
    with g1:
        st.subheader("📊 ราคาเฉลี่ยแยกตามหมวดหมู่ (ก-ฮ)")
        # กราฟแท่งแสดงราคาเฉลี่ยรายหมวดหมู่ เพื่อดูอินไซต์ว่าหมวดไหนมูลค่าสูง
        cat_avg = df_filtered.groupby('category')['compensation_price'].mean().sort_values(ascending=False).reset_index()
        fig_bar = px.bar(cat_avg, x='category', y='compensation_price', color='compensation_price',
                         color_continuous_scale='Greens', labels={'compensation_price':'ราคาเฉลี่ย (฿)'})
        st.plotly_chart(fig_bar, use_container_width=True)

    with g2:
        st.subheader("🥧 สัดส่วนประเภทพืช")
        pie_data = df_filtered['account_type'].value_counts().reset_index()
        fig_pie = px.pie(pie_data, values='count', names='account_type', hole=0.5,
                         color_discrete_sequence=['#2E7D32', '#A5D6A7'])
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- TABLE ---
    st.subheader("📑 รายละเอียดข้อมูล")
    st.dataframe(df_filtered.sort_values('compensation_price', ascending=False), use_container_width=True, hide_index=True)

else:
    # --- ADD DATA FORM ---
    st.subheader("➕ เพิ่มรายการพืชใหม่")
    with st.form("add_form", clear_on_submit=True):
        a1, a2, a3 = st.columns(3)
        p_id = a1.text_input("รหัสพืช (ID)")
        p_name = a2.text_input("ชื่อพืช")
        p_price = a3.number_input("ราคาค่าทดแทน (บาท)", min_value=0.0)
        
        a4, a5, a6 = st.columns(3)
        p_cat = a4.text_input("หมวดหมู่ (ก-ฮ)")
        p_cond = a5.selectbox("สภาพพืช", ["มีผล/ขนาดใหญ่", "ไม่มีผล/ขนาดเล็ก"])
        p_acc = a6.selectbox("ประเภทบัญชี", ["A", "B"])
        
        if st.form_submit_button("💾 บันทึกข้อมูล"):
            if p_id and p_name:
                new_row = {
                    'plant_id': p_id, 'plant_name': p_name, 'compensation_price': p_price,
                    'category': p_cat, 'plant_condition': p_cond, 'account_type': p_acc,
                    'is_active': 1, 'unit': 'ต้น', 'year': 2568 # กำหนดปีคงที่
                }
                st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
                st.session_state.df.to_csv(DATA_PATH, index=False, encoding='utf-8-sig')
                st.success("บันทึกข้อมูลเรียบร้อยแล้ว!")
                st.balloons()
            else:
                st.error("กรุณากรอกรหัสและชื่อพืชให้ครบถ้วน")