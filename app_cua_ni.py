import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import time
import pytz 

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN (UI/UX CHUẨN DETAILING)
# ==========================================
st.set_page_config(page_title="LKTV DETAILING - 2026", layout="centered", page_icon="🧼")

st.markdown("""
    <style>
        header, footer, .stAppDeployButton {display: none !important; visibility: hidden !important;}
        [data-testid="stStatusWidget"], [data-testid="stToolbar"] {display: none !important;}
        #MainMenu {visibility: hidden !important;}
        .main .block-container { padding-top: 1rem !important; padding-bottom: 250px !important; }
        
        /* BẢNG HIỆU LKTV CHUYÊN NGHIỆP */
        .bang-hieu-lktv {
            text-align: center;
            background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
            color: white;
            padding: 25px;
            border-radius: 20px;
            margin-bottom: 20px;
            box-shadow: 0px 10px 30px rgba(0,0,0,0.3);
            border: 1px solid #ffffff20;
        }
        .logo-img { width: 100px; height: 100px; object-fit: cover; border-radius: 50%; border: 3px solid #f1c40f; margin-bottom: 10px; }
        .ten-tiem { font-size: 26px; font-weight: 800; color: #ffffff; letter-spacing: 1px; text-transform: uppercase; }
        .thong-tin-phu { font-size: 14px; opacity: 0.8; margin-top: 5px; }
        .slogan { font-size: 16px; color: #f1c40f; font-weight: 500; margin-top: 10px; font-style: italic; }
    </style>
    """, unsafe_allow_html=True)

# --- HÀM CHUYỂN ĐỔI LINK GOOGLE DRIVE ---
def format_drive_link(link):
    if 'drive.google.com' in link:
        if 'file/d/' in link:
            file_id = link.split('file/d/')[1].split('/')[0]
            return f'https://drive.google.com/uc?id={file_id}'
    return link

# ==========================================
# 2. KẾT NỐI DỮ LIỆU
# ==========================================
def get_gspread_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["connections"]["gsheets"], scopes=scope)
    return gspread.authorize(creds)

def get_settings():
    try:
        client = get_gspread_client()
        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        ws = sh.worksheet("ThietLap")
        records = ws.get_all_values()
        # Chuyển dữ liệu từ Sheet thành Dictionary (Cột A là Key, Cột B là Value)
        return {row[0]: row[1] for row in records if len(row) > 1}
    except Exception as e:
        return {"TenTiem": "LKTV DETAILING", "Logo": "", "Diachi": "LONG XUYÊN", "SDT": "0978888888", "Slogan": "Nơi Đặt Niềm Tin.."}

# ==========================================
# 3. GIAO DIỆN BẢNG HIỆU
# ==========================================
def display_header(settings):
    logo_url = format_drive_link(settings.get('Logo', ''))
    
    with st.container():
        st.markdown(f"""
            <div class="bang-hieu-lktv">
                <img src="{logo_url}" class="logo-img" onerror="this.style.display='none'">
                <div class="ten-tiem">{settings.get('TenTiem', 'LKTV DETAILING')}</div>
                <div class="thong-tin-phu">
                    📍 {settings.get('Diachi', 'LONG XUYÊN, AN GIANG')} <br>
                    📞 {settings.get('SDT', '0978888888')}
                </div>
                <div class="slogan">{settings.get('Slogan', 'Nơi Đặt Niềm Tin..')}</div>
            </div>
        """, unsafe_allow_html=True)

# ==========================================
# 4. LUỒNG CHÍNH CỦA APP
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.update({"logged_in": False, "role": None, "username": None, "login_time": None})

# (Giữ nguyên logic Login và Main App từ các bản trước...)

def main():
    settings = get_settings()
    
    if not st.session_state["logged_in"]:
        # MÀN HÌNH ĐĂNG NHẬP
        display_header(settings)
        with st.form("login"):
            u = st.text_input("Tên đăng nhập")
            p = st.text_input("Mật khẩu", type="password")
            if st.form_submit_button("VÀO NHÀ", use_container_width=True):
                if u == "admin" and p == "2026":
                    st.session_state.update({"logged_in": True, "role": "admin", "username": "Ní Chủ", "login_time": time.time()})
                    st.rerun()
                else: st.error("Sai chìa khóa!")
    else:
        # GIAO DIỆN CHÍNH
        display_header(settings)
        st.success(f"Chào ní: {st.session_state['username']}")
        
        # Phần nhập liệu hằng ngày của ní nằm ở đây...
        
        if st.button("🚪 THOÁT"):
            st.session_state["logged_in"] = False
            st.rerun()

if __name__ == "__main__":
    main()
    
