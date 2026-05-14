import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import time
import pytz
import hashlib

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN & BẢO MẬT
# ==========================================
st.set_page_config(page_title="LKTV DETAILING - 2026", layout="centered", page_icon="🧼")

st.markdown("""
    <style>
        header, footer, .stAppDeployButton {display: none !important; visibility: hidden !important;}
        [data-testid="stStatusWidget"], [data-testid="stToolbar"] {display: none !important;}
        #MainMenu {visibility: hidden !important;}
        .main .block-container { padding-top: 1rem !important; padding-bottom: 100px !important; }
        
        .bang-hieu-lktv {
            text-align: center;
            background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
            color: white; padding: 25px; border-radius: 20px;
            margin-bottom: 20px; box-shadow: 0px 10px 30px rgba(0,0,0,0.3);
            border: 1px solid #ffffff20;
        }
        .logo-img { width: 100px; height: 100px; object-fit: cover; border-radius: 50%; border: 3px solid #f1c40f; margin-bottom: 10px; background: #000; }
        .ten-tiem { font-size: 26px; font-weight: 800; color: #ffffff; text-transform: uppercase; }
        .slogan { font-size: 16px; color: #f1c40f; font-weight: 500; font-style: italic; }
    </style>
    """, unsafe_allow_html=True)

# --- HÀM MÃ HÓA SHA-256 ---
def hash_password(password):
    return hashlib.sha256(str(password).encode()).hexdigest()

# --- XỬ LÝ LINK DRIVE ---
def format_drive_link(link):
    if not link or not isinstance(link, str): return ""
    if 'drive.google.com' in link:
        file_id = ""
        if 'file/d/' in link: file_id = link.split('file/d/')[1].split('/')[0]
        elif 'id=' in link: file_id = link.split('id=')[1].split('&')[0]
        if file_id: return f'https://lh3.googleusercontent.com/d/{file_id}'
    return link

# ==========================================
# 2. KẾT NỐI GOOGLE SHEETS
# ==========================================
def get_gspread_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["connections"]["gsheets"], scopes=scope)
    return gspread.authorize(creds)

@st.cache_data(ttl=60)
def get_settings():
    try:
        client = get_gspread_client()
        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        ws = sh.worksheet("ThietLap")
        records = ws.get_all_values()
        return {row[0]: row[1] for row in records if len(row) > 1}
    except:
        return {"TenTiem": "LKTV DETAILING", "Logo": "", "Diachi": "LONG XUYÊN", "SDT": "0978888888", "Slogan": "Nơi Đặt Niềm Tin.."}

def get_admin_creds():
    try:
        client = get_gspread_client()
        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        ws = sh.worksheet("Admin")
        data = ws.get_all_records()
        if data:
            return str(data[0]['Tài khoản']), str(data[0]['Mật khẩu'])
    except:
        # Dự phòng mặc định (admin/2026) nếu chưa có sheet Admin
        return "admin", "8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92"

def get_service_data():
    try:
        client = get_gspread_client()
        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        worksheet = sh.worksheet("DanhMuc")
        records = worksheet.get_all_records()
        return {r['Tên Sản Phẩm']: float(str(r['Đơn Giá']).replace(',','')) for r in records if r['Tên Sản Phẩm']}
    except: return {"Lỗi kết nối": 0}

# ==========================================
# 3. GIAO DIỆN CHÍNH
# ==========================================
def display_header(settings):
    logo_url = format_drive_link(settings.get('Logo', ''))
    st.markdown(f"""
        <div class="bang-hieu-lktv">
            <img src="{logo_url}" class="logo-img">
            <div class="ten-tiem">{settings.get('TenTiem', 'LKTV DETAILING')}</div>
            <div class="thong-tin-phu">📍 {settings.get('Diachi', 'LONG XUYÊN')} | 📞 {settings.get('SDT', '')}</div>
            <div class="slogan">{settings.get('Slogan', '')}</div>
        </div>
    """, unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.update({"logged_in": False})

def main():
    settings = get_settings()
    
    if not st.session_state["logged_in"]:
        display_header(settings)
        with st.form("login_form"):
            st.markdown("### 🔐 XÁC THỰC CHỦ TIỆM")
            u_input = st.text_input("Tên đăng nhập")
            p_input = st.text_input("Mật khẩu", type="password")
            if st.form_submit_button("VÀO NHÀ", use_container_width=True):
                real_user, hashed_pass = get_admin_creds()
                if u_input == real_user and hash_password(p_input) == hashed_pass:
                    st.session_state["logged_in"] = True
                    st.rerun()
                else:
                    st.error("Chìa khóa sai rồi ní ơi!")
    else:
        display_header(settings)
        tab1, tab2 = st.tabs(["📝 NHẬP LIỆU", "⚙️ BẢO MẬT"])
        
        with tab1:
            # (Giữ nguyên phần form nhập liệu cũ của ní ở đây)
            st.success("Chào ní! Chúc tiệm hôm nay bùng nổ doanh số.")
            if st.button("🚪 ĐĂNG XUẤT", use_container_width=True):
                st.session_state["logged_in"] = False
                st.rerun()

        with tab2:
            st.subheader("🛡️ Công cụ đổi mật khẩu")
            st.info("Nhập pass mới vào đây, rồi copy mã nhận được dán vào Sheet Admin.")
            new_pass = st.text_input("Nhập mật khẩu mới muốn đặt", type="password")
            if new_pass:
                ma_moi = hash_password(new_pass)
                st.code(ma_moi, language="text")
                st.warning("Ní copy dãy trên dán vào ô B2 trong sheet Admin nhé!")

if __name__ == "__main__":
    main()
            
