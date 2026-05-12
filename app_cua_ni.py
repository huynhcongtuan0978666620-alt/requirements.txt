import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- CẤU HÌNH LINK CHUẨN ---
# Tôi đã lược bỏ phần đuôi dư thừa để tránh lỗi 404
URL_KHO = "https://docs.google.com/spreadsheets/d/1vnbmjqQ-RSVYg3xP4qRzTFMvuVr3kBE-QLGgKzn5LA4/edit?usp=sharing"

st.set_page_config(page_title="Quản Lý Pha Chế V3.0", page_icon="🧪", layout="wide")

# Kết nối
conn = st.connection("gsheets", type=GSheetsConnection)

def doc_du_lieu(sheet_name):
    # Thêm tham số để ép buộc đọc đúng sheet theo tên
    return conn.read(spreadsheet=URL_KHO, worksheet=sheet_name, ttl=0)

# --- ĐĂNG NHẬP ---
if "auth" not in st.session_state:
    st.session_state.update({"auth": False, "user": ""})

if not st.session_state.auth:
    _, col_login, _ = st.columns([1, 1.5, 1])
    with col_login:
        st.markdown("<h2 style='text-align: center;'>💎 ĐĂNG NHẬP HỆ THỐNG</h2>", unsafe_allow_html=True)
        p = st.text_input("Số điện thoại (Tài khoản)")
        pw = st.text_input("Mật khẩu", type="password")
        if st.button("XÁC NHẬN VÀO HỆ THỐNG"):
            try:
                df_nv = doc_du_lieu("NhanVien")
                # Ép kiểu string để tránh lỗi mất số 0 đầu
                p_str = str(p).strip()
                pw_str = str(pw).strip()
                
                user = df_nv[(df_nv['Số điện thoại'].astype(str).str.contains(p_str)) & 
                             (df_nv['Mật khẩu'].astype(str) == pw_str)]
                
                if not user.empty:
                    st.session_state.auth = True
                    st.session_state.user = user.iloc[0]['Tên nhân viên']
                    st.rerun()
                else:
                    st.error("Sai tài khoản hoặc mật khẩu rồi ní ơi!")
            except Exception as e:
                st.error(f"Lỗi: {e}. Ní kiểm tra Tab 'NhanVien' trên Sheets nhé!")
    st.stop()

# --- GIAO DIỆN NHẬP LIỆU ---
st.sidebar.subheader(f"👤 {st.session_state.user}")
if st.sidebar.button("🔓 Thoát"):
    st.session_state.auth = False
    st.rerun()

tab1, tab2 = st.tabs(["📝 NHẬP MẺ HÀNG", "🕵️ SOÁT SỔ CÁI"])

with tab1:
    try:
        df_dm = doc_du_lieu("DanhMuc")
        list_sp = df_dm['Tên Sản Phẩm'].tolist()
        
        c_l, c_r = st.columns([1, 1.2])
        with c_l:
            sp = st.selectbox("Sản phẩm", list_sp)
            rx = st.number_input("Số lượng RX (Lít)", 0.0)
            tn = st.number_input("Số lượng TN (Lít)", 0.0)
            
            t = rx + tn
            p_rx = f"{round((rx/t)*100,1)}%" if t > 0 else "0%"
            p_tn = f"{round((tn/t)*100,1)}%" if t > 0 else "0%"
            st.info(f"Tỷ lệ: RX {p_rx} - TN {p_tn}")
            
            d = st.slider("Chất lượng (xx/10)", 0, 10, 8)
            n = st.text_area("Ghi chú/Hướng dẫn", "Chuẩn quy trình.")
            
            if st.button("🚀 GỬI DỮ LIỆU"):
                new = pd.DataFrame([{
                    "Ngày": datetime.now().strftime('%d/%m/%Y'),
                    "Người làm": st.session_state.user, "Sản phẩm": sp,
                    "SL Rửa Xe": rx, "Tỷ lệ RX": p_rx, "SL Tẩy Nhôm": tn, "Tỷ lệ TN": p_tn,
                    "Đánh giá": f"{d}/10", "Ghi chú": n, "Giờ lưu": datetime.now().strftime('%H:%M:%S')
                }])
                old = doc_du_lieu("BaoCao")
                combined = pd.concat([old, new], ignore_index=True)
                conn.update(spreadsheet=URL_KHO, worksheet="BaoCao", data=combined)
                st.success("ĐÃ LƯU VÀO KHO!")
                st.balloons()
        with c_r:
            st.subheader("5 mẻ mới nhất")
            st.dataframe(doc_du_lieu("BaoCao").tail(5))
    except: st.warning("Đang tải dữ liệu...")

with tab2:
    st.subheader("Sổ cái tổng")
    try: st.dataframe(doc_du_lieu("BaoCao"), use_container_width=True)
    except: st.info("Trống.")
