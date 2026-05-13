import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime, timedelta

# --- 1. CẤU HÌNH & MAKEUP ---
st.set_page_config(page_title="Hệ Thống Lab 2026", layout="centered", page_icon="🧪")

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
    creds = Credentials.from_service_account_info(st.secrets["connections"]["gsheets"], scopes=scope)
    return gspread.authorize(creds)

# --- 3. KHỞI TẠO BIẾN TẠM ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["role"] = None
if "last_submit_time" not in st.session_state:
    st.session_state["last_submit_time"] = None

# --- 4. GIAO DIỆN ĐĂNG NHẬP ---
def login_screen():
    st.markdown("<h1 style='text-align: center;'>🔐 QUẢN LÝ LAB 2026</h1>", unsafe_allow_html=True)
    with st.form("login_form"):
        user = st.text_input("Tên đăng nhập / SĐT")
        password = st.text_input("Mật khẩu", type="password")
        if st.form_submit_button("ĐĂNG NHẬP", use_container_width=True):
            if user == "admin" and password == "2026": 
                st.session_state["logged_in"] = True
                st.session_state["username"] = "Chủ tiệm"
                st.session_state["role"] = "admin"
                st.rerun()
            elif user.isdigit() and len(user) >= 10 and password == "123456":
                st.session_state["logged_in"] = True
                st.session_state["username"] = f"NV: {user}"
                st.session_state["role"] = "staff"
                st.rerun()
            else:
                st.error("Thông tin không đúng ní ơi!")

# --- 5. GIAO DIỆN CHÍNH ---
def main_app():
    with st.sidebar:
        st.success(f"🟢 {st.session_state['username']}")
        if st.button("ĐĂNG XUẤT"):
            st.session_state["logged_in"] = False
            st.rerun()

    st.title("🧪 QUẢN LÝ PHA CHẾ")
    
    with st.expander("🚀 NHẬP MẺ MỚI", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            nguoi_lam = st.text_input("Người thực hiện", value=st.session_state["username"], disabled=True)
            san_pham = st.selectbox("Sản phẩm", ["DBX V1.2", "DBX V1.3", "Dung dịch Rửa Xe", "Tẩy Nhôm"])
            diem_so = st.select_slider("Đánh giá", options=[f"{i}/10" for i in range(1, 11)], value="8/10")
        with col2:
            ngay = st.date_input("Ngày thực hiện", datetime.now())
            so_luong = st.number_input("Số lượng (Lít)", min_value=0.0, step=0.1, format="%.1f")
            ghi_chu = st.text_input("Ghi chú", value="Pha chế tại Lab.")

    # --- CƠ CHẾ KIỂM TRA THÔNG MINH ---
    is_duplicate = False
    try:
        client = get_gspread_client()
        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        sheet = sh.worksheet("BaoCao")
        last_row = sheet.get_all_values()[-1]
        
        # Kiểm tra nếu trùng 100% dữ liệu mẻ vừa rồi
        if last_row[1] == nguoi_lam and last_row[2] == san_pham and float(str(last_row[3]).replace(',','.')) == so_luong:
            is_duplicate = True
    except:
        pass

    confirm_duplicate = False
    if is_duplicate:
        st.warning("⚠️ Hệ thống thấy mẻ này giống hệt mẻ vừa lưu!")
        confirm_duplicate = st.checkbox("Xác nhận đây là mẻ mới (không phải ấn nhầm)")

    # Nút bấm chỉ mở khi: Không trùng HOẶC Trùng nhưng đã tích xác nhận
    btn_disabled = is_duplicate and not confirm_duplicate

    if st.button("🚀 LƯU VÀO SỔ CÁI", type="primary", use_container_width=True, disabled=btn_disabled):
        if so_luong <= 0:
            st.warning("Số lượng phải lớn hơn 0!")
        else:
            try:
                sl_rua_xe = so_luong if "Tẩy Nhôm" not in san_pham else 0
                sl_tay_nhom = so_luong if "Tẩy Nhôm" in san_pham else 0
                gio_hien_tai = datetime.now().strftime("%H:%M:%S")
                
                new_row = [ngay.strftime("%d/%m/%Y"), nguoi_lam, san_pham, sl_rua_xe, sl_tay_nhom, diem_so, ghi_chu, gio_hien_tai]
                sheet.append_row(new_row)
                
                st.success(f"Đã lưu thành công mẻ {san_pham}!")
                st.balloons()
                st.rerun() 
            except Exception as e:
                st.error(f"Lỗi: {e}")

    # --- PHẦN BÁO CÁO CHO CHỦ ---
    if st.session_state["role"] == "admin":
        st.divider()
        st.subheader("📊 BÁO CÁO TỔNG HỢP")
        try:
            data = sheet.get_all_records()
            if data:
                df = pd.DataFrame(data)
                st.dataframe(df.tail(15))
        except:
            st.info("Đang tải dữ liệu...")

# --- ĐIỀU HƯỚNG ---
if not st.session_state["logged_in"]:
    login_screen()
else:
    main_app()
                 
