import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import time
import pytz
import hashlib

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN LKTV DETAILING
# ==========================================
st.set_page_config(page_title="LKTV DETAILING - 2026", layout="centered", page_icon="🧼")

st.markdown("""
    <style>
        header, footer, .stAppDeployButton {display: none !important; visibility: hidden !important;}
        .bang-hieu-lktv {
            text-align: center;
            background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
            color: white; padding: 25px; border-radius: 20px;
            margin-bottom: 20px; box-shadow: 0px 10px 30px rgba(0,0,0,0.3);
            border: 1px solid #ffffff20;
        }
        .logo-img { 
            width: 100px; height: 100px; object-fit: cover; 
            border-radius: 50%; border: 3px solid #f1c40f; 
            margin-bottom: 10px; background: #000; 
        }
        .ten-tiem { font-size: 26px; font-weight: 800; color: #ffffff; text-transform: uppercase; }
        .slogan { font-size: 16px; color: #f1c40f; font-weight: 500; font-style: italic; }
    </style>
    """, unsafe_allow_html=True)

# --- HÀM BẢO MẬT & TIỆN ÍCH ---
def hash_password(password):
    return hashlib.sha256(str(password).strip().encode()).hexdigest()

def get_now_vn():
    return datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))

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
        return {"TenTiem": "LKTV DETAILING", "Logo": "", "Diachi": "LONG XUYÊN", "Slogan": "Nơi Đặt Niềm Tin.."}

def get_all_users():
    try:
        client = get_gspread_client()
        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        ws = sh.worksheet("Admin")
        return ws.get_all_records()
    except:
        return []

# ==========================================
# 3. GIAO DIỆN HIỂN THỊ
# ==========================================
def display_header(settings):
    st.markdown(f"""
        <div class="bang-hieu-lktv">
            <div class="ten-tiem">{settings.get('TenTiem', 'LKTV DETAILING')}</div>
            <div class="thong-tin-phu">📍 {settings.get('Diachi', 'LONG XUYÊN')}</div>
            <div class="slogan">{settings.get('Slogan', 'Nơi Đặt Niềm Tin..')}</div>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 4. LOGIC ĐĂNG NHẬP & PHÂN QUYỀN
# ==========================================
def main():
    settings = get_settings()
    
    if "logged_in" not in st.session_state:
        st.session_state.update({"logged_in": False, "role": None, "user": None})

    if not st.session_state["logged_in"]:
        display_header(settings)
        with st.form("login_form"):
            st.markdown("### 🔐 XÁC THỰC NGƯỜI DÙNG")
            u_input = st.text_input("Tên đăng nhập / SĐT").strip()
            p_input = st.text_input("Mật khẩu", type="password").strip()
            
            if st.form_submit_button("VÀO NHÀ", use_container_width=True):
                # A. CỬA DỰ PHÒNG CHO NÍ (DÙNG KHI SHEET LỖI)
                if u_input == "admin" and p_input == "2026":
                    st.session_state.update({"logged_in": True, "role": "Admin", "user": "Chủ Tiệm (Dự phòng)"})
                    st.rerun()

                # B. KIỂM TRA TRÊN GOOGLE SHEETS (DÀNH CHO NHÂN VIÊN)
                users = get_all_users()
                found = False
                p_hashed = hash_password(p_input)
                
                for row in users:
                    db_user = str(row.get('Tài khoản', '')).strip()
                    db_pass = str(row.get('Mật khẩu', '')).strip()
                    db_role = row.get('Quyền', 'Nhân viên')
                    
                    if u_input == db_user and p_hashed == db_pass:
                        st.session_state.update({
                            "logged_in": True, 
                            "role": db_role,
                            "user": u_input
                        })
                        found = True
                        st.rerun()
                
                if not found:
                    st.error("Chìa khóa sai rồi ní ơi! Kiểm tra lại mật khẩu hoặc liên hệ Admin.")
    else:
        # --- GIAO DIỆN SAU KHI VÀO NHÀ ---
        display_header(settings)
        
        if st.session_state["role"] == "Admin":
            tabs = st.tabs(["📝 NHẬP LIỆU", "📈 BÁO CÁO", "⚙️ CÀI ĐẶT"])
        else:
            tabs = st.tabs(["📝 NHẬP LIỆU"])

        with tabs[0]:
            st.info(f"👤 Chào {st.session_state['user']} ({st.session_state['role']})")
            st.write("Mời ní/nhân viên nhập dữ liệu vào đây...")
            # (Phần code form nhập liệu ní dán tiếp vào đây nhé)
            
            if st.button("🚪 ĐĂNG XUẤT", use_container_width=True):
                st.session_state.update({"logged_in": False, "role": None, "user": None})
                st.rerun()

        if st.session_state["role"] == "Admin":
            with tabs[-1]:
                st.subheader("🛡️ QUẢN TRỊ MẬT MÃ")
                mk_moi = st.text_input("Tạo mã SHA-256 cho pass mới:", type="password")
                if mk_moi:
                    st.code(hash_password(mk_moi))
                    st.caption("Copy dòng này dán vào cột B (Mật khẩu) trong sheet Admin.")

if __name__ == "__main__":
    main()
    
