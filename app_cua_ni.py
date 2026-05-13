import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

# --- 1. CẤU HÌNH TRANG ---
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

# --- 3. KIỂM TRẠNG THÁI ĐĂNG NHẬP ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["role"] = None # Lưu vai trò: Admin hoặc Nhân viên

# --- 4. GIAO DIỆN ĐĂNG NHẬP PHÂN QUYỀN ---
def login_screen():
    st.markdown("<h1 style='text-align: center;'>🔐 HỆ THỐNG PHÂN QUYỀN</h1>", unsafe_allow_html=True)
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form"):
                user = st.text_input("Tên đăng nhập / Số điện thoại")
                password = st.text_input("Mật khẩu", type="password")
                submit = st.form_submit_button("XÁC NHẬN ĐĂNG NHẬP", use_container_width=True)
                
                if submit:
                    # 1. Kiểm tra quyền Chủ (Admin)
                    if user == "admin" and password == "2026": 
                        st.session_state["logged_in"] = True
                        st.session_state["username"] = "Chủ tiệm"
                        st.session_state["role"] = "admin"
                        st.rerun()
                    
                    # 2. Kiểm tra quyền Nhân viên (SĐT bất kỳ, pass 123456)
                    elif user.isdigit() and len(user) >= 10 and password == "123456":
                        st.session_state["logged_in"] = True
                        st.session_state["username"] = f"NV: {user}"
                        st.session_state["role"] = "staff"
                        st.rerun()
                    else:
                        st.error("Thông tin đăng nhập không đúng, ní ơi!")

# --- 5. GIAO DIỆN CHÍNH ---
def main_app():
    with st.sidebar:
        st.success(f"🟢 {st.session_state['username']}")
        if st.button("ĐĂNG XUẤT"):
            st.session_state["logged_in"] = False
            st.rerun()
        st.divider()
        st.info(f"Quyền hạn: {st.session_state['role'].upper()}")

    st.title("🧪 QUẢN LÝ PHA CHẾ")
    
    # --- PHẦN NHẬP LIỆU (Cả Chủ và Nhân viên đều thấy) ---
    with st.expander("🚀 NHẬP MẺ PHA CHẾ MỚI", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            # Tự động điền tên người làm dựa trên thông tin đăng nhập
            nguoi_lam = st.text_input("Người thực hiện", value=st.session_state["username"], disabled=True)
            san_pham = st.selectbox("Sản phẩm", ["DBX V1.2", "DBX V1.3", "Dung dịch Rửa Xe", "Tẩy Nhôm"])
            diem_so = st.select_slider("Đánh giá chất lượng", options=[f"{i}/10" for i in range(1, 11)], value="8/10")
        with col2:
            ngay = st.date_input("Ngày thực hiện", datetime.now())
            so_luong = st.number_input("Số lượng (Lít)", min_value=0.0, step=0.1, format="%.1f")
            ghi_chu = st.text_input("Ghi chú nhanh", value="Pha chế tại Lab.")

    if st.button("🚀 LƯU VÀO SỔ CÁI", type="primary", use_container_width=True):
        if so_luong <= 0:
            st.warning("Số lượng phải lớn hơn 0 ní ơi!")
        else:
            try:
                client = get_gspread_client()
                sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
                sheet = sh.worksheet("BaoCao")
                
                sl_rua_xe = so_luong if "Tẩy Nhôm" not in san_pham else 0
                sl_tay_nhom = so_luong if "Tẩy Nhôm" in san_pham else 0
                gio_hien_tai = datetime.now().strftime("%H:%M:%S")
                
                new_row = [ngay.strftime("%d/%m/%Y"), nguoi_lam, san_pham, sl_rua_xe, sl_tay_nhom, diem_so, ghi_chu, gio_hien_tai]
                sheet.append_row(new_row)
                st.success("Đã lưu thành công!")
            except Exception as e:
                st.error(f"Lỗi: {e}")

    # --- PHẦN XEM DỮ LIỆU (Chỉ Chủ mới thấy toàn bộ lịch sử) ---
    if st.session_state["role"] == "admin":
        st.divider()
        st.subheader("📊 BÁO CÁO TỔNG HỢP (Chỉ dành cho Chủ)")
        try:
            client = get_gspread_client()
            sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
            data = sh.worksheet("BaoCao").get_all_records()
            if data:
                df = pd.DataFrame(data)
                st.dataframe(df.tail(10)) # Hiện 10 dòng gần nhất
        except:
            st.info("Chưa có dữ liệu.")
    else:
        st.info("💡 Nhân viên chỉ có quyền nhập liệu. Cảm ơn ní đã làm việc!")

# --- ĐIỀU HƯỚNG ---
if not st.session_state["logged_in"]:
    login_screen()
else:
    main_app()
    
