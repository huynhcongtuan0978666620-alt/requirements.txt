import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import time
import pytz
import hashlib

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN (FIX TAB & TÍNH TOÁN)
# ==========================================
st.set_page_config(page_title="LKTV DETAILING - 2026", layout="centered", page_icon="🧼")

st.markdown("""
    <style>
        header, footer, .stAppDeployButton {display: none !important; visibility: hidden !important;}
        [data-testid="stStatusWidget"], [data-testid="stToolbar"] {display: none !important;}
        .bang-hieu-lktv {
            text-align: center;
            background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
            color: white; padding: 25px; border-radius: 20px;
            margin-bottom: 20px; box-shadow: 0px 10px 30px rgba(0,0,0,0.3);
            border: 1px solid #ffffff20;
        }
        .logo-img { width: 100px; height: 100px; object-fit: cover; border-radius: 50%; border: 3px solid #f1c40f; margin-bottom: 10px; background: #000; }
        .ten-tiem { font-size: 26px; font-weight: 800; color: #ffffff; text-transform: uppercase; }
        
        /* Chỉnh Tab rõ nét */
        .stTabs [data-baseweb="tab"] { height: 50px; background-color: #ffffff; border-radius: 10px 10px 0 0; }
        .stTabs [data-baseweb="tab"] p { color: #000000 !important; font-weight: 700 !important; }
        .stTabs [data-baseweb="tab"][aria-selected="true"] { background-color: #f1c40f !important; }
        
        /* Hiển thị tiền thừa nổi bật */
        .tien-thua-box {
            background-color: #d4edda; color: #155724;
            padding: 15px; border-radius: 10px; text-align: center;
            font-size: 20px; font-weight: bold; border: 2px dashed #28a745;
            margin: 10px 0;
        }
    </style>
    """, unsafe_allow_html=True)

# --- HÀM HỆ THỐNG ---
def hash_password(password): return hashlib.sha256(str(password).strip().encode()).hexdigest()
def get_now_vn(): return datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))

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
    except: return {"TenTiem": "LKTV DETAILING"}

@st.cache_data(ttl=60)
def get_service_data():
    try:
        client = get_gspread_client()
        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        return {r['Tên Sản Phẩm']: float(str(r['Đơn Giá']).replace(',','')) for r in sh.worksheet("DanhMuc").get_all_records() if r['Tên Sản Phẩm']}
    except: return {"Rửa xe": 50000}

# ==========================================
# GIAO DIỆN CHÍNH
# ==========================================
def main():
    settings = get_settings()
    if "logged_in" not in st.session_state:
        st.session_state.update({"logged_in": False, "role": None, "user": None, "last_submit": 0})

    if not st.session_state["logged_in"]:
        # (Phần Login giữ nguyên như cũ cho gọn)
        st.title("ĐĂNG NHẬP")
        with st.form("login"):
            u = st.text_input("User")
            p = st.text_input("Pass", type="password")
            if st.form_submit_button("Vào"):
                if u == "admin" and p == "2026": 
                    st.session_state.update({"logged_in": True, "role": "Admin", "user": "Chủ Tiệm"})
                    st.rerun()
    else:
        # Header
        logo_url = format_drive_link(settings.get('Logo', ''))
        st.markdown(f'<div class="bang-hieu-lktv"><img src="{logo_url}" class="logo-img"><div class="ten-tiem">{settings.get("TenTiem")}</div></div>', unsafe_allow_html=True)
        
        tabs = st.tabs(["📝 NHẬP LIỆU", "📈 BÁO CÁO", "⚙️ CÀI ĐẶT"])

        with tabs[0]:
            services = get_service_data()
            
            # --- FORM NHẬP LIỆU CẢI TIẾN ---
            kh = st.text_input("Tên khách hàng", "Khách lẻ")
            sdt = st.text_input("SĐT khách hàng")
            dv = st.selectbox("Dịch vụ", list(services.keys()))
            sl = st.number_input("Số lượng", 0.5, 100.0, 1.0, 0.5)
            
            # Tính toán ngay lập tức
            don_gia = services.get(dv, 0)
            tong_bill = don_gia * sl
            
            st.divider()
            st.markdown(f"### 🧾 TỔNG THANH TOÁN: `{tong_bill:,.0f} VNĐ`")
            
            # Ô khách đưa tiền
            khach_dua = st.number_input("Khách thanh toán (VNĐ)", min_value=0.0, step=1000.0, value=float(tong_bill))
            
            # Tính tiền thừa
            tien_thua = khach_dua - tong_bill
            if tien_thua > 0:
                st.markdown(f'<div class="tien-thua-box">💵 Trả lại khách: {tien_thua:,.0f} VNĐ</div>', unsafe_allow_html=True)
            elif tien_thua < 0:
                st.warning(f"Khách còn thiếu: {abs(tien_thua):,.0f} VNĐ")

            if st.button("🚀 NHẬP LIỆU NGAY", use_container_width=True, type="primary"):
                try:
                    client = get_gspread_client()
                    sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
                    ws = sh.worksheet("BaoCao")
                    now = get_now_vn()
                    # Cột I: Tổng cộng (Thành tiền), Cột J: Thời gian
                    ws.append_row([now.strftime("%d/%m/%Y"), st.session_state['user'], kh, sdt, dv, sl, don_gia, tong_bill, tong_bill, now.strftime("%H:%M:%S")])
                    ws.sort((1, 'des'), (10, 'des'))
                    st.success("Đã lưu đơn thành công!")
                    st.balloons()
                except Exception as e: st.error(f"Lỗi: {e}")

if __name__ == "__main__": main()
            
