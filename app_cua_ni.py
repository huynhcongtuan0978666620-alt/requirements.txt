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
# 🌟 MENU ĐIỀU CHỈNH MÀU SẮC (DESIGN SYSTEM) - V14
# Ní chỉ cần thay đổi các mã HEX ở đây, toàn bộ App sẽ đổi màu theo.
# =====================================================================
THEME_COLORS = {
    # 1. Màu nền (Backgrounds)
    "bg_app": "#EEF4F8",            # Nền tổng thể của toàn bộ App
    "bg_card": "#ffffff",           # Nền của các thẻ (Card UI)
    "bg_box_chung": "#f8f9fa",      # Nền của các ô số liệu (Thực thu, Tiền thối...)
    "bg_vip_box": "#eaf2e6",        # Nền của thông báo Khách quen (Màu xanh ngọc nhạt)
    "bg_shake_box": "#fff1f0",      # Nền của thông báo lỗi/chờ (Màu đỏ nhạt)
    "bg_badge_hang": "#fffbfa",     # Nền của huy hiệu hạng khách hàng

    # 2. Màu chủ đạo & Điểm nhấn (Primary & Accents)
    "primary": "#6FA8DC",           # Màu chủ đạo (Viền card, Tab đang chọn, Nút bấm chính)
    "accent_vip": "#13c2c2",        # Màu nhấn cho thông báo VIP/Khách quen
    "accent_danger": "#cf1322",     # Màu nhấn cho lỗi/cảnh báo (Màu đỏ đậm)
    "accent_zalo": "#0068ff",       # Màu chuẩn của nút Zalo
    "accent_chiet_khau": "#d93025", # Màu đỏ cho tiền chiết khấu / giảm trừ

    # 3. Màu chữ (Typography)
    "text_main": "#111111",         # Màu chữ chính (Tiêu đề, số liệu quan trọng)
    "text_secondary": "#555555",    # Màu chữ phụ (Tiêu đề các mục nhỏ)
    "text_muted": "#888888",        # Màu chữ mờ (Ghi chú, nhãn phụ)
    "text_title": "#2c3e50",        # Màu chữ của các tiêu đề khối (.the-quan-ly-flat)
    "text_badge": "#d4380d",        # Màu chữ của huy hiệu hạng khách hàng
    
    # 4. Màu viền (Borders)
    "border_light": "#eaeaea",      # Viền mỏng phân cách các khối
    "border_input": "#cccccc",      # Viền của ô nhập liệu (Text input, Number input)
    "border_badge": "#ffe1df",      # Viền của huy hiệu hạng khách hàng
    "border_vip": "#87e8de",        # Viền của thông báo VIP

    # 5. Bóng đổ (Shadows)
    "shadow_light": "rgba(0,0,0,0.05)",  # Bóng đổ nhẹ cho Card và Tabs
    "shadow_heavy": "rgba(0,0,0,0.08)",  # Bóng đổ đậm hơn cho Hóa đơn xuất
    "shadow_toast": "rgba(0,0,0,0.1)",   # Bóng đổ cho Toast (Thông báo nổi)
}


# =====================================================================
# 1. CẤU HÌNH GIAO DIỆN V14
# =====================================================================
st.set_page_config(
    page_title="LKTV Channel V14", 
    layout="centered", 
    page_icon="💎",
    initial_sidebar_state="collapsed"
)

def get_now_vn():
    vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    return datetime.now(vn_tz)

