import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import time

# --- 1. CẤU HÌNH GIAO DIỆN & ẨN MENU (THEO ẢNH Screenshot_20260513_182407_Chrome_2.jpg) ---
st.set_page_config(page_title="Hệ Thống Lab 2026", layout="centered", page_icon="🧪")

# Đoạn mã CSS này sẽ ẩn thanh trên cùng và nút Deploy phía dưới
st.markdown("""
    <style>
        /* Ẩn thanh Header phía trên (Share, Star, Github, Menu) */
        header {visibility: hidden;}
        
        /* Ẩn nút 'Deploy' và các thành phần liên quan ở góc dưới bên phải */
        .stAppDeployButton {display:none;}
        footer {visibility: hidden;}
        
        /* Tùy chỉnh thêm để khung đăng nhập cân đối hơn */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 0rem;
        }
    </style>
    """, unsafe_allow_html=True)

# --- 2. KẾT NỐI GOOGLE SHEETS (GIỮ NGUYÊN) ---
def get_gspread_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["connections"]["gsheets"], scopes=scope)
    return gspread.authorize(creds)

# --- 3. CƠ CHẾ LƯU DỮ LIỆU AN TOÀN ---
def safe_append_row(sheet, row_data):
    max_retries = 3 
    for i in range(max_retries):
        try:
            sheet.append_row(row_data)
            return True
        except Exception:
            if i < max_retries - 1:
                time.sleep(2)
                continue
            return False

# --- 4. CÁC HÀM BỔ TRỢ ---
def get_product_list():
    try:
        client = get_gspread_client()
        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        sheet_dm = sh.worksheet("DanhMuc")
        products = sheet_dm.col_values(1)[1:]
        return [p.strip() for p in products if p.strip()]
    except:
        return ["Rửa Xe Tay Ga", "Rửa Xe Số", "Thay Nhớt"]

def check_login(user_input, pass_input):
    try:
        client = get_gspread_client()
        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        sheet_nv = sh.worksheet("NhanVien")
        data_nv = sheet_nv.get_all_records()
        for row in data_nv:
            if str(row['Số Điện Thoại (Login)']).strip() == str(user_input).strip() and \
               str(row['Mật Khẩu']).strip() == str(pass_input).strip():
                return True, row['Tên Nhân Viên']
        return False, None
    except:
        return False, None

# --- 5. MÀN HÌNH ĐĂNG NHẬP SẠCH SẼ ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["role"] = None

def login_screen():
    # Thêm icon ổ khóa cho giống ảnh ní gửi
    st.markdown("<h1 style='text-align: center;'>🔐 ĐĂNG NHẬP HỆ THỐNG</h1>", unsafe_allow_html=True)
    
    with st.container():
        # Tạo khung bao quanh cho chuyên nghiệp
        with st.form("login_form"):
            user = st.text_input("Tên đăng nhập")
            password = st.text_input("Mật khẩu", type="password")
            if st.form_submit_button("XÁC NHẬN ĐĂNG NHẬP", use_container_width=True):
                if user == "admin" and password == "2026": 
                    st.session_state["logged_in"] = True
                    st.session_state["role"] = "admin"
                    st.session_state["username"] = "Chủ tiệm"
                    st.rerun()
                else:
                    success, full_name = check_login(user, password)
                    if success:
                        st.session_state["logged_in"] = True
                        st.session_state["role"] = "staff"
                        st.session_state["username"] = full_name
                        st.rerun()
                    else:
                        st.error("Thông tin đăng nhập chưa đúng ní ơi!")

# --- 6. GIAO DIỆN CHÍNH (GIỮ NGUYÊN) ---
def main_app():
    client = get_gspread_client()
    sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
    sheet_bc = sh.worksheet("BaoCao")

    with st.sidebar:
        st.success(f"🟢 {st.session_state['username']}")
        if st.button("ĐĂNG XUẤT"):
            st.session_state["logged_in"] = False
            st.rerun()

    st.title("🧪 QUẢN LÝ DỊCH VỤ")
    danh_sach_sp = get_product_list()

    with st.expander("🚀 NHẬP DỮ LIỆU", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            nguoi_lam = st.text_input("Người thực hiện", value=st.session_state["username"], disabled=True)
            san_pham = st.selectbox("Dịch vụ / Sản phẩm", danh_sach_sp)
            diem_so = st.select_slider("Đánh giá", options=[f"{i}/10" for i in range(1, 11)], value="9/10")
        with col2:
            ngay = st.date_input("Ngày thực hiện", datetime.now())
            so_luong = st.number_input("Số lượng", min_value=0.0, step=1.0, format="%.0f")
            ghi_chu = st.text_input("Ghi chú", value="Thực hiện tại tiệm.")

    # Kiểm tra trùng (Logic cũ)
    btn_disabled = False
    show_confirm = False
    try:
        all_vals = sheet_bc.get_all_values()
        count_dup = 0
        for row in reversed(all_vals):
            if row[1] == nguoi_lam and row[2] == san_pham and float(str(row[3]).replace(',','.')) == so_luong:
                count_dup += 1
            else: break
        if count_dup >= 1:
            last_time_dt = datetime.strptime(f"{all_vals[-1][0]} {all_vals[-1][7]}", "%d/%m/%Y %H:%M:%S")
            diff = (datetime.now() - last_time_dt).total_seconds()
            if count_dup == 1 and diff < 60: btn_disabled = True
            else: show_confirm = True
    except: pass

    confirm_check = st.checkbox("Xác nhận dữ liệu đúng") if show_confirm else False
    final_disabled = btn_disabled or (show_confirm and not confirm_check)

    if st.button("🚀 LƯU VÀO SỔ CÁI", type="primary", use_container_width=True, disabled=final_disabled):
        if so_luong > 0:
            with st.status("Đang đồng bộ..."):
                sl_rua_xe = so_luong if "Nhớt" not in san_pham else 0
                sl_thay_nhot = so_luong if "Nhớt" in san_pham else 0
                gio_luu = datetime.now().strftime("%H:%M:%S")
                new_row = [ngay.strftime("%d/%m/%Y"), nguoi_lam, san_pham, sl_rua_xe, sl_thay_nhot, diem_so, ghi_chu, gio_luu]
                if safe_append_row(sheet_bc, new_row):
                    st.success("Đã lưu!"); st.balloons(); time.sleep(1); st.rerun()

    if st.session_state["role"] == "admin":
        st.divider(); st.subheader("📊 BÁO CÁO")
        try:
            df = pd.DataFrame(sheet_bc.get_all_records())
            st.dataframe(df.tail(15))
        except: st.info("Đang tải dữ liệu...")

# --- KHỞI CHẠY ---
if not st.session_state["logged_in"]:
    login_screen()
else:
    main_app()
    
