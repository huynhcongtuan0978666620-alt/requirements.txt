import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import time

# --- 1. GIAO DIỆN SIÊU SẠCH (ẨN TOÀN BỘ CỦM ICON ĐỎ/TÍM) ---
st.set_page_config(page_title="Hệ Thống Lab 2026", layout="centered", page_icon="🧪")

st.markdown("""
    <style>
        header, footer, .stAppDeployButton {display: none !important; visibility: hidden !important;}
        [data-testid="stStatusWidget"], [data-testid="stToolbar"] {display: none !important;}
        .block-container {padding-top: 1rem !important; padding-bottom: 0rem !important;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. KẾT NỐI GOOGLE SHEETS ---
def get_gspread_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["connections"]["gsheets"], scopes=scope)
    return gspread.authorize(creds)

# --- 3. HÀM LƯU DỮ LIỆU & QUẢN LÝ ---
def safe_append_row(sheet, row_data):
    try:
        sheet.append_row(row_data)
        return True
    except: return False

def get_product_list():
    try:
        client = get_gspread_client()
        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        return [p.strip() for p in sh.worksheet("DanhMuc").col_values(1)[1:] if p.strip()]
    except: return ["Rửa Xe Tay Ga", "Rửa Xe Số", "Thay Nhớt"]

# --- 4. KIỂM TRA ĐĂNG NHẬP ---
if "logged_in" not in st.session_state:
    st.session_state.update({"logged_in": False, "last_submit": 0})

# --- 5. MÀN HÌNH CHÍNH ---
def main_app():
    client = get_gspread_client()
    sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
    sheet_bc = sh.worksheet("BaoCao")

    st.title("🧪 QUẢN LÝ DỊCH VỤ")
    
    with st.expander("🚀 NHẬP DỮ LIỆU", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            nguoi_lam = st.text_input("Người thực hiện", value=st.session_state.get("username", "Nhân Viên"), disabled=True)
            san_pham = st.selectbox("Dịch vụ", get_product_list())
            diem = st.select_slider("Đánh giá", options=[f"{i}/10" for i in range(1, 11)], value="9/10")
        with c2:
            ngay = st.date_input("Ngày", datetime.now())
            sl = st.number_input("Số lượng", min_value=0.0, step=1.0, format="%.0f")
            note = st.text_input("Ghi chú", value="Thực hiện tại tiệm.")

    # --- LOGIC THỜI GIAN CHỜ (ANTI-SPAM) ---
    COOLDOWN_TIME = 3 # Giây chờ giữa 2 lần bấm
    current_time = time.time()
    time_passed = current_time - st.session_state["last_submit"]
    
    if time_passed < COOLDOWN_TIME:
        con_lai = int(COOLDOWN_TIME - time_passed)
        st.warning(f"⏳ Vui lòng đợi {con_lai} giây để hệ thống ổn định...")
        st.button("🚀 ĐANG KHÓA NÚT...", disabled=True, use_container_width=True)
    else:
        if st.button("🚀 LƯU VÀO SỔ CÁI", type="primary", use_container_width=True):
            if sl <= 0:
                st.error("Số lượng phải lớn hơn 0 ní ơi!")
            else:
                with st.status("🚀 Đang ghi dữ liệu, vui lòng không bấm liên tiếp...", expanded=True) as status:
                    # Giả lập thời gian chờ xử lý để ngăn bấm nhanh
                    time.sleep(1.5) 
                    
                    sl_rx = sl if "Nhớt" not in san_pham else 0
                    sl_tn = sl if "Nhớt" in san_pham else 0
                    gio = datetime.now().strftime("%H:%M:%S")
                    row = [ngay.strftime("%d/%m/%Y"), nguoi_lam, san_pham, sl_rx, sl_tn, diem, note, gio]
                    
                    if safe_append_row(sheet_bc, row):
                        st.session_state["last_submit"] = time.time() # Cập nhật thời gian bấm
                        status.update(label="✅ ĐÃ LƯU THÀNH CÔNG!", state="complete", expanded=False)
                        st.success("Dữ liệu đã vào sổ!")
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Lỗi kết nối Google Sheets!")

    if st.sidebar.button("ĐĂNG XUẤT"):
        st.session_state["logged_in"] = False
        st.rerun()

# --- KHỞI CHẠY ---
if not st.session_state["logged_in"]:
    # Màn hình đăng nhập rút gọn để test nhanh
    with st.form("login"):
        u = st.text_input("User"); p = st.text_input("Pass", type="password")
        if st.form_submit_button("LOGIN"):
            if u == "admin" and p == "2026":
                st.session_state.update({"logged_in": True, "username": "Chủ tiệm"})
                st.rerun()
            else: st.error("Sai pass!")
else:
    main_app()
    