def inject_advanced_ui_js():
    js_code = f"""
    <script>
    const parentDoc = window.parent.document;
    function showPremiumToast(text) {{
        let t = parentDoc.createElement('div');
        t.innerText = text;
        t.style.cssText = "position:fixed; top:15%; left:50%; transform:translate(-50%, -50%); background: {THEME_COLORS['bg_card']}; color:{THEME_COLORS['text_main']}; padding:15px 30px; border-radius:12px; font-weight:bold; box-shadow: 0 10px 30px {THEME_COLORS['shadow_toast']}; border-left: 5px solid {THEME_COLORS['primary']}; z-index:9999999; font-size:15px; transition: opacity 0.5s; text-align:center;";
        parentDoc.body.appendChild(t);
        setTimeout(() => {{ t.style.opacity = '0'; setTimeout(()=>t.remove(), 500); }}, 2500);
    }}
    if(!parentDoc.body.hasAttribute('data-fw-v14')) {{
        parentDoc.body.setAttribute('data-fw-v14', '1');
        let clicks = 0;
        let timer = null;
        parentDoc.addEventListener('click', (e) => {{
            clicks++;
            clearTimeout(timer);
            timer = setTimeout(() => {{ clicks = 0; }}, 1000); 
            if(clicks >= 3) {{
                clicks = 0;
                showPremiumToast('🎉 Chào mừng đến với NHÀ CỦA HIỀN 🎉');
                for(let i=0; i<60; i++) {{
                    let f = parentDoc.createElement('div');
                    f.style.cssText = `position:fixed; width:8px; height:8px; border-radius:100%; background-color:${{['{THEME_COLORS['primary']}', '{THEME_COLORS['bg_card']}', '#40a9ff', '#87e8de'][Math.floor(Math.random()*4)]}}; left:50%; top:50%; transform:translate(-50%, -50%); pointer-events:none; z-index:9999998; transition: all 1.5s cubic-bezier(0.25, 1, 0.5, 1);`;
                    parentDoc.body.appendChild(f);
                    setTimeout(() => {{
                        const angle = Math.random() * Math.PI * 2;
                        const dist = 50 + Math.random() * 300;
                        f.style.left = `calc(50% + ${{Math.cos(angle)*dist}}px)`;
                        f.style.top = `calc(50% + ${{Math.sin(angle)*dist}}px)`;
                        f.style.opacity = '0';
                    }}, 50);
                    setTimeout(()=>f.remove(), 1600);
                }}
            }}
        }});
    }}
    </script>
    """
    st.components.v1.html(js_code, height=0, width=0)

def apply_v14_theme():
    # Sử dụng bộ màu từ THEME_COLORS
    p = THEME_COLORS['primary']
    bg = THEME_COLORS['bg_app']
    card = THEME_COLORS['bg_card']
    shadow = THEME_COLORS['shadow_light']
    txt_main = THEME_COLORS['text_main']
    txt_sub = THEME_COLORS['text_secondary']
    txt_muted = THEME_COLORS['text_muted']
    txt_title = THEME_COLORS['text_title']
    b_light = THEME_COLORS['border_light']
    b_input = THEME_COLORS['border_input']

    st.markdown(f"""
    <style>
        /* 1. Tổng thể & Reset */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
        html, body, .stApp {{ font-family: 'Inter', sans-serif !important; background-color: {bg} !important; padding-top: 0px !important; }}
        
        /* 2. Ẩn mặc định Streamlit & Ép layout khít */
        header, footer, [data-testid='stToolbar'], [data-testid='stDecoration'] {{ display: none !important; }}
        [data-testid="stVerticalBlock"] {{ gap: 5px !important; }}
        
        /* 3. Tùy chỉnh Tabs */
        [data-testid="stTabs"] [role="tablist"] {{
            background: {card}; border-radius: 12px; padding: 5px; box-shadow: 0 4px 6px {shadow}; margin-bottom: 5px !important;
        }}
        button[data-baseweb="tab"] {{ background-color: transparent !important; }}
        button[data-baseweb="tab"] p {{ color: {txt_muted} !important; font-weight: 600 !important; font-size: 14px; }}
        button[data-baseweb="tab"][aria-selected="true"] {{ background-color: {p} !important; border-radius: 8px; }}
        button[data-baseweb="tab"][aria-selected="true"] p {{ color: {txt_main} !important; }}
        
        /* 4. Card UI (Container) */
        [data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: {card} !important; border: none !important; border-radius: 15px !important;
            border-left: 5px solid {p} !important; box-shadow: 2px 2px 10px {shadow} !important;
            padding: 15px !important; margin-bottom: 8px !important;
        }}

        /* 5. Buttons */
        div[data-testid="stButton"] button {{ border-radius: 10px !important; font-weight: 600 !important; border: 1px solid {b_light}; background: {card}; }}
        div[data-testid="stButton"] button[kind="primary"] {{ background-color: {p} !important; color: {txt_main} !important; border: none !important; }}
        
        /* 6. Inputs */
        .stTextInput>div>div>input, .stNumberInput>div>div>input {{ border-radius: 8px !important; border: 1px solid {b_input}; }}
        
        /* 7. Typography V14 & Layout */
        .the-quan-ly-flat {{ color: {txt_title}; font-weight: 800; font-size: 18px; margin-bottom: 10px; border-bottom: 2px solid {p}; padding-bottom: 5px; text-transform: uppercase; }}
        .box-chung {{ background-color: {THEME_COLORS['bg_box_chung']}; padding: 10px; border-radius: 10px; text-align: center; border: 1px solid {b_light}; font-size: 18px; font-weight: 800; color: {txt_main}; }}
        .chiet-khau-box {{ color: {THEME_COLORS['accent_chiet_khau']} !important; }} 
        .khach-tra-box {{ background-color: {p} !important; color: {txt_main} !important; border:none; }}
        .tien-thua-box {{ background-color: {THEME_COLORS['bg_box_chung']}; color: {txt_main}; padding: 15px; border-radius: 10px; text-align: center; font-size: 18px; font-weight: 700; border: 1px dashed {p}; margin: 10px 0; }}
        
        /* 8. Hóa đơn xuất */
        .hoa-don-khung {{ background-color: {card} !important; color: {txt_main} !important; padding: 20px !important; border-radius: 15px !important; border-top: 8px solid {p} !important; box-shadow: 0 4px 12px {THEME_COLORS['shadow_heavy']}; margin-top: 5px; }}
        
        /* 9. Utilities */
        .lsc-shake {{ background-color: {THEME_COLORS['bg_shake_box']}; color: {THEME_COLORS['accent_danger']} !important; padding: 10px; border-radius: 8px; text-align: center; font-size: 13px; font-weight:600; margin-bottom: 10px; border-left: 4px solid {THEME_COLORS['accent_danger']}; }}
        .lsc-vip {{ background-color: {THEME_COLORS['bg_vip_box']}; color: {THEME_COLORS['accent_vip']} !important; padding: 8px; border-radius: 8px; text-align: center; font-size: 13px; margin-bottom: 8px; font-weight: 700; border: 1px solid {THEME_COLORS['border_vip']}; }}
    </style>
    """, unsafe_allow_html=True)

