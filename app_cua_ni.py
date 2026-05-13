import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# URL file BC_DULIEU_DEMO_2026 của ní
URL_MOI = "https://docs.google.com/spreadsheets/d/1wkWwXtNSY2E9DEm1lG2fRk0WEmNy2XDUUteppiyJgBo/edit?usp=sharing"

st.set_page_config(page_title="Pha Chế DBX 2026", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

st.markdown("<h2 style='text-align: center;'>🧪 QUẢN LÝ PHA CHẾ THỰC CHIẾN</h2>", unsafe_allow_html=True)

# 1. GIAO DIỆN NHẬP LIỆU
with st.container():
    c1, c2 = st.columns(2)
    with c1:
        sp = st.selectbox("Sản phẩm", ["DBX V1.2", "DBX V1.3", "Dung dịch Rửa Xe", "Tẩy Nhôm"])
        rx = st.number_input("Lượng Rửa Xe (Lít)", 0.0, step=0.1)
        tn = st.number_input("Lượng Tẩy Nhôm (Lít)", 0.0, step=0.1)
    with c2:
        dg = st.slider("Đánh giá (xx/10)", 1, 10, 8)
        gc = st.text_area("Ghi chú thao tác", "Pha chế tại Lab.")

tong = rx + tn
if tong > 0:
    st.info(f"📊 Tỷ lệ: RX {(rx/tong)*100:.1f}% - TN {(tn/tong)*100:.1f}% (Tổng: {tong} Lít)")

# 2. XỬ LÝ LƯU DỮ LIỆU (Đã tối ưu để tránh lỗi 400)
if st.button("🚀 LƯU VÀO SỔ CÁI"):
    try:
        new_row = pd.DataFrame([{
            "Ngày": datetime.now().strftime("%d/%m/%Y"),
            "Người làm": "Chủ tiệm",
            "Sản phẩm": sp,
            "SL Rửa Xe": rx,
            "SL Tẩy Nhôm": tn,
            "Đánh giá": f"{dg}/10",
            "Ghi chú": gc,
            "Giờ lưu": datetime.now().strftime("%H:%M:%S")
        }])
        
        # Đọc dữ liệu hiện có
        try:
            df_old = conn.read(spreadsheet=URL_MOI, worksheet="BaoCao", ttl=0)
            df_final = pd.concat([df_old, new_row], ignore_index=True)
        except:
            # Nếu tab BaoCao chưa có gì, dùng luôn dòng mới
            df_final = new_row
            
        # Ghi đè vào Sheets
        conn.update(spreadsheet=URL_MOI, worksheet="BaoCao", data=df_final)
        st.balloons()
        st.success("✅ ĐÃ LƯU THÀNH CÔNG!")
    except Exception as e:
        st.error(f"Lỗi: {e}")
