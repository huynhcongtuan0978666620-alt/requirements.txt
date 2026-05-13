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

# --- 3. KIỂM TRẠNG THÁI ĐĂNG NHẬP ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["role"] = None
if "last_submit_time" not in st.session_state:
    st.session_state["last_submit_time"] = None

# --- 4. GIAO DIỆN ĐĂNG NHẬP ---
def login_screen():
    st.markdown("<h1 style='text-align: center;'>🔐 HỆ THỐNG LAB THỰC CHIẾN</h1>", unsafe_allow_html=True)
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form"):
                user = st.text_input("Tên đăng nhập / SĐT")
                password = st.text_input("Mật khẩu", type="password")
                submit = st.form_submit_button("XÁC NHẬN", use_container_width=True)
                if submit:
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
                        st.error("Sai thông tin rồi ní!")

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

    # KIỂM TRA THỜI GIAN GIỮA 2 LẦN BẤM (Chặn bấm liên tục trong 10 giây)
    can_submit = True
    if st.session_state["last_submit_time"]:
        if datetime.now() - st.session_state["last_submit_time"] < timedelta(seconds=10):
            can_submit = False

    if st.button("🚀 LƯU VÀO SỔ CÁI", type="primary", use_container_width=True, disabled=not can_submit):
        try:
            client = get_gspread_client()
            sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
            sheet = sh.worksheet("BaoCao")
            
            # --- TẦNG BẢO VỆ 2: KIỂM TRA TRÙNG LẶP ---
            last_row = sheet.get_all_values()[-1] # Lấy dòng cuối cùng trong Sheets
            gio_hien_tai = datetime.now().strftime("%H:%M:%S")
            
            # Nếu dòng cuối giống hệt dữ liệu đang định nhập (Sản phẩm + Số lượng + Người làm)
            # Và thời gian lưu chỉ cách nhau rất ngắn thì chặn lại
            if last_row[1] == nguoi_lam and last_row[2] == san_pham and float(str(last_row[3]).replace(',','.')) == so_luong:
                st.warning("⚠️ Mẻ này ní vừa mới lưu xong mà! Đừng bấm nữa, dữ liệu đã lên sổ rồi.")
            else:
                sl_rua_xe = so_luong if "Tẩy Nhôm" not in san_pham else 0
                sl_tay_nhom = so_luong if "Tẩy Nhôm" in san_pham else 0
                
                new_row = [ngay.strftime("%d/%m/%Y"), nguoi_lam, san_pham, sl_rua_xe, sl_tay_nhom, diem_so, ghi_chu, gio_hien_tai]
                sheet.append_row(new_row)
                
                st.session_state["last_submit_time"] = datetime.now() # Lưu lại giờ bấm
                st.success(f"Đã lưu thành công mẻ {san_pham}!")
                st.balloons()
                st.rerun() # Tải lại trang để khóa nút tạm thời
        except Exception as e:
            st.error(f"Lỗi: {e}")

    if not can_submit:
        st.info("⏳ Hệ thống đang xử lý, vui lòng đợi vài giây để nhập mẻ tiếp theo...")

    # --- CHỈ CHỦ MỚI THẤY BẢO CÁO ---
    if st.session_state["role"] == "admin":
        st.divider()
        st.subheader("📊 BÁO CÁO TỔNG HỢP")
        try:
            client = get_gspread_client()
            sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
            data = sh.worksheet("BaoCao").get_all_records()
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
                     