def render_balloons_html():
    colors = [THEME_COLORS['primary'], THEME_COLORS['bg_card'], THEME_COLORS['bg_app']]
    html_balloons = '<div class="balloon-container-css" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: 9999998; overflow: hidden;">'
    for i in range(20):
        left_pos = random.uniform(5, 95)
        color = random.choice(colors)
        size_ratio = random.uniform(0.6, 1.0)
        w, h = int(40 * size_ratio), int(55 * size_ratio)
        delay = round(random.uniform(0.0, 2.0), 2)
        duration = round(random.uniform(4.0, 6.0), 2)
        html_balloons += f'<div style="position: absolute; bottom: -100px; border-radius: 50% 50% 50% 50% / 40% 40% 60% 60%; opacity: 0.8; background-color: {color}; left: {left_pos}vw; width: {w}px; height: {h}px; animation: fly-up-skywards-pure {duration}s linear {delay}s forwards; box-shadow: 0 4px 6px {THEME_COLORS["shadow_light"]};"></div>'
    html_balloons += '<style>@keyframes fly-up-skywards-pure { 0% { transform: translateY(110vh); opacity: 0; } 10% { opacity: 0.8; } 90% { opacity: 0.8; } 100% { transform: translateY(-120vh); opacity: 0; } }</style></div>'
    st.markdown(html_balloons, unsafe_allow_html=True)

