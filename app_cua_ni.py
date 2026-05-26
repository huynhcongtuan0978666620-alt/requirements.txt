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
# 1. CẤU HÌNH GIAO DIỆN & STYLE CSS CAO CẤP CHUYỂN ĐỔI CHỦ ĐỀ (VISION V12.1)
# =====================================================================
st.set_page_config(
    page_title="LKTV DETAILING - VISION V12", 
    layout="centered", 
    page_icon="⚜️",
    initial_sidebar_state="collapsed"
)

def generate_css_animations(theme="light"):
    is_dark = (theme == "dark")
    bg_app = "#121212" if is_dark else "#fcfcfc"
    bg_box = "#1e1e1e" if is_dark else "#ffffff"
    text_color = "#ffffff" if is_dark else "#111111"
    border_color = "#333333" if is_dark else "#eaeaea"
    sub_text = "#aaaaaa" if is_dark else "#666666"
    
    return f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        html, body {{
            font-family: 'Inter', '-apple-system', BlinkMacSystemFont, sans-serif !important;
            background-color: {bg_app} !important; 
            color: {text_color} !important;
            overscroll-behavior-y: none !important; 
        }}
        
        html {{
            overscroll-behavior: none !important; 
        }}

        .stApp {{
            padding-top: 50px !important; 
            padding-bottom: 75px !important; 
            background-color: transparent !important;
        }}

        /* Giấu sạch menu và tàn dư giao diện thừa của Streamlit */
        header, footer, #MainMenu, .stAppDeployButton, [data-testid="stStatusWidget"], [data-testid="stToolbar"],
        div[class*="stAppViewerToolbar"], div[data-testid="stAppViewerToolbar"], footer + div,
        div[data-testid="stViewerToolbar"], .stViewerToolbar, [data-testid="stManageAppTR"],
        div[class^="StyledViewerBottomBar"] {{
            display: none !important; visibility: hidden !important; height: 0 !important; width: 0 !important; opacity: 0 !important; pointer-events: none !important;
        }}

        .banner-top, .banner-bottom {{
            position: fixed !important; left: 0 !important; right: 0 !important; height: 40px !important;
            background: {"#1e1e1e" if is_dark else "#ffffff"} !important; color: {text_color} !important; font-size: 13px !important; font-weight: 600 !important; 
            letter-spacing: 2px !important; display: flex !important; align-items: center !important; justify-content: center !important; 
            z-index: 999999 !important; border-bottom: 1px solid {border_color} !important; 
        }}
        .banner-top {{ top: 0px !important; }}
        .banner-bottom {{ bottom: 0 !important; top: auto !important; border-top: 1px solid {border_color} !important; border-bottom: none !important; justify-content: flex-start !important; padding-left: 20px !important; }}

        .bang-hieu-lktv {{
            display: flex !important; align-items: center !important; justify-content: flex-start !important; gap: 15px !important;
            margin-bottom: 20px !important; padding: 12px 15px !important; border-radius: 8px !important; background: {bg_box} !important; 
            box-shadow: 0px 2px 12px rgba(0,0,0,0.03) !important; border: 1px solid {border_color} !important;
        }}
        .logo-img {{ width: 55px !important; height: 55px !important; object-fit: cover !important; border-radius: 50% !important; border: 1px solid {border_color} !important; margin: 0 !important; display: block !important; }}
        .thong-tin-cum {{ text-align: left !important; }}
        .ten-tiem {{ font-size: 16px !important; font-weight: 700 !important; color: {text_color} !important; text-transform: uppercase !important; margin-bottom: 2px !important; letter-spacing: 1px !important; }}
        .thong-tin-phu {{ font-size: 11px !important; color: {sub_text} !important; margin: 1px 0 !important; font-weight: 400; line-height: 1.3; }}
        
        [data-testid="stTabs"] [role="tablist"] {{ gap: 0 !important; border-bottom: 1px solid {border_color} !important; margin-bottom: 25px !important; }}
        button[data-baseweb="tab"] {{ background-color: transparent !important; border-radius: 0 !important; padding: 12px 20px !important; border: none !important; border-bottom: 2px solid transparent !important; transition: all 0.2s ease !important; }}
        button[data-baseweb="tab"] p {{ color: {sub_text} !important; font-size: 14px !important; font-weight: 600 !important; }}
        button[data-baseweb="tab"][aria-selected="true"] {{ border-bottom: 2px solid {text_color} !important; }}
        button[data-baseweb="tab"][aria-selected="true"] p {{ color: {text_color} !important; }}

        .the-quan-ly-flat {{ color: {text_color}; font-weight: 600; font-size: 15px; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 1px; border-bottom: 1px solid {border_color}; padding-bottom: 8px;}}
        .nhan-tieu-de {{ font-size: 11px !important; font-weight: 600 !important; margin-bottom: 8px !important; text-transform: uppercase !important; color: {sub_text} !important; letter-spacing: 0.5px; text-align: center;}}
        
        .box-chung {{ background-color: {bg_box}; padding: 15px 10px; border-radius: 8px; text-align: center; border: 1px solid {border_color}; font-size: 18px; font-weight: 700; box-shadow: 0 2px 8px rgba(0,0,0,0.02); word-wrap: break-word; }}
        .tong-don-box {{ color: {text_color}; }}
        .chiet-khau-box {{ color: #d93025; }} 
        .khach-tra-box {{ background-color: {text_color}; color: {bg_box}; border: none; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
        .tien-thua-box {{ background-color: {"#2a2a2a" if is_dark else "#f8f9fa"}; color: {text_color}; padding: 18px; border-radius: 8px; text-align: center; font-size: 18px; font-weight: 700; border: 1px solid {border_color}; margin: 20px 0; }}

        div[data-testid="stButton"] button {{ border-radius: 6px !important; font-weight: 600 !important; transition: all 0.2s !important; }}
        div[data-testid="stButton"] button[kind="primary"] {{ background-color: {text_color} !important; color: {bg_box} !important; border: none !important; }}
        div[data-testid="stButton"] button[kind="primary"]:hover {{ background-color: {"#dddddd" if is_dark else "#333333"} !important; box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important; }}
        
        /* Đồng bộ nhãn font chữ cho Dark Mode */
        label p, div[data-testid="stMarkdownContainer"] p {{ color: {text_color} !important; }}
        div[data-testid="stPopover"] div[button] {{ border: none !important; }}

        .btn-zalo {{ display: block; width: 100%; text-align: center; padding: 12px; background-color: #0068ff; color: white !important; font-weight: 700; border-radius: 6px; text-decoration: none; margin-top: 15px; transition: all 0.2s; }}
        .btn-zalo:hover {{ background-color: #0055d4; }}

        .hoa-don-khung {{ background-color: {bg_box} !important; color: {text_color} !important; padding: 30px 25px !important; border-radius: 8px !important; border: 1px solid {border_color} !important; box-shadow: 0px 10px 30px rgba(0,0,0,0.05) !important; margin-top: 20px !important; }}
        .hd-header {{ text-align: center; border-bottom: 1px solid {border_color}; padding-bottom: 15px; margin-bottom: 20px; }}
        .hd-title {{ font-size: 18px; text-transform: uppercase; margin-top: 10px; letter-spacing: 2px; font-weight: 700; color: {text_color}; }}
        
        .hd-table-sanpham {{ width: 100% !important; border-collapse: collapse !important; margin: 10px 0 !important; }}
        .hd-table-sanpham tr {{ border-bottom: 1px dashed {border_color} !important; }}
        .hd-table-sanpham td {{ padding: 10px 0 !important; vertical-align: top !important; }}
        .hd-item-name {{ font-weight: 600 !important; color: {text_color} !important; font-size: 14px !important; text-align: left !important; }}
        .hd-item-sub {{ font-size: 12px !important; color: {sub_text} !important; margin-top: 3px !important; text-align: left !important; }}
        .hd-item-price {{ text-align: right !important; font-weight: 700 !important; color: {text_color} !important; font-size: 14px !important; white-space: nowrap !important; }}

        .hd-items {{ border-bottom: 1px solid {border_color}; padding-bottom: 10px; margin-bottom: 15px; }}
        .lsc-shake {{ background-color: #fff1f0; color: #cf1322; padding: 12px; border-radius: 6px; border: 1px solid #ffa39e; text-align: center; font-size: 13px; margin-bottom: 15px; }}
        .lsc-vip {{ background-color: #f6ffed; color: #389e0d; padding: 10px; border-radius: 6px; border: 1px solid #b7eb8f; text-align: center; font-size: 13px; margin-bottom: 10px; font-weight: 600; }}

        .firework-container {{ position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: 9999999; overflow: hidden; background: transparent; }}
        .css-particle {{ position: absolute; width: 4px; height: 4px; border-radius: 50%; opacity: 0; animation: explode-mega 3.0s ease-out 2 forwards; }}
        
        /* ĐÃ FIX: Nhân đôi dấu ngoặc nhọn để tránh lỗi f-string */
        @keyframes explode-mega {{ 
            0% {{ transform: translate(0, 0); opacity: 0; }} 
            20% {{ opacity: 0.8; }} 
            100% {{ transform: translate(var(--cx), var(--cy)) scale(0.1); opacity: 0; }} 
        }}
        
        .balloon-container-css {{ position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: 9999998; overflow: hidden; }}
        .fixed-balloon {{ position: absolute; bottom: -100px; border-radius: 50% 50% 50% 50% / 40% 40% 60% 60%; opacity: 0.6; animation: fly-up-skywards-pure linear forwards; }}
        
        /* ĐÃ FIX: Nhân đôi dấu ngoặc nhọn */
        @keyframes fly-up-skywards-pure {{ 
            0% {{ transform: translateY(110vh); opacity: 0; }} 
            10% {{ opacity: 0.6; }} 
            90% {{ opacity: 0.6; }} 
            100% {{ transform: translateY(-120vh); opacity: 0; }} 
        }}
    </style>
    """
    
def render_fireworks_html():
    colors = ['#d4af37', '#111111', '#cccccc', '#ff4d4f', '#52c41a']
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
    colors = ['#e0e0e0', '#f5f5f5', '#d4af37', '#40a9ff']
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

# =====================================================================
# 2. HÀM CORE KẾT NỐI & LIÊN KẾT GOOGLE SHEETS
# =====================================================================
def get_now_vn():
    return datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))

@st.cache_resource
def get_gspread_client():
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

@st.cache_data(ttl=15)
def get_plkh_data():
    try:
        client = get_gspread_client()
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        return client.open_by_url(url).worksheet("PLKH").get_all_values()
    except Exception: return []

def get_huy_hieu(tong_chi):
    if tong_chi >= 10000000: return "💎 DIAMOND"
    elif tong_chi >= 5000000: return "🥇 GOLD"
    elif tong_chi >= 3000000: return "🥈 SILVER"
    elif tong_chi >= 1000000: return "🥉 THÂN THIẾT"
    return "🌱 TIỀM NĂNG"

@st.cache_data(ttl=300)
def get_bao_cao_va_bill_tam():
    try:
        client = get_gspread_client()
        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        bc_values = sh.worksheet("BaoCao").get_all_values()
        tam_records = sh.worksheet("BillTam").get_all_values()
        return bc_values, tam_records
    except Exception:
        return [], []

def luu_bill_tam(gio_hang, nhan_vien, kh_sdt="", kh_ten="Khách lẻ"):
    try:
        client = get_gspread_client()
        ws = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"]).worksheet("BillTam")
        chi_tiet = " | ".join([f"{item['dich_vu']} (x{int(item['so_luong']) if float(item['so_luong']).is_integer() else item['so_luong']})" for item in gio_hang])
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
        get_bao_cao_va_bill_tam.clear()
        return True
    except Exception as e:
        st.error(f"Lỗi lưu nháp: {e}")
        return False

def xoa_bill_tam_dong_gốc(index_sheet_row):
    try:
        client = get_gspread_client()
        ws = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"]).worksheet("BillTam")
        ws.delete_rows(index_sheet_row)
        get_bao_cao_va_bill_tam.clear()
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
            <div class="thong-tin-cum">
                <div class="ten-tiem">{settings.get('TenTiem', 'SALON KIM HIỀN')}</div>
                <div class="thong-tin-phu">📍 {settings.get('Diachi', '131, TRẦN BÌNH TRỌNG, LONG XUYÊN')}</div>
                <div class="thong-tin-phu">📞 Hotline: {settings.get('SDT', '0947.58.1516')}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def gui_email_backup(noi_dung):
    try:
        sender_email = "huynhcongtuan0978666620@gmail.com"
        password = "lwui aesw vqal ytcq" 
        receiver_emails = ["huynhcongtuan0978666620@gmail.com"]
        
        gio_vn_mail = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh')).strftime('%d/%m/%Y %H:%M')
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = ", ".join(receiver_emails)
        msg['Subject'] = f"HOÁ ĐƠN DỊCH VỤ - {gio_vn_mail}"
        msg.attach(MIMEText(noi_dung, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_emails, msg.as_string())
        server.quit()
    except Exception: pass

def gui_telegram_notification(noi_dung):
    try:
        if "telegram" in st.secrets:
            tele_configs = st.secrets["telegram"]
            bot_token = tele_configs.get("bot_token")
            chat_id = tele_configs.get("chat_id")
            if bot_token and chat_id:
                url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                requests.post(url, json={"chat_id": chat_id, "text": noi_dung}, timeout=10)
    except Exception: pass

# =====================================================================
# 3. LUỒNG ĐIỀU HƯỚNG VÀ XỬ LÝ CHÍNH
# =====================================================================
def main():
    init_states = {
        "last_submit": None, "submit_count": 0, "submitting": False, 
        "logged_in": False, "role": None, "full_name": None, "gio_hang": [], 
        "bill_vua_in": None, "trigger_boom": False, "trigger_balloons": False,
        "kh_sdt_val": "", "kh_ten_val": "Khách lẻ", "start_time": get_now_vn(),
        "reset_counter": 0, "tho_chot_val": "",
        "hang_hien_tai": "", "tong_chi_tieu_val": 0.0,
        "theme": "light", "scroll_trigger": None
    }
    for key, val in init_states.items():
        if key not in st.session_state: st.session_state[key] = val

    # Render CSS theo Theme hiện tại
    st.markdown(generate_css_animations(st.session_state.theme), unsafe_allow_html=True)

    st.markdown("""
    <div class="banner-top">QUẢN LÝ DỊCH VỤ</div>
    <div class="banner-bottom">SALON KIM HIỀN © 2026 - VISION V12</div>
    """, unsafe_allow_html=True)

    settings = get_settings()

    # --- KHU VỰC THAO TÁC TIỆN ÍCH MENU "..." TOÀN CỤC ---
    c_header, c_menu = st.columns([88, 12])
    with c_header:
        display_header(settings)
    with c_menu:
        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
        with st.popover("...", help="Menu cấu hình nhanh hệ thống"):
            st.markdown("<div style='font-size:12px; font-weight:700; color:#888; text-align:center;'>TÙY CHỌN HỆ THỐNG</div>", unsafe_allow_html=True)
            
            # 1. Chuyển chủ đề Sáng / Tối
            lbl_theme = "☀️ Chế độ Sáng" if st.session_state.theme == "light" else "🌙 Chế độ Tối"
            if st.button(lbl_theme, use_container_width=True):
                st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
                st.rerun()
            
            # 2. Điều hướng Cuộn Trang
            c_up, c_down = st.columns(2)
            with c_up:
                if st.button("⬆️ Lên", use_container_width=True):
                    st.session_state.scroll_trigger = "up"
            with c_down:
                if st.button("⬇️ Xuống", use_container_width=True):
                    st.session_state.scroll_trigger = "down"
            
            # 3. Làm mới ứng dụng F5
            if st.button("🔄 Làm mới F5", use_container_width=True):
                st.rerun()
                
            # 4. Kích hoạt hiệu ứng ăn mừng pháo hoa
            if st.button("🎉 Pháo hoa", use_container_width=True):
                st.session_state.trigger_boom = True
                st.rerun()
                
            # 5. Trợ giúp nhanh
            if st.button("💡 Trợ giúp", use_container_width=True):
                st.info("Hệ thống App Quản Lý Salon Kim Hiền V12 độc quyền.")
                
            # 6. Gọi Admin Khẩn cấp thông qua Hotline
            st.markdown('<a href="tel:0978666620" class="btn-zalo" style="background-color:#28a745; text-align:center; display:block; text-decoration:none; margin-top:5px; padding:8px; font-size:12px;">📞 Gọi cho Admin</a>', unsafe_allow_html=True)
            
            # 7. Đăng xuất nhanh
            if st.session_state["logged_in"]:
                if st.button("🚪 Đăng xuất", use_container_width=True, type="primary"):
                    st.session_state.clear()
                    st.rerun()

    # Thực thi lệnh cuộn trang bằng Javascript
    if st.session_state.scroll_trigger == "down":
        st.components.v1.html("<script>window.parent.document.querySelector('section.main').scrollTo({top: window.parent.document.querySelector('section.main').scrollHeight, behavior: 'smooth'});</script>", height=0, width=0)
        st.session_state.scroll_trigger = None
    elif st.session_state.scroll_trigger == "up":
        st.components.v1.html("<script>window.parent.document.querySelector('section.main').scrollTo({top: 0, behavior: 'smooth'});</script>", height=0, width=0)
        st.session_state.scroll_trigger = None

    # Kích hoạt hiệu ứng hình ảnh nếu được kích hoạt
    if st.session_state.trigger_boom:
        st.markdown(render_fireworks_html(), unsafe_allow_html=True)
        st.session_state.trigger_boom = False
    if st.session_state.trigger_balloons:
        render_balloons_html()  
        st.session_state.trigger_balloons = False

    # --- ĐĂNG NHẬP HỆ THỐNG ---
    if not st.session_state["logged_in"]:
        # Đọc thông tin tài khoản đã ghi nhớ từ query_params (nếu có)
        saved_u = st.query_params.get("saved_u", "")
        saved_p = st.query_params.get("saved_p", "")
        remember_me_default = True if saved_u else False

        with st.form("login_section"):
            st.markdown("<div class='the-quan-ly-flat' style='text-align: center; border:none; margin-bottom: 5px;'>ĐĂNG NHẬP HỆ THỐNG</div>", unsafe_allow_html=True)
            u = st.text_input("Tài khoản (Số điện thoại)", value=saved_u)
            p = st.text_input("Mật khẩu", type="password", value=saved_p)
            remember_me = st.checkbox("Ghi nhớ mật khẩu đăng nhập", value=remember_me_default)
            
            if st.form_submit_button("Xác nhận Đăng Nhập", use_container_width=True, type="primary"):
                if u == "admin" and p == "2026":
                    if remember_me:
                        st.query_params["saved_u"] = u
                        st.query_params["saved_p"] = p
                    else:
                        if "saved_u" in st.query_params: del st.query_params["saved_u"]
                        if "saved_p" in st.query_params: del st.query_params["saved_p"]
                        
                    st.session_state.update({"logged_in": True, "role": "Admin", "full_name": "Quản lý", "trigger_balloons": True, "tho_chot_val": "Quản lý"})
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
                            if remember_me:
                                st.query_params["saved_u"] = u
                                st.query_params["saved_p"] = p
                            else:
                                if "saved_u" in st.query_params: del st.query_params["saved_u"]
                                if "saved_p" in st.query_params: del st.query_params["saved_p"]
                                
                            ten_that = str(found_row[col_ten_idx]).strip() if col_ten_idx != -1 and col_ten_idx < len(found_row) else "Nhân viên"
                            st.session_state.update({"logged_in": True, "role": "NhanVien", "full_name": ten_that, "trigger_balloons": True, "tho_chot_val": ten_that})
                            time.sleep(0.3)
                            st.rerun()
                        else: st.error("Thông tin số điện thoại hoặc mật khẩu không chính xác.")
                    else: st.error("Lỗi dữ liệu hệ thống hoặc đang bị nghẽn mạng Google Sheets.")
        
        if st.button("Làm mới hoàn toàn ứng dụng", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # --- ĐỂ SAU KHI ĐĂNG NHẬP THÀNH CÔNG ---
    else:
        t_list = ["TẠO ĐƠN HÀNG", "BILL CHỜ", "BÁO CÁO", "CÀI ĐẶT"] if st.session_state["role"] == "Admin" else ["TẠO ĐƠN HÀNG"]
        tabs = st.tabs(t_list)

        services = get_service_data()
        dv_list = list(services.keys())
        
        raw_nv = get_nhan_vien_data()
        ds_tho = []
        if len(raw_nv) > 1:
            headers_nv = [str(h).strip().lower() for h in raw_nv[0]]
            c_ten = next((i for i, h in enumerate(headers_nv) if 'tên' in h or 'nhân viên' in h), -1)
            if c_ten != -1:
                ds_tho = [str(r[c_ten]).strip() for r in raw_nv[1:] if len(r) > c_ten and str(r[c_ten]).strip()]

        # =================================================================
        # TAB 1: TIẾN HÀNH LÊN ĐƠN HÀNG
        # =================================================================
        with tabs[0]:
            st.markdown(f"<div style='text-align: right; font-size: 13px; color: #888; margin-bottom: 15px;'>Thành viên: <b>{st.session_state.full_name}</b> | VN: {get_now_vn().strftime('%H:%M %d/%m/%y')}</div>", unsafe_allow_html=True)
            
            if st.session_state.get("bill_vua_in"):
                st.write("")
                st.markdown('<div class="the-quan-ly-flat">🧾 HOÁ ĐƠN DỊCH VỤ VỪA KHỞI TẠO</div>', unsafe_allow_html=True)
                st.markdown(st.session_state.bill_vua_in, unsafe_allow_html=True)
                st.write("")
                if st.button("❌ ĐÓNG & ẨN HÓA ĐƠN NÀY", use_container_width=True, type="primary"):
                    st.session_state.bill_vua_in = None
                    st.rerun()
                st.markdown("<br><hr>", unsafe_allow_html=True)
            
            st.markdown('<div class="the-quan-ly-flat" style="border:none; margin-bottom:5px; padding-bottom:5px;">THÔNG TIN KHÁCH HÀNG</div>', unsafe_allow_html=True)
            
            so_lan_den = 0
            c1, c2 = st.columns(2)
            with c1: 
                kh_sdt = st.text_input("Số điện thoại khách", value=st.session_state.kh_sdt_val)
                if kh_sdt != st.session_state.kh_sdt_val:
                    st.session_state.kh_sdt_val = kh_sdt
                    sdt_nhap_so = kh_sdt.strip()
                    
                    st.session_state.kh_ten_val = "Khách lẻ"
                    st.session_state.hang_hien_tai = ""
                    st.session_state.tong_chi_tieu_val = 0.0
                    
                    if sdt_nhap_so:
                        ds_kh = get_khach_hang_data()
                        sdt_khong_0 = sdt_nhap_so[1:] if sdt_nhap_so.startswith('0') else sdt_nhap_so
                        sdt_co_0 = '0' + sdt_nhap_so if not sdt_nhap_so.startswith('0') else sdt_nhap_so
                        
                        if sdt_nhap_so in ds_kh: st.session_state.kh_ten_val = ds_kh[sdt_nhap_so]
                        elif sdt_khong_0 in ds_kh: st.session_state.kh_ten_val = ds_kh[sdt_khong_0]
                        elif sdt_co_0 in ds_kh: st.session_state.kh_ten_val = ds_kh[sdt_co_0]
                        
                        try:
                            plkh_rows = get_plkh_data()
                            for row in plkh_rows[1:]:
                                if len(row) >= 2 and (str(row[0]).strip() in [sdt_nhap_so, sdt_khong_0, sdt_co_0]):
                                    val_raw = str(row[1]).replace(',', '').replace('.', '').replace('đ', '').strip()
                                    tong_chi = float(val_raw or 0)
                                    st.session_state.tong_chi_tieu_val = tong_chi
                                    st.session_state.hang_hien_tai = get_huy_hieu(tong_chi)
                                    break
                            else:
                                st.session_state.hang_hien_tai = "🌱 TIỀM NĂNG"
                        except:
                            st.session_state.hang_hien_tai = "🌱 TIỀM NĂNG"
                    st.rerun() 
                    
            with c2: 
                kh_ten = st.text_input("Tên khách hàng", value=st.session_state.kh_ten_val)
                if kh_ten != st.session_state.kh_ten_val: st.session_state.kh_ten_val = kh_ten
                
            if st.session_state.kh_sdt_val.strip() and st.session_state.kh_ten_val != "Khách lẻ":
                try:
                    bc_val, _ = get_bao_cao_va_bill_tam()
                    if len(bc_val) > 1:
                        df_hist = pd.DataFrame(bc_val[1:], columns=bc_val[0])
                        c_sdt_hist = next((c for c in df_hist.columns if 'sđt' in c.lower() or 'sdt' in c.lower() or 'thoại' in c.lower()), None)
                        c_ma_hist = next((c for c in df_hist.columns if 'mã' in c.lower() or 'hd' in c.lower() or 'hđ' in c.lower()), None)
                        if c_sdt_hist and c_ma_hist:
                            sdt_check = st.session_state.kh_sdt_val.strip()
                            s_k_0 = sdt_check[1:] if sdt_check.startswith('0') else sdt_check
                            matches = df_hist[df_hist[c_sdt_hist].astype(str).str.contains(s_k_0, na=False)]
                            so_lan_den = len(matches[c_ma_hist].unique())
                except: pass

            if so_lan_den > 0:
                st.markdown(f'<div class="lsc-vip">🌟 Khách siêu quen: Đã ghé tiệm {so_lan_den} lần!</div>', unsafe_allow_html=True)
            
            if st.session_state["role"] == "Admin" and st.session_state.kh_sdt_val.strip() and st.session_state.hang_hien_tai:
                st.markdown(f"""
                    <div style="text-align: right; margin-top: -10px; margin-bottom: 15px;">
                        <span style="background-color: #fffbfa; padding: 4px 12px; border-radius: 12px; border: 1px solid #ffe1df; font-size: 11px; font-weight: 700; color: #d4380d; text-transform: uppercase;">
                            {st.session_state.hang_hien_tai} | Tích lũy: {st.session_state.tong_chi_tieu_val:,.0f} đ
                        </span>
                    </div>
                """, unsafe_allow_html=True)

            st.write("")
            st.markdown('<div class="the-quan-ly-flat">DANH SÁCH DỊCH VỤ DÙNG</div>', unsafe_allow_html=True)
            
            max_dv_cho_phep = 3 if st.session_state.get("role") == "NhanVien" else None
            
            dich_vu_chon_multi = st.multiselect(
                "Chạm chọn dịch vụ...", 
                options=dv_list if dv_list else ["Đang tải danh mục..."], 
                max_selections=max_dv_cho_phep,
                placeholder="Chọn tối đa 3 dịch vụ..." if max_dv_cho_phep else "Ní cứ chọn thoải mái nhiều dịch vụ...",
                key=f"dv_multi_key_{st.session_state.reset_counter}"
            )
            
            if st.button("➕ THÊM VÀO GIỎ HÀNG", type="primary", use_container_width=True):
                if not dich_vu_chon_multi:
                    st.warning("⚠️ Vui lòng lựa chọn ít nhất một dịch vụ!")
                else:
                    for dv in dich_vu_chon_multi:
                        info_dv = services.get(dv, {"gia": 0.0, "hoa_hong": 0.0})
                        gia_goc = info_dv.get("gia", 0.0)
                        phan_tram_hh = info_dv.get("hoa_hong", 0.0)
                        sl_mac_dinh = 1.0  
                        
                        existing = next((item for item in st.session_state.gio_hang if item["dich_vu"] == dv), None)
                        if existing:
                            existing["so_luong"] += sl_mac_dinh
                            existing["thanh_tien"] = existing["so_luong"] * existing["don_gia"]
                        else:
                            st.session_state.gio_hang.append({
                                "dich_vu": dv, "so_luong": sl_mac_dinh, "don_gia": gia_goc,
                                "thanh_tien": gia_goc * sl_mac_dinh, "phan_tram_hh": phan_tram_hh
                            })
                            
                    if 'start_time' not in st.session_state or len(st.session_state.gio_hang) == len(dich_vu_chon_multi):
                        st.session_state.start_time = get_now_vn()
                    st.session_state.reset_counter += 1  
                    st.toast(f"✅ Đã đưa thành công {len(dich_vu_chon_multi)} dịch vụ!")
                    time.sleep(0.3)
                    st.rerun()

            # --- KHU VỰC CHI TIẾT GIỎ HÀNG ---
            t_bill = 0.0
            if st.session_state.gio_hang:
                st.write("")
                so_luong_mon = len(st.session_state.gio_hang)
                st.markdown(f'<div class="the-quan-ly-flat">🛒 GIỎ HÀNG HIỆN TẠI ({so_luong_mon} món)</div>', unsafe_allow_html=True)
                
                for idx, item in enumerate(st.session_state.gio_hang):
                    st.markdown(f"<div style='font-size:14px; font-weight:600; margin-bottom:6px;'>📍 {item['dich_vu']}</div>", unsafe_allow_html=True)
                    
                    c_sl, c_tt, c_del = st.columns([5, 3, 2])
                    with c_sl:
                        new_sl = st.number_input(
                            "Số lượng:", min_value=0.5, max_value=50.0, 
                            value=float(item['so_luong']), step=0.5, 
                            key=f"cart_sl_{item['dich_vu']}_{idx}"
                        )
                        if new_sl != item['so_luong']:
                            item['so_luong'] = new_sl
                            item['thanh_tien'] = new_sl * item['don_gia']
                            st.rerun()
                    with c_tt:
                        st.markdown(f"<div style='font-size:11px; color:#888; text-transform:uppercase; margin-bottom:8px; text-align:right;'>Thành tiền</div><div style='font-size:14px; font-weight:700; text-align:right; padding-top:5px;'>{item['thanh_tien']:,.0f}đ</div>", unsafe_allow_html=True)
                    with c_del:
                        st.markdown("<div style='font-size:11px; color:#888; text-transform:uppercase; margin-bottom:8px; text-align:center;'>Xóa</div>", unsafe_allow_html=True)
                        if st.button("🗑️", key=f"del_{idx}", use_container_width=True):
                            st.session_state.gio_hang.pop(idx)
                            st.rerun()
                            
                    st.markdown("<div style='margin: 12px 0; border-bottom: 1px dashed #eaeaea;'></div>", unsafe_allow_html=True)
                    t_bill += item['thanh_tien']

                st.write("")
                if st.button("💾 TẠM LƯU ĐƠN VÀO BILL CHỜ", use_container_width=True):
                    if luu_bill_tam(st.session_state.gio_hang, st.session_state.full_name, st.session_state.kh_sdt_val, st.session_state.kh_ten_val):
                        st.session_state.update({
                            "gio_hang": [], "kh_sdt_val": "", "kh_ten_val": "Khách lẻ", 
                            "hang_hien_tai": "", "tong_chi_tieu_val": 0.0,
                            "tho_chot_val": st.session_state.full_name
                        })
                        st.toast("✅ Đã lưu đơn tạm thành công!")
                        time.sleep(1)
                        st.rerun()

            if t_bill > 0:
                st.markdown('<div class="the-quan-ly-flat">THU NGÂN & CHIẾT KHẤU</div>', unsafe_allow_html=True)
                
                options_tho = [t for t in ds_tho if t.strip()]
                if st.session_state.full_name not in options_tho: options_tho.append(st.session_state.full_name)
                if "tho_chot_val" not in st.session_state or not st.session_state.tho_chot_val: st.session_state.tho_chot_val = st.session_state.full_name
                if st.session_state.tho_chot_val not in options_tho: options_tho.append(st.session_state.tho_chot_val)
                
                try: idx_default = options_tho.index(st.session_state.tho_chot_val)
                except ValueError: idx_default = 0
                
                chot_tho = st.selectbox("Thợ thực hiện (Tính KPI):", options=options_tho, index=idx_default)

                col_nhap1, col_nhap2 = st.columns(2)
                with col_nhap1: tien_giam = st.number_input("Chiết khấu thẳng (VND)", min_value=0.0, max_value=float(t_bill), value=0.0, step=1000.0)
                with col_nhap2: khuyen_mai = st.number_input("Khuyến mãi trừ thêm (VND)", min_value=0.0, max_value=float(t_bill), value=0.0, step=1000.0)
                
                ghi_chu = st.text_input("Ghi chú đơn hàng")
                
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
                
                st.markdown(f'<div style="text-align:right; font-size:13px; color:#888; margin-top:8px;">Hoa hồng thợ hưởng: <b>{t_cong_tho_chinh_xac:,.0f}đ</b></div>', unsafe_allow_html=True)
                
                st.write("")
                kh_dua = st.number_input("Số tiền mặt khách trả", 0.0, value=float(t_khach_tra))
                t_du = kh_dua - t_khach_tra
                
                if t_du > 0: st.markdown(f'<div class="tien-thua-box">Tiền thối lại khách: <span>{t_du:,.0f} VND</span></div>', unsafe_allow_html=True)

                can_go = True
                if st.session_state["role"] == "NhanVien" and st.session_state.last_submit:
                    tg_cho = (get_now_vn() - st.session_state.last_submit).total_seconds() / 60
                    han_muc = 1 if st.session_state.submit_count == 1 else 2 if st.session_state.submit_count >= 2 else 0
                    if tg_cho < han_muc:
                        can_go = False
                        st.markdown(f'<div class="lsc-shake">Vui lòng chờ {round(han_muc - tg_cho, 1)} phút để bấm tạo hóa đơn tiếp theo.</div>', unsafe_allow_html=True)

                if can_go:
                    cam_ket = st.checkbox("Tôi cam kết số liệu nhập trên là chuẩn xác")
                    if not st.session_state.submitting:
                        if st.button("🚀 XÁC NHẬN & XUẤT HÓA ĐƠN", use_container_width=True, type="primary"):
                            if cam_ket:
                                st.session_state.submitting = True
                                st.rerun()
                            else: st.warning("Vui lòng tích chọn xác nhận trước khi lưu.")
                    else:
                        st.button("Đang đồng bộ dữ liệu lên mây Google...", disabled=True, use_container_width=True)
                        try:
                            cl = get_gspread_client()
                            ws = cl.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"]).worksheet("BaoCao")
                            bay_gio = get_now_vn()
                            ma_hd = f"HD{bay_gio.strftime('%y%m%d%H%M')}"
                            
                            start_time = st.session_state.get("start_time", bay_gio)
                            thoi_gian_phuc_vu = max(0, int((bay_gio - start_time).total_seconds() / 60))
                            tien_thoi = kh_dua - t_khach_tra
                            
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
                                    bay_gio.strftime("%H:%M:%S"), chuoi_ghi_chu, hoa_hong_tung_dong, ma_hd,
                                    kh_dua, tien_thoi, f"{thoi_gian_phuc_vu} phút", chot_tho
                                ])
                                
                                sl_sach = int(item['so_luong']) if float(item['so_luong']).is_integer() else item['so_luong']
                                
                                html_items += f"""<tr>
<td style="text-align: left; border: none !important; padding: 6px 0px !important;">
<div class="hd-item-name">{item["dich_vu"]}</div>
<div class="hd-item-sub">{sl_sach} x {item['don_gia']:,.0f}đ</div>
</td>
<td style="text-align: right; border: none !important; padding: 6px 0px !important; vertical-align: middle;">
<div class="hd-item-price">{item["thanh_tien"]:,.0f}đ</div>
</td>
</tr>"""
                                chi_tiet_tele += f"\n- {item['dich_vu']} (x{sl_sach}): {item['thanh_tien']:,.0f}đ"
                                
                            ws.append_rows(rows_to_append)
                            get_bao_cao_va_bill_tam.clear() 
                            get_plkh_data.clear()
                            
                            if chot_sdt and chot_sdt != "":
                                ds_kh_hien_tai = get_khach_hang_data()
                                sdt_khong_0 = chot_sdt[1:] if chot_sdt.startswith('0') else chot_sdt
                                sdt_co_0 = '0' + chot_sdt if not chot_sdt.startswith('0') else chot_sdt
                                is_sdt_cu = (chot_sdt in ds_kh_hien_tai) or (sdt_khong_0 in ds_kh_hien_tai) or (sdt_co_0 in ds_kh_hien_tai)
                                
                                if not is_sdt_cu and chot_ten != "Khách lẻ" and chot_ten != "":
                                    ws_kh = cl.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"]).worksheet("KhachHang")
                                    ws_kh.append_row([chot_sdt, chot_ten])
                                    st.cache_data.clear() 
                            
                            huy_hieu_bill = ""
                            if st.session_state["role"] == "Admin" and chot_sdt and chot_ten != "Khách lẻ":
                                if st.session_state.hang_hien_tai and st.session_state.hang_hien_tai != "🌱 TIỀM NĂNG":
                                    huy_hieu_bill = st.session_state.hang_hien_tai

                            huy_hieu_text_tele = f" | Hạng: {huy_hieu_bill}" if huy_hieu_bill else ""

                            noi_dung_mail = (
                                f"THÔNG BÁO - Đã thanh toán\n \n=====================\n \n"
                                f"Mã ĐH: {ma_hd} | {bay_gio.strftime('%d/%m/%Y %H:%M')}\nKhách hàng: {chot_ten} - {chot_sdt}{huy_hieu_text_tele}\n"
                                f"Thu ngân: {st.session_state.full_name}\nThợ thực hiện: {chot_tho}\n \n=====================\n \n"
                                f"Dịch vụ:{chi_tiet_tele}\n \n=====================\n \n"
                                f"Tổng bill: {t_bill:,.0f} đ\nChiết khấu/KM: -{tong_tru_gia:,.0f} đ\nKhách đưa: {kh_dua:,.0f} đ\n"
                                f"Tiền thối: {tien_thoi:,.0f} đ\nPhục vụ: {thoi_gian_phuc_vu} phút\n \n=====================\n \n"
                                f"THỰC THU: {t_khach_tra:,.0f} đ\n"
                            )
                            gui_email_backup(noi_dung_mail)
                            gui_telegram_notification(noi_dung_mail)
                            
                            # NÚT KÍCH HOẠT MỞ ZALO VÀ CHỦ ĐỘNG TÌM KIẾM THEO SĐT
                            btn_zalo_html = ""
                            if chot_sdt and chot_sdt != "":
                                sdt_zalo_clean = str(chot_sdt).strip().replace(" ", "").replace("+84", "0")
                                if not sdt_zalo_clean.startswith('0') and sdt_zalo_clean != "":
                                    sdt_zalo_clean = '0' + sdt_zalo_clean
                                btn_zalo_html = f'<a href="zalo://conversation?phone={sdt_zalo_clean}" target="_blank" class="btn-zalo">💬 Nhắn tin cho khách qua Zalo</a>'
                            
                            html_huy_hieu_bill_goc = f'<div style="font-size: 11px; color: #d4380d; font-weight: bold; text-align: right; margin-top: -15px; margin-bottom: 15px; letter-spacing: 0.5px;">Hạng: {huy_hieu_bill}</div>' if huy_hieu_bill else ""
                            
                            # Toàn bộ lõi bảng hóa đơn đã được thêm tiêu đề "Dịch vụ có trong bill:" và giữ nguyên cấu trúc xóa viền
                            st.session_state.bill_vua_in = f"""<style>
.hoa-don-khung table, .hoa-don-khung tr, .hoa-don-khung td {{
    border: none !important;
    background: transparent !important;
    background-color: transparent !important;
}}
</style>
<div class="hoa-don-khung">
<div class="hd-header">
    <div style="font-size: 18px; font-weight: 800;">{settings.get('TenTiem', 'SALON KIM HIỀN')}</div>
    <div style="font-size: 13px; color: #666; margin-top:4px;">{settings.get('Diachi', '')}</div>
    <div style="font-size: 13px; color: #666;">SĐT: {settings.get('SDT', '')}</div>
    <div class="hd-title">HÓA ĐƠN DỊCH VỤ</div>
    <div style="font-size: 12px; color: #888; margin-top:5px;">Mã số: {ma_hd}</div>
</div>
    <div style="font-size: 13px; font-weight: 600; color: #555; text-align: left; margin-bottom: 8px; border-bottom: 1px dashed #eaeaea; padding-bottom: 5px;">Chi tiết dịch vụ:</div>
{html_huy_hieu_bill_goc}
<div style="border-bottom: 1px solid #eaeaea; padding-bottom: 10px; margin-bottom: 15px; font-size: 14px; color: #444;">
    <div style="display: flex; justify-content: space-between; margin-bottom: 6px;"><span>Ngày:</span> <span>{bay_gio.strftime('%d/%m/%Y %H:%M')}</span></div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 6px;"><span>Khách hàng:</span> <span style="font-weight:600;">{chot_ten}</span></div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 6px;"><span>Thu ngân:</span> <span>{st.session_state.full_name}</span></div>
    <div style="display: flex; justify-content: space-between;"><span>Thợ thực hiện:</span> <span style="font-weight:600;">{chot_tho}</span></div>
</div>
<div class="hd-items" style="margin-bottom: 15px;">
    <div style="font-size: 13px; font-weight: 600; color: #555; text-align: left; margin-bottom: 8px; border-bottom: 1px dashed #eaeaea; padding-bottom: 5px;">Chi tiết dịch vụ:</div>
    <table style="width: 100%; border-collapse: collapse; border: none !important;">
        {html_items}
    </table>
</div>
<div style="font-size: 14px; border-bottom: 1px solid #eaeaea; padding-bottom: 10px; margin-bottom: 15px;">
    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;"><span>Cộng tiền:</span> <span>{t_bill:,.0f}</span></div>
    <div style="display: flex; justify-content: space-between; color: #d93025; margin-bottom: 8px;"><span>Chiết khấu:</span> <span>-{tien_giam:,.0f}</span></div>
    <div style="display: flex; justify-content: space-between; color: #d93025; margin-bottom: 8px;"><span>Khuyến mãi:</span> <span>-{khuyen_mai:,.0f}</span></div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;"><span>Khách đưa:</span> <span>{kh_dua:,.0f}</span></div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;"><span>Tiền thối:</span> <span>{tien_thoi:,.0f}</span></div>
    <div style="display: flex; justify-content: space-between;"><span>Thời gian phục vụ:</span> <span>{thoi_gian_phuc_vu} phút</span></div>
</div>
    <div style="font-size: 13px; font-weight: 600; color: #555; text-align: left; margin-bottom: 8px; border-bottom: 1px dashed #eaeaea; padding-bottom: 5px;">Sô tiền cần thanh toán:</div>
<div style="font-size: 15px; font-weight: 700;">
    <div style="display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 18px;"><span>TỔNG CỘNG:</span> <span>{t_khach_tra:,.0f}</span></div>
</div>
<div style="text-align: center; margin-top: 25px; font-size: 13px; color: #888;">
    Cảm ơn quý khách đã sử dụng dịch vụ!
</div>
{btn_zalo_html}
</div>"""

                            st.session_state.update({
                                "gio_hang": [], "last_submit": bay_gio, "submit_count": st.session_state.submit_count + 1, 
                                "submitting": False, "trigger_boom": True, "kh_sdt_val": "", "kh_ten_val": "Khách lẻ",
                                "hang_hien_tai": "", "tong_chi_tieu_val": 0.0,
                                "start_time": get_now_vn(), "tho_chot_val": st.session_state.full_name
                            })
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Hệ thống bận (Google Quota), vui lòng thử lại sau 30 giây: {e}")
                            st.session_state.submitting = False

        # =================================================================
        # TAB 2 & 3 & 4 CẤU HÌNH DÀNH CHO QUẢN TRỊ ADMIN
        # =================================================================
        if st.session_state["role"] == "Admin":
            with tabs[1]:
                st.markdown('<div class="the-quan-ly-flat">QUẢN LÝ BILL CHỜ</div>', unsafe_allow_html=True)
                if st.button("🔄 Làm mới danh sách đơn chờ", use_container_width=True):
                    get_bao_cao_va_bill_tam.clear() 
                    st.rerun()
                    
                try:
                    _, data_tam = get_bao_cao_va_bill_tam()
                    if len(data_tam) > 1:
                        rows_tam = data_tam[1:]
                        st.write(f"Đang ghi nhận **{len(rows_tam)}** đơn hàng nháp chờ xử lý:")
                        
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
                            
                            with st.container(border=True):
                                col_info, col_act = st.columns([7, 3])
                                with col_info:
                                    st.markdown(f"👤 **Khách:** {ten_kh} ({sdt_kh if sdt_kh else 'Không SĐT'})")
                                    st.markdown(f"🛠 **Chi tiết:** `{chi_tiet_dv}`")
                                    try:
                                        tien_float = float(t_tien_str.replace(',','').replace('.',''))
                                        st.markdown(f"💰 **Tạm tính:** `{tien_float:,.0f}đ` | 🤝 **Thợ:** {tho_lam}")
                                    except:
                                        st.markdown(f"💰 **Tạm tính:** `{t_tien_str}đ` | 🤝 **Thợ:** {tho_lam}")
                                
                                with col_act:
                                    st.write("")
                                    if st.button("🛒 Nạp ra chốt đơn", key=f"load_bill_{sheet_row_idx}", use_container_width=True, type="primary"):
                                        with st.spinner("Đang lấy dữ liệu..."):
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
                                            st.session_state.tho_chot_val = tho_lam 
                                            st.session_state.bill_vua_in = None
                                            
                                            try:
                                                plkh_rows = get_plkh_data()
                                                s_k_0 = sdt_kh[1:] if sdt_kh.startswith('0') else sdt_kh
                                                s_c_0 = '0' + sdt_kh if not sdt_kh.startswith('0') else sdt_kh
                                                for row in plkh_rows[1:]:
                                                    if len(row) >= 2 and (str(row[0]).strip() in [sdt_kh, s_k_0, s_c_0]):
                                                        val_raw = str(row[1]).replace(',', '').replace('.', '').replace('đ', '').strip()
                                                        tong_chi = float(val_raw or 0)
                                                        st.session_state.tong_chi_tieu_val = tong_chi
                                                        st.session_state.hang_hien_tai = get_huy_hieu(tong_chi)
                                                        break
                                                else:
                                                    st.session_state.hang_hien_tai = "🌱 TIỀM NĂNG"
                                                    st.session_state.tong_chi_tieu_val = 0.0
                                            except: pass
                                            
                                            try:
                                                tz_vn = pytz.timezone('Asia/Ho_Chi_Minh')
                                                thoi_gian_goc = datetime.strptime(t_tao_str, "%Y-%m-%d %H:%M:%S")
                                                st.session_state.start_time = tz_vn.localize(thoi_gian_goc)
                                            except Exception:
                                                st.session_state.start_time = get_now_vn() 
                                            
                                            if xoa_bill_tam_dong_gốc(sheet_row_idx):
                                                st.toast("⚡ Đã nạp thành công dữ liệu!")
                                                time.sleep(0.5)
                                                st.rerun()
                    else: st.info("Không có đơn chờ xử lý.")
                except Exception as e: st.error(f"Hệ thống phản hồi chậm, ní vui lòng ấn thử lại: {e}")

            with tabs[2]:
                st.markdown('<div class="the-quan-ly-flat">BÁO CÁO DOANH THU TỔNG HỢP</div>', unsafe_allow_html=True)
                if st.button("⏰ Cập nhật dữ liệu", use_container_width=True):
                    get_bao_cao_va_bill_tam.clear()
                    st.rerun()
                
                try:
                    bc_values, tam_records = get_bao_cao_va_bill_tam()
                    don_cho = max(0, len(tam_records) - 1) if tam_records else 0
                    
                    tong_doanh_thu = trung_binh = tong_don = so_khach = 0
                    df_hien_thi = pd.DataFrame()
                    df_bc = pd.DataFrame()
                    
                    if len(bc_values) > 1:
                        headers = bc_values[0]
                        df_bc = pd.DataFrame(bc_values[1:], columns=headers)
                        
                        col_tien = next((c for c in df_bc.columns if 'tiền' in c.lower() or 'tien' in c.lower()), 'Thành tiền')
                        col_ngay = next((c for c in df_bc.columns if 'ngày' in c.lower() or 'ngay' in c.lower()), 'Ngày')
                        col_ma_hd = next((c for c in df_bc.columns if 'mã' in c.lower() or 'hd' in c.lower() or 'hđ' in c.lower()), None)
                        col_khach = next((c for c in df_bc.columns if 'khách' in c.lower() or 'khach' in c.lower()), None)
                        
                        df_bc[col_tien] = pd.to_numeric(df_bc[col_tien].astype(str).str.replace(',', '').str.replace('.', ''), errors='coerce').fillna(0)
                        
                        today = get_now_vn().strftime("%d/%m/%Y")
                        df_today = df_bc[df_bc[col_ngay] == today] if col_ngay in df_bc.columns else pd.DataFrame()

                        tong_doanh_thu = df_today[col_tien].sum() if not df_today.empty else 0
                        if col_ma_hd and not df_today.empty:
                            tong_don = len([x for x in df_today[col_ma_hd].unique() if str(x).strip() != ''])
                        trung_binh = tong_doanh_thu / tong_don if tong_don > 0 else 0
                        
                        if col_khach and not df_today.empty: so_khach = len(df_today[col_khach].unique())

                        df_hien_thi = df_bc.tail(50).copy()
                        df_hien_thi.index = range(1, len(df_hien_thi) + 1)
                    
                    c1, c2 = st.columns(2)
                    c1.metric("💰 Doanh thu hôm nay", f"{tong_doanh_thu:,.0f}đ")
                    c2.metric("💳 Bình quân đơn", f"{trung_binh:,.0f}đ")
                    
                    c3, c4, c5 = st.columns(3)
                    c3.metric("📦 Tổng đơn", tong_don)
                    c4.metric("👥 Tổng lượt khách", so_khach)
                    c5.metric("⏳ Đơn chờ xử lý", don_cho)
                    
                    st.write("")
                    if not df_bc.empty:
                        col_chart, col_kpi = st.columns([6, 4])
                        with col_chart:
                            st.markdown('<div class="nhan-tieu-de">📈 BIỂU ĐỒ DOANH THU PHÁT SINH</div>', unsafe_allow_html=True)
                            df_chart = df_bc.groupby(col_ngay)[col_tien].sum().reset_index()
                            df_chart_7 = df_chart.tail(7).set_index(col_ngay)
                            st.bar_chart(df_chart_7, use_container_width=True)

                        with col_kpi:
                            st.markdown('<div class="nhan-tieu-de">🏆 KPI DOANH SỐ THỢ HÔM NAY</div>', unsafe_allow_html=True)
                            if not df_today.empty:
                                if len(df_today.columns) >= 16:
                                    col_tho_name = df_today.columns[15] 
                                    kpi_df = df_today.groupby(col_tho_name)[col_tien].sum().reset_index()
                                    kpi_df.columns = ["Tên thợ", "Doanh thu"]
                                    kpi_df = kpi_df.sort_values(by="Doanh thu", ascending=False)
                                    kpi_df["Doanh thu"] = kpi_df["Doanh thu"].apply(lambda x: f"{x:,.0f} đ")
                                    st.dataframe(kpi_df, use_container_width=True, hide_index=True)
                                else:
                                    st.warning(f"Hiện tại chỉ cấu hình được {len(df_today.columns)} cột trên file Sheets.")
                            else:
                                st.info("Chưa có ghi nhận giao dịch tính KPI.")

                    st.write("")
                    st.markdown('<div class="the-quan-ly-flat">CHI TIẾT 50 GIAO DỊCH GẦN NHẤT</div>', unsafe_allow_html=True)
                    if not df_hien_thi.empty: st.dataframe(df_hien_thi, use_container_width=True)
                    else: st.info("Không có dữ liệu hiển thị.")
                        
                except Exception as e: 
                    st.error(f"Kết nối mây dữ liệu gián đoạn: {e}")

            with tabs[3]:
                st.markdown('<div class="the-quan-ly-flat">QUẢN TRỊ HỆ THỐNG TRUNG TÂM</div>', unsafe_allow_html=True)
                if st.button("♻️ Ép buộc xóa bộ nhớ Cache"):
                    st.cache_data.clear()
                    st.success("Đã đồng bộ sạch sẽ dữ liệu mới!")
                    time.sleep(0.5)
                    st.rerun()
                
                if st.button("Đăng xuất Admin khẩn cấp", use_container_width=True):
                    st.session_state.clear()
                    st.rerun()

if __name__ == "__main__":
    main()
