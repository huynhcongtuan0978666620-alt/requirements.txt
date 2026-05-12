import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- CẤU HÌNH ĐƯỜNG ỐNG ---
# Link Google Sheets của ní
URL_KHO = "https://docs.google.com/spreadsheets/d/1Rv74WGZbptvDWqAVuCw2h0Ob0OgcPk8ovgjhwq83SQg/edit?usp=sharing"

st.set_page_config(page_title="Quản Trị V3.0 - Cloud", page_icon="☁️", layout="wide")

# Thiết lập kết nối
conn = st.connection("gsheets", type=GSheetsConnection)

def doc_du_lieu(sheet_name):
    return conn.read(spreadsheet=URL_KHO, worksheet=sheet_name, ttl=0)

# --- KIỂM TRA ĐĂNG NHẬP ---
if "auth" not in st.session_state:
    st.session_state.update({"auth": False, "user": ""})

if not st.session_state.auth:
    _, col_login, _ = st.columns([1, 1.5, 1])
    with col_login:
        st.markdown("<h2 style='text-align: center;'>💎 ĐĂNG NHẬP HỆ THỐNG</h2>", unsafe_allow_html=True)
        p = st.text_input("Số điện thoại (Tài khoản)")
        pw = st.text_input("Mật khẩu", type="password")
        if st.button("XÁC NHẬN VÀO HỆ THỐNG"):
            df_nv = doc_du_lieu("NhanVien")
            user = df_nv[(df_nv['Số điện thoại'].astype(str) == str(p).strip()) & 
                         (df_nv['Mật khẩu'].astype(str) == str(pw).strip())]
            if not user.empty:
                st.session_state.auth = True
                st.session_state.user = user.iloc[0]['Tên nhân viên']
                st.rerun()
            else:
                st.error("Thông tin đăng nhập không đúng!")
    st.stop()

# --- GIAO DIỆN CHÍNH ---
st.sidebar.subheader(f"👤 {st.session_state.user}")
if st.sidebar.button("🔓 Đăng xuất"):
    st.session_state.auth = False
    st.rerun()

tab_nhap, tab_soat = st.tabs(["📝 NHẬP MẺ HÀNG", "🕵️ SOÁT SỔ CÁI"])

# --- TAB 1: NHẬP LIỆU ---
with tab_nhap:
    df_dm = doc_du_lieu("DanhMuc")
    list_sp = df_dm['Tên Sản Phẩm'].tolist()

    col_trai, col_phai = st.columns([1, 1.2])
    with col_trai:
        st.subheader("Thông tin pha chế")
        sp = st.selectbox("Sản phẩm", list_sp)
        c1, c2 = st.columns(2)
        rx = c1.number_input("SL Rửa Xe (RX)", 0)
        tn = c2.number_input("SL Tẩy Nhôm (TN)", 0)
        
        tong = rx + tn
        p_rx = round((rx/tong)*100, 2) if tong > 0 else 0
        p_tn = round((tn/tong)*100, 2) if tong > 0 else 0
        st.info(f"Tỷ lệ: RX {p_rx}% | TN {p_tn}%")
        
        diem = st.slider("Chất lượng mẻ (xx/10)", 0, 10, 8)
        note = st.text_area("Ghi chú thao tác", "Thao tác chuẩn quy trình")

        if st.button("🚀 GỬI HÀNG VÀO KHO GOOGLE"):
            # Chuẩn bị dòng dữ liệu mới
            new_row = [
                datetime.now().strftime('%d/%m/%Y'),
                st.session_state.user,
                sp, rx, f"{p_rx}%", tn, f"{p_tn}%", 
                f"{diem}/10", note,
                datetime.now().strftime('%H:%M:%S')
            ]
            
            try:
                # Đọc sổ cái hiện tại, thêm dòng mới và cập nhật lên mây
                df_bc = doc_du_lieu("BaoCao")
                df_bc.loc[len(df_bc)] = new_row
                conn.update(spreadsheet=URL_KHO, worksheet="BaoCao", data=df_bc)
                st.success("✅ ĐÃ ĐỒNG BỘ VÀO KHO AN TOÀN!")
                st.balloons()
            except Exception as e:
                st.error(f"❌ LỖI VẬN CHUYỂN: {e}")

    with col_phai:
        st.subheader("5 mẻ vừa cập bến")
        df_view = doc_du_lieu("BaoCao")
        st.dataframe(df_view.tail(5), use_container_width=True)

# --- TAB 2: SOÁT SỔ ---
with tab_soat:
    st.subheader("🔍 Nhật ký tổng kho")
    df_full = doc_du_lieu("BaoCao")
    st.write(f"Tổng cộng có: **{len(df_full)}** mẻ đã ghi nhận.")
    st.dataframe(df_full, use_container_width=True)
