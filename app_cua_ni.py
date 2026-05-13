import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime, timedelta
import time

# --- 1. CẤU HÌNH ---
st.set_page_config(page_title="Hệ Thống Lab 2026", layout="centered", page_icon="🧪")
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;} .stAppDeployButton {display:none;}</style>", unsafe_allow_html=True)

# --- 2. KẾT NỐI GOOGLE SHEETS ---
def get_gspread_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["connections"]["gsheets"], scopes=scope)
    return gspread.authorize(creds)

# --- 3. HÀM LẤY DANH MỤC TỪ ẢNH 1778687852043.jpg ---
def get_product_list():
    try:
        client = get_gspread_client()
        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        sheet_dm = sh.worksheet("DanhMuc")
        products = sheet_dm.col_values(1)[1:] # Lấy từ dòng 2 trở xuống
        return [p.strip() for p in products if p.strip()]
    except:
        return ["Rửa Xe Tay Ga", "Rửa Xe Số", "Thay Nhớt"] # Dự phòng nếu lỗi

# --- 4. KIỂM TRA ĐĂNG NHẬP ---
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
    except: return False, None

# --- 5. ĐIỀU HƯỚNG ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["role"] = None

def login_screen():
    st.markdown("<h1 style='text-align: center;'>🔐 QUẢN LÝ LAB 2026</h1>", unsafe_allow_html=True)
    with st.form("login_form"):
        user = st.text_input("Tên đăng nhập (SĐT)")
        password = st.text_input("Mật khẩu", type="password")
        if st.form_submit_button("XÁC NHẬN", use_container_width=True):
            if user == "admin" and password == "2026": 
                st.session_state["logged_in"] = True; st.session_state["role"] = "admin"; st.session_state["username"] = "Chủ tiệm"; st.rerun()
            else:
                success, full_name = check_login(user, password)
                if success: st.session_state["logged_in"] = True; st.session_state["role"] = "staff"; st.session_state["username"] = full_name; st.rerun()
                else: st.error("Sai thông tin rồi ní!")

# --- 6. GIAO DIỆN CHÍNH ---
def main_app():
    client = get_gspread_client()
    sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
    sheet_bc = sh.worksheet("BaoCao")

    with st.sidebar:
        st.success(f"🟢 {st.session_state['username']}")
        if st.button("ĐĂNG XUẤT"): st.session_state["logged_in"] = False; st.rerun()

    st.title("🧪 QUẢN LÝ DỊCH VỤ")
    danh_sach_sp = get_product_list()

    with st.expander("🚀 NHẬP MẺ MỚI / DỊCH VỤ", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            nguoi_lam = st.text_input("Người thực hiện", value=st.session_state["username"], disabled=True)
            san_pham = st.selectbox("Dịch vụ / Sản phẩm", danh_sach_sp)
            diem_so = st.select_slider("Đánh giá", options=[f"{i}/10" for i in range(1, 11)], value="9/10")
        with col2:
            ngay = st.date_input("Ngày thực hiện", datetime.now())
            so_luong = st.number_input("Số lượng (Lần/Lít)", min_value=0.0, step=1.0, format="%.0f")
            ghi_chu = st.text_input("Ghi chú", value="Thực hiện tại tiệm.")

    # --- CHỐNG TRÙNG LẶP ---
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
            if count_dup == 1:
                if diff < 60: btn_disabled = True; st.warning(f"⚠️ Đợi {60-int(diff)}s...")
                else: show_confirm = True
            elif count_dup == 2:
                if diff < 300: btn_disabled = True; st.warning(f"⚠️ Đợi {5-int(diff/60)}p...")
                else: st.error("❗ XÁC NHẬN LẦN 3?"); show_confirm = True
            elif count_dup >= 3:
                btn_disabled = True; st.error("🚫 Hết quyền nhập. LH: 0978666620")
    except: pass

    confirm_check = st.checkbox("Xác nhận dữ liệu đúng") if show_confirm else False
    final_disabled = btn_disabled or (show_confirm and not confirm_check)

    if st.button("🚀 LƯU VÀO SỔ CÁI", type="primary", use_container_width=True, disabled=final_disabled):
        if so_luong > 0:
            try:
                # Logic phân loại tự động vào các cột Rửa xe / Thay nhớt
                sl_rua_xe = so_luong if "Nhớt" not in san_pham else 0
                sl_thay_nhot = so_luong if "Nhớt" in san_pham else 0
                
                gio_luu = datetime.now().strftime("%H:%M:%S")
                new_row = [ngay.strftime("%d/%m/%Y"), nguoi_lam, san_pham, sl_rua_xe, sl_thay_nhot, diem_so, ghi_chu, gio_luu]
                sheet_bc.append_row(new_row)
                st.success("Đã lưu thành công!"); st.balloons(); time.sleep(1); st.rerun()
            except Exception as e: st.error(f"Lỗi: {e}")

    if st.session_state["role"] == "admin":
        st.divider(); st.subheader("📊 BÁO CÁO TỔNG HỢP")
        try: df = pd.DataFrame(sheet_bc.get_all_records()); st.dataframe(df.tail(15))
        except: st.info("Đang tải...")

if not st.session_state["logged_in"]: login_screen()
else: main_app()
            
