import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# URL CHUẨN
URL_KHO = "https://docs.google.com/spreadsheets/d/1vnbmjqQ-RSVYg3xP4qRzTFMvuVr3kBE-QLGgKzn5LA4/edit?usp=sharing"

st.set_page_config(page_title="Quản Lý Pha Chế V3.0", page_icon="🧪", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

def doc_du_lieu(sheet_name):
    return conn.read(spreadsheet=URL_KHO, worksheet=sheet_name, ttl=0)

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
                # Tìm kiếm không phân biệt số 0 ở đầu
                p_val = str(p).strip().lstrip('0')
                pw_val = str(pw).strip()
                
                # Kiểm tra cột (đã đổi sang không dấu)
                user = df_nv[df_nv['So_dien_thoai'].astype(str).str.contains(p_val) & 
                             (df_nv['Mat_khau'].astype(str) == pw_val)]
                
                if not user.empty:
                    st.session_state.auth = True
                    st.session_state.user = user.iloc[0]['Ten_nhan_vien']
                    st.rerun()
                else:
                    st.error("Sai rồi ní ơi!")
            except Exception as e:
                st.error(f"Lỗi: {e}. Ní kiểm tra tên cột A1, B1, C1 trên Sheets nhé!")
    st.stop()

# --- PHẦN NHẬP LIỆU ---
st.sidebar.subheader(f"👤 {st.session_state.user}")
if st.sidebar.button("Thoát"):
    st.session_state.auth = False
    st.rerun()

try:
    tab1, tab2 = st.tabs(["📝 NHẬP MẺ HÀNG", "🕵️ SOÁT SỔ CÁI"])
    with tab1:
        df_dm = doc_du_lieu("DanhMuc")
        sp = st.selectbox("Sản phẩm", df_dm['Tên Sản Phẩm'].tolist())
        c1, c2 = st.columns(2)
        rx = c1.number_input("Lít Rửa Xe", 0.0)
        tn = c2.number_input("Lít Tẩy Nhôm", 0.0)
        d = st.slider("Chất lượng", 0, 10, 8)
        n = st.text_area("Ghi chú", "Chuẩn quy trình.")
        if st.button("🚀 GỬI DỮ LIỆU"):
            new = pd.DataFrame([{"Ngày": datetime.now().strftime('%d/%m/%Y'), "Người làm": st.session_state.user, "Sản phẩm": sp, "SL Rửa Xe": rx, "SL Tẩy Nhôm": tn, "Đánh giá": f"{d}/10", "Ghi chú": n, "Giờ lưu": datetime.now().strftime('%H:%M:%S')}])
            old = doc_du_lieu("BaoCao")
            conn.update(spreadsheet=URL_KHO, worksheet="BaoCao", data=pd.concat([old, new], ignore_index=True))
            st.success("ĐÃ LƯU!")
            st.balloons()
    with tab2:
        st.dataframe(doc_du_lieu("BaoCao"), use_container_width=True)
except:
    st.info("Đang tải dữ liệu...")