# =====================================================================
# 2. CƠ CHẾ KẾT NỐI (GIỮ NGUYÊN 100% TỪ V13)
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
        st.error(f"Lỗi khởi tạo kết nối Sheets: {e}")
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
    if tong_chi >= 10000000: return "DIAMOND"
    elif tong_chi >= 5000000: return "GOLD"
    elif tong_chi >= 3000000: return "SILVER"
    elif tong_chi >= 1000000: return "THÂN THIẾT"
    return "TIỀM NĂNG"

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
# 3. LUỒNG ĐIỀU HƯỚNG VÀ XỬ LÝ CHÍNH (V14 - 5 TABS)
# =====================================================================
def main():
    init_states = {
        "last_submit": None, "submit_count": 0, "submitting": False, 
        "logged_in": False, "role": None, "full_name": None, "gio_hang": [], 
        "bill_vua_in": None, "trigger_balloons": False,
        "kh_sdt_val": "", "kh_ten_val": "Khách lẻ", "start_time": get_now_vn(),
        "reset_counter": 0, "tho_chot_val": "",
        "hang_hien_tai": "", "tong_chi_tieu_val": 0.0,
        "theme": "light", "scroll_trigger": None
    }
    for key, val in init_states.items():
        if key not in st.session_state: st.session_state[key] = val

    # Áp dụng UI V14
    apply_v14_theme()
    inject_advanced_ui_js()

    if st.session_state.trigger_balloons:
        render_balloons_html()  
        st.session_state.trigger_balloons = False

    settings = get_settings()

    # --- ĐĂNG NHẬP ---
    if not st.session_state["logged_in"]:
        saved_u = st.query_params.get("saved_u", "")
        saved_p = st.query_params.get("saved_p", "")
        with st.container(border=True):
            st.markdown(f"<h2 style='text-align:center; color:{THEME_COLORS['text_title']}; font-weight:800;'>ECO TIME V14</h2>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center; color:{THEME_COLORS['text_muted']}; margin-top:-10px; margin-bottom:20px;'>ĐĂNG NHẬP HỆ THỐNG</p>", unsafe_allow_html=True)
            u = st.text_input("Tài khoản (Số điện thoại)", value=saved_u)
            p = st.text_input("Mật khẩu", type="password", value=saved_p)
            remember_me = st.checkbox("Ghi nhớ mật khẩu", value=bool(saved_u))
            
            if st.button("Xác nhận Đăng Nhập", use_container_width=True, type="primary"):
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

    # --- KHU VỰC LÀM VIỆC CHÍNH (5 TABS) ---
    else:
        tabs = st.tabs(["🏠 Tổng quan", "📄 Lên hóa đơn", "📅 Lịch hẹn", "📊 Báo cáo", "⚙️ Thêm"])

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
        # TAB 1: 🏠 TỔNG QUAN
        # =================================================================
        with tabs[0]:
            with st.container(border=True):
                direct_logo_url = format_drive_direct_url(settings.get('Logo', ''))
                fallback_gif = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
                st.markdown(f"""
                    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center;">
                        <img src="{direct_logo_url}" style="width: 85px; height: 85px; border-radius: 50%; border: 3px solid {THEME_COLORS['primary']}; object-fit: cover; margin-bottom: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);" onerror="this.onerror=null;this.src='{fallback_gif}';">
                        <div style="font-size: 22px; font-weight: 900; color: {THEME_COLORS['text_main']}; text-transform: uppercase; letter-spacing: 1px;">{settings.get('TenTiem', 'SALON KIM HIỀN')}</div>
                        <div style="font-size: 13px; color: {THEME_COLORS['text_muted']}; margin-top: 5px; text-align: center;">
                            <div>{settings.get('Diachi', '131, TRẦN BÌNH TRỌNG, LONG XUYÊN')}</div>
                            <div style="margin-top: 3px;">Hotline: {settings.get('SDT', '0947.58.1516')}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            with st.container(border=True):
                st.markdown(f"**Chào mừng, {st.session_state.full_name}!**")
                st.markdown(f"<span style='color:{THEME_COLORS['text_muted']}; font-size:13px;'>Hôm nay là: {get_now_vn().strftime('%d/%m/%Y')}</span>", unsafe_allow_html=True)

            if st.session_state.get("bill_vua_in"):
                with st.container(border=True):
                    st.markdown('<div class="the-quan-ly-flat">🧾 HOÁ ĐƠN VỪA KHỞI TẠO</div>', unsafe_allow_html=True)
                    st.markdown(st.session_state.bill_vua_in, unsafe_allow_html=True)
                    if st.button("❌ ẨN BILL NÀY", use_container_width=True, type="primary"):
                        st.session_state.bill_vua_in = None
                        st.rerun()

        # =================================================================
        # TAB 2: 📄 HÓA ĐƠN (TẠO ĐƠN HÀNG)
        # =================================================================
        with tabs[1]:
            with st.container(border=True):
                st.markdown('<div class="the-quan-ly-flat">THÔNG TIN KHÁCH HÀNG</div>', unsafe_allow_html=True)
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
                                    st.session_state.hang_hien_tai = "TIỀM NĂNG"
                            except:
                                st.session_state.hang_hien_tai = "TIỀM NĂNG"
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
                    st.markdown(f'<div class="lsc-vip">🌟 Khách hàng quen: Đã ghé tiệm {so_lan_den} lần!</div>', unsafe_allow_html=True)
                
                if st.session_state["role"] == "Admin" and st.session_state.kh_sdt_val.strip() and st.session_state.hang_hien_tai:
                    st.markdown(f"""
                        <div style="text-align: right; margin-top: -5px; margin-bottom: 10px;">
                            <span style="background-color: {THEME_COLORS['bg_badge_hang']}; padding: 4px 12px; border-radius: 12px; border: 1px solid {THEME_COLORS['border_badge']}; font-size: 11px; font-weight: 700; color: {THEME_COLORS['text_badge']};">
                                {st.session_state.hang_hien_tai} | Tích lũy: {st.session_state.tong_chi_tieu_val:,.0f} đ
                            </span>
                        </div>
                    """, unsafe_allow_html=True)

            with st.container(border=True):
                st.markdown('<div class="the-quan-ly-flat">DANH SÁCH DỊCH VỤ</div>', unsafe_allow_html=True)
                max_dv = 3 if st.session_state.get("role") == "NhanVien" else None
                
                dv_chon = st.multiselect(
                    "Chạm chọn dịch vụ...", 
                    options=dv_list if dv_list else ["Đang tải danh mục..."], 
                    max_selections=max_dv,
                    placeholder="Chọn tối đa 3 dịch vụ..." if max_dv else "Chọn dịch vụ...",
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
                with st.container(border=True):
                    st.markdown(f'<div class="the-quan-ly-flat">🛒 GIỎ HÀNG ({len(st.session_state.gio_hang)} món)</div>', unsafe_allow_html=True)
                    
                    for idx, item in enumerate(st.session_state.gio_hang):
                        st.markdown(f"<div style='font-size:15px; font-weight:800; color:{THEME_COLORS['primary']}; margin-bottom:6px;'>📍 {item['dich_vu']}</div>", unsafe_allow_html=True)
                        
                        c_sl, c_tt, c_del = st.columns([5, 3, 2])
                        with c_sl:
                            new_sl = st.number_input("Số lượng:", min_value=0.5, max_value=50.0, value=float(item['so_luong']), step=0.5, key=f"cart_sl_{idx}")
                            if new_sl != item['so_luong']:
                                item['so_luong'] = new_sl
                                item['thanh_tien'] = new_sl * item['don_gia']
                                st.rerun()
                        with c_tt:
                            st.markdown(f"<div style='font-size:11px; color:{THEME_COLORS['text_muted']}; text-transform:uppercase; margin-bottom:8px; text-align:right;'>Thành tiền</div><div style='font-size:15px; font-weight:800; text-align:right; padding-top:5px; color:{THEME_COLORS['text_main']};'>{item['thanh_tien']:,.0f}đ</div>", unsafe_allow_html=True)
                        with c_del:
                            st.markdown(f"<div style='font-size:11px; color:{THEME_COLORS['text_muted']}; text-transform:uppercase; margin-bottom:8px; text-align:center;'>Xóa</div>", unsafe_allow_html=True)
                            if st.button("🗑️", key=f"del_{idx}", use_container_width=True):
                                st.session_state.gio_hang.pop(idx)
                                st.rerun()
                                
                        st.markdown(f"<div style='margin: 12px 0; border-bottom: 1px dashed {THEME_COLORS['border_light']};'></div>", unsafe_allow_html=True)
                        t_bill += item['thanh_tien']

                    if st.button("💾 LƯU ĐƠN VÀO BILL CHỜ", use_container_width=True):
                        if luu_bill_tam(st.session_state.gio_hang, st.session_state.full_name, st.session_state.kh_sdt_val, st.session_state.kh_ten_val):
                            st.session_state.update({"gio_hang": [], "kh_sdt_val": "", "kh_ten_val": "Khách lẻ", "hang_hien_tai": "", "tong_chi_tieu_val": 0.0, "tho_chot_val": st.session_state.full_name})
                            st.toast("✅ Đã lưu đơn tạm!")
                            time.sleep(1)
                            st.rerun()

            if t_bill > 0:
                with st.container(border=True):
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
                    with cb1: st.markdown(f'<div style="font-size: 11px; font-weight: 600; color: {THEME_COLORS["text_muted"]}; text-align: center;">Tổng bill</div><div class="box-chung">{t_bill:,.0f}</div>', unsafe_allow_html=True)
                    with cb2: st.markdown(f'<div style="font-size: 11px; font-weight: 600; color: {THEME_COLORS["text_muted"]}; text-align: center;">Chiết khấu</div><div class="box-chung chiet-khau-box">{tien_giam:,.0f}</div>', unsafe_allow_html=True)
                    with cb3: st.markdown(f'<div style="font-size: 11px; font-weight: 600; color: {THEME_COLORS["text_muted"]}; text-align: center;">Khuyến mãi</div><div class="box-chung chiet-khau-box">{khuyen_mai:,.0f}</div>', unsafe_allow_html=True)
                    with cb4: st.markdown(f'<div style="font-size: 11px; font-weight: 600; color: {THEME_COLORS["text_muted"]}; text-align: center;">Thực thu</div><div class="box-chung khach-tra-box">{t_khach_tra:,.0f}</div>', unsafe_allow_html=True)
                    
                    st.markdown(f'<div style="text-align:right; font-size:13px; color:{THEME_COLORS["text_muted"]}; margin-top:8px;">Hoa hồng thợ: <b>{t_cong_tho:,.0f}đ</b></div>', unsafe_allow_html=True)
                    
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
                        cam_ket = st.checkbox("Xác nhận đơn hàng")
                        if not st.session_state.submitting:
                            if st.button("🚀 XUẤT HÓA ĐƠN", use_container_width=True, type="primary"):
                                if cam_ket:
                                    st.session_state.submitting = True
                                    st.rerun()
                                else: st.warning("Vui lòng xác nhận.")
                        else:
                            st.button("Đang đồng bộ...", disabled=True, use_container_width=True)
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
                                    html_items += f"""<tr><td style="text-align: left; border: none; padding: 6px 0;"><div style="font-weight: 600; color: {THEME_COLORS['text_main']}; font-size: 14px;">{item["dich_vu"]}</div><div style="font-size: 12px; color: {THEME_COLORS['text_secondary']};">{sl_sach} x {item['don_gia']:,.0f}đ</div></td><td style="text-align: right; border: none; padding: 6px 0; vertical-align: middle;"><div style="font-weight: 700; color: {THEME_COLORS['text_main']}; font-size: 14px;">{item["thanh_tien"]:,.0f}đ</div></td></tr>"""
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
                                
                                huy_hieu_bill = st.session_state.hang_hien_tai if (st.session_state["role"] == "Admin" and c_sdt and c_ten != "Khách lẻ" and st.session_state.hang_hien_tai != "TIỀM NĂNG") else ""
                                huy_hieu_tele = f" | Hạng: {huy_hieu_bill}" if huy_hieu_bill else ""

                                nd_mail = f"THÔNG BÁO - Đã thanh toán ✅\n \nMã ĐH: {ma_hd} | {bay_gio.strftime('%d/%m/%Y %H:%M')}\nKhách: {c_ten} - {c_sdt}{huy_hieu_tele}\nThu ngân: {st.session_state.full_name}\nThợ: {chot_tho}\n \nDịch vụ:{chi_tiet_tele}\n \nTổng bill: {t_bill:,.0f} đ\nTrừ: -{tong_tru:,.0f} đ\nKhách đưa: {kh_dua:,.0f} đ\nTiền thối: {t_du:,.0f} đ\nPhục vụ: {tg_phuc_vu} phút\n \nTHỰC THU: {t_khach_tra:,.0f} đ"
                                gui_email_backup(nd_mail)
                                gui_telegram_notification(nd_mail)
                                
                                btn_zl = ""
                                if c_sdt:
                                    zl_sdt = str(c_sdt).strip().replace(" ", "").replace("+84", "0")
                                    if not zl_sdt.startswith('0') and zl_sdt: zl_sdt = '0' + zl_sdt
                                    btn_zl = f'<div style="text-align: center; margin-top: 15px;"><a href="https://zalo.me/{zl_sdt}" target="_blank" style="background-color: {THEME_COLORS["accent_zalo"]}; color: #ffffff; padding: 10px 20px; font-weight: bold; border-radius: 8px; text-decoration: none;">CSKH qua Zalo 📲</a></div>'
                                
                                html_hh = f'<div style="font-size: 11px; color: {THEME_COLORS["text_badge"]}; font-weight: bold; text-align: right; margin-top: -15px; margin-bottom: 15px;">Hạng: {huy_hieu_bill}</div>' if huy_hieu_bill else ""
                                
                                st.session_state.bill_vua_in = f"""<style>.hoa-don-khung table, .hoa-don-khung tr, .hoa-don-khung td {{border: none !important; background: transparent !important;}}</style>
<div class="hoa-don-khung">
<div style="text-align: center; border-bottom: 1px dashed {THEME_COLORS['border_input']}; padding-bottom: 15px; margin-bottom: 20px;"><div style="font-size: 20px; font-weight: 900; color: {THEME_COLORS['text_main']};">{settings.get('TenTiem', 'SALON KIM HIỀN')}</div><div style="font-size: 13px; color: {THEME_COLORS['text_secondary']}; margin-top:4px;">{settings.get('Diachi', '')}</div><div style="font-size: 13px; color: {THEME_COLORS['text_secondary']};">SĐT: {settings.get('SDT', '')}</div><div style="font-size: 18px; font-weight: 800; color: {THEME_COLORS['text_main']}; margin-top:10px;">HÓA ĐƠN DỊCH VỤ</div><div style="font-size: 12px; color: {THEME_COLORS['text_muted']}; margin-top:5px;">Mã số: {ma_hd}</div></div>
<div style="font-size: 13px; font-weight: 600; color: {THEME_COLORS['text_secondary']}; text-align: left; margin-bottom: 8px; border-bottom: 1px dashed {THEME_COLORS['border_light']}; padding-bottom: 5px;">Thông tin khách hàng:</div>
{html_hh}
<div style="border-bottom: 1px solid {THEME_COLORS['border_light']}; padding-bottom: 10px; margin-bottom: 15px; font-size: 14px; color: {THEME_COLORS['text_secondary']};">
    <div style="display: flex; justify-content: space-between; margin-bottom: 6px;"><span>Ngày:</span> <span style="text-align: right;">{bay_gio.strftime('%d/%m/%Y %H:%M')}</span></div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 6px;"><span>Khách hàng:</span> <span style="font-weight:700; color: {THEME_COLORS['text_main']}; text-align: right;">{c_ten}</span></div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 6px;"><span>Thu ngân:</span> <span style="text-align: right;">{st.session_state.full_name}</span></div>
    <div style="display: flex; justify-content: space-between;"><span>Thợ thực hiện:</span> <span style="font-weight:700; color: {THEME_COLORS['text_main']}; text-align: right;">{chot_tho}</span></div>
</div>
<div style="margin-bottom: 15px;"><div style="font-size: 13px; font-weight: 600; color: {THEME_COLORS['text_secondary']}; text-align: left; margin-bottom: 8px; border-bottom: 1px dashed {THEME_COLORS['border_light']}; padding-bottom: 5px;">Chi tiết dịch vụ:</div>
    <table style="width: 100%; border-collapse: collapse;">{html_items}</table>
</div>
<div style="font-size: 14px; border-bottom: 1px solid {THEME_COLORS['border_light']}; padding-bottom: 10px; margin-bottom: 15px; color: {THEME_COLORS['text_main']};">
<div style="font-size: 13px; font-weight: 600; color: {THEME_COLORS['text_secondary']}; text-align: left; margin-bottom: 8px; border-bottom: 1px dashed {THEME_COLORS['border_light']}; padding-bottom: 5px;"> </div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;"><span>Cộng tiền:</span> <span style="text-align: right; font-weight: 600;">{t_bill:,.0f}</span></div>
    <div style="display: flex; justify-content: space-between; color: {THEME_COLORS['accent_chiet_khau']}; margin-bottom: 8px;"><span>Giảm trừ:</span> <span style="text-align: right; font-weight: 600;">-{tong_tru:,.0f}</span></div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;"><span>Khách đưa:</span> <span style="text-align: right; font-weight: 600;">{kh_dua:,.0f}</span></div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;"><span>Tiền thối:</span> <span style="text-align: right; font-weight: 600;">{t_du:,.0f}</span></div>
    <div style="display: flex; justify-content: space-between;"><span>Thời gian phục vụ:</span> <span style="text-align: right;">{tg_phuc_vu} phút</span></div>
</div>
<div style="font-size: 13px; font-weight: 600; color: {THEME_COLORS['text_secondary']}; text-align: left; margin-bottom: 8px; border-bottom: 1px dashed {THEME_COLORS['border_light']}; padding-bottom: 5px;">Số tiền cần thanh toán:</div>
<div style="display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 18px; font-weight: 900; color: {THEME_COLORS['text_main']};"><span>TỔNG CỘNG:</span> <span style="text-align: right; color: {THEME_COLORS['accent_chiet_khau']};">{t_khach_tra:,.0f}</span></div>
<div style="text-align: center; margin-top: 25px; font-size: 13px; color: {THEME_COLORS['text_muted']}; font-style: italic;">Cảm ơn quý khách đã sử dụng dịch vụ!</div>
{btn_zl}
</div>"""
                                st.session_state.update({
                                    "gio_hang": [], "last_submit": bay_gio, "submit_count": st.session_state.submit_count + 1, 
                                    "submitting": False, "kh_sdt_val": "", "kh_ten_val": "Khách lẻ",
                                    "hang_hien_tai": "", "tong_chi_tieu_val": 0.0,
                                    "start_time": get_now_vn(), "tho_chot_val": st.session_state.full_name
                                })
                                st.rerun()
                            except Exception as e:
                                st.error(f"Hệ thống gián đoạn, vui lòng nhấn Tạo Đơn lại: {e}")
                                st.session_state.submitting = False

        # =================================================================
        # TAB 3: 📅 LỊCH HẸN
        # =================================================================
        with tabs[2]:
            with st.container(border=True):
                st.markdown('<div class="the-quan-ly-flat">LỊCH HẸN KHÁCH HÀNG</div>', unsafe_allow_html=True)
                st.info("Tính năng quản lý lịch hẹn đang được phát triển ở phiên bản tiếp theo.")

        # =================================================================
        # TAB 4: 📊 BÁO CÁO (CHỈ ADMIN)
        # =================================================================
        with tabs[3]:
            if st.session_state["role"] == "Admin":
                with st.container(border=True):
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
                        c4.metric("👥 Tổng khách", so_khach)
                        c5.metric("⏳ Tổng đơn chờ", don_cho)
                        
                        if not df_bc.empty:
                            col_chart, col_kpi = st.columns([6, 4])
                            with col_chart:
                                st.markdown(f'<div style="font-size: 14px; font-weight: 700; color: {THEME_COLORS["text_secondary"]}; text-align: center; margin-bottom: 10px;">📈 BIỂU ĐỒ DOANH THU</div>', unsafe_allow_html=True)
                                st.bar_chart(df_bc.groupby(c_ngay)[c_tien].sum().reset_index().tail(7).set_index(c_ngay), use_container_width=True, color=THEME_COLORS['primary'])
                            with col_kpi:
                                st.markdown(f'<div style="font-size: 14px; font-weight: 700; color: {THEME_COLORS["text_secondary"]}; text-align: center; margin-bottom: 10px;">🏆 KPI THỢ HÔM NAY</div>', unsafe_allow_html=True)
                                if not df_today.empty and len(df_today.columns) >= 16:
                                    kpi_df = df_today.groupby(df_today.columns[15])[c_tien].sum().reset_index()
                                    kpi_df.columns = ["Tên thợ", "Doanh thu"]
                                    kpi_df = kpi_df.sort_values(by="Doanh thu", ascending=False)
                                    kpi_df["Doanh thu"] = kpi_df["Doanh thu"].apply(lambda x: f"{x:,.0f} đ")
                                    st.dataframe(kpi_df, use_container_width=True, hide_index=True)
                                else: st.info("Chưa có giao dịch.")

                        st.markdown('<div class="the-quan-ly-flat" style="margin-top:20px;">50 GIAO DỊCH GẦN NHẤT</div>', unsafe_allow_html=True)
                        if not df_hien_thi.empty: st.dataframe(df_hien_thi, use_container_width=True)
                    except Exception as e: st.error(f"Lỗi: {e}")
            else:
                st.warning("🔒 Chức năng này chỉ dành cho Quản lý.")

        # =================================================================
        # TAB 5: ⚙️ THÊM (BILL CHỜ & LAB V1.3 & CÀI ĐẶT)
        # =================================================================
        with tabs[4]:
            if st.session_state["role"] == "Admin":
                with st.container(border=True):
                    st.markdown('<div class="the-quan-ly-flat">QUẢN LÝ BILL CHỜ</div>', unsafe_allow_html=True)
                    if st.button("🔄 Làm mới bill chờ", use_container_width=True):
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

                with st.container(border=True):
                    st.markdown('<div class="the-quan-ly-flat">🧪 LAB V1.3 (Mẻ 3 Lít)</div>', unsafe_allow_html=True)
                    st.info("Khu vực quản lý công thức dung dịch nội bộ đang được phát triển.")

                with st.container(border=True):
                    st.markdown('<div class="the-quan-ly-flat">HỆ THỐNG</div>', unsafe_allow_html=True)
                    if st.button("♻️ LÀM MỚI BỘ NHỚ", use_container_width=True, type="primary"):
                        st.cache_data.clear()
                        st.cache_resource.clear() 
                        st.success("Đã xóa sạch bộ nhớ tạm và tái tạo lại toàn bộ đường truyền Google Sheets!")
                        time.sleep(1)
                        st.rerun()
                    
                    if st.button("🚪 Đăng xuất Admin", use_container_width=True):
                        st.session_state.clear()
                        st.rerun()
            else:
                with st.container(border=True):
                    st.markdown('<div class="the-quan-ly-flat">HỆ THỐNG</div>', unsafe_allow_html=True)
                    if st.button("🚪 Đăng xuất", use_container_width=True, type="primary"):
                        st.session_state.clear()
                        st.rerun()

if __name__ == "__main__":
    main()
