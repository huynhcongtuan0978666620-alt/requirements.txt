import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import time
import pytz
import hashlib

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN (THEME DARK LKTV)
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
        return {"TenTiem": "LKTV DETAILING", "Diachi": "LONG XUYÊN"}

def get_all_users():
    try:
        client = get_gspread_client()
        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        ws = sh.worksheet("Admin")
        return ws.get_all_records()
    except: return []

@st.cache_data(ttl=60)
def get_service_data():
    try:
        client = get_gspread_client()
        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        ws = sh.worksheet("DanhMuc")
        records = ws.get_all_records()
        # Tạo từ điển {Tên dịch vụ: Giá}
        return {r['Tên Sản Phẩm']: float(str(r['Đơn Giá']).replace(',','')) for r in records if r['Tên Sản Phẩm']}
    except: return {"Rửa xe (Mặc định)": 50000}

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
# 4. LOGIC CHÍNH
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
                if u_input == "admin" and p_input == "2026":
                    st.session_state.update({"logged_in": True, "role": "Admin", "user": "Chủ Tiệm"})
                    st.rerun()
                users = get_all_users()
                p_hashed = hash_password(p_input)
                for row in users:
                    if u_input == str(row.get('Tài khoản')).strip() and p_hashed == str(row.get('Mật khẩu')).strip():
                        st.session_state.update({"logged_in": True, "role": row.get('Quyền', 'Nhân viên'), "user": u_input})
                        st.rerun()
                st.error("Chìa khóa sai rồi ní!")
    else:
        display_header(settings)
        if st.session_state["role"] == "Admin":
            tabs = st.tabs(["📝 NHẬP LIỆU", "📈 BÁO CÁO", "⚙️ CÀI ĐẶT"])
        else:
            tabs = st.tabs(["📝 NHẬP LIỆU"])

        with tabs[0]:
            st.info(f"👤 Chào {st.session_state['user']} ({st.session_state['role']})")
            services = get_service_data()
            
            # --- FORM NHẬP LIỆU CHI TIẾT ---
            with st.form("form_nhap_lieu", clear_on_submit=True):
                st.subheader("📋 Lập phiếu dịch vụ")
                col1, col2 = st.columns(2)
                ten_kh = col1.text_input("Tên khách hàng", value="Khách lẻ")
                sdt_kh = col2.text_input("SĐT khách")
                
                dv_chon = st.selectbox("Chọn dịch vụ", list(services.keys()))
                sl = st.number_input("Số lượng", min_value=0.5, value=1.0, step=0.5)
                
                don_gia = services.get(dv_chon, 0)
                thanh_tien = don_gia * sl
                st.warning(f"💰 Đơn giá: {don_gia:,.0f} | Thành tiền: {thanh_tien:,.0f} VNĐ")
                
                ghi_chu = st.text_area("Ghi chú thực chiến (Tình trạng xe...)")
                
                if st.form_submit_button("LƯU DỮ LIỆU", use_container_width=True):
                    try:
                        client = get_gspread_client()
                        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
                        ws_bc = sh.worksheet("BaoCao")
                        now = get_now_vn()
                        ws_bc.append_row([
                            now.strftime("%d/%m/%Y"), ten_kh, sdt_kh, 
                            dv_chon, sl, don_gia, thanh_tien, 
                            ghi_chu, now.strftime("%H:%M:%S"), st.session_state['user']
                        ])
                        st.success("Đã ghi sổ thành công rồi ní ơi! 🎉")
                        st.balloons()
                    except: st.error("Lỗi lưu dữ liệu! Kiểm tra lại sheet BaoCao nhé ní.")
            
            if st.button("🚪 ĐĂNG XUẤT", use_container_width=True):
                st.session_state.update({"logged_in": False, "role": None})
                st.rerun()

        if st.session_state["role"] == "Admin" and len(tabs) > 1:
            with tabs[2]:
                st.subheader("🛡️ QUẢN TRỊ MẬT MÃ")
                mk = st.text_input("Mật khẩu mới", type="password")
                if mk: st.code(hash_password(mk))

if __name__ == "__main__":
    main()
            
