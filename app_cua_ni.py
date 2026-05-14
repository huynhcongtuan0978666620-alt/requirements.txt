import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import time
import pytz
import hashlib

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN (UI/UX LKTV DETAILING)
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
        .logo-img { 
            width: 100px; height: 100px; object-fit: cover; 
            border-radius: 50%; border: 3px solid #f1c40f; 
            margin-bottom: 10px; background: #000; 
        }
        .ten-tiem { font-size: 26px; font-weight: 800; color: #ffffff; text-transform: uppercase; }
        .thong-tin-phu { font-size: 14px; opacity: 0.8; }
        .slogan { font-size: 16px; color: #f1c40f; font-weight: 500; font-style: italic; }
    </style>
    """, unsafe_allow_html=True)

# --- HÀM BẢO MẬT & TIỆN ÍCH ---
def hash_password(password):
    return hashlib.sha256(str(password).encode()).hexdigest()

def format_drive_link(link):
    if not link or not isinstance(link, str): return ""
    if 'drive.google.com' in link:
        file_id = ""
        if 'file/d/' in link: file_id = link.split('file/d/')[1].split('/')[0]
        elif 'id=' in link: file_id = link.split('id=')[1].split('&')[0]
        if file_id: return f'https://lh3.googleusercontent.com/d/{file_id}'
    return link

def get_now_vn():
    return datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))

# ==========================================
# 2. KẾT NỐI DỮ LIỆU GOOGLE SHEETS
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
        return {"TenTiem": "LKTV DETAILING", "Logo": "", "Diachi": "LONG XUYÊN"}

def get_all_users():
    try:
        client = get_gspread_client()
        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        ws = sh.worksheet("Admin")
        return ws.get_all_records()
    except:
        # Nếu lỗi sheet Admin, cho phép admin/2026 vào để xử lý
        return [{"Tài khoản": "admin", "Mật khẩu": "8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92", "Quyền": "Admin"}]

def get_service_data():
    try:
        client = get_gspread_client()
        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        ws = sh.worksheet("DanhMuc")
        return {r['Tên Sản Phẩm']: float(str(r['Đơn Giá']).replace(',','')) for r in ws.get_all_records() if r['Tên Sản Phẩm']}
    except: return {"Rửa xe": 50000}

# ==========================================
# 3. GIAO DIỆN HIỂN THỊ
# ==========================================
def display_header(settings):
    logo_url = format_drive_link(settings.get('Logo', ''))
    st.markdown(f"""
        <div class="bang-hieu-lktv">
            <img src="{logo_url}" class="logo-img">
            <div class="ten-tiem">{settings.get('TenTiem', 'LKTV DETAILING')}</div>
            <div class="thong-tin-phu">📍 {settings.get('Diachi', 'LONG XUYÊN')} | 📞 {settings.get('SDT', '')}</div>
            <div class="slogan">{settings.get('Slogan', 'Nơi Đặt Niềm Tin..')}</div>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 4. LOGIC CHÍNH CỦA APP
# ==========================================
def main():
    settings = get_settings()
    
    if "logged_in" not in st.session_state:
        st.session_state.update({"logged_in": False, "role": None, "user": None})

    if not st.session_state["logged_in"]:
        # --- MÀN HÌNH ĐĂNG NHẬP ---
        display_header(settings)
        with st.form("login_form"):
            st.markdown("### 🔐 XÁC THỰC NGƯỜI DÙNG")
            u_input = st.text_input("Tên đăng nhập / SĐT")
            p_input = st.text_input("Mật khẩu", type="password")
            if st.form_submit_button("VÀO NHÀ", use_container_width=True):
                users = get_all_users()
                found = False
                for row in users:
                    if str(u_input) == str(row['Tài khoản']) and hash_password(p_input) == str(row['Mật khẩu']):
                        st.session_state.update({"logged_in": True, "role": row.get('Quyền', 'Nhân viên'), "user": u_input})
                        found = True
                        st.rerun()
                if not found: st.error("Chìa khóa sai rồi ní ơi!")
    else:
        # --- MÀN HÌNH LÀM VIỆC ---
        display_header(settings)
        
        # Phân quyền Tabs
        if st.session_state["role"] == "Admin":
            tabs = st.tabs(["📝 NHẬP LIỆU", "📈 BÁO CÁO", "⚙️ CÀI ĐẶT"])
        else:
            tabs = st.tabs(["📝 NHẬP LIỆU"])

        with tabs[0]:
            st.info(f"👤 Chào {st.session_state['user']} ({st.session_state['role']})")
            services = get_service_data()
            with st.form("nhap_lieu_form", clear_on_submit=True):
                khach = st.text_input("Tên khách hàng", value="Khách lẻ")
                sdt = st.text_input("SĐT khách")
                dv = st.selectbox("Dịch vụ", list(services.keys()))
                sl = st.number_input("Số lượng", min_value=1.0, value=1.0, step=0.5)
                note = st.text_area("Ghi chú")
                
                if st.form_submit_button("LƯU PHIẾU", use_container_width=True):
                    # Logic ghi vào sheet BaoCao
                    client = get_gspread_client()
                    sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
                    ws_bc = sh.worksheet("BaoCao")
                    now = get_now_vn()
                    don_gia = services.get(dv, 0)
                    ws_bc.append_row([now.strftime("%d/%m/%Y"), khach, sdt, dv, sl, don_gia, sl*don_gia, note, now.strftime("%H:%M:%S")])
                    st.success("Đã ghi sổ thành công!")
            
            if st.button("🚪 ĐĂNG XUẤT", use_container_width=True):
                st.session_state.update({"logged_in": False, "role": None})
                st.rerun()

        if st.session_state["role"] == "Admin" and len(tabs) > 2:
            with tabs[2]:
                st.subheader("🛡️ Quản lý mật mã (Admin Only)")
                st.write("Nhập mật khẩu mới cho ní hoặc nhân viên để lấy mã dán vào Sheet Admin:")
                mk_moi = st.text_input("Mật khẩu mới", type="password")
                if mk_moi:
                    st.code(hash_password(mk_moi))
                    st.warning("Copy mã trên dán vào ô Mật khẩu trong sheet Admin nhé ní.")

if __name__ == "__main__":
    main()
    
