import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime, timedelta
import time

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

def login_screen():
    st.markdown("<h1 style='text-align: center;'>🔐 QUẢN LÝ LAB 2026</h1>", unsafe_allow_html=True)
    with st.form("login_form"):
        user = st.text_input("Tên đăng nhập / SĐT")
        password = st.text_input("Mật khẩu", type="password")
        if st.form_submit_button("XÁC NHẬN", use_container_width=True):
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
            else: st.error("Sai thông tin rồi ní!")

# --- 4. GIAO DIỆN CHÍNH ---
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

    # --- HỆ THỐNG KIỂM SOÁT TRÙNG LẶP ĐA TẦNG ---
    btn_disabled = False
    warning_msg = ""
    show_confirm = False
    count_dup = 0
    
    try:
        client = get_gspread_client()
        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        sheet = sh.worksheet("BaoCao")
        all_vals = sheet.get_all_values()
        
        # Đếm số lần trùng lặp liên tiếp từ dưới lên
        for row in reversed(all_vals):
            if row[1] == nguoi_lam and row[2] == san_pham and float(str(row[3]).replace(',','.')) == so_luong:
                count_dup += 1
            else:
                break
        
        if count_dup >= 1:
            last_time_str = all_vals[-1][7]
            last_time_dt = datetime.strptime(f"{all_vals[-1][0]} {last_time_str}", "%d/%m/%Y %H:%M:%S")
            diff_sec = (datetime.now() - last_time_dt).total_seconds()

            if count_dup == 1:
                # Lần 2 (trùng 1 lần trước đó): Cách 1 phút, cần xác nhận
                if diff_sec < 60:
                    btn_disabled = True
                    warning_msg = f"⚠️ Ní vừa lưu mẻ này. Đợi {60 - int(diff_sec)} giây để nhập mẻ tiếp theo."
                else:
                    show_confirm = True
            
            elif count_dup == 2:
                # Lần 3 (trùng 2 lần trước đó): Cách 5 phút, xác nhận đanh thép
                if diff_sec < 300:
                    btn_disabled = True
                    warning_msg = f"⚠️ Đã trùng 2 lần! Vui lòng đợi {5 - int(diff_sec/60)} phút để nhập tiếp mẻ thứ 3."
                else:
                    st.error("❗ ĐÂY LÀ LẦN THỨ 3 BẠN NHẬP TRÙNG DỮ LIỆU, BẠN CÓ CHẮC CHẮN ĐÂY LÀ ĐÚNG CHỨ?")
                    show_confirm = True

            elif count_dup >= 3:
                # Lần 4 trở đi: Khóa hoàn toàn
                btn_disabled = True
                st.error("🚫 Bạn hết quyền nhập liệu vì đã nhập 3 lần liên tiếp, hãy liên hệ ngay với chủ tiệm qua số 0978666620 để giải quyết.")
    except: pass

    if warning_msg: st.warning(warning_msg)
    
    confirm_check = False
    if show_confirm:
        confirm_check = st.checkbox("Tôi xác nhận dữ liệu này là hoàn toàn chính xác.")

    # Điều kiện để nút Lưu hoạt động
    final_disabled = btn_disabled or (show_confirm and not confirm_check)

    if st.button("🚀 LƯU VÀO SỔ CÁI", type="primary", use_container_width=True, disabled=final_disabled):
        if so_luong <= 0:
            st.warning("Số lượng phải lớn hơn 0!")
        else:
            try:
                sl_rua_xe = so_luong if "Tẩy Nhôm" not in san_pham else 0
                sl_tay_nhom = so_luong if "Tẩy Nhôm" in san_pham else 0
                gio_luu = datetime.now().strftime("%H:%M:%S")
                new_row = [ngay.strftime("%d/%m/%Y"), nguoi_lam, san_pham, sl_rua_xe, sl_tay_nhom, diem_so, ghi_chu, gio_luu]
                sheet.append_row(new_row)
                st.success("Đã lưu thành công!")
                st.balloons()
                time.sleep(1)
                st.rerun() 
            except Exception as e: st.error(f"Lỗi: {e}")

    # --- BÁO CÁO CHO CHỦ ---
    if st.session_state["role"] == "admin":
        st.divider()
        st.subheader("📊 BÁO CÁO TỔNG HỢP")
        try:
            df = pd.DataFrame(sheet.get_all_records())
            st.dataframe(df.tail(15))
        except: st.info("Đang tải...")

if not st.session_state["logged_in"]:
    login_screen()
else:
    main_app()
                    
