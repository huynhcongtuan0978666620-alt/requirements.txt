import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import pytz
import time
import re
import random
import math
import smtplib
import requests  # Thêm thư viện gọi API Telegram
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# =====================================================================
# 1. CẤU HÌNH GIAO DIỆN & STYLE CSS CAO CẤP (KHÓA RE-LOAD & BÓNG BAY SO LE)
# =====================================================================
st.set_page_config(
    page_title="LKTV DETAILING - PREMIUM", 
    layout="centered", 
    page_icon="✂️",
    initial_sidebar_state="collapsed"
)

def generate_css_animations():
    css_animation = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght=300;400;500;600;700;800;900&display=swap');

        /* 🚫 KHÓA CHẾT TÍNH NĂNG KÉO ĐỂ TẢI LẠI TRANG (PULL-TO-REFRESH) VÀ TRÀN MÀN HÌNH CHROME/SAFARI */
        html, body {
            font-family: 'Inter', '-apple-system', BlinkMacSystemFont, sans-serif !important;
            background-color: #f8f9fa !important;
            overscroll-behavior-y: contain !important; 
            overscroll-behavior: contain !important;
        }

        .stApp {
            padding-top: 75px !important; 
            padding-bottom: 75px !important; /* Tăng khoảng cách đáy để không bị cấn nút */
            background-color: transparent !important;
            overscroll-behavior-y: contain !important; /* Bảo vệ lớp bọc nội bộ Streamlit */
        }

        /* 🚫 DIỆT TẬN GỐC THANH "MANAGE APP" VÀ TOÀN BỘ LOGO/MENU HỆ THỐNG GỐC */
        header, footer, .stAppDeployButton, [data-testid="stStatusWidget"], [data-testid="stToolbar"],
        div[class*="stAppViewerToolbar"], div[data-testid="stAppViewerToolbar"], footer + div,
        div[data-testid="stViewerToolbar"], .stViewerToolbar, [data-testid="stManageAppTR"] {
            display: none !important; 
            visibility: hidden !important;
            height: 0 !important; width: 0 !important; opacity: 0 !important; pointer-events: none !important;
        }

        /* Khóa cứng dòng "Manage app" dưới đáy màn hình điện thoại */
        div[class^="StyledViewerBottomBar"] {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
        }

        .the-quan-ly-flat {
            background-color: #ffffff !important; padding: 15px !important; border-radius: 12px !important;
            border-left: 6px solid #7d8f15 !important; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
            text-align: center !important; font-weight: 700 !important; font-size: 14px !important; margin-bottom: 20px !important;
        }
        
        .nhan-tieu-de { font-size: 13px !important; font-weight: 700 !important; margin-bottom: 5px !important; text-transform: uppercase !important; }

        .banner-top {
            position: fixed !important; left: 0 !important; right: 0 !important; top: 0px !important; height: 48px !important;
            background: #111111 !important; color: #f1c40f !important; font-size: 15px !important; font-weight: 800 !important; 
            letter-spacing: 1px !important; display: flex !important; align-items: center !important; justify-content: center !important; 
            z-index: 999999 !important; border-bottom: 3px solid #7d8f15 !important; box-shadow: 0px 4px 15px rgba(0,0,0,0.3) !important;
        }
        
        /* ĐÃ SỬA LỆCH TRÁI THEO Ý NÍ */
        .banner-bottom { 
            position: fixed !important; left: 0 !important; right: 0 !important; height: 48px !important;
            background: #111111 !important; color: #f1c40f !important; font-size: 15px !important; font-weight: 800 !important; 
            letter-spacing: 1px !important; z-index: 999999 !important; 
            bottom: 0 !important; top: auto !important; border-top: 3px solid #7d8f15 !important; 
            box-shadow: 0px -4px 15px rgba(0,0,0,0.2) !important; 
            display: flex !important; align-items: center !important; 
            justify-content: flex-start !important; /* Đẩy chữ lệch sang bên trái */
            padding-left: 15px !important; /* Tạo khoảng đệm cách mép trái màn hình */
        }

        .bang-hieu-lktv {
            text-align: center; margin-bottom: 25px !important; padding: 25px !important; border-radius: 24px !important;
            background: linear-gradient(135deg, #111827 0%, #1f2937 100%) !important;
            color: white !important; box-shadow: 0px 15px 35px rgba(0,0,0,0.25) !important; border: 1px solid rgba(255, 255, 255, 0.08) !important;
        }
        .logo-img { 
            width: 110px !important; height: 110px !important; object-fit: cover !important; border-radius: 50% !important; 
            border: 4px solid #f1c40f !important; margin: 0 auto 15px auto !important; display: block !important;
            box-shadow: 0 0 20px rgba(241, 196, 15, 0.4) !important;
        }
        .ten-tiem { font-size: 24px !important; font-weight: 900 !important; color: #ffffff !important; text-transform: uppercase !important; margin-bottom: 6px !important; letter-spacing: 2px !important; }
        .thong-tin-phu { font-size: 12px !important; color: #9ca3af !important; margin: 5px 0 !important; font-weight: 400; }
        .slogan { font-size: 15px !important; color: #f1c40f !important; font-weight: 600 !important; font-style: italic !important; margin-top: 15px !important; border-top: 1px solid rgba(255,255,255,0.1) !important; padding-top: 12px !important; }
        
        [data-testid="stTabs"] [role="tablist"] div { height: 0px !important; background-color: transparent !important; border: none !important; }
        [data-testid="stTabs"] [role="tablist"] { display: flex !important; width: 100% !important; justify-content: center !important; align-items: center !important; gap: 6px !important; padding: 0 !important; margin: 0 auto 15px auto !important; }

        button[data-baseweb="tab"] {
            flex: 1 1 100% !important; height: 54px !important; display: flex !important; align-items: center !important;
            justify-content: center !important; text-align: center !important; background-color: #e2e8f0 !important; 
            border-radius: 10px !important; padding: 10px 4px !important; border: none !important; outline: none !important;
            white-space: nowrap !important; transition: all 0.2s ease-in-out !important;
        }

        button[data-baseweb="tab"] p, button[data-baseweb="tab"] span, button[data-baseweb="tab"] div[data-testid="stMarkdownContainer"] {
            color: #334155 !important; font-size: 16px !important; font-weight: 700 !important; text-align: center !important;
            justify-content: center !important; align-items: center !important; display: flex !important; margin: 0 auto !important; width: 100% !important;
        }

        button[data-baseweb="tab"][aria-selected="true"] { background-color: #f1c40f !important; border: none !important; outline: none !important; box-shadow: 0 4px 12px rgba(241, 196, 15, 0.4) !important; }

        .tong-don-box { background-color: #fef3c7; color: #b45309; padding: 16px; border-radius: 16px; text-align: center; border: 3px dashed #d97706; font-size: 24px; font-weight: 900; box-shadow: 0px 4px 10px rgba(0,0,0,0.02); }
        .chiet-khau-box { background-color: #fee2e2; color: #b91c1c; padding: 16px; border-radius: 16px; text-align: center; border: 3px dashed #ef4444; font-size: 24px; font-weight: 900; box-shadow: 0px 4px 10px rgba(0,0,0,0.02); }
        .khach-tra-box { background-color: #d1fae5; color: #065f46; padding: 16px; border-radius: 16px; text-align: center; border: 3px dashed #059669; font-size: 24px; font-weight: 900; box-shadow: 0px 4px 10px rgba(0,0,0,0.02); }
        .cong-tho-box { background-color: #f3f4f6; color: #1f2937; padding: 16px; border-radius: 16px; text-align: center; border: 3px dashed #4b5563; font-size: 24px; font-weight: 900; box-shadow: 0px 4px 10px rgba(0,0,0,0.02); }
        
        div[data-testid="stButton"] button[kind="primary"] { animation: pulse-button-new 1.5s infinite ease-in-out !important; }
        @keyframes pulse-button-new {
            0% { transform: scale(1); }
            50% { transform: scale(1.02); box-shadow: 0 0 15px rgba(241, 196, 15, 0.6) !important; }
            100% { transform: scale(1); }
        }

        .tien-thua-box { 
            background-color: #d1fae5; color: #065f46; padding: 22px; border-radius: 16px; text-align: center; 
            font-size: 26px; font-weight: 900; border: 3px dashed #059669; margin: 20px 0; 
            animation: bounce-steel 1.2s infinite ease-in-out !important; 
        }
        @keyframes bounce-steel {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-8px); box-shadow: 0 10px 20px rgba(5, 150, 105, 0.2); }
        }

        .lsc-shake { animation: shake-warn 0.5s infinite linear !important; }
        @keyframes shake-warn {
            0%, 100% { transform: translate(0, 0) rotate(0deg); }
            20% { transform: translate(-2px, 1px) rotate(-1deg); }
            40% { transform: translate(1px, -1px) rotate(1deg); }
            60% { transform: translate(-1px, -2px) rotate(-1deg); }
            80% { transform: translate(2px, 1px) rotate(1deg); }
        }

        .hoa-don-khung { background-color: #ffffff !important; color: #111111 !important; padding: 20px !important; border-radius: 16px !important; border: 2px solid #111111 !important; font-family: 'SFMono-Regular', Consolas, monospace !important; box-shadow: 0px 10px 25px rgba(0,0,0,0.08) !important; margin-top: 20px !important; }
        .hd-header { text-align: center; font-weight: bold; border-bottom: 2px dashed #111111; padding-bottom: 12px; margin-bottom: 15px; }
        .hd-title { font-size: 22px; text-transform: uppercase; margin-top: 6px; letter-spacing: 1px; font-weight: 900; color: #111111; }
        
        .hd-row-item { display: flex !important; justify-content: space-between !important; align-items: flex-start !important; margin-bottom: 12px !important; font-size: 13px !important; width: 100% !important; line-height: 1.4 !important; }
        .hd-item-name { flex: 1 !important; padding-right: 15px !important; text-align: left !important; word-break: break-word !important; }
        .hd-item-price { text-align: right !important; white-space: nowrap !important; font-weight: bold !important; }
        .hd-items { border-bottom: 2px dashed #111111; padding-bottom: 12px; margin-bottom: 12px; }

        /* 🎆 HIỆU ỨNG PHÁO HOA */
        .firework-container { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: 9999999; overflow: hidden; background: transparent; }
        .css-particle { position: absolute; width: 6px; height: 6px; border-radius: 50%; opacity: 0; animation: explode-mega 4.0s ease-out 3 forwards; }
        @keyframes explode-mega {
            0% { transform: translate(0, 0); opacity: 0; }
            20% { opacity: 1; }
            80% { opacity: 0.8; }
            100% { transform: translate(var(--cx), var(--cy)) scale(0.1); opacity: 0; }
        }

        /* 🎈 HIỆU ỨNG BÓNG BAY KHÔNG CHÙM */
        .balloon-container-css { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: 9999998; overflow: hidden; background: transparent; }
        .fixed-balloon { 
            position: absolute !important; bottom: -120px !important; 
            border-radius: 50% 50% 50% 50% / 40% 40% 60% 60%; opacity: 0.9; 
            box-shadow: inset -6px -6px rgba(0,0,0,0.15), 2px 2px 8px rgba(0,0,0,0.1);
            animation: fly-up-skywards-pure linear forwards; 
        }
        .fixed-balloon::after { 
            content: ""; position: absolute; bottom: -12px; left: 50%; 
            transform: translateX(-50%); width: 2px; height: 14px; 
            background-color: rgba(0, 0, 0, 0.22); 
        }
        @keyframes fly-up-skywards-pure {
            0% { transform: translateY(110vh) rotate(0deg); opacity: 0; }
            8% { opacity: 0.9; }
            90% { opacity: 0.9; }
            100% { transform: translateY(-130vh) rotate(var(--rot, 15deg)); opacity: 0; }
        }
    </style>
    """
    return css_animation

# Hàm kết xuất pháo hoa mừng chốt đơn
def render_fireworks_html():
    colors = ['#ff0055', '#00ffcc', '#ffcc00', '#ff6600', '#00ff00', '#ff00ff', '#ffffff', '#e74c3c', '#3498db']
    html_particles = '<div class="firework-container">'
    centers = [(25, 20), (50, 15), (75, 20)]
    for cx, cy in centers:
        for i in range(80): 
            angle = random.uniform(0, 2 * 3.14159)
            distance = random.uniform(50, 200)
            target_x = int(math.cos(angle) * distance)
            target_y = int(math.sin(angle) * distance)
            color = random.choice(colors)
            delay = round(random.uniform(0, 0.1), 2)
            html_particles += f'<div class="css-particle" style="background-color: {color}; left: {cx}vw; top: {cy}vh; --cx: {target_x}px; --cy: {target_y}px; animation-delay: {delay}s;"></div>'
    html_particles += '</div>'
    return html_particles

# Hàm tạo bóng bay lệch pha, dập dìu chống lỗi Re-render của Streamlit
def render_balloons_html():
    colors = ['#ff4d4d', '#ff944d', '#ffff4d', '#4dff4d', '#4dffff', '#4d4dff', '#ff4dff', '#ff3385', '#00ffcc']
    html_balloons = '<div class="balloon-container-css">'
    for i in range(45):
        left_pos = random.uniform(4, 92)
        color = random.choice(colors)
        size_ratio = random.uniform(0.7, 1.3)
        width = int(50 * size_ratio)
        height = int(65 * size_ratio)
        delay = round(random.uniform(0.0, 4.5), 2)
        duration = round(random.uniform(3.8, 5.8), 2)
        rotation = random.randint(-20, 20)
        
        html_balloons += f"""
        <div class="fixed-balloon" style="
            background-color: {color}; 
            left: {left_pos}vw; 
            width: {width}px; 
            height: {height}px; 
            animation-delay: {delay}s; 
            animation-duration: {duration}s; 
            --rot: {rotation}deg;">
        </div>"""
    html_balloons += '</div>'
    st.markdown(html_balloons, unsafe_allow_html=True)

st.markdown(generate_css_animations(), unsafe_allow_html=True)

st.markdown("""
<div class="banner-top">⭐⭐BAO NGON LUÔN NÍ ƠI⭐⭐</div>
<div class="banner-bottom"> KIM HIỀN 2026 🌹🌹🌹 </div>
""", unsafe_allow_html=True)

# =====================================================================
# 2. HÀM CORE HỆ THỐNG - TRUY XUẤT AN TOÀN DỮ LIỆU
# =====================================================================
def get_now_vn():
    return datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))

def get_gspread_client():
    creds_info = st.secrets["connections"]["gsheets"]["spreadsheet_credentials"] if "spreadsheet_credentials" in st.secrets["connections"]["gsheets"] else st.secrets["connections"]["gsheets"]
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    return gspread.authorize(Credentials.from_service_account_info(creds_info, scopes=scope))

def format_drive_direct_url(link):
    if not link or not isinstance(link, str): return ""
    match = re.search(r'(pires=|/d/|id=)([a-zA-Z0-9-_]{33,40})', link.strip())
    return f"https://lh3.googleusercontent.com/d/{match.group(2)}" if match else ""

@st.cache_data(ttl=1200)
def get_settings():
    try:
        client = get_gspread_client()
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        rows = client.open_by_url(url).worksheet("ThietLap").get_all_values()
        return {str(row[0]).strip(): str(row[1]).strip() for row in rows if len(row) > 1}
    except Exception:
        return {"TenTiem": "SALON KIM HIỀN", "Diachi": "131, TRẦN BÌNH TRỌNG, LONG XUYÊN", "SDT": "0947.58.1516"}

@st.cache_data(ttl=900)
def get_service_data():
    try:
        client = get_gspread_client()
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        rows = client.open_by_url(url).worksheet("DanhMuc").get_all_values()
        danh_sach_dv = {}
        for row in rows[1:]:
            if len(row) >= 2:
                ten_dv = str(row[0]).strip()
                if not ten_dv: continue
                try: gia_goc = float(str(row[1]).replace('.', '').replace(',', '').strip())
                except: gia_goc = 0.0
                hoa_hong = 0.0
                if len(row) >= 3 and row[2]:
                    try:
                        raw_hh = str(row[2]).replace('%', '').replace(',', '.').strip()
                        hoa_hong = float(raw_hh)
                        if 0 < hoa_hong < 1.0: hoa_hong *= 100
                    except: hoa_hong = 0.0
                danh_sach_dv[ten_dv] = {"gia": gia_goc, "hoa_hong": hoa_hong}
        return danh_sach_dv
    except Exception: return {}

@st.cache_data(ttl=900)
def get_nhan_vien_data():
    try:
        client = get_gspread_client()
        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        return sh.worksheet("NhanVien").get_all_values()
    except Exception: return []

# --- HÀM ĐỌC DANH SÁCH KHÁCH HÀNG TỪ SHEET "KhachHang" (ĐỒNG BỘ REALTIME 100%) ---
@st.cache_data(ttl=5)
def get_khach_hang_data():
    try:
        client = get_gspread_client()
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        rows = client.open_by_url(url).worksheet("KhachHang").get_all_values()
        
        ds_kh = {}
        for row in rows[1:]:
            if len(row) >= 2:
                sdt_raw = str(row[0]).strip().replace(".0", "")
                ten_kh = str(row[1]).strip()
                if sdt_raw:
                    ds_kh[sdt_raw] = ten_kh
        return ds_kh
    except Exception: 
        return {}

def display_header(settings):
    direct_logo_url = format_drive_direct_url(settings.get('Logo', ''))
    fallback_gif = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
    st.markdown(f"""
        <div class="bang-hieu-lktv">
            <img src="{direct_logo_url}" class="logo-img" onerror="this.onerror=null;this.src='{fallback_gif}';">
            <div class="ten-tiem">{settings.get('TenTiem', 'SALON KIM HIỀN')}</div>
            <div class="thong-tin-phu">📍 {settings.get('Diachi', '131, TRẦN BÌNH TRỌNG')}</div>
            <div class="thong-tin-phu">☎️ {settings.get('SDT', '0947.58.1516')}</div>
            <div class="slogan">{settings.get('Slogan', '"Nơi Bạn Đặt Niềm Tin"')}</div>
        </div>
    """, unsafe_allow_html=True)

def gui_email_backup(noi_dung):
    try:
        sender_email = "huynhcongtuan0978666620@gmail.com"
        password = "lwui aesw vqal ytcq" 
        receiver_email = "huynhcongtuan0978666620@gmail.com"
        gio_vn_mail = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh')).strftime('%d/%m/%Y %H:%M')
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = f"ĐH DỊCH VỤ SALON - {gio_vn_mail}"
        msg.attach(MIMEText(noi_dung, 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        server.send_message(msg)
        server.quit()
    except Exception as e: print(f"Lỗi gửi mail: {e}")

# =====================================================================
# THÊM HÀM GỬI THÔNG BÁO QUA TELEGRAM BOT REALTIME
# =====================================================================
def gui_telegram_notification(noi_dung):
    try:
        bot_token = st.secrets["telegram"]["bot_token"]
        chat_id = st.secrets["telegram"]["chat_id"]
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": noi_dung, "parse_mode": "Markdown"}
        
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            st.error(f"Telegram lỗi: {response.text}")
    except Exception as e: 
        st.error(f"Lỗi kết nối Telegram: {str(e)}")

# --- HÀM CALLBACK TỰ ĐỘNG TRA CỨU TÊN KHÁCH KHI NHẬP SĐT (ĐÃ FIX ĐỒNG BỘ STATE CHUẨN) ---
def xu_ly_tra_cuu_khach_hang():
    sdt_nhap = st.session_state.widget_kh_sdt.strip()
    ds_kh = get_khach_hang_data()
    
    if sdt_nhap:
        sdt_khong_0 = sdt_nhap[1:] if sdt_nhap.startswith('0') else sdt_nhap
        sdt_co_0 = '0' + sdt_nhap if not sdt_nhap.startswith('0') else sdt_nhap
        
        if sdt_nhap in ds_kh:
            ten_tim_duoc = ds_kh[sdt_nhap]
        elif sdt_khong_0 in ds_kh:
            ten_tim_duoc = ds_kh[sdt_khong_0]
        elif sdt_co_0 in ds_kh:
            ten_tim_duoc = ds_kh[sdt_co_0]
        else:
            # SĐT Mới hoàn toàn -> Đặt trống để nhân viên tự nhập tên mới
            ten_tim_duoc = ""
    else:
        ten_tim_duoc = "Khách lẻ"
        
    st.session_state.state_kh_sdt = sdt_nhap
    st.session_state.state_kh_ten = ten_tim_duoc
    # Đồng bộ ép buộc trực tiếp vào widget_kh_ten_input của Streamlit
    st.session_state.widget_kh_ten_input = ten_tim_duoc

# =====================================================================
# 3. LUỒNG ĐIỀU HƯỚNG CHÍNH (MAIN APPLICATION LOGIC)
# =====================================================================
def main():
    init_states = {
        "last_submit": None, "submit_count": 0, "submitting": False, 
        "adding_cart": False, "logged_in": False, "role": None, 
        "full_name": None, "gio_hang": [], "bill_vua_in": None, 
        "trigger_boom": False, "trigger_balloons": False,
        "state_kh_ten": "Khách lẻ", "state_kh_sdt": "" 
    }
    for key, val in init_states.items():
        if key not in st.session_state: st.session_state[key] = val

    settings = get_settings()

    if st.session_state.trigger_boom:
        st.markdown(render_fireworks_html(), unsafe_allow_html=True)
        st.session_state.trigger_boom = False

    if st.session_state.trigger_balloons:
        render_balloons_html()  
        st.session_state.trigger_balloons = False

    # --- PHÂN HỆ ĐĂNG NHẬP ---
    if not st.session_state["logged_in"]:
        display_header(settings)
        with st.form("login_section"):
            st.markdown("<h3 style='text-align: center;'>🔐 ĐĂNG NHẬP</h3>", unsafe_allow_html=True)
            u = st.text_input("Tài khoản (SĐT)")
            p = st.text_input("Mật khẩu", type="password")
            
            if st.form_submit_button("XÁC NHẬN ĐĂNG NHẬP", use_container_width=True):
                if u == "admin" and p == "2026":
                    st.session_state.update({
                        "logged_in": True, "role": "Admin", 
                        "full_name": "Chủ Tiệm", "trigger_balloons": True
                    })
                    st.rerun()
                else:
                    raw_data = get_nhan_vien_data()
                    if len(raw_data) > 0:
                        headers = [str(h).strip() for h in raw_data[0]]
                        col_sdt_idx = next((i for i, h in enumerate(headers) if 'số điện thoại' in h.lower() or 'sđt' in h.lower() or 'tai khoan' in h.lower()), -1)
                        col_mk_idx = next((i for i, h in enumerate(headers) if 'mật khẩu' in h.lower() or 'mat khau' in h.lower() or 'code' in h.lower()), -1)
                        
                        # --- ĐÃ SỬA LỖI CÚ PHÁP TẠI ĐÂY ---
                        col_ten_idx = next((i for i, h in enumerate(headers) if 'tên' in h.lower() or 'nhân viên' in h.lower()), -1)
                        # ----------------------------------
                        
                        found_row = None
                        sdt_nhap = str(u).strip().lstrip('0')
                        for r in raw_data[1:]:
                            if len(r) > max(col_sdt_idx, col_mk_idx):
                                sdt_sheet = str(r[col_sdt_idx]).strip().lstrip('0')
                                mk_sheet = str(r[col_mk_idx]).strip()
                                if sdt_nhap == sdt_sheet and p.strip() == mk_sheet and sdt_nhap != "":
                                    found_row = r
                                    break
                                    
                        if found_row:
                            ten_that = str(found_row[col_ten_idx]).strip() if col_ten_idx != -1 and col_ten_idx < len(found_row) else "Nhân viên"
                            st.session_state.update({
                                "logged_in": True, "role": "NhanVien", 
                                "full_name": ten_that, "trigger_balloons": True
                            })
                            st.success(f"Chào mừng {ten_that}!")
                            time.sleep(0.5)
                            st.rerun()
                        else: st.error("Tài khoản hoặc Mật khẩu không chính xác!")
                    else: st.error("Lỗi dữ liệu cổng Nhân Viên!")
        
        st.write("") 
        col_reload1, col_reload2 = st.columns([4, 6])
        with col_reload1:
            if st.button("🔄 TẢI LẠI APP", use_container_width=True):
                st.session_state.clear()
                st.rerun()
        with col_reload2:
            st.caption("💡 *Nếu app bị đứng hình hoặc lag mạng, bấm nút kế bên để làm mới nhé ní!*")

    # --- PHÂN HỆ HOẠT ĐỘNG CHÍNH ---
    else:
        display_header(settings)
        t_list = ["🛒 NHẬP LIỆU", "📈 BÁO CÁO", "⚙️ CÀI ĐẶT"] if st.session_state["role"] == "Admin" else ["🛒 NHẬP LIỆU"]
        tabs = st.tabs(t_list)

        # TAB 1: NHẬP LIỆU & LÊN ĐƠN HÀNG
        with tabs[0]:
            st.info(f"👨‍🔧 **Nhân viên:** {st.session_state.full_name} | 🕒 **Giờ hiện tại:** {get_now_vn().strftime('%H:%M')}")
            st.markdown('<div class="the-quan-ly-flat">📝 NHẬP "ĐƠN HÀNG" BÊN DƯỚI NHẾ!</div>', unsafe_allow_html=True)
            
            services = get_service_data()
            dv_list = list(services.keys())
            
            c1, c2 = st.columns(2)
            with c1: 
                kh_sdt = st.text_input(
                    "📞 SĐT khách", 
                    value=st.session_state.state_kh_sdt, 
                    key="widget_kh_sdt", 
                    on_change=xu_ly_tra_cuu_khach_hang
                )
                    
            with c2: 
                # Khởi tạo giá trị widget_kh_ten_input nếu chưa có trong session state
                if "widget_kh_ten_input" not in st.session_state:
                    st.session_state.widget_kh_ten_input = st.session_state.state_kh_ten
                    
                kh_ten = st.text_input(
                    "👤 Tên khách hàng", 
                    key="widget_kh_ten_input"
                )
                st.session_state.state_kh_ten = kh_ten

            st.markdown("#### 👉 CHỌN DỊCH VỤ THÊM VÀO ĐƠN")
            box_chon_dv = st.selectbox("📥 Dịch vụ", options=dv_list if dv_list else ["Không có dữ liệu"], index=None, placeholder="Gõ chữ để tìm nhanh...")
            box_sl = st.number_input("🔢 Số lượng", min_value=0.0, max_value=2.0, value=0.0, step=0.5)
            
            if st.session_state.adding_cart:
                st.button("⏳ ĐANG THÊM VÀO GIỎ...", disabled=True, use_container_width=True)
            else:
                if st.button("🛒 THÊM VÀO GIỎ ĐƠN", use_container_width=True):
                    if not box_chon_dv or box_chon_dv == "Không có dữ liệu":
                        st.error("🚫 Vui lòng chọn một dịch vụ cụ thể trước khi thêm!")
                    elif box_sl <= 0: st.error("Vui lòng chọn số lượng lớn hơn 0!")
                    else:
                        st.session_state.adding_cart = True
                        if any(item["dich_vu"] == box_chon_dv for item in st.session_state.gio_hang):
                            st.error(f"🚫 Dịch vụ đã tồn tại trong giỏ!")
                            st.session_state.adding_cart = False
                        else:
                            info_dv = services.get(box_chon_dv, {"gia": 0.0, "hoa_hong": 0.0})
                            gia_goc = info_dv.get("gia", 0.0)
                            phan_tram_hh = info_dv.get("hoa_hong", 0.0)
                            t_bill_item = gia_goc * box_sl
                            
                            st.session_state.gio_hang.append({
                                "dich_vu": box_chon_dv, "so_luong": box_sl, "don_gia": gia_goc,
                                "thanh_tien": t_bill_item, "phan_tram_hh": phan_tram_hh,
                                "tiem_cong_tho": t_bill_item * (phan_tram_hh / 100.0)
                            })
                            st.success(f"Đã thêm thành công!")
                            st.session_state.bill_vua_in = None
                            st.session_state.adding_cart = False
                            time.sleep(0.1)
                            st.rerun()

            # CHI TIẾT GIỎ HÀNG CHỜ LƯU
            t_bill, t_cong_tho = 0.0, 0.0
            if st.session_state.gio_hang:
                st.markdown("---")
                st.markdown(f"📦 **CHI TIẾT ĐƠN HÀNG CHỜ LƯU ({len(st.session_state.gio_hang)} món)**")
                for idx, item in enumerate(st.session_state.gio_hang):
                    col_item1, col_item2, col_item3 = st.columns([5.0, 3.5, 1.5])
                    with col_item1: st.markdown(f"**{idx+1}. {item['dich_vu']}** (SL: {item['so_luong']})")
                    with col_item2: st.markdown(f"{item['thanh_tien']:,.0f}đ (Công: {item['tiem_cong_tho']:,.0f}đ)")
                    with col_item3:
                        if st.button("Xóa", key=f"del_{idx}", use_container_width=True):
                            st.session_state.gio_hang.pop(idx)
                            st.session_state.bill_vua_in = None
                            st.rerun()
                    t_bill += item['thanh_tien']
                    t_cong_tho += item['tiem_cong_tho']

            # THANH TOÁN ĐƠN & KHU VỰC THU NGÂN (CHIẾT KHẤU)
            if t_bill > 0:
                st.divider()
                st.markdown("### 🧮 PHÂN HỆ THU NGÂN (TÍNH TOÁN CHIẾT KHẤU)")
                
                tien_giam = st.number_input("🎁 Số tiền CHIẾT KHẤU KHÁCH HÀNG (đ)", min_value=0.0, max_value=float(t_bill), value=0.0, step=1000.0)
                t_khach_tra = max(0.0, t_bill - tien_giam)
                
                ghi_chu = st.text_input("📝 Ghi chú tổng đơn (nếu có)", placeholder="Ví dụ: Khách làm kỹ, giảm giá khai trương...")
                st.write("")
                
                col_bill1, col_bill2, col_bill3 = st.columns(3)
                with col_bill1: 
                    st.markdown(f'<div class="nhan-tieu-de" style="color: #b45309;">💰 Tổng Đơn</div><div class="tong-don-box">{t_bill:,.0f} đ</div>', unsafe_allow_html=True)
                with col_bill2: 
                    st.markdown(f'<div class="nhan-tieu-de" style="color: #b91c1c;">🎁 Chiết Khấu</div><div class="chiet-khau-box">{tien_giam:,.0f} đ</div>', unsafe_allow_html=True)
                with col_bill3: 
                    st.markdown(f'<div class="nhan-tieu-de" style="color: #065f46;">🔥 Khách Phải Trả</div><div class="khach-tra-box">{t_khach_tra:,.0f} đ</div>', unsafe_allow_html=True)
                
                st.markdown(f'<div class="nhan-tieu-de" style="color: #4b5563; margin-top:15px;">🛠️ Tiền công thợ tổng: <b>{t_cong_tho:,.0f} đ</b></div>', unsafe_allow_html=True)
                
                st.write("")
                kh_dua = st.number_input("💵 Tiền khách đưa thực tế", 0.0, value=float(t_khach_tra))
                t_du = kh_dua - t_khach_tra
                
                if t_du > 0:
                    st.markdown(f'<div class="tien-thua-box">💵 TIỀN THỐI LẠI KHÁCH: {t_du:,.0f} đ</div>', unsafe_allow_html=True)

                can_go = True
                if st.session_state.last_submit:
                    tg_cho = (get_now_vn() - st.session_state.last_submit).total_seconds() / 60
                    han_muc = 1 if st.session_state.submit_count == 1 else 2 if st.session_state.submit_count >= 2 else 0
                    if tg_cho < han_muc:
                        can_go = False
                        st.markdown(f'<div class="lsc-shake" style="background-color: #fee2e2; color: #991b1b; padding: 12px; border-radius: 10px; border: 2px solid #ef4444; text-align: center; font-weight: bold; font-size: 14px;">🚫 HÀNG RÀO THÉP CHỐNG TRÙNG: Vui lòng đợi thêm {round(han_muc - tg_cho, 1)} phút để tiếp tục đơn mới.</div>', unsafe_allow_html=True)

                if can_go:
                    cam_ket = st.checkbox("✅ XÁC NHẬN ĐƠN KHÔNG TRÙNG LẶP")
                    if not st.session_state.submitting:
                        if st.button("🚀 CHỐT ĐƠN & ĐỒNG BỘ", use_container_width=True, type="primary"):
                            if cam_ket:
                                st.session_state.submitting = True
                                st.rerun()
                            else: st.error("Chưa tích chọn ô xác nhận cam kết!")
                    else:
                        st.button("⏳ ĐANG XỬ LÝ VÀ ĐỒNG BỘ...", disabled=True, use_container_width=True)
                        try:
                            cl = get_gspread_client()
                            ws = cl.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"]).worksheet("BaoCao")
                            bay_gio = get_now_vn()
                            ma_hd = f"HD-{bay_gio.strftime('%Y%m%d-%H%M%S')}"
                            
                            rows_to_append = []
                            html_items = ""
                            chi_tiet_tele = "" 
                            
                            for idx, item in enumerate(st.session_state.gio_hang):
                                rows_to_append.append([
                                    bay_gio.strftime("%d/%m/%Y"), st.session_state.full_name, kh_ten, kh_sdt,
                                    item['dich_vu'], item['so_luong'], item['don_gia'], item['thanh_tien'],
                                    bay_gio.strftime("%H:%M:%S"), f"[Chiết khấu đơn: {tien_giam:,.0f}đ] " + ghi_chu, item['tiem_cong_tho'], ma_hd
                                ])
                                html_items += f"""
                                <div class="hd-row-item">
                                    <div class="hd-item-name">{idx+1}. {item["dich_vu"]} (x{item["so_luong"]})</div>
                                    <div class="hd-item-price">{item["thanh_tien"]:,.0f} đ</div>
                                </div>"""
                                chi_tiet_tele += f"\n🔹 {item['dich_vu']} (SL: {int(item['so_luong'])}): {item['thanh_tien']:,.0f}đ"
                            
                            ws.append_rows(rows_to_append)
                            
                            # --- 🚀 CHỐT TỰ ĐỘNG CẬP NHẬT DATA KHÁCH HÀNG MỚI LÊN GOOGLE SHEET KHÔNG LỖI TRÙNG ---
                            sdt_luu = str(kh_sdt).strip()
                            ten_luu = str(kh_ten).strip()
                            if sdt_luu and sdt_luu != "":
                                ds_kh_hien_tai = get_khach_hang_data()
                                # So khớp linh hoạt định dạng để chống trùng lặp
                                sdt_khong_0 = sdt_luu[1:] if sdt_luu.startswith('0') else sdt_luu
                                sdt_co_0 = '0' + sdt_luu if not sdt_luu.startswith('0') else sdt_luu
                                
                                is_sdt_cu = (sdt_luu in ds_kh_hien_tai) or (sdt_khong_0 in ds_kh_hien_tai) or (sdt_co_0 in ds_kh_hien_tai)
                                
                                if not is_sdt_cu and ten_luu != "Khách lẻ" and ten_luu != "":
                                    ws_kh = cl.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"]).worksheet("KhachHang")
                                    ws_kh.append_row([sdt_luu, ten_luu])
                                    st.cache_data.clear() 
                            
                            # Nội dung email/telegram hệ thống
                            noi_dung_mail = (
                                f"✌️ XIN CHÀO.\n"
                                f"🧾 ĐƠN HÀNG MỚI - SALON KIM HIỀN\n"
                                f"----------------------------------------\n"
                                f"🆔 Mã đơn: {ma_hd}\n"
                                f"⏰ Thời gian: {bay_gio.strftime('%d/%m/%Y %H:%M:%S')}\n"
                                f"👤 Khách hàng: {kh_ten} ({kh_sdt if kh_sdt else 'Không có SĐT'})\n"
                                f"👨‍🔧 Nhân viên lập: {st.session_state.full_name}\n"
                                f"💬 Ghi chú: {ghi_chu if ghi_chu else 'Không có'}\n"
                                f"----------------------------------------\n"
                                f"📦 Chi tiết dịch vụ: {chi_tiet_tele}\n"
                                f"----------------------------------------\n"
                                f"💰 Tổng tiền gốc: {t_bill:,.0f} đ\n"
                                f"🎁 Chiết khấu: -{tien_giam:,.0f} đ\n"
                                f"🔥 THỰC THU KHÁCH TRẢ: {t_khach_tra:,.0f} đ\n"
                                f"💵 Khách đưa: {kh_dua:,.0f} đ | Thối lại: {t_du:,.0f} đ\n"
                                f"🛠️ Tiền công thợ: {t_cong_tho:,.0f} đ\n"
                                f"----------------------------------------\n"
                                f"♥️ SALON KIM HIỀN\n"
                                f"♥️ Zalo: 0947.58.1516\n"
                                f"♥️ 131 Trần Bình Trọng, Mỹ Xuyên, Long Xuyên, AG (Cũ)\n"
                                f"♥️ Cảm Ơn Quý Khách.\n"
                            )
                            gui_email_backup(noi_dung_mail)
                            gui_telegram_notification(noi_dung_mail)

                            st.session_state.bill_vua_in = f"""
                            <div class="hoa-don-khung">
                                <div class="hd-header">
                                    <div style="font-size: 16px; font-weight: 900;">{settings.get('TenTiem', 'SALON KIM HIỀN')}</div>
                                    <div style="font-size: 11px;">📍 {settings.get('Diachi', 'AN GIANG')}</div>
                                    <div style="font-size: 11px;">☎️ {settings.get('SDT', '0947.58.1516')}</div>
                                    <div class="hd-title">🧾 PHIẾU THANH TOÁN</div>
                                    <div style="font-size: 11px; margin-top:5px;">Mã đơn: {ma_hd}</div>
                                </div>
                                <div style="border-bottom: 1px dashed #111111; padding-bottom: 5px; margin-bottom: 10px; font-size: 13px;">
                                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;"><span>Ngày lập:</span> <span>{bay_gio.strftime('%d/%m/%Y %H:%M')}</span></div>
                                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;"><span>Khách hàng:</span> <span>{kh_ten}</span></div>
                                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;"><span>Nhân viên:</span> <span>{st.session_state.full_name}</span></div>
                                </div>
                                <div class="hd-items">{html_items}</div>
                                <div style="font-size: 13px; border-bottom: 1px dashed #111111; padding-bottom: 8px; margin-bottom: 8px;">
                                    <div style="display: flex; justify-content: space-between; margin-bottom: 6px;"><span>Tổng tiền gốc:</span> <span>{t_bill:,.0f} đ</span></div>
                                    <div style="display: flex; justify-content: space-between; margin-bottom: 6px; color: #b91c1c; font-weight: bold;"><span>Chiết khấu khách hàng:</span> <span>-{tien_giam:,.0f} đ</span></div>
                                </div>
                                <div style="font-size: 14px; font-weight: bold;">
                                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px; color: #065f46; font-size: 15px;"><span>TỔNG TIỀN PHẢI TRẢ:</span> <span>{t_khach_tra:,.0f} đ</span></div>
                                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px; font-weight: normal; font-size: 13px;"><span>Khách đưa:</span> <span>{kh_dua:,.0f} đ</span></div>
                                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px; color: #4b5563; font-weight: normal; font-size: 13px;"><span>Tiền thối lại:</span> <span>{t_du:,.0f} đ</span></div>
                                </div>
                                <div style="text-align: center; margin-top: 20px; font-size: 12px; font-style: italic; border-top: 1px dashed #111111; padding-top: 10px;">
                                    {settings.get('Slogan', '"Nơi Bạn Đặt Niềm Tin"')} <br> ♥️ Cảm ơn quý khách! ♥️
                                </div>
                            </div>"""

                            # Reset thông tin để chuẩn bị cho đơn sau và dọn sạch widget_kh_ten_input
                            st.session_state.update({
                                "gio_hang": [], "last_submit": bay_gio, 
                                "submit_count": st.session_state.submit_count + 1, 
                                "submitting": False, "trigger_boom": True,
                                "state_kh_ten": "Khách lẻ", "state_kh_sdt": "",
                                "widget_kh_ten_input": "Khách lẻ"
                            })
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Lỗi lưu dữ liệu: {e}")
                            st.session_state.submitting = False
            else: st.warning("⚠️ Giỏ hàng hiện đang trống nhen ní.")

            if st.session_state.bill_vua_in:
                st.success("🎉 ĐỒNG BỘ THÀNH CÔNG! ĐÃ XUẤT HOÁ ĐƠN ĐIỆN TỬ & EMAIL + TELEGRAM REALTIME BACKUP!")
                st.markdown("---")
                st.markdown("### 🧾 HOÁ ĐƠN THANH TOÁN (Có chiết khấu)")
                st.markdown(st.session_state.bill_vua_in, unsafe_allow_html=True)

            st.divider()
            if st.button("🚪 THOÁT APP", use_container_width=True):
                st.session_state.clear()
                st.rerun()

        # PHÂN HỆ ADMIN
        if st.session_state["role"] == "Admin":
            with tabs[1]:
                st.markdown("### 📊 DOANH THU THỰC TẾ REALTIME")
                st.markdown('<div class="the-quan-ly-flat">📊 BẤM NÚT TẢI DƯỚI ĐÂY ĐỂ ĐỌC BÁO CÁO MỚI NHẤT</div>', unsafe_allow_html=True)
                
                if st.button("🔄 TẢI/CẬP NHẬT DOANH THU REALTIME", use_container_width=True, type="primary"):
                    try:
                        cl = get_gspread_client()
                        ws_bc = cl.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"]).worksheet("BaoCao")
                        du_lieu = ws_bc.get_all_records()
                        if du_lieu:
                            df_bc = pd.DataFrame(du_lieu)
                            df_hien_thi = df_bc.tail(50).copy()
                            df_hien_thi.index = range(1, len(df_hien_thi) + 1)
                            df_hien_thi.index.name = "Stt"
                            st.dataframe(df_hien_thi, use_container_width=True)
                            
                            ngay_nay = get_now_vn().strftime("%d/%m/%Y")
                            df_h = df_bc[df_bc['Ngày'] == ngay_nay]
                            c1, c2, c3 = st.columns(3)
                            c1.metric("📊 TỔNG DOANH THU HÔM NAY", f"{df_h['Thành tiền'].sum():,.0f} đ")
                            c2.metric("🧾 TỔNG ĐƠN HÀNG", len(df_h))
                            c3.metric("💎 TRUNG BÌNH", f"{df_h['Thành tiền'].mean() if len(df_h)>0 else 0:,.0f} đ")
                        else: st.info("Chưa có dữ liệu báo cáo.")
                    except Exception as e: st.error(f"Lỗi giới hạn lệnh đọc: {e}")

            with tabs[2]:
                st.markdown("### ⚙️ HỆ THỐNG QUẢN TRỊ CAO CẤP")
                st.markdown('<div class="the-quan-ly-flat">🔗 LIÊN KẾT GOOGLE SHEET GỐC</div>', unsafe_allow_html=True)
                st.markdown(f"👉 **Đường dẫn quản lý:** [Bấm để mở file dữ liệu trên Google Sheets]({st.secrets['connections']['gsheets']['spreadsheet']})")
                
                if st.button("♻️ BẤM LÀM MỚI DANH MỤC & CÀI ĐẶT (CLEAR CACHE)"):
                    st.cache_data.clear()
                    st.success("Đã làm sạch bộ nhớ đệm! Danh mục và nhân viên đã được đồng bộ mới.")
                    time.sleep(0.5)
                    st.rerun()
                    
                st.markdown('<div class="the-quan-ly-flat">✍️ ĐĂNG KÝ TK “NHÂN VIÊN“</div>', unsafe_allow_html=True)
                try:
                    cl = get_gspread_client()
                    sh = cl.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
                    ws_user = sh.worksheet("NhanVien")
                    with st.form("add_user_form", clear_on_submit=True):
                        new_sdt = st.text_input("📱 Số điện thoại nhân viên (Tài khoản)")
                        new_code = st.text_input("🔑 Mã đăng nhập (Mật khẩu)")
                        new_name = st.text_input("🏷️ Tên nhân viên hiển thị")
                        if st.form_submit_button("👌 CẤP MÃ MỚI"):
                            if new_sdt and new_code and new_name:
                                ws_user.append_row([new_sdt.strip(), new_code.strip(), new_name.strip()])
                                st.success(f"Đã tạo tài khoản cho {new_name}!")
                                st.cache_data.clear()
                                time.sleep(0.5)
                                st.rerun()
                            else: st.error("Vui lòng không để trống thông tin!")
                    
                    st.write("📋 **Danh sách nhân sự:**")
                    raw_nv = get_nhan_vien_data()
                    if len(raw_nv) > 1: st.table(pd.DataFrame(raw_nv[1:], columns=raw_nv[0]))
                except Exception as e: st.error(f"Lỗi hệ thống nhân sự: {e}")
                
                st.divider()
                if st.button("🚪 THOÁT KHỎI HỆ THỐNG QUẢN TRỊ", use_container_width=True):
                    st.session_state.clear()
                    st.rerun()

if __name__ == "__main__":
    main()
