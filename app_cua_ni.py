import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import pytz
import hashlib
import time

# ==========================================
# GIAO DIỆN CHUẨN SALON KIM HIỀN - NGUYÊN BẢN
# ==========================================
st.set_page_config(page_title="SALON KIM HIỀN", layout="centered", page_icon="✂️")

st.markdown("""
    <style>
        header, footer, .stAppDeployButton {display: none !important; visibility: hidden !important;}
        [data-testid="stStatusWidget"], [data-testid="stToolbar"] {display: none !important;}
        
        /* Khung bảng hiệu giữ nguyên như hình 1778774656136.jpg */
        .bang-hieu-kim-hien {
            text-align: center;
            background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
            color: white; padding: 25px; border-radius: 20px;
            margin-bottom: 20px; box-shadow: 0px 10px 30px rgba(0,0,0,0.3);
            border: 1px solid #ffffff20;
        }
        .logo-tron { width: 100px; height: 100px; object-fit: cover; border-radius: 50%; border: 3px solid #f1c40f; margin-bottom: 10px; background: #000; }
        .ten-tiem { font-size: 28px; font-weight: 800; color: #ffffff; text-transform: uppercase; margin-bottom: 5px; }
        .thong-tin-phu { font-size: 15px; color: #ecf0f1; opacity: 0.9; margin-bottom: 2px; }
        .sdt-tiem { font-size: 18px; color: #f1c40f; font-weight: 700; margin-top: 5px; }
        .slogan { font-size: 15px; color: #f1c40f; font-weight: 500; font-style: italic; margin-top: 10px; border-top: 1px solid #ffffff30; padding-top: 10px; }

        /* CÂN GIỮA CÁC TAB */
        .stTabs [data-baseweb="tab-list"] { display: flex; justify-content: center; gap: 10px; width: 100%; }
        .stTabs [data-baseweb="tab"] { flex: 1; height: 50px; background-color: #ffffff; border-radius: 10px 10px 0 0; max-width: 150px; }
        .stTabs [data-baseweb="tab"] p { color: #000000 !important; font-weight: 700 !important; text-align: center; width: 100%; }
        .stTabs [data-baseweb="tab"][aria-selected="true"] { background-color: #f1c40f !important; }
    </style>
    """, unsafe_allow_html=True)

# --- HÀM HỆ THỐNG ---
def hash_password(password): 
    return hashlib.sha256(str(password).strip().encode()).hexdigest()

def get_now_vn(): 
    return datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))

def format_drive_link(link):
    if not link or not isinstance(link, str): return ""
    if 'drive.google.com' in link:
        file_id = ""
        if 'file/d/' in link: file_id = link.split('file/d/')[1].split('/')[0]
        elif 'id=' in link: file_id = link.split('id=')[1].split('&')[0]
        if file_id: return f'https://lh3.googleusercontent.com/d/{file_id}'
    return link

def get_gspread_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["connections"]["gsheets"], scopes=scope)
    return gspread.authorize(creds)

@st.cache_data(ttl=60)
def get_settings():
    try:
        client = get_gspread_client()
        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        return {row[0]: row[1] for row in sh.worksheet("ThietLap").get_all_values() if len(row) > 1}
    except: return {"TenTiem": "SALON KIM HIỀN"}

def display_header(settings):
    logo_url = format_drive_link(settings.get('Logo', ''))
    st.markdown(f"""
        <div class="bang-hieu-kim-hien">
            <img src="{logo_url}" class="logo-tron">
            <div class="ten-tiem">{settings.get('TenTiem', 'SALON KIM HIỀN')}</div>
            <div class="thong-tin-phu">📍 131, TRẦN BÌNH TRỌNG, MỸ XUYÊN, LONG XUYÊN, AN GIANG</div>
            <div class="sdt-tiem">📞 0978.888.888</div>
            <div class="slogan">"Nơi Bạn Đặt Niềm Tin"</div>
        </div>
    """, unsafe_allow_html=True)

def main():
    settings = get_settings()
    if "is_saving" not in st.session_state: st.session_state.is_saving = False
    if "logged_in" not in st.session_state: st.session_state.update({"logged_in": False, "role": None})

    if not st.session_state["logged_in"]:
        display_header(settings)
        with st.form("login_form"):
            u = st.text_input("Tài khoản")
            p = st.text_input("Mật khẩu", type="password")
            if st.form_submit_button("ĐĂNG NHẬP", use_container_width=True):
                if u == "admin" and p == "2026":
                    st.session_state.update({"logged_in": True, "role": "Admin", "full_name": "Chủ Tiệm", "phone": "0978888888"})
                    st.rerun()
                # Thêm logic check nhân viên từ Admin sheet tại đây
                st.error("Sai thông tin!")
    else:
        display_header(settings)
        tabs = st.tabs(["📝 NHẬP LIỆU", "📈 BÁO CÁO", "⚙️ CÀI ĐẶT"] if st.session_state["role"] == "Admin" else ["📝 NHẬP LIỆU"])

        with tabs[0]:
            st.info(f"👷 Nhân viên: {st.session_state.get('full_name')} | {st.session_state.get('phone')}")
            # ... (Các trường nhập liệu giữ nguyên)

            # CHỐNG TRÙNG ĐƠN TUYỆT ĐỐI
            if st.session_state.is_saving:
                st.warning("⚠️ ĐANG LƯU ĐƠN, VUI LÒNG ĐỢI...")
                st.button("🚀 ĐANG XỬ LÝ...", disabled=True, use_container_width=True)
                # Logic ghi vào gspread tại đây...
                time.sleep(2)
                st.session_state.is_processing = False
                st.rerun()
            else:
                if st.button("🚀 XÁC NHẬN LƯU ĐƠN", use_container_width=True, type="primary"):
                    st.session_state.is_saving = True
                    st.rerun()

if __name__ == "__main__":
    main()
    
