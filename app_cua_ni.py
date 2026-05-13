import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

# --- 1. CẤU HÌNH TRANG & GIẤU TIỆN ÍCH THỪA ---
st.set_page_config(page_title="Hệ Thống Lab 2026", layout="centered", page_icon="🧪")

# Đoạn mã CSS để giấu Menu, Footer và nút Deploy của Streamlit
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stAppDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. KẾT NỐI GOOGLE SHEETS ---
def get_gspread_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    # Lấy thông tin từ Secrets đã cấu hình
    creds = Credentials.from_service_account_info(st.secrets["connections"]["gsheets"], scopes=scope)
    return gspread.authorize(creds)

# --- 3. KIỂM TRẠNG THÁI ĐĂNG NHẬP ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# --- 4. GIAO DIỆN ĐĂNG NHẬP ---
def login_screen():
    st.markdown("<h1 style='text-align: center;'>🔐 ĐĂNG NHẬP HỆ THỐNG</h1>", unsafe_allow_html=True)
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form"):
                user = st.text_input("Tên đăng nhập")
                password = st.text_input("Mật khẩu", type="password")
                submit = st.form_submit_button("XÁC NHẬN ĐĂNG NHẬP", use_container_width=True)
                
                if submit:
                    if user == "admin" and password == "2026": 
                        st.session_state["logged_in"] = True
                        st.session_state["username"] = user
                        st.rerun()
                    else:
                        st.error("Sai thông tin rồi ní ơi!")

# --- 5. GIAO DIỆN CHÍNH (Sau khi đăng nhập) ---
def main_app():
    with st.sidebar:
        st.success(f"🟢 Đang trực: {st.session_state['username']}")
        if st.button("ĐĂNG XUẤT"):
            st.session_state["logged_in"] = False
            st.rerun()
        st.divider()
        st.info("Hệ thống quản lý Lab v1.4")

    st.title("🧪 QUẢN LÝ PHA CHẾ THỰC CHIẾN")
    
    # Khu vực nhập liệu mở rộng đủ 8 cột
    with st.expander("🚀 NHẬP MẺ PHA CHẾ MỚI", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            nguoi_lam = st.text_input("Người thực hiện", value="Chủ tiệm")
            san_pham = st.selectbox("Sản phẩm pha chế", ["DBX V1.2", "DBX V1.3", "Dung dịch Rửa Xe", "Tẩy Nhôm"])
            diem_so = st.select_slider("Đánh giá chất lượng", options=[f"{i}/10" for i in range(1, 11)], value="8/10")
        with col2:
            ngay = st.date_input("Ngày thực hiện", datetime.now())
            so_luong = st.number_input("Số lượng (Lít)", min_value=0.0, step=0.1, format="%.1f")
            ghi_chu = st.text_input("Ghi chú nhanh", value="Pha chế tại Lab.")

    if st.button("🚀 LƯU VÀO SỔ CÁI", type="primary", use_container_width=True):
        if so_luong <= 0:
            st.warning("Ní ơi, số lượng phải lớn hơn 0 mới lưu được chứ!")
        else:
            try:
                with st.spinner("Đang đẩy dữ liệu lên Sheets..."):
                    client = get_gspread_client()
                    sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
                    sheet = sh.worksheet("BaoCao")
                    
                    # Tự động phân loại số lượng vào cột D hoặc E
                    sl_rua_xe = so_luong if "Tẩy Nhôm" not in san_pham else 0
                    sl_tay_nhom = so_luong if "Tẩy Nhôm" in san_pham else 0
                    
                    # Lấy giờ lưu thực tế
                    gio_hien_tai = datetime.now().strftime("%H:%M:%S")
                    
                    # Dòng dữ liệu đầy đủ 8 cột: Ngày, Người làm, Sản phẩm, SL Rửa Xe, SL Tẩy Nhôm, Đánh giá, Ghi chú, Giờ lưu
                    new_row = [
                        ngay.strftime("%d/%m/%Y"), 
                        nguoi_lam, 
                        san_pham, 
                        sl_rua_xe, 
                        sl_tay_nhom, 
                        diem_so, 
                        ghi_chu, 
                        gio_hien_tai
                    ]
                    
                    sheet.append_row(new_row)
                    st.success(f"Đã lưu mẻ {san_pham} thành công vào lúc {gio_hien_tai}!")
                    st.balloons()
            except Exception as e:
                st.error(f"Lỗi kết nối rồi ní: {e}")

    # Hiển thị lịch sử
    st.divider()
    st.subheader("📊 5 mẻ pha chế gần nhất")
    try:
        client = get_gspread_client()
        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        data = sh.worksheet("BaoCao").get_all_records()
        if data:
            df = pd.DataFrame(data)
            st.table(df.tail(5))
    except:
        st.info("Chưa có dữ liệu hiển thị hoặc đang cập nhật...")

# --- ĐIỀU HƯỚNG ---
if not st.session_state["logged_in"]:
    login_screen()
else:
    main_app()
    
