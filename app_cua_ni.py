import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# URL CHUẨN CỦA NÍ
URL_KHO = "https://docs.google.com/spreadsheets/d/1vnbmjqQ-RSVYg3xP4qRzTFMvuVr3kBE-QLGgKzn5LA4/edit?usp=sharing"

st.set_page_config(page_title="Hệ Thống Pha Chế", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

def doc_du_lieu(sheet_name):
    # Ép buộc lấy dữ liệu thô để tránh lỗi định dạng
    return conn.read(spreadsheet=URL_KHO, worksheet=sheet_name, ttl=0).astype(str)

if "auth" not in st.session_state:
    st.session_state.update({"auth": False, "user": ""})

if not st.session_state.auth:
    _, col_login, _ = st.columns([1, 1.5, 1])
    with col_login:
        st.markdown("<h2 style='text-align: center;'>💎 ĐĂNG NHẬP</h2>", unsafe_allow_html=True)
        p = st.text_input("Số điện thoại")
        pw = st.text_input("Mật khẩu", type="password")
        if st.button("XÁC NHẬN"):
            try:
                df_nv = doc_du_lieu("NhanVien")
                # Xử lý số điện thoại: bỏ số 0 đầu nếu có để so sánh linh hoạt
                p_clean = p.strip().lstrip('0')
                
                # Tìm user trong cột So_dien_thoai (đã đổi tên)
                user = df_nv[df_nv['So_dien_thoai'].str.contains(p_clean) & (df_nv['Mat_khau'] == pw.strip())]
                
                if not user.empty:
                    st.session_state.auth = True
                    st.session_state.user = user.iloc[0]['Ten_nhan_vien']
                    st.rerun()
                else:
                    st.error("Sai tài khoản hoặc mật khẩu!")
            except Exception as e:
                st.error(f"Lỗi kết nối: {e}. Ní kiểm tra lại cột A1 trên Sheets nhé!")
    st.stop()

# --- GIAO DIỆN SAU KHI VÀO ---
st.sidebar.subheader(f"👤 {st.session_state.user}")
if st.sidebar.button("Thoát"):
    st.session_state.auth = False
    st.rerun()

tab1, tab2 = st.tabs(["📝 NHẬP LIỆU", "🕵️ SOÁT SỔ"])
with tab1:
    try:
        df_dm = doc_du_lieu("DanhMuc")
        sp = st.selectbox("Sản phẩm", df_dm['Tên Sản Phẩm'].tolist())
        rx = st.number_input("Lít Rửa Xe", 0.0)
        tn = st.number_input("Lít Tẩy Nhôm", 0.0)
        if st.button("🚀 LƯU"):
            new = pd.DataFrame([{"Ngày": datetime.now().strftime('%d/%m/%Y'), "Người làm": st.session_state.user, "Sản phẩm": sp, "SL Rửa Xe": rx, "SL Tẩy Nhôm": tn, "Giờ lưu": datetime.now().strftime('%H:%M:%S')}])
            old = doc_du_lieu("BaoCao")
            conn.update(spreadsheet=URL_KHO, worksheet="BaoCao", data=pd.concat([old, new], ignore_index=True))
            st.success("ĐÃ LƯU THÀNH CÔNG!")
            st.balloons()
    except: st.info("Đang tải dữ liệu...")
with tab2:
    try: st.dataframe(doc_du_lieu("BaoCao"), use_container_width=True)
    except: st.write("Chưa có dữ liệu.")
