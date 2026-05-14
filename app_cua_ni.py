import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import time
import pytz 

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN & CSS (ẨN THANH THỪA)
# ==========================================
st.set_page_config(page_title="Hệ Thống Lab 2026", layout="centered", page_icon="🧪")

st.markdown("""
    <style>
        header, footer, .stAppDeployButton {display: none !important; visibility: hidden !important;}
        [data-testid="stStatusWidget"], [data-testid="stToolbar"] {display: none !important;}
        #MainMenu {visibility: hidden !important;}
        .stActionButton {display: none !important;}
        div[data-testid="stConnectionStatus"] {display: none !important;}
        .main .block-container { padding-top: 1rem !important; padding-bottom: 250px !important; }
        iframe[title="manage-app"], iframe { display: none !important; height: 0px !important; width: 0px !important; }
    </style>
    """, unsafe_allow_html=True)

def get_now_vn():
    tz = pytz.timezone('Asia/Ho_Chi_Minh')
    return datetime.now(tz)

# ==========================================
# 2. KẾT NỐI GOOGLE SHEETS
# ==========================================
def get_gspread_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["connections"]["gsheets"], scopes=scope)
    return gspread.authorize(creds)

# ==========================================
# 3. HÀM XỬ LÝ LOGIC DỮ LIỆU
# ==========================================
def get_service_data():
    try:
        client = get_gspread_client()
        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        worksheet = sh.worksheet("DanhMuc")
        records = worksheet.get_all_records()
        return {r['Tên Sản Phẩm']: float(str(r['Đơn Giá']).replace(',','')) for r in records if r['Tên Sản Phẩm']}
    except: return {"Lỗi kết nối": 0}

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

# ==========================================
# 4. QUẢN LÝ TRẠNG THÁI & AUTO LOGOUT (10 PHÚT)
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.update({"logged_in": False, "role": None, "username": None, "login_time": None, "logout_message": None})

if st.session_state["logged_in"] and st.session_state["login_time"]:
    if time.time() - st.session_state["login_time"] > 600:
        st.session_state.update({"logged_in": False, "logout_message": "Bạn đã bị mời ra khỏi nơi đây vì bạn đã ở lại quá lâu"})
        st.rerun()

# ==========================================
# 5. CỬA SỔ ĐĂNG NHẬP (HÀNG RÀO)
# ==========================================
def login_screen():
    st.markdown("<h2 style='text-align: center;'>🔐 ĐĂNG NHẬP HỆ THỐNG</h2>", unsafe_allow_html=True)
    if st.session_state["logout_message"]:
        st.warning(st.session_state["logout_message"])
        st.session_state["logout_message"] = None

    with st.form("login_form"):
        user = st.text_input("Tên đăng nhập (SĐT)")
        password = st.text_input("Mật khẩu", type="password")
        if st.form_submit_button("XÁC NHẬN ĐĂNG NHẬP", use_container_width=True):
            if user == "admin" and password == "2026":
                st.session_state.update({"logged_in": True, "role": "admin", "username": "Chủ tiệm", "login_time": time.time()})
                st.rerun()
            else:
                success, name = check_login(user, password)
                if success:
                    st.session_state.update({"logged_in": True, "role": "staff", "username": name, "login_time": time.time()})
                    st.rerun()
                else: st.error("😔 Sai thông tin rồi ní ơi!")

# ==========================================
# 6. GIAO DIỆN CHÍNH (BÊN TRONG NHÀ)
# ==========================================
def main_app():
    client = get_gspread_client()
    sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
    sheet_bc = sh.worksheet("BaoCao")
    service_dict = get_service_data()
    now_vn = get_now_vn()

    # --- PHẦN ADMIN (CHỦ THẤY) ---
    if st.session_state["role"] == "admin":
        st.title("📊 BÁO CÁO")
        df = pd.DataFrame(sheet_bc.get_all_records())
        if not df.empty:
            today_str = now_vn.strftime("%d/%m/%Y")
            df_today = df[df['Ngày'] == today_str]
            c1, c2 = st.columns(2)
            c1.metric("Khách hôm nay", len(df_today))
            c2.metric("Doanh thu", f"{df_today['Thành tiền'].sum():,.0f}đ")
        st.divider()

    # --- PHẦN NHẬP LIỆU (AI CŨNG THẤY) ---
    st.subheader("📝 LẬP HÓA ĐƠN MỚI")
    ten_kh = st.text_input("👤 Tên khách hàng", value="Khách vãng lai")
    sdt_kh = st.text_input("📞 SĐT khách hàng")
    san_pham = st.selectbox("🛠️ Chọn dịch vụ", list(service_dict.keys()))
    
    col_qty, col_price = st.columns(2)
    with col_qty:
        so_luong = st.number_input("🔢 Số lượng", min_value=1.0, value=1.0)
    with col_price:
        don_gia = service_dict.get(san_pham, 0)
        st.info(f"💰 Đơn giá: {don_gia:,.0f}đ")

    thanh_tien = don_gia * so_luong
    st.warning(f"🧾 THÀNH TIỀN: {thanh_tien:,.0f}đ")
    da_thanh_toan = st.number_input("💵 Tiền khách trả", min_value=0.0, value=float(thanh_tien))

    # --- NÚT XÁC NHẬN ---
    if st.button("🚀 XÁC NHẬN NHẬP LIỆU", type="primary", use_container_width=True):
        with st.status("🔄 Đang ghi sổ..."):
            row = [now_vn.strftime("%d/%m/%Y"), st.session_state["username"], ten_kh, sdt_kh, san_pham, so_luong, don_gia, thanh_tien, da_thanh_toan, now_vn.strftime("%H:%M:%S")]
            sheet_bc.append_row(row)
            st.session_state["login_time"] = time.time()
            st.success("Xong!"); st.balloons(); time.sleep(1); st.rerun()

    st.divider()
    
    # --- NÚT THOÁT APP: ĐƯA RA NGOÀI MẶT TIỀN CHO DỄ THẤY ---
    col_out, col_time = st.columns([1, 1])
    with col_out:
        if st.button("🚪 THOÁT APP", use_container_width=True):
            st.session_state["logged_in"] = False
            st.rerun()
    with col_time:
        remain = 600 - (time.time() - st.session_state["login_time"])
        st.write(f"⏱️ Còn: {int(remain//60)}p {int(remain%60)}s")

if not st.session_state["logged_in"]:
    login_screen()
else:
    main_app()
                                            
