import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import pytz
import hashlib
import time
import base64
import re
import io

# --- 1. CẤU HÌNH GIAO DIỆN CHUẨN LKTV V25.0 NGUYÊN BẢN ---
st.set_page_config(
    page_title="LKTV DETAILING - IRONCLAD", 
    layout="centered", 
    page_icon="✂️",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
        /* ẨN THÀNH PHẦN THỪA KHÔNG CẦN THIẾT */
        header, footer, .stAppDeployButton {display: none !important; visibility: hidden !important;}
        [data-testid="stStatusWidget"], [data-testid="stToolbar"] {display: none !important;}
        
        /* BẢNG HIỆU LKTV HOÀN HẢO KHỚP 100% */
        .bang-hieu-lktv {
            text-align: center;
            background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%) !important;
            color: white !important; 
            padding: 25px 25px 15px 25px !important; 
            border-radius: 20px !important;
            margin-bottom: 25px !important; 
            box-shadow: 0px 10px 30px rgba(0,0,0,0.4) !important;
            border: 1px solid #ffffff20 !important;
        }
        
        /* CANH GIỮA VÙNG CHỨA LOGO CHÍNH CHỦ ST.IMAGE */
        .logo-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: 12px !important;
        }
        /* BO TRÒN VÀ TẠO VIỀN VÀNG KHỚP 100% STYLE CŨ */
        .logo-container img { 
            width: 120px !important; 
            height: 120px !important; 
            object-fit: cover !important; 
            border-radius: 50% !important; 
            border: 4px solid #f1c40f !important; 
            box-shadow: 0 0 15px rgba(241, 196, 15, 0.5) !important;
        }
        
        .ten-tiem { 
            font-size: 32px !important; 
            font-weight: 900 !important; 
            color: #ffffff !important; 
            text-transform: uppercase !important; 
            margin-bottom: 5px !important; 
            letter-spacing: 3px !important;
            text-align: center;
        }
        .thong-tin-phu { 
            font-size: 16px !important; 
            color: #ecf0f1 !important; 
            opacity: 0.9 !important; 
            margin: 4px 0 !important; 
            text-align: center;
        }
        .slogan { 
            font-size: 17px !important; 
            color: #f1c40f !important; 
            font-weight: 600 !important; 
            font-style: italic !important; 
            margin-top: 15px !important; 
            border-top: 1px solid #ffffff20 !important; 
            padding-top: 10px !important; 
            text-align: center;
        }
        
        /* TABS ĐỒNG BỘ */
        .stTabs [data-baseweb="tab-list"] { display: flex; justify-content: center; gap: 15px; width: 100%; }
        .stTabs [data-baseweb="tab"] { flex: 1; height: 60px; background-color: #ffffff; border-radius: 15px 15px 0 0; border: 1px solid #dee2e6;}
        .stTabs [data-baseweb="tab"] p { color: #1a1a1a !important; font-weight: 800 !important; font-size: 17px; text-align: center;}
        .stTabs [data-baseweb="tab"][aria-selected="true"] { background-color: #f1c40f !important; border-bottom: 5px solid #d4ac0d; }

        /* BOX TIỀN THỪA PULSE */
        .tien-thua-box {
            background-color: #d4edda; color: #155724; padding: 25px; border-radius: 15px;
            text-align: center; font-size: 26px; font-weight: 800; border: 4px dashed #28a745;
            margin: 20px 0; animation: pulse-steel 2.5s infinite;
        }
        @keyframes pulse-steel { 
            0% {transform: scale(1); box-shadow: 0 0 0 0 rgba(40, 167, 69, 0.4);} 
            70% {transform: scale(1.03); box-shadow: 0 0 0 15px rgba(40, 167, 69, 0);} 
            100% {transform: scale(1);} 
        }
    </style>
""", unsafe_allow_html=True)

# --- 2. HÀM HỆ THỐNG ---
def get_now_vn():
    return datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))

def get_gspread_client():
    creds_info = st.secrets["connections"]["gsheets"]
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    return gspread.authorize(creds)

def extract_drive_id(link):
    if not link or not isinstance(link, str): return ""
    link = link.strip()
    match = re.search(r'(pires=|/d/|id=)([a-zA-Z0-9-_]{33,40})', link)
    if match: return match.group(2)
    if len(link) >= 33 and '/' not in link and '=' not in link: return link
    return ""

@st.cache_data(ttl=600)
def load_drive_image_bytes(drive_link):
    """ Tải ảnh từ API Drive bằng quyền Bot về dạng chuỗi Bytes thô an toàn tuyệt đối """
    f_id = extract_drive_id(drive_link)
    if not f_id: return None
    try:
        client = get_gspread_client()
        auth_session = client.auth.session
        api_url = f"https://www.googleapis.com/drive/v3/files/{f_id}?alt=media"
        response = auth_session.get(api_url, timeout=15)
        if response.status_code == 200:
            return response.content
    except Exception:
        pass
    return None

@st.cache_data(ttl=5)
def get_settings():
    try:
        client = get_gspread_client()
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sh = client.open_by_url(url)
        rows = sh.worksheet("ThietLap").get_all_values()
        return {str(row[0]).strip(): str(row[1]).strip() for row in rows if len(row) > 1}
    except Exception:
        return {
            "TenTiem": "SALON KIM HIỀN", 
            "Diachi": "131, TRẦN BÌNH TRỌNG, MỸ XUYÊN, LONG XUYÊN, AN GIANG (AG CŨ)", 
            "SDT": "0978888888",
            "Slogan": "\"Nơi Bạn Đặt Niềm Tin\"",
            "Logo": ""
        }

@st.cache_data(ttl=60)
def get_service_data():
    try:
        client = get_gspread_client()
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sh = client.open_by_url(url)
        rows = sh.worksheet("DanhMuc").get_all_values()
        return {row[0]: float(row[1]) for row in rows[1:] if len(row) > 1}
    except: return {}

def display_header(settings):
    raw_logo = settings.get('Logo', '')
    img_bytes = load_drive_image_bytes(raw_logo)
    
    # BẮT ĐẦU DỰNG KHUNG BẢNG HIỆU LKTV
    st.markdown('<div class="bang-hieu-lktv">', unsafe_allow_html=True)
    
    # Nút thắt tối cao: Sử dụng hàm st.image chính chủ của Streamlit để vượt qua rào cản CSP
    if img_bytes:
        st.markdown('<div class="logo-container">', unsafe_allow_html=True)
        st.image(io.BytesIO(img_bytes), width=120)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Nếu chưa nạp được ảnh, chừa khoảng trống nhỏ cho cân đối bảng hiệu
        st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
        
    st.markdown(f"""
            <div class="ten-tiem">{settings.get('TenTiem', 'SALON KIM HIỀN')}</div>
            <div class="thong-tin-phu">📍 {settings.get('Diachi', '131, TRẦN BÌNH TRỌNG, MỸ XUYÊN, LONG XUYÊN, AN GIANG (AG CŨ)')}</div>
            <div class="thong-tin-phu">📞 {settings.get('SDT', '0978888888')}</div>
            <div class="slogan">{settings.get('Slogan', '"Nơi Bạn Đặt Niềm Tin"')}</div>
        </div>
    """, unsafe_allow_html=True)

# --- 3. HÀM CHÍNH ---
def main():
    if "last_submit" not in st.session_state: st.session_state.last_submit = None
    if "submit_count" not in st.session_state: st.session_state.submit_count = 0
    if "submitting" not in st.session_state: st.session_state.submitting = False
    if "logged_in" not in st.session_state:
        st.session_state.update({"logged_in": False, "role": None, "full_name": None})

    settings = get_settings()

    if not st.session_state["logged_in"]:
        display_header(settings)
        with st.form("login_section"):
            st.markdown("<h3 style='text-align: center;'>🔐 ĐĂNG NHẬP</h3>", unsafe_allow_html=True)
            u = st.text_input("Tài khoản (SĐT)")
            p = st.text_input("Mật khẩu", type="password")
            if st.form_submit_button("XÁC NHẬN", use_container_width=True):
                if u == "admin" and p == "2026":
                    st.session_state.update({"logged_in": True, "role": "Admin", "full_name": "Chủ Tiệm"})
                    st.rerun()
                else:
                    try:
                        cl = get_gspread_client()
                        sh = cl.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
                        ws_user = sh.worksheet("NhanVien")
                        user_list = ws_user.get_all_records()
                        
                        found_user = None
                        for row in user_list:
                            sdt_sheet = str(row.get('Số Điện Thoại', '')).strip()
                            sdt_nhap = str(u).strip()
                            
                            if sdt_nhap.lstrip('0') == sdt_sheet.lstrip('0') and sdt_nhap.lstrip('0') != "":
                                pass_sheet = str(row.get('Mật Khẩu', '')).strip()
                                if p.strip() == pass_sheet:
                                    found_user = row
                                    break

                        if found_user:
                            ten_that = found_user.get('Tên Nhân Viên', 'Nhân viên')
                            st.session_state.update({
                                "logged_in": True, 
                                "role": "NhanVien", 
                                "full_name": ten_that
                            })
                            st.success(f"Chào mừng {ten_that}!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("SĐT hoặc Mật khẩu không đúng!")
                    except Exception as e:
                        st.error(f"Lỗi đăng nhập: {e}")

    else:
        display_header(settings)
        t_list = ["📝 NHẬP LIỆU", "📈 BÁO CÁO", "⚙️ CÀI ĐẶT"] if st.session_state["role"] == "Admin" else ["📝 NHẬP LIỆU"]
        tabs = st.tabs(t_list)

        with tabs[0]:
            st.info(f"👨‍🔧 **Nhân viên:** {st.session_state.full_name} | 🕒 **Giờ:** {get_now_vn().strftime('%H:%M')}")
            services = get_service_data()
            
            c1, c2 = st.columns(2)
            with c1: kh_ten = st.text_input("Tên khách hàng", "Khách lẻ")
            with c2: kh_sdt = st.text_input("SĐT")
            
            dv_chon = st.selectbox("Dịch vụ", list(services.keys()))
            dv_sl = st.number_input("Số lượng", 0.5, 100.0, 1.0, 0.5)
            ghi_chu = st.text_input("Ghi chú thêm (nếu có)", placeholder="Ví dụ: Khách hẹn quay lại, xe trầy nhẹ...")
            
            gia_goc = services.get(dv_chon, 0)
            t_bill = gia_goc * dv_sl
            
            st.divider()
            st.markdown(f"<h2 style='text-align: center; color: #f1c40f;'>TỔNG: {t_bill:,.0f} đ</h2>", unsafe_allow_html=True)
            
            kh_tra = st.number_input("Tiền khách đưa", 0.0, value=float(t_bill))
            t_du = kh_tra - t_bill
            if t_du > 0:
                st.markdown(f'<div class="tien-thua-box">💵 THỐI LẠI: {t_du:,.0f} đ</div>', unsafe_allow_html=True)

            can_go = True
            if st.session_state.last_submit:
                tg_cho = (get_now_vn() - st.session_state.last_submit).total_seconds() / 60
                han_muc = 3 if st.session_state.submit_count == 1 else 5 if st.session_state.submit_count >= 2 else 0
                if tg_cho < han_muc:
                    can_go = False
                    st.error(f"🚫 HÀNG RÀO THÉP: Chờ {round(han_muc - tg_cho, 1)} phút.")

            if can_go:
                cam_ket = st.checkbox("XÁC NHẬN ĐƠN KHÔNG TRÙNG LẶP")
                if not st.session_state.submitting:
                    if st.button("🚀 LƯU VÀO SHEET", use_container_width=True, type="primary"):
                        if cam_ket:
                            st.session_state.submitting = True
                            st.rerun()
                        else: st.error("Chưa tích xác nhận!")
                else:
                    st
