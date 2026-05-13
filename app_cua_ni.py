import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime, timedelta
import time

# --- 1. CẤU HÌNH GIAO DIỆN ---
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

# --- 3. HÀM KIỂM TRA ĐĂNG NHẬP TỪ SHEETS ---
def check_login(user_input, pass_input):
    try:
        client = get_gspread_client()
        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        sheet_nv = sh.worksheet("NhanVien")
        data_nv = sheet_nv.get_all_records()
        
        for row in data_nv:
            # So khớp SĐT và Mật khẩu (ép về kiểu chuỗi để tránh lỗi định dạng số)
            if str(row['Số Điện Thoại (Login)']).strip() == str(user_input).strip() and \
               str(row['Mật Khẩu']).strip() == str(pass_input).strip():
                return True, row['Tên Nhân Viên']
        return False, None
    except Exception as e:
        return False, None

# --- 4. KHỞI TẠO TRẠNG THÁI ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["role"] = None

# --- 5. MÀN HÌNH ĐĂNG NHẬP ---
def login_screen():
    st.markdown("<h1 style='text-align: center;'>🔐 QUẢN LÝ LAB 2026</h1>", unsafe_allow_html=True)
    with st.form("login_form"):
        user = st.text_input("Tên đăng nhập (SĐT)")
        password = st.text_input("Mật khẩu", type="password")
        submit = st.form_submit_button("XÁC NHẬN", use_container_width=True)
        if submit:
            # Quyền Admin cố định
            if user == "admin" and password == "2026": 
                st.session_state["logged_in"] = True
                st.session_state["username"] = "Chủ tiệm"
                st.session_state["role"] = "admin"
                st.rerun()
            # Quyền Nhân viên check từ Sheets
            else:
                success, full_name = check_login(user, password)
                if success:
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = full_name
                    st.session_state["role"] = "staff"
                    st.rerun()
                else:
                    st.error("SĐT hoặc Mật khẩu không đúng rồi ní!")

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

    # --- LOGIC CHỐNG GIAN DỐI 4 TẦNG ---
    btn_disabled = False
    warning_msg = ""
    show_confirm = False
    count_dup = 0
    
    try:
        all_vals = sheet_bc.get_all_values()
        for row in reversed(all_vals):
            if row[1] == nguoi_lam and row[2] == san_pham and float(str(row[3]).replace(',','.')) == so_luong:
                count_dup += 1
            else: break
        
        if count_dup >= 1:
            last_time_dt = datetime.strptime(f"{all_vals[-1][0]} {all_vals[-1][7]}", "%d/%m/%Y %H:%M:%S")
            diff_sec = (datetime.now() - last_time_dt).total_seconds()

            if count_dup == 1:
                if diff_sec < 60: 
                    btn_disabled = True
                    warning_msg = f"⚠️ Đợi {60 - int(diff_sec)} giây để nhập mẻ tiếp theo."
                else: show_confirm = True
            elif count_dup == 2:
                if diff_sec < 300: 
                    btn_disabled = True
                    warning_msg = f"⚠️ Đã trùng 2 lần! Đợi {5 - int(diff_sec/60)} phút."
                else: 
                    st.error("❗ ĐÂY LÀ LẦN THỨ 3 BẠN NHẬP TRÙNG, BẠN CHẮC CHẮN CHỨ?")
                    show_confirm = True
            elif count_dup >= 3:
                btn_disabled = True
                st.error("🚫 Bạn hết quyền nhập liệu. LH chủ tiệm: 0978666620")
    except: pass

    if warning_msg: st.warning(warning_msg)
    confirm_check = st.checkbox("Xác nhận dữ liệu chính xác") if show_confirm else False
    final_disabled = btn_disabled or (show_confirm and not confirm_check)

    if st.button("🚀 LƯU VÀO SỔ CÁI", type="primary", use_container_width=True, disabled=final_disabled):
        if so_luong > 0:
            try:
                sl_rua_xe = so_luong if "Tẩy Nhôm" not in san_pham else 0
                sl_tay_nhom = so_luong if "Tẩy Nhôm" in san_pham else 0
                gio_luu = datetime.now().strftime("%H:%M:%S")
                new_row = [ngay.strftime("%d/%m/%Y"), nguoi_lam, san_pham, sl_rua_xe, sl_tay_nhom, diem_so, ghi_chu, gio_luu]
                sheet_bc.append_row(new_row)
                st.success("Đã lưu thành công!"); st.balloons(); time.sleep(1); st.rerun() 
            except Exception as e: st.error(f"Lỗi: {e}")

    # --- CHỈ CHỦ MỚI THẤY BÁO CÁO ---
    if st.session_state["role"] == "admin":
        st.divider(); st.subheader("📊 BÁO CÁO TỔNG HỢP (Chỉ dành cho Chủ)")
        try:
            df = pd.DataFrame(sheet_bc.get_all_records())
            st.dataframe(df.tail(15))
        except: st.info("Đang tải dữ liệu...")

# --- ĐIỀU HƯỚNG ---
if not st.session_state["logged_in"]:
    login_screen()
else:
    main_app()
                
