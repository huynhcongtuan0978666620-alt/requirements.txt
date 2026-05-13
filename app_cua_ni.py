import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import time

# --- 1. CẤU HÌNH GIAO DIỆN & DIỆT TẬN GỐC UI THỪA ---
st.set_page_config(page_title="Hệ Thống Lab 2026", layout="centered", page_icon="🧪")

st.markdown("""
    <style>
        /* 1. ẨN TOÀN BỘ HEADER VÀ FOOTER */
        header, footer, .stAppDeployButton {
            display: none !important;
            visibility: hidden !important;
        }

        /* 2. ẨN CỤM ICON VƯƠNG MIỆN/LÂU ĐÀI (STATUS WIDGET) */
        [data-testid="stStatusWidget"], 
        [data-testid="stToolbar"],
        .st-emotion-cache-zt5igj, 
        .st-emotion-cache-15zrgzn {
            display: none !important;
            height: 0px !important;
            width: 0px !important;
            overflow: hidden !important;
        }

        /* 3. ÉP TRÀN MÀN HÌNH ĐỂ KHÔNG CÒN CHỖ CHO TOOLBAR */
        #root > div:nth-child(1) > div.withScreencast > div > div > div {
            padding-top: 0px !important;
        }
        
        /* 4. ẨN NÚT CHẤM BA DÒNG VÀ MENU PHỤ */
        #MainMenu {visibility: hidden !important;}

        /* 5. TỐI ƯU KHOẢNG TRẮNG CHO ĐIỆN THOẠI */
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 0rem !important;
            max-width: 100% !important;
        }
    </style>
    """, unsafe_allow_html=True)

# --- 2. KẾT NỐI GOOGLE SHEETS ---
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
        except:
            if i < max_retries - 1:
                time.sleep(2)
                continue
            return False

# --- 4. HÀM QUẢN LÝ ---
def get_product_list():
    try:
        client = get_gspread_client()
        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        sheet_dm = sh.worksheet("DanhMuc")
        return [p.strip() for p in sheet_dm.col_values(1)[1:] if p.strip()]
    except:
        return ["Rửa Xe Tay Ga", "Rửa Xe Số", "Thay Nhớt"]

def check_login(user_input, pass_input):
    try:
        client = get_gspread_client()
        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        sheet_nv = sh.worksheet("NhanVien")
        for row in sheet_nv.get_all_records():
            if str(row['Số Điện Thoại (Login)']).strip() == str(user_input).strip() and \
               str(row['Mật Khẩu']).strip() == str(pass_input).strip():
                return True, row['Tên Nhân Viên']
        return False, None
    except: return False, None

# --- 5. MÀN HÌNH ĐĂNG NHẬP ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["role"] = None

def login_screen():
    st.markdown("<h1 style='text-align: center;'>🔐 ĐĂNG NHẬP HỆ THỐNG</h1>", unsafe_allow_html=True)
    with st.form("login_form"):
        user = st.text_input("Tên đăng nhập (SĐT)")
        password = st.text_input("Mật khẩu", type="password")
        if st.form_submit_button("XÁC NHẬN ĐĂNG NHẬP", use_container_width=True):
            if user == "admin" and password == "2026": 
                st.session_state.update({"logged_in": True, "role": "admin", "username": "Chủ tiệm"})
                st.rerun()
            else:
                success, name = check_login(user, password)
                if success:
                    st.session_state.update({"logged_in": True, "role": "staff", "username": name})
                    st.rerun()
                else: st.error("Thông tin chưa đúng ní ơi!")

# --- 6. GIAO DIỆN CHÍNH ---
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
        c1, c2 = st.columns(2)
        with c1:
            nguoi_lam = st.text_input("Người thực hiện", value=st.session_state["username"], disabled=True)
            san_pham = st.selectbox("Dịch vụ", danh_sach_sp)
            diem = st.select_slider("Đánh giá", options=[f"{i}/10" for i in range(1, 11)], value="9/10")
        with c2:
            ngay = st.date_input("Ngày", datetime.now())
            sl = st.number_input("Số lượng", min_value=0.0, step=1.0, format="%.0f")
            note = st.text_input("Ghi chú", value="Thực hiện tại tiệm.")

    # Kiểm tra trùng (Rút gọn)
    btn_off, confirm_on = False, False
    try:
        data = sheet_bc.get_all_values()
        count = 0
        for r in reversed(data):
            if r[1] == nguoi_lam and r[2] == san_pham and float(str(r[3]).replace(',','.')) == sl: count += 1
            else: break
        if count >= 1: confirm_on = True
    except: pass

    check = st.checkbox("Xác nhận dữ liệu đúng") if confirm_on else False
    if st.button("🚀 LƯU VÀO SỔ CÁI", type="primary", use_container_width=True, disabled=(confirm_on and not check)):
        if sl > 0:
            with st.status("Đang đồng bộ..."):
                sl_rx = sl if "Nhớt" not in san_pham else 0
                sl_tn = sl if "Nhớt" in san_pham else 0
                gio = datetime.now().strftime("%H:%M:%S")
                row = [ngay.strftime("%d/%m/%Y"), nguoi_lam, san_pham, sl_rx, sl_tn, diem, note, gio]
                if safe_append_row(sheet_bc, row):
                    st.success("Xong!"); st.balloons(); time.sleep(1); st.rerun()

    if st.session_state["role"] == "admin":
        st.divider(); st.subheader("📊 BÁO CÁO")
        try: st.dataframe(pd.DataFrame(sheet_bc.get_all_records()).tail(10))
        except: st.info("Chờ xíu...")

if not st.session_state["logged_in"]: login_screen()
else: main_app()
    
