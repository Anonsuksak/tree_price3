import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Plant Compensation Dashboard", layout="wide")

# 2. Mock Data (จำลองจากที่คุณให้มา)
# ในการใช้งานจริง แนะนำให้โหลดจาก CSV โดยใช้ pd.read_csv('your_file.csv')
if 'df' not in st.session_state:
    data = {
        'plant_id': ['PLTA0001', 'PLTA0143', 'PLTA0293', 'PLTA0190', 'PLTB0001'],
        'plant_name': ['กรรณิการ์', 'ทุเรียนพันธุ์ดี', 'มะม่วงพันธุ์ดี', 'ปาล์มน้ำมัน', 'ข้าวนาปรัง'],
        'account_type': ['A', 'A', 'A', 'A', 'B'],
        'category': ['ก', 'ท', 'ม', 'ป', 'ข'],
        'est_price_large': [550, 28253, 5150, 5840, 1500],
        'est_price_small': [275, 4000, 2575, 2000, 800],
        'unit': ['ต้น', 'ต้น', 'ต้น', 'ต้น', 'ไร่'],
        'is_active': [1, 1, 1, 1, 1]
    }
    st.session_state.df = pd.DataFrame(data)

# 3. Sidebar Navigation
st.sidebar.title("🌳 Menu")
page = st.sidebar.radio("Go to", ["Dashboard", "Search & Details", "Add New Data"])

# --- PAGE: DASHBOARD ---
if page == "Dashboard":
    st.title("📊 Analytics Dashboard")
    
    # Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Plant Records", len(st.session_state.df))
    c2.metric("Max Compensation (A)", f"{st.session_state.df['est_price_large'].max():,.0f} ฿")
    c3.metric("Avg Price (A)", f"{st.session_state.df[st.session_state.df['account_type']=='A']['est_price_large'].mean():,.0f} ฿")

    # Chart 1: Bar Chart
    st.subheader("Compensation Comparison (Large vs Small)")
    fig = px.bar(st.session_state.df, x='plant_name', y=['est_price_large', 'est_price_small'], 
                 barmode='group', labels={'value': 'Price (Baht)', 'variable': 'Size'})
    st.plotly_chart(fig, use_container_width=True)

# --- PAGE: SEARCH ---
elif page == "Search & Details":
    st.title("🔍 Search Plant Data")
    search_query = st.text_input("Enter plant name or ID")
    
    filtered_df = st.session_state.df[
        st.session_state.df['plant_name'].str.contains(search_query, na=False) |
        st.session_state.df['plant_id'].str.contains(search_query, na=False)
    ]
    
    st.dataframe(filtered_df, use_container_width=True)

# --- PAGE: ADD DATA ---
elif page == "Add New Data":
    st.title("➕ Add New Plant Record")
    with st.form("add_form"):
        col1, col2 = st.columns(2)
        p_id = col1.text_input("Plant ID (e.g., PLTAXXXX)")
        p_name = col2.text_input("Plant Name")
        p_type = col1.selectbox("Account Type", ["A", "B"])
        p_unit = col2.text_input("Unit (e.g., ต้น, ไร่)")
        p_large = col1.number_input("Large Size Price", min_value=0)
        p_small = col2.number_input("Small Size Price", min_value=0)
        
        submitted = st.form_submit_button("Save to Database")
        if submitted:
            new_row = {
                'plant_id': p_id, 'plant_name': p_name, 'account_type': p_type,
                'category': p_name[0], 'est_price_large': p_large, 
                'est_price_small': p_small, 'unit': p_unit, 'is_active': 1
            }
            st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
            st.success("New plant data added successfully!")
