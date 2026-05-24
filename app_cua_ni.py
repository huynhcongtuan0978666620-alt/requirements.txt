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
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# =====================================================================
# 1. CẤU HÌNH GIAO DIỆN & STYLE CSS CAO CẤP (MINIMALIST & PREMIUM)
# =====================================================================
st.set_page_config(
    page_title="LKTV DETAILING - PREMIUM", 
    layout="centered", 
    page_icon="⚜️",
    initial_sidebar_state="collapsed"
)

def generate_css_animations():
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght=300;400;500;600;700&display=swap');

        html, body {
            font-family: 'Inter', '-apple-system', BlinkMacSystemFont, sans-serif !important;
            background-color: #fcfcfc !important; 
            overscroll-behavior-y: contain !important; 
        }

        .stApp {
            padding-top: 50px !important; 
            padding-bottom: 75px !important; 
            background-color: transparent !important;
        }

        header, footer, .stAppDeployButton, [data-testid="stStatusWidget"], [data-testid="stToolbar"],
        div[class*="stAppViewerToolbar"], div[data-testid="stAppViewerToolbar"], footer + div,
        div[data-testid="stViewerToolbar"], .stViewerToolbar, [data-testid="stManageAppTR"],
        div[class^="StyledViewerBottomBar"] {
            display: none !important; visibility: hidden !important; height: 0 !important; width: 0 !important; opacity: 0 !important; pointer-events: none !important;
        }

        .banner-top, .banner-bottom {
            position: fixed !important; left: 0 !important; right: 0 !important; height: 40px !important;
            background: #ffffff !important; color: #111111 !important; font-size: 13px !important; font-weight: 600 !important; 
            letter-spacing: 2px !important; display: flex !important; align-items: center !important; justify-content: center !important; 
            z-index: 999999 !important; border-bottom: 1px solid #eaeaea !important; 
        }
        .banner-top { top: 0px !important; }
        .banner-bottom { bottom: 0 !important; top: auto !important; border-top: 1px solid #eaeaea !important; border-bottom: none !important; justify-content: flex-start !important; padding-left: 20px !important; }

        .bang-hieu-lktv {
            text-align: center; margin-bottom: 30px !important; padding: 30px !important; border-radius: 12px !important;
            background: #ffffff !important; color: #111111 !important; 
            box-shadow: 0px 4px 24px rgba(0,0,0,0.04) !important; border: 1px solid #f0f0f0 !important;
        }
        .logo-img { 
            width: 90px !important; height: 90px !important; object-fit: cover !important; border-radius: 50% !important; 
            border: 2px solid #eaeaea !important; margin: 0 auto 15px auto !important; display: block !important;
        }
        .ten-tiem { font-size: 22px !important; font-weight: 700 !important; color: #111111 !important; text-transform: uppercase !important; margin-bottom: 4px !important; letter-spacing: 3px !important; }
        .thong-tin-phu { font-size: 13px !important; color: #666666 !important; margin: 4px 0 !important; font-weight: 400; }
        .slogan { font-size: 13px !important; color: #888888 !important; font-style: italic !important; margin-top: 15px !important; }
        
        [data-testid="stTabs"] [role="tablist"] { gap: 0 !important; border-bottom: 1px solid #eaeaea !important; margin-bottom: 25px !important; }
        button[data-baseweb="tab"] {
            background-color: transparent !important; border-radius: 0 !important; padding: 12px 20px !important; 
            border: none !important; border-bottom: 2px solid transparent !important; transition: all 0.2s ease !important;
        }
        button[data-baseweb="tab"] p { color: #888888 !important; font-size: 14px !important; font-weight: 600 !important; }
        button[data-baseweb="tab"][aria-selected="true"] { border-bottom: 2px solid #111111 !important; }
        button[data-baseweb="tab"][aria-selected="true"] p { color: #111111 !important; }

        .the-quan-ly-flat { color: #111; font-weight: 600; font-size: 15px; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 1px; border-bottom: 1px solid #eaeaea; padding-bottom: 8px;}
        .nhan-tieu-de { font-size: 11px !important; font-weight: 600 !important; margin-bottom: 8px !important; text-transform: uppercase !important; color: #666 !important; letter-spacing: 0.5px; text-align: center;}
        
        .box-chung {
            background-color: #ffffff; padding: 15px 10px; border-radius: 8px; text-align: center; 
            border: 1px solid #eaeaea; font-size: 18px; font-weight: 700; box-shadow: 0 2px 8px rgba(0,0,0,0.02);
            word-wrap: break-word;
        }
        .tong-don-box { color: #111111; }
        .chiet-khau-box { color: #d93025; } 
        .khach-tra-box { background-color: #111111; color: #ffffff; border: none; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        .tien-thua-box { background-color: #f8f9fa; color: #111; padding: 18px; border-radius: 8px; text-align: center; font-size: 18px; font-weight: 700; border: 1px solid #eaeaea; margin: 20px 0; }

        div[data-testid="stButton"] button { border-radius: 6px !important; font-weight: 600 !important; transition: all 0.2s !important; }
        div[data-testid="stButton"] button[kind="primary"] { background-color: #111111 !important; color: #ffffff !important; border: none !important; }
        div[data-testid="stButton"] button[kind="primary"]:hover { background-color: #333333 !important; box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important; }

        .hoa-don-khung { background-color: #ffffff !important; color: #333333 !important; padding: 30px 25px !important; border-radius: 8px !important; border: 1px solid #e0e0e0 !important; box-shadow: 0px 10px 30px rgba(0,0,0,0.05) !important; margin-top: 20px !important; }
        .hd-header { text-align: center; border-bottom: 1px solid #eaeaea; padding-bottom: 15px; margin-bottom: 20px; }
        .hd-title { font-size: 18px; text-transform: uppercase; margin-top: 10px; letter-spacing: 2px; font-weight: 700; color: #111111; }
        
        .hd-row-item { display: flex !important; justify-content: space-between !important; align-items: flex-start !important; margin-bottom: 12px !important; font-size: 14px !important; width: 100% !important; }
        .hd-item-name { flex: 1 !important; padding-right: 15px !important; text-align: left !important; color: #444; }
        .hd-item-price { text-align: right !important; white-space: nowrap !important; font-weight: 600 !important; color: #111; }
        .hd-items { border-bottom: 1px solid #eaeaea; padding-bottom: 15px; margin-bottom: 15px; }

        .lsc-shake { background-color: #fff1f0; color: #cf1322; padding: 12px; border-radius: 6px; border: 1px solid #ffa39e; text-align: center; font-size: 13px; margin-bottom: 15px; }

        .firework-container { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: 9999999; overflow: hidden; background: transparent; }
        .css-particle { position: absolute; width: 4px; height: 4px; border-radius: 50%; opacity: 0; animation: explode-mega 3.0s ease-out 2 forwards; }
        @keyframes explode-mega { 0% { transform: translate(0, 0); opacity: 0; } 20% { opacity: 0.8; } 100% { transform: translate(var(--cx), var(--cy)) scale(0.1); opacity: 0; } }
        
        .balloon-container-css { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: 9999998; overflow: hidden; }
        .fixed-balloon { position: absolute; bottom: -100px; border-radius: 50% 50% 50% 50% / 40% 40% 60% 60%; opacity: 0.6; animation: fly-up-skywards-pure linear forwards; }
        @keyframes fly-up-skywards-pure { 0% { transform: translateY(110vh); opacity: 0; } 10% { opacity: 0.6; } 90% { opacity: 0.6; } 100% { transform: translateY(-120vh); opacity: 0; } }
    </style>
    """

def render_fireworks_html():
    colors = ['#d4af37', '#111111', '#cccccc']
    html_particles = '<div class="firework-container">'
    centers = [(25, 20), (50, 15), (75, 20)]
    for cx, cy in centers:
        for i in range(50): 
            angle = random.uniform(0, 2 * 3.14159)
            distance = random.uniform(30, 150)
            target_x = int(math.cos(angle) * distance)
            target_y = int(math.sin(angle) * distance)
            color = random.choice(colors)
            delay = round(random.uniform(0, 0.1), 2)
            html_particles += f'<div class="css-particle" style="background-color: {color}; left: {cx}vw; top: {cy}vh; --cx: {target_x}px; --cy: {target_y}px; animation-delay: {delay}s;"></div>'
    html_particles += '</div>'
    return html_particles

def render_balloons_html():
    colors = ['#e0e0e0', '#f5f5f5', '#d4af37']
    html_balloons = '<div class="balloon-container-css">'
    for i in range(20):
        left_pos = random.uniform(5, 95)
        color = random.choice(colors)
        size_ratio = random.uniform(0.6, 1.0)
        width = int(40 * size_ratio)
        height = int(55 * size_ratio)
        delay = round(random.uniform(0.0, 2.0), 2)
        duration = round(random.uniform(4.0, 6.0), 2)
        html_balloons += f'<div class="fixed-balloon" style="background-color: {color}; left: {left_pos}vw; width: {width}px; height: {height}px; animation-delay: {delay}s; animation-duration: {duration}s;"></div>'
    html_balloons += '</div>'
    st.markdown(html_balloons, unsafe_allow_html=True)

st.markdown(generate_css_animations(), unsafe_allow_html=True)

st.markdown("""
<div class="banner-top">HỆ THỐNG QUẢN LÝ DỊCH VỤ</div>
<div class="banner-bottom">SALON KIM HIỀN © 2026</div>
""", unsafe_allow_html=True)

# =====================================================================
# 2. HÀM CORE KẾT NỐI (TỐI ƯU HÓA CACHE CHỐNG LỖI QUOTA 429)
# =====================================================================
def get_now_vn():
    return datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))

@st.cache_resource
def get_gspread_client():
    """Tạo kết nối duy nhất, tránh khởi tạo lại nhiều lần gây nghẽn băng thông"""
    creds_info = st.secrets["connections"]["gsheets"]["spreadsheet_credentials"] if "spreadsheet_credentials" in st.secrets["connections"]["gsheets"] else st.secrets["connections"]["gsheets"]
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    return gspread.authorize(Credentials.from_service_account_info(creds_info, scopes=scope))

def format_drive_direct_url(link):
    if not link or not isinstance(link, str): return ""
    match = re.search(r'(pires=|/d/|id=)([a-zA-Z0-9-_]{33,40})', link.strip())
    return f"https://lh3.googleusercontent.com/d/{match.group(2)}" if match else ""

@st.cache_data(ttl=3600)
def get_settings():
    try:
        client = get_gspread_client()
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        rows = client.open_by_url(url).worksheet("ThietLap").get_all_values()
        return {str(row[0]).strip(): str(row[1]).strip() for row in rows if len(row) > 1}
    except Exception:
        return {"TenTiem": "SALON KIM HIỀN", "Diachi": "131, TRẦN BÌNH TRỌNG, LONG XUYÊN", "SDT": "0947.58.1516", "Slogan": "Nơi Bạn Đặt Niềm Tin"}

@st.cache_data(ttl=3600)
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

@st.cache_data(ttl=3600)
def get_nhan_vien_data():
    try:
        client = get_gspread_client()
        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        return sh.worksheet("NhanVien").get_all_values()
    except Exception: return []

@st.cache_data(ttl=60)
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
                if sdt_raw: ds_kh[sdt_raw] = ten_kh
        return ds_kh
    except Exception: return {}

def luu_bill_tam(gio_hang, nhan_vien, kh_sdt="", kh_ten="Khách lẻ"):
    try:
        client = get_gspread_client()
        ws = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"]).worksheet("BillTam")
        chi_tiet = " | ".join([f"{item['dich_vu']} (x{item['so_luong']})" for item in gio_hang])
        tong_tien = sum([item['thanh_tien'] for item in gio_hang])
        
        ws.append_row([
            get_now_vn().strftime("%Y-%m-%d %H:%M:%S"), 
            chi_tiet, 
            tong_tien, 
            nhan_vien, 
            str(kh_sdt).strip(), 
            str(kh_ten).strip(), 
            "CHỜ XỬ LÝ"
        ])
        return True
    except Exception as e:
        st.error(f"Lỗi lưu nháp: {e}")
        return False

def xoa_bill_tam_dong_gốc(index_sheet_row):
    try:
        client = get_gspread_client()
        ws = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"]).worksheet("BillTam")
        ws.delete_rows(index_sheet_row)
        return True
    except Exception as e:
        st.error(f"Lỗi xóa bill tạm trên Sheets: {e}")
        return False

def display_header(settings):
    direct_logo_url = format_drive_direct_url(settings.get('Logo', ''))
    fallback_gif = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
    st.markdown(f"""
        <div class="bang-hieu-lktv">
            <img src="{direct_logo_url}" class="logo-img" onerror="this.onerror=null;this.src='{fallback_gif}';">
            <div class="ten-tiem">{settings.get('TenTiem', 'SALON KIM HIỀN')}</div>
            <div class="thong-tin-phu">{settings.get('Diachi', '131, TRẦN BÌNH TRỌNG')}</div>
            <div class="thong-tin-phu">Hotline: {settings.get('SDT', '0947.58.1516')}</div>
            <div class="slogan">{settings.get('Slogan', 'Nơi Bạn Đặt Niềm Tin')}</div>
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
        msg['Subject'] = f"ĐH DỊCH VỤ - {gio_vn_mail}"
        msg.attach(MIMEText(noi_dung, 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        server.send_message(msg)
        server.quit()
    except Exception: pass

def gui_telegram_notification(noi_dung):
    try:
        bot_token = st.secrets["telegram"]["bot_token"]
        chat_id = st.secrets["telegram"]["chat_id"]
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": noi_dung, "parse_mode": "Markdown"}, timeout=10)
    except Exception: pass

# =====================================================================
# 3. LUỒNG ĐIỀU HƯỚNG CHÍNH
# =====================================================================
def main():
    init_states = {
        "last_submit": None, "submit_count": 0, "submitting": False, 
        "logged_in": False, "role": None, "full_name": None, "gio_hang": [], 
        "bill_vua_in": None, "trigger_boom": False, "trigger_balloons": False,
        "kh_sdt_val": "", "kh_ten_val": "Khách lẻ"
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

    # --- ĐĂNG NHẬP ---
    if not st.session_state["logged_in"]:
        display_header(settings)
        with st.form("login_section"):
            st.markdown("<div class='the-quan-ly-flat' style='text-align: center; border:none;'>ĐĂNG NHẬP HỆ THỐNG</div>", unsafe_allow_html=True)
            u = st.text_input("Tài khoản (Số điện thoại)")
            p = st.text_input("Mật khẩu", type="password")
            
            if st.form_submit_button("Xác nhận", use_container_width=True, type="primary"):
                if u == "admin" and p == "2026":
                    st.session_state.update({"logged_in": True, "role": "Admin", "full_name": "Quản lý", "trigger_balloons": True})
                    st.rerun()
                else:
                    raw_data = get_nhan_vien_data()
                    if len(raw_data) > 0:
                        headers = [str(h).strip() for h in raw_data[0]]
                        col_sdt_idx = next((i for i, h in enumerate(headers) if 'số điện thoại' in h.lower() or 'sđt' in h.lower() or 'tai khoan' in h.lower()), -1)
                        col_mk_idx = next((i for i, h in enumerate(headers) if 'mật khẩu' in h.lower() or 'mat khau' in h.lower() or 'code' in h.lower()), -1)
                        col_ten_idx = next((i for i, h in enumerate(headers) if 'tên' in h.lower() or 'nhân viên' in h.lower()), -1)
                        
                        found_row = None
                        sdt_nhap = str(u).strip().lstrip('0')
                        for r in raw_data[1:]:
                            if len(r) > max(col_sdt_idx, col_mk_idx):
                                if sdt_nhap == str(r[col_sdt_idx]).strip().lstrip('0') and p.strip() == str(r[col_mk_idx]).strip() and sdt_nhap != "":
                                    found_row = r
                                    break
                                    
                        if found_row:
                            ten_that = str(found_row[col_ten_idx]).strip() if col_ten_idx != -1 and col_ten_idx < len(found_row) else "Nhân viên"
                            st.session_state.update({"logged_in": True, "role": "NhanVien", "full_name": ten_that, "trigger_balloons": True})
                            time.sleep(0.3)
                            st.rerun()
                        else: st.error("Thông tin đăng nhập không chính xác.")
                    else: st.error("Lỗi dữ liệu nhân viên hoặc đang bị nghẽn mạng Google.")
        
        if st.button("Làm mới ứng dụng", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # --- TRANG CHỦ ---
    else:
        display_header(settings)
        t_list = ["TẠO ĐƠN HÀNG", "BILL CHỜ", "BÁO CÁO", "CÀI ĐẶT"] if st.session_state["role"] == "Admin" else ["TẠO ĐƠN HÀNG"]
        tabs = st.tabs(t_list)

        services = get_service_data()
        dv_list = list(services.keys())

        # =================================================================
        # TAB 1: TẠO ĐƠN HÀNG
        # =================================================================
        with tabs[0]:
            st.markdown(f"<div style='text-align: right; font-size: 13px; color: #666; margin-bottom: 15px;'>Nhân viên: <b>{st.session_state.full_name}</b> | {get_now_vn().strftime('%H:%M %d/%m')}</div>", unsafe_allow_html=True)
            
            st.markdown('<div class="the-quan-ly-flat">THÔNG TIN KHÁCH HÀNG</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1: 
                kh_sdt = st.text_input("Số điện thoại", value=st.session_state.kh_sdt_val)
                if kh_sdt != st.session_state.kh_sdt_val:
                    st.session_state.kh_sdt_val = kh_sdt
                    sdt_nhap_so = kh_sdt.strip()
                    if sdt_nhap_so:
                        ds_kh = get_khach_hang_data()
                        sdt_khong_0 = sdt_nhap_so[1:] if sdt_nhap_so.startswith('0') else sdt_nhap_so
                        sdt_co_0 = '0' + sdt_nhap_so if not sdt_nhap_so.startswith('0') else sdt_nhap_so
                        
                        if sdt_nhap_so in ds_kh: st.session_state.kh_ten_val = ds_kh[sdt_nhap_so]
                        elif sdt_khong_0 in ds_kh: st.session_state.kh_ten_val = ds_kh[sdt_khong_0]
                        elif sdt_co_0 in ds_kh: st.session_state.kh_ten_val = ds_kh[sdt_co_0]
                        else: st.session_state.kh_ten_val = "" 
                    else: st.session_state.kh_ten_val = "Khách lẻ"
                    st.rerun() 
                    
            with c2: 
                kh_ten = st.text_input("Tên khách hàng", value=st.session_state.kh_ten_val)
                if kh_ten != st.session_state.kh_ten_val: st.session_state.kh_ten_val = kh_ten

            st.write("")
            
            st.markdown('<div class="the-quan-ly-flat">LÊN ĐƠN DỊCH VỤ / SẢN PHẨM</div>', unsafe_allow_html=True)
            col_dv, col_sl = st.columns([7, 3])
            with col_dv:
                box_chon_dv = st.selectbox(
                    "Chọn dịch vụ...", 
                    options=dv_list if dv_list else ["Không có dữ liệu hoặc Google Sheets đang bận..."], 
                    index=None,
                    placeholder="Ví dụ: Gội đầu, Cắt tóc..."
                )
            with col_sl:
                box_sl = st.number_input("Số lượng", min_value=0.5, max_value=5.0, value=1.0, step=0.5, key="main_sl_input")
            
            if st.button("➕ THÊM VÀO GIỎ HÀNG", type="primary", use_container_width=True):
                if not box_chon_dv or "Không có dữ liệu" in box_chon_dv:
                    st.warning("⚠️ Vui lòng chọn dịch vụ trước khi thêm.")
                else:
                    if any(item["dich_vu"] == box_chon_dv for item in st.session_state.gio_hang):
                        st.toast("⚠️ Dịch vụ này đã có trong giỏ hàng rồi ní!")
                    else:
                        info_dv = services.get(box_chon_dv, {"gia": 0.0, "hoa_hong": 0.0})
                        gia_goc = info_dv.get("gia", 0.0)
                        phan_tram_hh = info_dv.get("hoa_hong", 0.0)
                        t_bill_item = gia_goc * box_sl
                        
                        st.session_state.gio_hang.append({
                            "dich_vu": box_chon_dv, "so_luong": box_sl, "don_gia": gia_goc,
                            "thanh_tien": t_bill_item, "phan_tram_hh": phan_tram_hh
                        })
                        st.session_state.bill_vua_in = None
                        st.toast(f"✅ Đã thêm: {box_chon_dv}")
                        time.sleep(0.3)
                        st.rerun()

            t_bill = 0.0
            if st.session_state.gio_hang:
                st.write("")
                st.markdown(f"**Danh sách dịch vụ ({len(st.session_state.gio_hang)})**")
                for idx, item in enumerate(st.session_state.gio_hang):
                    col_item1, col_item2, col_item3 = st.columns([5.5, 3.0, 1.5])
                    with col_item1: st.markdown(f"<span style='font-size:14px'>{item['dich_vu']} (x{item['so_luong']})</span>", unsafe_allow_html=True)
                    with col_item2: st.markdown(f"<span style='font-size:14px; font-weight:600;'>{item['thanh_tien']:,.0f}đ</span>", unsafe_allow_html=True)
                    with col_item3:
                        if st.button("Xóa", key=f"del_{idx}"):
                            st.session_state.gio_hang.pop(idx)
                            st.session_state.bill_vua_in = None
                            st.rerun()
                    t_bill += item['thanh_tien']

                st.write("")
                if st.button("💾 LƯU NHÁP VÀO BILL CHỜ (CHO THỢ)", use_container_width=True):
                    if luu_bill_tam(st.session_state.gio_hang, st.session_state.full_name, st.session_state.kh_sdt_val, st.session_state.kh_ten_val):
                        st.session_state.gio_hang = []
                        st.session_state.kh_sdt_val = ""
                        st.session_state.kh_ten_val = "Khách lẻ"
                        st.toast("✅ Đã lưu nháp thành công!")
                        time.sleep(1)
                        st.rerun()

            if t_bill > 0:
                st.write("")
                st.markdown('<div class="the-quan-ly-flat">THU NGÂN</div>', unsafe_allow_html=True)
                
                col_nhap1, col_nhap2 = st.columns(2)
                with col_nhap1:
                    tien_giam = st.number_input("Chiết khấu (VND)", min_value=0.0, max_value=float(t_bill), value=0.0, step=1000.0)
                with col_nhap2:
                    khuyen_mai = st.number_input("Khuyến mãi (VND)", min_value=0.0, max_value=float(t_bill), value=0.0, step=1000.0)
                
                ghi_chu = st.text_input("Ghi chú hóa đơn")
                
                tong_tru_gia = tien_giam + khuyen_mai
                t_khach_tra = max(0.0, t_bill - tong_tru_gia)
                he_so_giam = t_khach_tra / t_bill if t_bill > 0 else 1.0
                t_cong_tho_chinh_xac = sum(item['thanh_tien'] * he_so_giam * (item['phan_tram_hh'] / 100.0) for item in st.session_state.gio_hang)
                
                st.write("")
                col_bill1, col_bill2, col_bill3, col_bill4 = st.columns(4)
                with col_bill1: st.markdown(f'<div class="nhan-tieu-de">Tổng bill</div><div class="box-chung tong-don-box">{t_bill:,.0f}</div>', unsafe_allow_html=True)
                with col_bill2: st.markdown(f'<div class="nhan-tieu-de">Chiết khấu</div><div class="box-chung chiet-khau-box">{tien_giam:,.0f}</div>', unsafe_allow_html=True)
                with col_bill3: st.markdown(f'<div class="nhan-tieu-de">Khuyến mãi</div><div class="box-chung chiet-khau-box">{khuyen_mai:,.0f}</div>', unsafe_allow_html=True)
                with col_bill4: st.markdown(f'<div class="nhan-tieu-de">Thực thu</div><div class="box-chung khach-tra-box">{t_khach_tra:,.0f}</div>', unsafe_allow_html=True)
                
                st.markdown(f'<div style="text-align:right; font-size:13px; color:#888; margin-top:8px;">Hoa hồng dịch vụ: <b>{t_cong_tho_chinh_xac:,.0f}đ</b></div>', unsafe_allow_html=True)
                
                st.write("")
                kh_dua = st.number_input("Tiền khách đưa", 0.0, value=float(t_khach_tra))
                t_du = kh_dua - t_khach_tra
                
                if t_du > 0:
                    st.markdown(f'<div class="tien-thua-box">Tiền thối lại: <span>{t_du:,.0f} VND</span></div>', unsafe_allow_html=True)

                can_go = True
                if st.session_state["role"] == "NhanVien" and st.session_state.last_submit:
                    tg_cho = (get_now_vn() - st.session_state.last_submit).total_seconds() / 60
                    han_muc = 1 if st.session_state.submit_count == 1 else 2 if st.session_state.submit_count >= 2 else 0
                    if tg_cho < han_muc:
                        can_go = False
                        st.markdown(f'<div class="lsc-shake">Vui lòng chờ {round(han_muc - tg_cho, 1)} phút để tạo đơn tiếp theo.</div>', unsafe_allow_html=True)

                if can_go:
                    cam_ket = st.checkbox("Xác nhận thông tin chính xác")
                    if not st.session_state.submitting:
                        if st.button("Xác nhận & Lưu hóa đơn", use_container_width=True, type="primary"):
                            if cam_ket:
                                st.session_state.submitting = True
                                st.rerun()
                            else: st.warning("Vui lòng tích chọn xác nhận.")
                    else:
                        st.button("Đang đồng bộ dữ liệu...", disabled=True, use_container_width=True)
                        try:
                            cl = get_gspread_client()
                            ws = cl.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"]).worksheet("BaoCao")
                            bay_gio = get_now_vn()
                            ma_hd = f"HD{bay_gio.strftime('%y%m%d%H%M')}"
                            
                            rows_to_append = []
                            html_items = ""
                            chi_tiet_tele = "" 
                            
                            chot_ten = st.session_state.kh_ten_val.strip() if st.session_state.kh_ten_val.strip() else "Khách lẻ"
                            chot_sdt = st.session_state.kh_sdt_val.strip()
                            chuoi_ghi_chu = f"[CK: {tien_giam:,.0f} | KM: {khuyen_mai:,.0f}] " + ghi_chu
                            
                            for idx, item in enumerate(st.session_state.gio_hang):
                                hoa_hong_tung_dong = item['thanh_tien'] * he_so_giam * (item['phan_tram_hh'] / 100.0)
                                rows_to_append.append([
                                    bay_gio.strftime("%d/%m/%Y"), st.session_state.full_name, chot_ten, chot_sdt,
                                    item['dich_vu'], item['so_luong'], item['don_gia'], item['thanh_tien'],
                                    bay_gio.strftime("%H:%M:%S"), chuoi_ghi_chu, hoa_hong_tung_dong, ma_hd
                                ])
                                html_items += f"""
                                <div class="hd-row-item">
                                    <div class="hd-item-name">{item["dich_vu"]} (x{item["so_luong"]})</div>
                                    <div class="hd-item-price">{item["thanh_tien"]:,.0f}</div>
                                </div>"""
                                chi_tiet_tele += f"\n- {item['dich_vu']} (x{int(item['so_luong'])}): {item['thanh_tien']:,.0f}đ"
                            
                            ws.append_rows(rows_to_append)
                            
                            if chot_sdt and chot_sdt != "":
                                ds_kh_hien_tai = get_khach_hang_data()
                                sdt_khong_0 = chot_sdt[1:] if chot_sdt.startswith('0') else chot_sdt
                                sdt_co_0 = '0' + chot_sdt if not chot_sdt.startswith('0') else chot_sdt
                                is_sdt_cu = (chot_sdt in ds_kh_hien_tai) or (sdt_khong_0 in ds_kh_hien_tai) or (sdt_co_0 in ds_kh_hien_tai)
                                
                                if not is_sdt_cu and chot_ten != "Khách lẻ" and chot_ten != "":
                                    ws_kh = cl.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"]).worksheet("KhachHang")
                                    ws_kh.append_row([chot_sdt, chot_ten])
                                    st.cache_data.clear() 
                            
                            noi_dung_mail = (
                                f"THÔNG BÁO\n"
                                f"Đã thanh toán ĐƠN HÀNG\n"
                                f" \n"
                                f"=====================\n"
                                f" \n"
                                f"Mã ĐH: {ma_hd} | {bay_gio.strftime('%d/%m/%Y %H:%M')}\n"
                                f"Khách hàng: {chot_ten} - {chot_sdt}\n"
                                f"Nhân viên: {st.session_state.full_name}\n"
                                f" \n"
                                f"=====================\n"
                                f" \n"
                                f"Dịch vụ:{chi_tiet_tele}\n"
                                f" \n"
                                f"=====================\n"
                                f" \n"
                                f"Tổng bill: {t_bill:,.0f} đ\n"
                                f"Chiết khấu: -{tien_giam:,.0f} đ\n"
                                f"Khuyến mãi: -{khuyen_mai:,.0f} đ\n"
                                f" \n"
                                f"=====================\n"
                                f" \n"
                                f"THỰC THU: {t_khach_tra:,.0f} đ\n"
                                f" \n"
                                f"=====================\n"
                                f" \n"
                                f"Cảm ơn quý khách đã sử dụng dịch vụ!\n"
                            )
                            gui_email_backup(noi_dung_mail)
                            gui_telegram_notification(noi_dung_mail)

                            st.session_state.bill_vua_in = f"""
                            <div class="hoa-don-khung">
                                <div class="hd-header">
                                    <div style="font-size: 18px; font-weight: 800;">{settings.get('TenTiem', 'SALON KIM HIỀN')}</div>
                                    <div style="font-size: 13px; color: #666; margin-top:4px;">{settings.get('Diachi', '')}</div>
                                    <div style="font-size: 13px; color: #666;">SĐT: {settings.get('SDT', '')}</div>
                                    <div class="hd-title">HÓA ĐƠN DỊCH VỤ</div>
                                    <div style="font-size: 12px; color: #888; margin-top:5px;">Mã số: {ma_hd}</div>
                                </div>
                                <div style="border-bottom: 1px solid #eaeaea; padding-bottom: 10px; margin-bottom: 15px; font-size: 14px; color: #444;">
                                    <div style="display: flex; justify-content: space-between; margin-bottom: 6px;"><span>Ngày:</span> <span>{bay_gio.strftime('%d/%m/%Y %H:%M')}</span></div>
                                    <div style="display: flex; justify-content: space-between; margin-bottom: 6px;"><span>Khách hàng:</span> <span style="font-weight:600;">{chot_ten}</span></div>
                                    <div style="display: flex; justify-content: space-between;"><span>Nhân viên:</span> <span>{st.session_state.full_name}</span></div>
                                </div>
                                <div class="hd-items">{html_items}</div>
                                <div style="font-size: 14px; border-bottom: 1px solid #eaeaea; padding-bottom: 10px; margin-bottom: 15px;">
                                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;"><span>Cộng tiền:</span> <span>{t_bill:,.0f}</span></div>
                                    <div style="display: flex; justify-content: space-between; color: #d93025; margin-bottom: 8px;"><span>Chiết khấu:</span> <span>-{tien_giam:,.0f}</span></div>
                                    <div style="display: flex; justify-content: space-between; color: #d93025;"><span>Khuyến mãi:</span> <span>-{khuyen_mai:,.0f}</span></div>
                                </div>
                                <div style="font-size: 15px; font-weight: 700;">
                                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 18px;"><span>TỔNG CỘNG:</span> <span>{t_khach_tra:,.0f}</span></div>
                                </div>
                                <div style="text-align: center; margin-top: 25px; font-size: 13px; color: #888;">
                                    Cảm ơn quý khách đã sử dụng dịch vụ!
                                </div>
                            </div>"""

                            st.session_state.update({
                                "gio_hang": [], "last_submit": bay_gio, "submit_count": st.session_state.submit_count + 1, 
                                "submitting": False, "trigger_boom": True, "kh_sdt_val": "", "kh_ten_val": "Khách lẻ"
                            })
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Hệ thống bận (Google Quota), vui lòng thử lại sau 30 giây: {e}")
                            st.session_state.submitting = False

            if st.session_state.bill_vua_in:
                st.markdown(st.session_state.bill_vua_in, unsafe_allow_html=True)

            st.write("")
            if st.button("Đăng xuất", use_container_width=True):
                st.session_state.clear()
                st.rerun()

        # =================================================================
        # TAB 2 & 3 & 4 DÀNH CHO ADMIN
        # =================================================================
        if st.session_state["role"] == "Admin":
            with tabs[1]:
                st.markdown('<div class="the-quan-ly-flat">QUẢN LÝ BILL CHỜ</div>', unsafe_allow_html=True)
                if st.button("🔄 Làm mới danh sách bill", use_container_width=True):
                    st.rerun()
                    
                try:
                    ws_tam = get_gspread_client().open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"]).worksheet("BillTam")
                    data_tam = ws_tam.get_all_values()
                    
                    if len(data_tam) > 1:
                        rows_tam = data_tam[1:]
                        st.write(f"Đang có **{len(rows_tam)}** đơn hàng chờ xử lý:")
                        
                        for i, row in enumerate(rows_tam):
                            sheet_row_idx = i + 2 
                            cleaned_row = [str(cell).strip() for cell in row]
                            valid_indices = [idx for idx, cell in enumerate(cleaned_row) if cell != ""]
                            
                            if not valid_indices: continue
                                
                            start_idx = valid_indices[0] 
                            real_data = cleaned_row[start_idx:]
                            
                            t_tao_str = real_data[0] if len(real_data) > 0 else ""
                            chi_tiet_dv = real_data[1] if len(real_data) > 1 else ""
                            t_tien_str = real_data[2] if len(real_data) > 2 else "0"
                            tho_lam = real_data[3] if len(real_data) > 3 else "Chưa rõ"
                            sdt_kh = real_data[4] if len(real_data) > 4 else ""
                            ten_kh = real_data[5] if len(real_data) > 5 else "Khách lẻ"
                            
                            if not t_tien_str: t_tien_str = "0"
                            t_status = "✅ Mới tạo"
                            
                            with st.container(border=True):
                                col_info, col_act = st.columns([7, 3])
                                with col_info:
                                    st.markdown(f"👤 **Khách hàng:** {ten_kh} ({sdt_kh if sdt_kh else 'Không có SĐT'})")
                                    st.markdown(f"🛠 **Dịch vụ:** `{chi_tiet_dv}`")
                                    try:
                                        tien_float = float(t_tien_str.replace(',','').replace('.',''))
                                        st.markdown(f"💰 **Tạm tính:** `{tien_float:,.0f}đ` | 🤝 **Thợ:** {tho_lam}")
                                    except:
                                        st.markdown(f"💰 **Tạm tính:** `{t_tien_str}đ` | 🤝 **Thợ:** {tho_lam}")
                                
                                with col_act:
                                    st.write("")
                                    if st.button("🛒 Nạp & Tính tiền", key=f"load_bill_{sheet_row_idx}", use_container_width=True, type="primary"):
                                        with st.spinner("Đang chuyển dữ liệu..."):
                                            new_gio_hang = []
                                            items = chi_tiet_dv.split(" | ")
                                            for item in items:
                                                if item.strip():
                                                    match_dv = re.match(r"(.+)\s*\(x([\d\.]+)\)", item.strip())
                                                    if match_dv:
                                                        t_dv = match_dv.group(1).strip()
                                                        s_luong = float(match_dv.group(2))
                                                        
                                                        info_goc = services.get(t_dv, {"gia": 0.0, "hoa_hong": 0.0})
                                                        g_goc = info_goc.get("gia", 0.0)
                                                        p_hh = info_goc.get("hoa_hong", 0.0)
                                                        
                                                        new_gio_hang.append({
                                                            "dich_vu": t_dv, "so_luong": s_luong, "don_gia": g_goc,
                                                            "thanh_tien": g_goc * s_luong, "phan_tram_hh": p_hh
                                                        })
                                            
                                            st.session_state.gio_hang = new_gio_hang
                                            st.session_state.kh_sdt_val = sdt_kh
                                            st.session_state.kh_ten_val = ten_kh
                                            st.session_state.bill_vua_in = None
                                            
                                            if xoa_bill_tam_dong_gốc(sheet_row_idx):
                                                st.toast("⚡ Đã nạp đơn sang mục 👉 TẠO ĐƠN HÀNG")
                                                time.sleep(0.5)
                                                st.rerun()
                    else:
                        st.info("Hiện không có đơn hàng chờ nào.")
                except Exception as e:
                    st.error(f"Google đang bận, ní chờ vài giây rồi bấm [Làm mới] lại nha: {e}")

            with tabs[2]:
                st.markdown('<div class="the-quan-ly-flat">BÁO CÁO TỔNG HỢP</div>', unsafe_allow_html=True)
                if st.button("Cập nhật dữ liệu báo cáo", use_container_width=True):
                    try:
                        cl = get_gspread_client()
                        ws_bc = cl.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"]).worksheet("BaoCao")
                        du_lieu = ws_bc.get_all_records()
                        if du_lieu:
                            df_bc = pd.DataFrame(du_lieu)
                            df_hien_thi = df_bc.tail(50).copy()
                            df_hien_thi.index = range(1, len(df_hien_thi) + 1)
                            st.dataframe(df_hien_thi, use_container_width=True)
                        else: st.info("Dữ liệu trống.")
                    except Exception: st.error("Tạm thời không thể kết nối Google Sheets để lấy báo cáo. Thử lại sau ít phút.")

            with tabs[3]:
                st.markdown('<div class="the-quan-ly-flat">QUẢN TRỊ HỆ THỐNG</div>', unsafe_allow_html=True)
                if st.button("Khôi phục ứng dụng (Clear Cache & Đồng bộ lại)"):
                    st.cache_data.clear()
                    st.success("Đã xóa bộ nhớ đệm thành công!")
                    time.sleep(0.5)
                    st.rerun()
                
                if st.button("Đăng xuất Admin", use_container_width=True):
                    st.session_state.clear()
                    st.rerun()

if __name__ == "__main__":
    main()
