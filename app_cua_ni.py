import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

# --- CẤU HÌNH TRANG (Bắt buộc ở đầu file) ---
st.set_page_config(page_title="Hệ Thống Lab 2026", layout="centered", page_icon="🧪")

# --- KẾT NỐI GOOGLE SHEETS (Dùng thông tin JSON ní đã gửi) ---
def get_gspread_client():
    # Sử dụng thông tin từ Secrets của ní đã thiết lập
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["connections"]["gsheets"], scopes=scope)
    return gspread.authorize(creds)

# --- KIỂM TRẠNG THÁI ĐĂNG NHẬP ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# --- GIAO DIỆN ĐĂNG NHẬP ---
def login_screen():
    st.markdown("<h1 style='text-align: center;'>🔐 ĐĂNG NHẬP HỆ THỐNG</h1>", unsafe_allow_html=True)
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form"):
                user = st.text_input("Tên đăng nhập")
                password = st.text_input("Mật khẩu", type="password")
                submit = st.form_submit_button("XÁC NHẬN ĐĂNG NHẬP")
                
                if submit:
                    # Ní có thể đổi pass ở đây (Hiện tại tôi để mặc định theo ý ní)
                    if user == "admin" and password == "2026": 
                        st.session_state["logged_in"] = True
                        st.session_state["username"] = user
                        st.rerun()
                    else:
                        st.error("Sai thông tin rồi ní ơi!")

# --- GIAO DIỆN CHÍNH (Sau khi đăng nhập) ---
def main_app():
    # Thanh bên Sidebar
    with st.sidebar:
        st.success(f"🟢 Đang trực: {st.session_state['username']}")
        if st.button("ĐĂNG XUẤT"):
            st.session_state["logged_in"] = False
            st.rerun()
        st.divider()
        st.info("Hệ thống quản lý Lab chuyên nghiệp v1.3")

    st.title("🧪 QUẢN LÝ PHA CHẾ THỰC CHIẾN")
    
    # Khu vực nhập liệu
    with st.expander("🚀 NHẬP MẺ PHA CHẾ MỚI", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            nguoi_lam = st.text_input("Người thực hiện", value="Chủ tiệm")
            san_pham = st.selectbox("Sản phẩm pha chế", ["DBX V1.2", "DBX V1.3", "Dung dịch Rửa Xe", "Tẩy Nhôm"])
        with col2:
            ngay = st.date_input("Ngày thực hiện", datetime.now())
            so_luong = st.number_input("Số lượng (Lít)", min_value=0.1, step=0.1)

    if st.button("🚀 LƯU VÀO SỔ CÁI", type="primary", use_container_width=True):
        try:
            with st.spinner("Đang đẩy dữ liệu lên Sheets..."):
                client = get_gspread_client()
                # Kết nối đúng file của ní
                sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
                sheet = sh.worksheet("BaoCao")
                
                # Chuẩn bị dòng dữ liệu
                new_row = [ngay.strftime("%d/%m/%Y"), nguoi_lam, san_pham, so_luong]
                sheet.append_row(new_row)
                
                st.success(f"Đã lưu mẻ {san_pham} ({so_luong} Lít) thành công!")
                st.balloons()
        except Exception as e:
            st.error(f"Lỗi rồi ní ơi: {e}")

    # Hiển thị bảng dữ liệu gần đây
    st.divider()
    st.subheader("📊 Lịch sử 5 mẻ gần nhất")
    try:
        client = get_gspread_client()
        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        df = pd.DataFrame(sh.worksheet("BaoCao").get_all_records())
        st.table(df.tail(5))
    except:
        st.write("Đang đợi dữ liệu mới...")

# --- ĐIỀU HƯỚNG ---
if not st.session_state["logged_in"]:
    login_screen()
else:
    main_app()
    
