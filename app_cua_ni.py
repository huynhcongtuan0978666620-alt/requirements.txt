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
# 1. CẤU HÌNH GIAO DIỆN & STYLE CSS CAO CẤP CHUYỂN ĐỔI CHỦ ĐỀ
# =====================================================================
st.set_page_config(
    page_title="LKTV DETAILING - VISION V12", 
    layout="centered", 
    page_icon="⚜️",
    initial_sidebar_state="collapsed"
)

def get_now_vn():
    vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    return datetime.now(vn_tz)

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

        html, body {{ font-family: 'Inter', sans-serif !important; background-color: {bg_app} !important; color: {text_color} !important; }}
        .stApp {{ padding-top: 50px !important; padding-bottom: 75px !important; background-color: transparent !important; }}
        header, footer, #MainMenu, .stAppDeployButton, [data-testid="stStatusWidget"], [data-testid="stToolbar"] {{ display: none !important; }}
        .banner-top, .banner-bottom {{ position: fixed !important; left: 0 !important; right: 0 !important; height: 40px !important; background: {"#1e1e1e" if is_dark else "#ffffff"} !important; color: {text_color} !important; font-size: 13px !important; font-weight: 600 !important; display: flex !important; align-items: center !important; justify-content: center !important; z-index: 999999 !important; border-bottom: 1px solid {border_color} !important; }}
        .banner-top {{ top: 0px !important; }}
        .banner-bottom {{ bottom: 0 !important; top: auto !important; border-top: 1px solid {border_color} !important; justify-content: flex-start !important; padding-left: 20px !important; }}
        .bang-hieu-lktv {{ display: flex !important; align-items: center !important; gap: 15px !important; margin-bottom: 20px !important; padding: 12px 15px !important; border-radius: 8px !important; background: {bg_box} !important; border: 1px solid {border_color} !important; }}
        .logo-img {{ width: 55px !important; height: 55px !important; border-radius: 50% !important; border: 1px solid {border_color} !important; }}
        .ten-tiem {{ font-size: 16px !important; font-weight: 700 !important; color: {text_color} !important; }}
        .thong-tin-phu {{ font-size: 11px !important; color: {sub_text} !important; }}
        [data-testid="stTabs"] [role="tablist"] {{ border-bottom: 1px solid {border_color} !important; margin-bottom: 25px !important; }}
        button[data-baseweb="tab"] p {{ color: {sub_text} !important; font-weight: 600 !important; }}
        button[data-baseweb="tab"][aria-selected="true"] p {{ color: {text_color} !important; }}
        .the-quan-ly-flat {{ color: {text_color}; font-weight: 600; font-size: 15px; margin-bottom: 15px; border-bottom: 1px solid {border_color}; padding-bottom: 8px;}}
        .nhan-tieu-de {{ font-size: 11px !important; font-weight: 600 !important; margin-bottom: 8px !important; color: {sub_text} !important; text-align: center;}}
        .box-chung {{ background-color: {bg_box}; padding: 15px 10px; border-radius: 8px; text-align: center; border: 1px solid {border_color}; font-size: 18px; font-weight: 700; }}
        .tong-don-box {{ color: {text_color}; }}
        .chiet-khau-box {{ color: #d93025; }} 
        .khach-tra-box {{ background-color: {text_color}; color: {bg_box}; }}
        .tien-thua-box {{ background-color: {"#2a2a2a" if is_dark else "#f8f9fa"}; color: {text_color}; padding: 18px; border-radius: 8px; text-align: center; font-size: 18px; font-weight: 700; border: 1px solid {border_color}; margin: 20px 0; }}
        div[data-testid="stButton"] button[kind="primary"] {{ background-color: {text_color} !important; color: {bg_box} !important; }}
        .btn-zalo {{ display: block; width: 100%; text-align: center; padding: 12px; background-color: #0068ff; color: white !important; font-weight: 700; border-radius: 6px; text-decoration: none; margin-top: 15px; }}
        .hoa-don-khung {{ background-color: {bg_box} !important; color: {text_color} !important; padding: 30px 25px !important; border-radius: 8px !important; border: 1px solid {border_color} !important; margin-top: 20px !important; }}
        .hd-header {{ text-align: center; border-bottom: 1px solid {border_color}; padding-bottom: 15px; margin-bottom: 20px; }}
        .hd-title {{ font-size: 18px; font-weight: 700; color: {text_color}; margin-top:10px;}}
        .hd-table-sanpham {{ width: 100% !important; border-collapse: collapse !important; }}
        .hd-item-name {{ font-weight: 600 !important; color: {text_color} !important; font-size: 14px !important; text-align: left !important; }}
        .hd-item-sub {{ font-size: 12px !important; color: {sub_text} !important; text-align: left !important; }}
        .hd-item-price {{ text-align: right !important; font-weight: 700 !important; color: {text_color} !important; font-size: 14px !important; }}
        .lsc-shake {{ background-color: #fff1f0; color: #cf1322; padding: 12px; border-radius: 6px; border: 1px solid #ffa39e; text-align: center; font-size: 13px; margin-bottom: 15px; }}
        .lsc-vip {{ background-color: #f6ffed; color: #389e0d; padding: 10px; border-radius: 6px; border: 1px solid #b7eb8f; text-align: center; font-size: 13px; margin-bottom: 10px; font-weight: 600; }}
        .firework-container {{ position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: 9999999; }}
        .css-particle {{ position: absolute; width: 4px; height: 4px; border-radius: 50%; opacity: 0; animation: explode-mega 3.0s ease-out 2 forwards; }}
        @keyframes explode-mega {{ 0% {{ transform: translate(0, 0); opacity: 0; }} 20% {{ opacity: 0.8; }} 100% {{ transform: translate(var(--cx), var(--cy)) scale(0.1); opacity: 0; }} }}
        .balloon-container-css {{ position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: 9999998; overflow: hidden; }}
        .fixed-balloon {{ position: absolute; bottom: -100px; border-radius: 50% 50% 50% 50% / 40% 40% 60% 60%; opacity: 0.6; animation: fly-up-skywards-pure linear forwards; }}
        @keyframes fly-up-skywards-pure {{ 0% {{ transform: translateY(110vh); opacity: 0; }} 10% {{ opacity: 0.6; }} 90% {{ opacity: 0.6; }} 100% {{ transform: translateY(-120vh); opacity: 0; }} }}
    </style>
    """

def render_fireworks_html():
    colors = ['#d4af37', '#111111', '#cccccc', '#ff4d4f', '#52c41a']
    html_particles = '<div class="firework-container">'
    for cx, cy in [(25, 20), (50, 15), (75, 20)]:
        for i in range(50): 
            angle = random.uniform(0, 2 * 3.14159)
            distance = random.uniform(30, 150)
            tx = int(math.cos(angle) * distance)
            ty = int(math.sin(angle) * distance)
            color = random.choice(colors)
            delay = round(random.uniform(0, 0.1), 2)
            html_particles += f'<div class="css-particle" style="background-color: {color}; left: {cx}vw; top: {cy}vh; --cx: {tx}px; --cy: {ty}px; animation-delay: {delay}s;"></div>'
    return html_particles + '</div>'

def render_balloons_html():
    colors = ['#e0e0e0', '#f5f5f5', '#d4af37', '#40a9ff']
    html_balloons = '<div class="balloon-container-css">'
    for i in range(20):
        left_pos = random.uniform(5, 95)
        color = random.choice(colors)
        size_ratio = random.uniform(0.6, 1.0)
        w, h = int(40 * size_ratio), int(55 * size_ratio)
        delay = round(random.uniform(0.0, 2.0), 2)
        duration = round(random.uniform(4.0, 6.0), 2)
        html_balloons += f'<div class="fixed-balloon" style="background-color: {color}; left: {left_pos}vw; width: {w}px; height: {h}px; animation-delay: {delay}s; animation-duration: {duration}s;"></div>'
    st.markdown(html_balloons + '</div>', unsafe_allow_html=True)

# =====================================================================
# 2. CƠ CHẾ KẾT NỐI TỐI ƯU (CHỐNG LỖI 429 & STALE CONNECTION)
# =====================================================================
@st.cache_resource
def get_google_sheet_workbook():
    try:
        if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
            secrets = dict(st.secrets["connections"]["gsheets"])
        else:
            secrets = dict(st.secrets)

        creds_info = {
            "type": secrets.get("type", "service_account"),
            "project_id": secrets.get("project_id", "hethongphache"),
            "private_key_id": secrets.get("private_key_id", ""),
            "private_key": secrets.get("private_key", "").replace("\\n", "\n"),
            "client_email": secrets.get("client_email", ""),
            "client_id": secrets.get("client_id", ""),
            "auth_uri": secrets.get("auth_uri", "https://accounts.google.com/o/oauth2/auth"),
            "token_uri": secrets.get("token_uri", "https://oauth2.googleapis.com/token"),
            "auth_provider_x509_cert_url": secrets.get("auth_provider_x509_cert_url", "https://www.googleapis.com/oauth2/v1/certs"),
            "client_x509_cert_url": secrets.get("client_x509_cert_url", "")
        }

        if not creds_info["client_email"]:
            st.error("LỖI: Chưa có 'client_email'. Vui lòng kiểm tra lại file Secrets.")
            st.stop()

        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        
        url = secrets.get("spreadsheet", "")
        if not url and "spreadsheet" in st.secrets:
            url = st.secrets["spreadsheet"]
            
        if len(url) < 50:
            return client.open_by_key(url)
        else:
            return client.open_by_url(url)
    except Exception as e:
        st.error(f"Lỗi khởi tạo kết nối Google Sheets: {e}")
        st.stop()

def format_drive_direct_url(link):
    if not link or not isinstance(link, str): return ""
    match = re.search(r'(pires=|/d/|id=)([a-zA-Z0-9-_]{33,40})', link.strip())
    return f"https://lh3.googleusercontent.com/d/{match.group(2)}" if match else ""

@st.cache_data(ttl=3600)
def get_settings():
    try:
        sh = get_google_sheet_workbook()
        rows = sh.worksheet("ThietLap").get_all_values()
        return {str(row[0]).strip(): str(row[1]).strip() for row in rows if len(row) > 1}
    except Exception:
        return {"TenTiem": "SALON KIM HIỀN", "Diachi": "131, TRẦN BÌNH TRỌNG, LONG XUYÊN", "SDT": "0947.58.1516"}

@st.cache_data(ttl=3600)
def get_service_data():
    try:
        sh = get_google_sheet_workbook()
        rows = sh.worksheet("DanhMuc").get_all_values()
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
        sh = get_google_sheet_workbook()
        return sh.worksheet("NhanVien").get_all_values()
    except Exception: return []

@st.cache_data(ttl=60)
def get_khach_hang_data():
    try:
        sh = get_google_sheet_workbook()
        rows = sh.worksheet("KhachHang").get_all_values()
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
        sh = get_google_sheet_workbook()
        return sh.worksheet("PLKH").get_all_values()
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
        sh = get_google_sheet_workbook()
        bc_values = sh.worksheet("BaoCao").get_all_values()
        tam_records = sh.worksheet("BillTam").get_all_values()
        return bc_values, tam_records
    except Exception:
        return [], []

def luu_bill_tam(gio_hang, nhan_vien, kh_sdt="", kh_ten="Khách lẻ"):
    try:
        sh = get_google_sheet_workbook()
        ws = sh.worksheet("BillTam")
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
        sh = get_google_sheet_workbook()
        ws = sh.worksheet("BillTam")
        ws.delete_rows(index_sheet_row)
        get_bao_cao_va_bill_tam.clear()
        return True
    except Exception as e:
        st.error(f"Lỗi xóa bill tạm trên Sheets: {e}")
        return False

def gui_email_backup(noi_dung):
    try:
        sender_email = "huynhcongtuan0978666620@gmail.com"
        password = "lwui aesw vqal ytcq" 
        receiver_emails = ["huynhcongtuan0978666620@gmail.com"]
        gio_vn_mail = get_now_vn().strftime('%d/%m/%Y %H:%M')
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

    st.markdown(generate_css_animations(st.session_state.theme), unsafe_allow_html=True)
    st.markdown("""<div class="banner-top">QUẢN LÝ DỊCH VỤ</div><div class="banner-bottom">SALON KIM HIỀN © 2026 - VISION V12</div>""", unsafe_allow_html=True)

    settings = get_settings()

    c_header, c_menu = st.columns([88, 12])
    with c_header:
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
    with c_menu:
        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
        with st.popover("...", help="Menu cấu hình nhanh"):
            st.markdown("<div style='font-size:12px; font-weight:700; color:#888; text-align:center;'>TÙY CHỌN</div>", unsafe_allow_html=True)
            if st.button("☀️ Sáng" if st.session_state.theme == "dark" else "🌙 Tối", use_container_width=True):
                st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
                st.rerun()
            c_up, c_down = st.columns(2)
            with c_up:
                if st.button("⬆️ Lên"): st.session_state.scroll_trigger = "up"
            with c_down:
                if st.button("⬇️ Xuống"): st.session_state.scroll_trigger = "down"
            if st.button("🔄 Làm mới F5", use_container_width=True): st.rerun()
            if st.button("🎉 Pháo hoa", use_container_width=True):
                st.session_state.trigger_boom = True
                st.rerun()
            st.markdown('<a href="tel:0978666620" class="btn-zalo" style="background-color:#28a745; text-align:center; padding:8px; font-size:12px;">📞 Gọi Admin</a>', unsafe_allow_html=True)
            if st.session_state["logged_in"]:
                if st.button("🚪 Đăng xuất", use_container_width=True, type="primary"):
                    st.session_state.clear()
                    st.rerun()

    if st.session_state.scroll_trigger == "down":
        st.components.v1.html("<script>window.parent.document.querySelector('section.main').scrollTo({top: window.parent.document.querySelector('section.main').scrollHeight, behavior: 'smooth'});</script>", height=0, width=0)
        st.session_state.scroll_trigger = None
    elif st.session_state.scroll_trigger == "up":
        st.components.v1.html("<script>window.parent.document.querySelector('section.main').scrollTo({top: 0, behavior: 'smooth'});</script>", height=0, width=0)
        st.session_state.scroll_trigger = None

    if st.session_state.trigger_boom:
        st.markdown(render_fireworks_html(), unsafe_allow_html=True)
        st.session_state.trigger_boom = False
    if st.session_state.trigger_balloons:
        render_balloons_html()  
        st.session_state.trigger_balloons = False

    # --- ĐĂNG NHẬP ---
    if not st.session_state["logged_in"]:
        saved_u = st.query_params.get("saved_u", "")
        saved_p = st.query_params.get("saved_p", "")
        with st.form("login_section"):
            st.markdown("<div class='the-quan-ly-flat' style='text-align: center; border:none; margin-bottom: 5px;'>ĐĂNG NHẬP HỆ THỐNG</div>", unsafe_allow_html=True)
            u = st.text_input("Tài khoản (Số điện thoại)", value=saved_u)
            p = st.text_input("Mật khẩu", type="password", value=saved_p)
            remember_me = st.checkbox("Ghi nhớ mật khẩu", value=bool(saved_u))
            
            if st.form_submit_button("Xác nhận Đăng Nhập", use_container_width=True, type="primary"):
                if u == "admin" and p == "2026":
                    if remember_me:
                        st.query_params["saved_u"] = u
                        st.query_params["saved_p"] = p
                    else:
                        st.query_params.clear()
                    st.session_state.update({"logged_in": True, "role": "Admin", "full_name": "Quản lý", "trigger_balloons": True, "tho_chot_val": "Quản lý"})
                    st.rerun()
                else:
                    raw_data = get_nhan_vien_data()
                    if len(raw_data) > 0:
                        headers = [str(h).strip() for h in raw_data[0]]
                        col_sdt_idx = next((i for i, h in enumerate(headers) if 'điện thoại' in h.lower() or 'sđt' in h.lower() or 'tai khoan' in h.lower()), -1)
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
                                st.query_params.clear()
                            ten_that = str(found_row[col_ten_idx]).strip() if col_ten_idx != -1 and col_ten_idx < len(found_row) else "Nhân viên"
                            st.session_state.update({"logged_in": True, "role": "NhanVien", "full_name": ten_that, "trigger_balloons": True, "tho_chot_val": ten_that})
                            time.sleep(0.3)
                            st.rerun()
                        else: st.error("Thông tin số điện thoại hoặc mật khẩu không chính xác.")
                    else: st.error("Hệ thống dữ liệu chưa sẵn sàng.")
        
        if st.button("Làm mới hoàn toàn ứng dụng", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # --- KHU VỰC LÀM VIỆC CHÍNH ---
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
        # TAB 1: TẠO ĐƠN
        # =================================================================
        with tabs[0]:
            st.markdown(f"<div style='text-align: right; font-size: 13px; color: #888; margin-bottom: 15px;'>Thành viên: <b>{st.session_state.full_name}</b> | VN: {get_now_vn().strftime('%H:%M %d/%m/%y')}</div>", unsafe_allow_html=True)
            
            if st.session_state.get("bill_vua_in"):
                st.markdown('<div class="the-quan-ly-flat">🧾 HOÁ ĐƠN DỊCH VỤ VỪA KHỞI TẠO</div>', unsafe_allow_html=True)
                st.markdown(st.session_state.bill_vua_in, unsafe_allow_html=True)
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
                        c_sdt_hist = next((c for c in df_hist.columns if 'sđt' in c.lower() or 'sdt' in c.lower()), None)
                        c_ma_hist = next((c for c in df_hist.columns if 'mã' in c.lower() or 'hd' in c.lower()), None)
                        if c_sdt_hist and c_ma_hist:
                            s_k_0 = st.session_state.kh_sdt_val.strip()
                            s_k_0 = s_k_0[1:] if s_k_0.startswith('0') else s_k_0
                            matches = df_hist[df_hist[c_sdt_hist].astype(str).str.contains(s_k_0, na=False)]
                            so_lan_den = len(matches[c_ma_hist].unique())
                except: pass

            if so_lan_den > 0:
                st.markdown(f'<div class="lsc-vip">🌟 Khách siêu quen: Đã ghé tiệm {so_lan_den} lần!</div>', unsafe_allow_html=True)
            
            if st.session_state["role"] == "Admin" and st.session_state.kh_sdt_val.strip() and st.session_state.hang_hien_tai:
                st.markdown(f"""
                    <div style="text-align: right; margin-top: -10px; margin-bottom: 15px;">
                        <span style="background-color: #fffbfa; padding: 4px 12px; border-radius: 12px; border: 1px solid #ffe1df; font-size: 11px; font-weight: 700; color: #d4380d;">
                            {st.session_state.hang_hien_tai} | Tích lũy: {st.session_state.tong_chi_tieu_val:,.0f} đ
                        </span>
                    </div>
                """, unsafe_allow_html=True)

            st.write("")
            st.markdown('<div class="the-quan-ly-flat">DANH SÁCH DỊCH VỤ</div>', unsafe_allow_html=True)
            max_dv = 3 if st.session_state.get("role") == "NhanVien" else None
            
            dv_chon = st.multiselect(
                "Chạm chọn dịch vụ...", 
                options=dv_list if dv_list else ["Đang tải danh mục..."], 
                max_selections=max_dv,
                placeholder="Chọn tối đa 3 dịch vụ..." if max_dv else "Chọn thoải mái nhiều dịch vụ...",
                key=f"dv_multi_key_{st.session_state.reset_counter}"
            )
            
            if st.button("➕ THÊM VÀO GIỎ HÀNG", type="primary", use_container_width=True):
                if not dv_chon:
                    st.warning("⚠️ Vui lòng lựa chọn ít nhất một dịch vụ!")
                else:
                    for dv in dv_chon:
                        info_dv = services.get(dv, {"gia": 0.0, "hoa_hong": 0.0})
                        gia_goc = info_dv.get("gia", 0.0)
                        phan_tram_hh = info_dv.get("hoa_hong", 0.0)
                        
                        existing = next((item for item in st.session_state.gio_hang if item["dich_vu"] == dv), None)
                        if existing:
                            existing["so_luong"] += 1.0
                            existing["thanh_tien"] = existing["so_luong"] * existing["don_gia"]
                        else:
                            st.session_state.gio_hang.append({
                                "dich_vu": dv, "so_luong": 1.0, "don_gia": gia_goc,
                                "thanh_tien": gia_goc, "phan_tram_hh": phan_tram_hh
                            })
                            
                    if 'start_time' not in st.session_state or len(st.session_state.gio_hang) == len(dv_chon):
                        st.session_state.start_time = get_now_vn()
                    st.session_state.reset_counter += 1  
                    st.toast(f"✅ Đã thêm {len(dv_chon)} dịch vụ!")
                    time.sleep(0.3)
                    st.rerun()

            t_bill = 0.0
            if st.session_state.gio_hang:
                st.write("")
                st.markdown(f'<div class="the-quan-ly-flat">🛒 GIỎ HÀNG ({len(st.session_state.gio_hang)} món)</div>', unsafe_allow_html=True)
                
                for idx, item in enumerate(st.session_state.gio_hang):
                    st.markdown(f"<div style='font-size:14px; font-weight:600; margin-bottom:6px;'>📍 {item['dich_vu']}</div>", unsafe_allow_html=True)
                    
                    c_sl, c_tt, c_del = st.columns([5, 3, 2])
                    with c_sl:
                        new_sl = st.number_input("Số lượng:", min_value=0.5, max_value=50.0, value=float(item['so_luong']), step=0.5, key=f"cart_sl_{idx}")
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

                if st.button("💾 TẠM LƯU ĐƠN VÀO BILL CHỜ", use_container_width=True):
                    if luu_bill_tam(st.session_state.gio_hang, st.session_state.full_name, st.session_state.kh_sdt_val, st.session_state.kh_ten_val):
                        st.session_state.update({"gio_hang": [], "kh_sdt_val": "", "kh_ten_val": "Khách lẻ", "hang_hien_tai": "", "tong_chi_tieu_val": 0.0, "tho_chot_val": st.session_state.full_name})
                        st.toast("✅ Đã lưu đơn tạm!")
                        time.sleep(1)
                        st.rerun()

            if t_bill > 0:
                st.markdown('<div class="the-quan-ly-flat">THU NGÂN & CHIẾT KHẤU</div>', unsafe_allow_html=True)
                
                opts_tho = [t for t in ds_tho if t.strip()]
                if st.session_state.full_name not in opts_tho: opts_tho.append(st.session_state.full_name)
                if not st.session_state.tho_chot_val: st.session_state.tho_chot_val = st.session_state.full_name
                if st.session_state.tho_chot_val not in opts_tho: opts_tho.append(st.session_state.tho_chot_val)
                
                try: idx_def = opts_tho.index(st.session_state.tho_chot_val)
                except: idx_def = 0
                
                chot_tho = st.selectbox("Thợ thực hiện (Tính KPI):", options=opts_tho, index=idx_def)

                cn1, cn2 = st.columns(2)
                with cn1: tien_giam = st.number_input("Chiết khấu (VND)", min_value=0.0, max_value=float(t_bill), value=0.0, step=1000.0)
                with cn2: khuyen_mai = st.number_input("Khuyến mãi trừ thêm", min_value=0.0, max_value=float(t_bill), value=0.0, step=1000.0)
                
                ghi_chu = st.text_input("Ghi chú đơn hàng")
                
                tong_tru = tien_giam + khuyen_mai
                t_khach_tra = max(0.0, t_bill - tong_tru)
                hs_giam = t_khach_tra / t_bill if t_bill > 0 else 1.0
                t_cong_tho = sum(item['thanh_tien'] * hs_giam * (item['phan_tram_hh'] / 100.0) for item in st.session_state.gio_hang)
                
                st.write("")
                cb1, cb2, cb3, cb4 = st.columns(4)
                with cb1: st.markdown(f'<div class="nhan-tieu-de">Tổng bill</div><div class="box-chung tong-don-box">{t_bill:,.0f}</div>', unsafe_allow_html=True)
                with cb2: st.markdown(f'<div class="nhan-tieu-de">Chiết khấu</div><div class="box-chung chiet-khau-box">{tien_giam:,.0f}</div>', unsafe_allow_html=True)
                with cb3: st.markdown(f'<div class="nhan-tieu-de">Khuyến mãi</div><div class="box-chung chiet-khau-box">{khuyen_mai:,.0f}</div>', unsafe_allow_html=True)
                with cb4: st.markdown(f'<div class="nhan-tieu-de">Thực thu</div><div class="box-chung khach-tra-box">{t_khach_tra:,.0f}</div>', unsafe_allow_html=True)
                
                st.markdown(f'<div style="text-align:right; font-size:13px; color:#888; margin-top:8px;">Hoa hồng thợ: <b>{t_cong_tho:,.0f}đ</b></div>', unsafe_allow_html=True)
                
                kh_dua = st.number_input("Số tiền mặt khách trả", 0.0, value=float(t_khach_tra))
                t_du = kh_dua - t_khach_tra
                if t_du > 0: st.markdown(f'<div class="tien-thua-box">Tiền thối lại: <span>{t_du:,.0f} VND</span></div>', unsafe_allow_html=True)

                can_go = True
                if st.session_state["role"] == "NhanVien" and st.session_state.last_submit:
                    tg_cho = (get_now_vn() - st.session_state.last_submit).total_seconds() / 60
                    han_muc = 1 if st.session_state.submit_count == 1 else 2 if st.session_state.submit_count >= 2 else 0
                    if tg_cho < han_muc:
                        can_go = False
                        st.markdown(f'<div class="lsc-shake">Vui lòng chờ {round(han_muc - tg_cho, 1)} phút để tạo đơn tiếp.</div>', unsafe_allow_html=True)

                if can_go:
                    cam_ket = st.checkbox("Tôi cam kết số liệu chuẩn xác")
                    if not st.session_state.submitting:
                        if st.button("🚀 XÁC NHẬN & XUẤT HÓA ĐƠN", use_container_width=True, type="primary"):
                            if cam_ket:
                                st.session_state.submitting = True
                                st.rerun()
                            else: st.warning("Vui lòng xác nhận trước khi lưu.")
                    else:
                        st.button("Đang đồng bộ Google Sheets...", disabled=True, use_container_width=True)
                        try:
                            sh = get_google_sheet_workbook()
                            ws = sh.worksheet("BaoCao")
                            bay_gio = get_now_vn()
                            ma_hd = f"HD{bay_gio.strftime('%y%m%d%H%M')}"
                            
                            start_time = st.session_state.get("start_time", bay_gio)
                            tg_phuc_vu = max(0, int((bay_gio - start_time).total_seconds() / 60))
                            
                            rows_to_append = []
                            html_items = ""
                            chi_tiet_tele = "" 
                            
                            c_ten = st.session_state.kh_ten_val.strip() if st.session_state.kh_ten_val.strip() else "Khách lẻ"
                            c_sdt = st.session_state.kh_sdt_val.strip()
                            c_ghi_chu = f"[CK: {tien_giam:,.0f} | KM: {khuyen_mai:,.0f}] {ghi_chu}"
                            
                            for item in st.session_state.gio_hang:
                                hh_dong = item['thanh_tien'] * hs_giam * (item['phan_tram_hh'] / 100.0)
                                rows_to_append.append([
                                    bay_gio.strftime("%d/%m/%Y"), st.session_state.full_name, c_ten, c_sdt,
                                    item['dich_vu'], item['so_luong'], item['don_gia'], item['thanh_tien'],
                                    bay_gio.strftime("%H:%M:%S"), c_ghi_chu, hh_dong, ma_hd,
                                    kh_dua, t_du, f"{tg_phuc_vu} phút", chot_tho
                                ])
                                
                                sl_sach = int(item['so_luong']) if float(item['so_luong']).is_integer() else item['so_luong']
                                html_items += f"""<tr><td style="text-align: left; border: none; padding: 6px 0;"><div class="hd-item-name">{item["dich_vu"]}</div><div class="hd-item-sub">{sl_sach} x {item['don_gia']:,.0f}đ</div></td><td style="text-align: right; border: none; padding: 6px 0; vertical-align: middle;"><div class="hd-item-price">{item["thanh_tien"]:,.0f}đ</div></td></tr>"""
                                chi_tiet_tele += f"\n- {item['dich_vu']} (x{sl_sach}): {item['thanh_tien']:,.0f}đ"
                                
                            ws.append_rows(rows_to_append)
                            get_bao_cao_va_bill_tam.clear() 
                            get_plkh_data.clear()
                            
                            if c_sdt:
                                ds_kh_hien_tai = get_khach_hang_data()
                                s_k_0 = c_sdt[1:] if c_sdt.startswith('0') else c_sdt
                                s_c_0 = '0' + c_sdt if not c_sdt.startswith('0') else c_sdt
                                is_sdt_cu = (c_sdt in ds_kh_hien_tai) or (s_k_0 in ds_kh_hien_tai) or (s_c_0 in ds_kh_hien_tai)
                                
                                if not is_sdt_cu and c_ten != "Khách lẻ" and c_ten != "":
                                    ws_kh = sh.worksheet("KhachHang")
                                    ws_kh.append_row([c_sdt, c_ten])
                                    st.cache_data.clear() 
                            
                            huy_hieu_bill = st.session_state.hang_hien_tai if (st.session_state["role"] == "Admin" and c_sdt and c_ten != "Khách lẻ" and st.session_state.hang_hien_tai != "🌱 TIỀM NĂNG") else ""
                            huy_hieu_tele = f" | Hạng: {huy_hieu_bill}" if huy_hieu_bill else ""

                            nd_mail = f"THÔNG BÁO - Đã thanh toán\n \nMã ĐH: {ma_hd} | {bay_gio.strftime('%d/%m/%Y %H:%M')}\nKhách: {c_ten} - {c_sdt}{huy_hieu_tele}\nThu ngân: {st.session_state.full_name}\nThợ: {chot_tho}\n \nDịch vụ:{chi_tiet_tele}\n \nTổng bill: {t_bill:,.0f} đ\nTrừ: -{tong_tru:,.0f} đ\nKhách đưa: {kh_dua:,.0f} đ\nTiền thối: {t_du:,.0f} đ\nPhục vụ: {tg_phuc_vu} phút\n \nTHỰC THU: {t_khach_tra:,.0f} đ"
                            gui_email_backup(nd_mail)
                            gui_telegram_notification(nd_mail)
                            
                            btn_zl = ""
                            if c_sdt:
                                zl_sdt = str(c_sdt).strip().replace(" ", "").replace("+84", "0")
                                if not zl_sdt.startswith('0') and zl_sdt: zl_sdt = '0' + zl_sdt
                                btn_zl = f'<a href="zalo://conversation?phone={zl_sdt}" target="_blank" class="btn-zalo">💬 Nhắn Zalo khách</a>'
                            
                            html_hh = f'<div style="font-size: 11px; color: #d4380d; font-weight: bold; text-align: right; margin-top: -15px; margin-bottom: 15px;">Hạng: {huy_hieu_bill}</div>' if huy_hieu_bill else ""
                            
                            st.session_state.bill_vua_in = f"""<style>.hoa-don-khung table, .hoa-don-khung tr, .hoa-don-khung td {{border: none !important; background: transparent !important;}}</style>
<div class="hoa-don-khung">
<div class="hd-header"><div style="font-size: 18px; font-weight: 800;">{settings.get('TenTiem', 'SALON KIM HIỀN')}</div><div style="font-size: 13px; color: #666; margin-top:4px;">{settings.get('Diachi', '')}</div><div style="font-size: 13px; color: #666;">SĐT: {settings.get('SDT', '')}</div><div class="hd-title">HÓA ĐƠN DỊCH VỤ</div><div style="font-size: 12px; color: #888; margin-top:5px;">Mã số: {ma_hd}</div></div>
<div style="font-size: 13px; font-weight: 600; color: #555; text-align: left; margin-bottom: 8px; border-bottom: 1px dashed #eaeaea; padding-bottom: 5px;">Thông tin khách hàng:</div>
{html_hh}
<div style="border-bottom: 1px solid #eaeaea; padding-bottom: 10px; margin-bottom: 15px; font-size: 14px; color: #444;">
    <div style="display: flex; justify-content: space-between; margin-bottom: 6px;"><span>Ngày:</span> <span>{bay_gio.strftime('%d/%m/%Y %H:%M')}</span></div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 6px;"><span>Khách hàng:</span> <span style="font-weight:600;">{c_ten}</span></div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 6px;"><span>Thu ngân:</span> <span>{st.session_state.full_name}</span></div>
    <div style="display: flex; justify-content: space-between;"><span>Thợ thực hiện:</span> <span style="font-weight:600;">{chot_tho}</span></div>
</div>
<div style="margin-bottom: 15px;"><div style="font-size: 13px; font-weight: 600; color: #555; text-align: left; margin-bottom: 8px; border-bottom: 1px dashed #eaeaea; padding-bottom: 5px;">Chi tiết dịch vụ:</div>
    <table style="width: 100%; border-collapse: collapse;">{html_items}</table>
</div>
<div style="font-size: 14px; border-bottom: 1px solid #eaeaea; padding-bottom: 10px; margin-bottom: 15px;">
    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;"><span>Cộng tiền:</span> <span>{t_bill:,.0f}</span></div>
    <div style="display: flex; justify-content: space-between; color: #d93025; margin-bottom: 8px;"><span>Giảm trừ:</span> <span>-{tong_tru:,.0f}</span></div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;"><span>Khách đưa:</span> <span>{kh_dua:,.0f}</span></div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;"><span>Tiền thối:</span> <span>{t_du:,.0f}</span></div>
    <div style="display: flex; justify-content: space-between;"><span>Thời gian phục vụ:</span> <span>{tg_phuc_vu} phút</span></div>
</div>
<div style="font-size: 13px; font-weight: 600; color: #555; text-align: left; margin-bottom: 8px; border-bottom: 1px dashed #eaeaea; padding-bottom: 5px;">Sô tiền thanh toán:</div>
<div style="font-size: 15px; font-weight: 700;"><div style="display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 18px;"><span>TỔNG CỘNG:</span> <span>{t_khach_tra:,.0f}</span></div></div>
<div style="text-align: center; margin-top: 25px; font-size: 13px; color: #888;">Cảm ơn quý khách đã sử dụng dịch vụ!</div>
{btn_zl}
</div>"""
                            st.session_state.update({
                                "gio_hang": [], "last_submit": bay_gio, "submit_count": st.session_state.submit_count + 1, 
                                "submitting": False, "trigger_boom": True, "kh_sdt_val": "", "kh_ten_val": "Khách lẻ",
                                "hang_hien_tai": "", "tong_chi_tieu_val": 0.0,
                                "start_time": get_now_vn(), "tho_chot_val": st.session_state.full_name
                            })
                            st.rerun()
                        except Exception as e:
                            st.error(f"Hệ thống gián đoạn, vui lòng nhấn Tạo Đơn lại: {e}")
                            st.session_state.submitting = False

        # =================================================================
        # TAB 2, 3, 4 DÀNH CHO ADMIN
        # =================================================================
        if st.session_state["role"] == "Admin":
            with tabs[1]:
                st.markdown('<div class="the-quan-ly-flat">QUẢN LÝ BILL CHỜ</div>', unsafe_allow_html=True)
                if st.button("🔄 Làm mới đơn chờ", use_container_width=True):
                    get_bao_cao_va_bill_tam.clear() 
                    st.rerun()
                try:
                    _, data_tam = get_bao_cao_va_bill_tam()
                    if len(data_tam) > 1:
                        rows_tam = data_tam[1:]
                        st.write(f"Đang ghi nhận **{len(rows_tam)}** đơn hàng nháp:")
                        for i, row in enumerate(rows_tam):
                            sheet_row_idx = i + 2 
                            cleaned = [str(c).strip() for c in row]
                            valid = [idx for idx, c in enumerate(cleaned) if c != ""]
                            if not valid: continue
                            real_data = cleaned[valid[0]:]
                            
                            t_tao_str = real_data[0] if len(real_data) > 0 else ""
                            chi_tiet_dv = real_data[1] if len(real_data) > 1 else ""
                            t_tien_str = real_data[2] if len(real_data) > 2 else "0"
                            tho_lam = real_data[3] if len(real_data) > 3 else "Chưa rõ"
                            sdt_kh = real_data[4] if len(real_data) > 4 else ""
                            ten_kh = real_data[5] if len(real_data) > 5 else "Khách lẻ"
                            
                            with st.container(border=True):
                                col_info, col_act = st.columns([7, 3])
                                with col_info:
                                    st.markdown(f"👤 **Khách:** {ten_kh} ({sdt_kh})")
                                    st.markdown(f"🛠 **Chi tiết:** `{chi_tiet_dv}`")
                                    try: st.markdown(f"💰 **Tạm tính:** `{float(t_tien_str.replace(',','').replace('.','')):,.0f}đ` | 🤝 **Thợ:** {tho_lam}")
                                    except: st.markdown(f"💰 **Tạm tính:** `{t_tien_str}đ` | 🤝 **Thợ:** {tho_lam}")
                                with col_act:
                                    st.write("")
                                    if st.button("🛒 Nạp ra", key=f"load_{sheet_row_idx}", use_container_width=True, type="primary"):
                                        with st.spinner("Đang nạp..."):
                                            new_gio = []
                                            for item in chi_tiet_dv.split(" | "):
                                                if item.strip():
                                                    match = re.match(r"(.+)\s*\(x([\d\.]+)\)", item.strip())
                                                    if match:
                                                        t_dv, s_l = match.group(1).strip(), float(match.group(2))
                                                        info = services.get(t_dv, {"gia": 0.0, "hoa_hong": 0.0})
                                                        new_gio.append({"dich_vu": t_dv, "so_luong": s_l, "don_gia": info.get("gia", 0.0), "thanh_tien": info.get("gia", 0.0) * s_l, "phan_tram_hh": info.get("hoa_hong", 0.0)})
                                            
                                            st.session_state.update({"gio_hang": new_gio, "kh_sdt_val": sdt_kh, "kh_ten_val": ten_kh, "tho_chot_val": tho_lam, "bill_vua_in": None})
                                            
                                            try:
                                                plkh = get_plkh_data()
                                                s_k = sdt_kh[1:] if sdt_kh.startswith('0') else sdt_kh
                                                for r in plkh[1:]:
                                                    if len(r) >= 2 and str(r[0]).strip() in [sdt_kh, s_k, '0'+s_k]:
                                                        t_chi = float(str(r[1]).replace(',', '').replace('.', '').replace('đ', '').strip() or 0)
                                                        st.session_state.update({"tong_chi_tieu_val": t_chi, "hang_hien_tai": get_huy_hieu(t_chi)})
                                                        break
                                            except: pass
                                            
                                            try: st.session_state.start_time = pytz.timezone('Asia/Ho_Chi_Minh').localize(datetime.strptime(t_tao_str, "%Y-%m-%d %H:%M:%S"))
                                            except: st.session_state.start_time = get_now_vn() 
                                            
                                            if xoa_bill_tam_dong_gốc(sheet_row_idx):
                                                st.toast("⚡ Đã nạp!")
                                                time.sleep(0.5)
                                                st.rerun()
                    else: st.info("Không có đơn chờ.")
                except Exception as e: st.error(f"Lỗi đọc đơn chờ: {e}")

            with tabs[2]:
                st.markdown('<div class="the-quan-ly-flat">BÁO CÁO DOANH THU</div>', unsafe_allow_html=True)
                if st.button("⏰ Cập nhật dữ liệu", use_container_width=True):
                    get_bao_cao_va_bill_tam.clear()
                    st.rerun()
                try:
                    bc_values, tam_records = get_bao_cao_va_bill_tam()
                    don_cho = max(0, len(tam_records) - 1) if tam_records else 0
                    tong_dt = trung_binh = tong_don = so_khach = 0
                    df_hien_thi = pd.DataFrame()
                    df_bc = pd.DataFrame()
                    
                    if len(bc_values) > 1:
                        df_bc = pd.DataFrame(bc_values[1:], columns=bc_values[0])
                        c_tien = next((c for c in df_bc.columns if 'tiền' in c.lower() or 'tien' in c.lower()), 'Thành tiền')
                        c_ngay = next((c for c in df_bc.columns if 'ngày' in c.lower() or 'ngay' in c.lower()), 'Ngày')
                        c_ma = next((c for c in df_bc.columns if 'mã' in c.lower() or 'hd' in c.lower()), None)
                        c_khach = next((c for c in df_bc.columns if 'khách' in c.lower()), None)
                        
                        df_bc[c_tien] = pd.to_numeric(df_bc[c_tien].astype(str).str.replace(',', '').str.replace('.', ''), errors='coerce').fillna(0)
                        df_today = df_bc[df_bc[c_ngay] == get_now_vn().strftime("%d/%m/%Y")] if c_ngay in df_bc.columns else pd.DataFrame()

                        tong_dt = df_today[c_tien].sum() if not df_today.empty else 0
                        if c_ma and not df_today.empty: tong_don = len([x for x in df_today[c_ma].unique() if str(x).strip() != ''])
                        trung_binh = tong_dt / tong_don if tong_don > 0 else 0
                        if c_khach and not df_today.empty: so_khach = len(df_today[c_khach].unique())

                        df_hien_thi = df_bc.tail(50).copy()
                        df_hien_thi.index = range(1, len(df_hien_thi) + 1)
                    
                    c1, c2 = st.columns(2)
                    c1.metric("💰 Doanh thu hôm nay", f"{tong_dt:,.0f}đ")
                    c2.metric("💳 Bình quân đơn", f"{trung_binh:,.0f}đ")
                    
                    c3, c4, c5 = st.columns(3)
                    c3.metric("📦 Tổng đơn", tong_don)
                    c4.metric("👥 Khách", so_khach)
                    c5.metric("⏳ Đơn chờ", don_cho)
                    
                    if not df_bc.empty:
                        col_chart, col_kpi = st.columns([6, 4])
                        with col_chart:
                            st.markdown('<div class="nhan-tieu-de">📈 BIỂU ĐỒ DOANH THU</div>', unsafe_allow_html=True)
                            st.bar_chart(df_bc.groupby(c_ngay)[c_tien].sum().reset_index().tail(7).set_index(c_ngay), use_container_width=True)
                        with col_kpi:
                            st.markdown('<div class="nhan-tieu-de">🏆 KPI THỢ HÔM NAY</div>', unsafe_allow_html=True)
                            if not df_today.empty and len(df_today.columns) >= 16:
                                kpi_df = df_today.groupby(df_today.columns[15])[c_tien].sum().reset_index()
                                kpi_df.columns = ["Tên thợ", "Doanh thu"]
                                kpi_df = kpi_df.sort_values(by="Doanh thu", ascending=False)
                                kpi_df["Doanh thu"] = kpi_df["Doanh thu"].apply(lambda x: f"{x:,.0f} đ")
                                st.dataframe(kpi_df, use_container_width=True, hide_index=True)
                            else: st.info("Chưa có giao dịch.")

                    st.markdown('<div class="the-quan-ly-flat">50 GIAO DỊCH GẦN NHẤT</div>', unsafe_allow_html=True)
                    if not df_hien_thi.empty: st.dataframe(df_hien_thi, use_container_width=True)
                except Exception as e: st.error(f"Lỗi: {e}")

            with tabs[3]:
                st.markdown('<div class="the-quan-ly-flat">QUẢN TRỊ TRUNG TÂM</div>', unsafe_allow_html=True)
                if st.button("♻️ ÉP BUỘC XÓA KẾT NỐI & LÀM MỚI BỘ NHỚ", use_container_width=True, type="primary"):
                    # NÚT NÀY LÀ CỨU CÁNH CHÍNH CHO VIỆC NGHẼN MẠNG
                    st.cache_data.clear()
                    st.cache_resource.clear() 
                    st.success("Đã xóa sạch bộ nhớ tạm và tái tạo lại toàn bộ đường truyền Google Sheets!")
                    time.sleep(1)
                    st.rerun()
                
                if st.button("Đăng xuất Admin khẩn cấp", use_container_width=True):
                    st.session_state.clear()
                    st.rerun()

if __name__ == "__main__":
    main()
