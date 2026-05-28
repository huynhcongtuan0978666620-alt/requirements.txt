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
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# =====================================================================
# 🌟 MENU ĐIỀU CHỈNH MÀU SẮC (DESIGN SYSTEM) - V15 PRO
# =====================================================================
THEME_COLORS = {
    "bg_app": "#EEF4F8",            
    "bg_card": "#ffffff",           
    "bg_box_chung": "#f8f9fa",      
    "bg_vip_box": "#eaf2e6",        
    "bg_shake_box": "#fff1f0",      
    "bg_badge_hang": "#fffbfa",     
    "primary": "#6FA8DC",           
    "accent_vip": "#13c2c2",        
    "accent_danger": "#cf1322",     
    "accent_zalo": "#0068ff",       
    "accent_chiet_khau": "#d93025", 
    "text_main": "#111111",         
    "text_secondary": "#555555",    
    "text_muted": "#888888",        
    "text_title": "#2c3e50",        
    "text_badge": "#d4380d",        
    "border_light": "#eaeaea",      
    "border_input": "#cccccc",      
    "border_badge": "#ffe1df",      
    "border_vip": "#87e8de",        
    "shadow_light": "rgba(0,0,0,0.05)",  
    "shadow_heavy": "rgba(0,0,0,0.08)",  
    "shadow_toast": "rgba(0,0,0,0.1)",   
}

# =====================================================================
# 1. CẤU HÌNH GIAO DIỆN V15
# =====================================================================
st.set_page_config(
    page_title="SALON PRO V15", 
    layout="centered", 
    page_icon="💇‍♀️",
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
    if(!parentDoc.body.hasAttribute('data-fw-v15')) {{
        parentDoc.body.setAttribute('data-fw-v15', '1');
        let clicks = 0;
        let timer = null;
        parentDoc.addEventListener('click', (e) => {{
            clicks++;
            clearTimeout(timer);
            timer = setTimeout(() => {{ clicks = 0; }}, 1000); 
            if(clicks >= 3) {{
                clicks = 0;
                showPremiumToast('🎉 Chào mừng đến với HỆ THỐNG SALON CHUYÊN NGHIỆP 🎉');
            }}
        }});
    }}
    </script>
    """
    st.components.v1.html(js_code, height=0, width=0)

def apply_v15_theme():
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
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
        html, body, .stApp {{ font-family: 'Inter', sans-serif !important; background-color: {bg} !important; padding-top: 0px !important; }}
        header, footer, [data-testid='stToolbar'], [data-testid='stDecoration'] {{ display: none !important; }}
        [data-testid="stVerticalBlock"] {{ gap: 5px !important; }}
        [data-testid="stTabs"] [role="tablist"] {{
            background: {card}; border-radius: 12px; padding: 5px; box-shadow: 0 4px 6px {shadow}; margin-bottom: 5px !important;
        }}
        button[data-baseweb="tab"] {{ background-color: transparent !important; }}
        button[data-baseweb="tab"] p {{ color: {txt_muted} !important; font-weight: 600 !important; font-size: 14px; }}
        button[data-baseweb="tab"][aria-selected="true"] {{ background-color: {p} !important; border-radius: 8px; }}
        button[data-baseweb="tab"][aria-selected="true"] p {{ color: {txt_main} !important; }}
        [data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: {card} !important; border: none !important; border-radius: 15px !important;
            border-left: 5px solid {p} !important; box-shadow: 2px 2px 10px {shadow} !important;
            padding: 15px !important; margin-bottom: 8px !important;
        }}
        div[data-testid="stButton"] button {{ border-radius: 10px !important; font-weight: 600 !important; border: 1px solid {b_light}; background: {card}; }}
        div[data-testid="stButton"] button[kind="primary"] {{ background-color: {p} !important; color: {txt_main} !important; border: none !important; }}
        .stTextInput>div>div>input, .stNumberInput>div>div>input, .stDateInput>div>div>input, .stTimeInput>div>div>input, .stTextArea>div>div>textarea {{ border-radius: 8px !important; border: 1px solid {b_input}; }}
        .the-quan-ly-flat {{ color: {txt_title}; font-weight: 800; font-size: 18px; margin-bottom: 10px; border-bottom: 2px solid {p}; padding-bottom: 5px; text-transform: uppercase; }}
        .box-chung {{ background-color: {THEME_COLORS['bg_box_chung']}; padding: 10px; border-radius: 10px; text-align: center; border: 1px solid {b_light}; font-size: 18px; font-weight: 800; color: {txt_main}; }}
        .chiet-khau-box {{ color: {THEME_COLORS['accent_chiet_khau']} !important; }} 
        .khach-tra-box {{ background-color: {p} !important; color: {txt_main} !important; border:none; }}
        .tien-thua-box {{ background-color: {THEME_COLORS['bg_box_chung']}; color: {txt_main}; padding: 15px; border-radius: 10px; text-align: center; font-size: 18px; font-weight: 700; border: 1px dashed {p}; margin: 10px 0; }}
        .hoa-don-khung {{ background-color: {card} !important; color: {txt_main} !important; padding: 20px !important; border-radius: 15px !important; border-top: 8px solid {p} !important; box-shadow: 0 4px 12px {THEME_COLORS['shadow_heavy']}; margin-top: 5px; }}
        .lsc-shake {{ background-color: {THEME_COLORS['bg_shake_box']}; color: {THEME_COLORS['accent_danger']} !important; padding: 10px; border-radius: 8px; text-align: center; font-size: 13px; font-weight:600; margin-bottom: 10px; border-left: 4px solid {THEME_COLORS['accent_danger']}; }}
        .lsc-vip {{ background-color: {THEME_COLORS['bg_vip_box']}; color: {THEME_COLORS['accent_vip']} !important; padding: 8px; border-radius: 8px; text-align: center; font-size: 13px; margin-bottom: 8px; font-weight: 700; border: 1px solid {THEME_COLORS['border_vip']}; }}
        .lich-hen-item {{ background: #fff; padding: 12px; border-radius: 10px; border: 1px solid #eee; border-left: 4px solid {p}; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }}
    </style>
    """, unsafe_allow_html=True)

# =====================================================================
# 2. CƠ CHẾ KẾT NỐI & DỮ LIỆU CHÍNH
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
            "token_uri": secrets.get("token_uri", "https://oauth2.googleapis.com/token"),
        }

        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        url = secrets.get("spreadsheet", "")
        if not url and "spreadsheet" in st.secrets:
            url = st.secrets["spreadsheet"]
        return client.open_by_key(url) if len(url) < 50 else client.open_by_url(url)
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
    except Exception: return {"TenTiem": "SALON KIM HIỀN", "Diachi": "131, TRẦN BÌNH TRỌNG, LONG XUYÊN", "SDT": "0947.58.1516"}

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
                    try: hoa_hong = float(str(row[2]).replace('%', '').replace(',', '.').strip())
                    except: hoa_hong = 0.0
                danh_sach_dv[ten_dv] = {"gia": gia_goc, "hoa_hong": hoa_hong}
        return danh_sach_dv
    except Exception: return {}

@st.cache_data(ttl=3600)
def get_nhan_vien_data():
    try: return get_google_sheet_workbook().worksheet("NhanVien").get_all_values()
    except Exception: return []

@st.cache_data(ttl=60)
def get_khach_hang_data():
    try:
        rows = get_google_sheet_workbook().worksheet("KhachHang").get_all_values()
        return {str(r[0]).strip().replace(".0", ""): str(r[1]).strip() for r in rows[1:] if len(r) >= 2 and str(r[0]).strip()}
    except Exception: return {}

@st.cache_data(ttl=15)
def get_plkh_data():
    try: return get_google_sheet_workbook().worksheet("PLKH").get_all_values()
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
        return sh.worksheet("BaoCao").get_all_values(), sh.worksheet("BillTam").get_all_values()
    except Exception: return [], []

@st.cache_data(ttl=60)
def get_lich_hen_data():
    try:
        sh = get_google_sheet_workbook()
        return sh.worksheet("LichHen").get_all_values()
    except Exception: return []

@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8-sig')

def luu_bill_tam(gio_hang, nhan_vien, kh_sdt="", kh_ten="Khách lẻ"):
    try:
        sh = get_google_sheet_workbook()
        ws = sh.worksheet("BillTam")
        chi_tiet = " | ".join([f"{item['dich_vu']} (x{item['so_luong']})" for item in gio_hang])
        tong_tien = sum([item['thanh_tien'] for item in gio_hang])
        ws.append_row([get_now_vn().strftime("%Y-%m-%d %H:%M:%S"), chi_tiet, tong_tien, nhan_vien, str(kh_sdt).strip(), str(kh_ten).strip(), "CHỜ XỬ LÝ"])
        get_bao_cao_va_bill_tam.clear()
        return True
    except Exception: return False

def gui_email_backup(noi_dung):
    try:
        sender_email = "huynhcongtuan0978666620@gmail.com"
        password = "lwui aesw vqal ytcq" 
        receiver_emails = ["huynhcongtuan0978666620@gmail.com"]
        gio_vn_mail = get_now_vn().strftime('%d/%m/%Y %H:%M')
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = ", ".join(receiver_emails)
        msg['Subject'] = f"HOÁ ĐƠN SALON DỊCH VỤ - {gio_vn_mail}"
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
# 3. CƠ CHẾ AUTO-SAVE NGẦM (BACKGROUND THREADING)
# =====================================================================
def background_save_draft(gio_hang_copy, nhan_vien, kh_sdt, kh_ten):
    try:
        sh = get_google_sheet_workbook()
        ws = sh.worksheet("BillTam")
        records = ws.get_all_values()
        draft_idx = -1
        for i, r in enumerate(records):
            if len(r) >= 7 and str(r[3]).strip() == nhan_vien and str(r[6]).strip() == "ĐANG SOẠN":
                draft_idx = i + 1 
                break
                
        chi_tiet = " | ".join([f"{item['dich_vu']} (x{item['so_luong']})" for item in gio_hang_copy])
        tong_tien = sum([item['thanh_tien'] for item in gio_hang_copy])
        
        if not gio_hang_copy and draft_idx != -1:
            ws.delete_rows(draft_idx)
        elif gio_hang_copy and draft_idx != -1:
            ws.update(f"A{draft_idx}:G{draft_idx}", [[get_now_vn().strftime("%Y-%m-%d %H:%M:%S"), chi_tiet, tong_tien, nhan_vien, kh_sdt, kh_ten, "ĐANG SOẠN"]])
        elif gio_hang_copy and draft_idx == -1:
            ws.append_row([get_now_vn().strftime("%Y-%m-%d %H:%M:%S"), chi_tiet, tong_tien, nhan_vien, kh_sdt, kh_ten, "ĐANG SOẠN"])
        get_bao_cao_va_bill_tam.clear()
    except Exception: pass

def trigger_auto_save():
    t = threading.Thread(target=background_save_draft, args=(
        list(st.session_state.gio_hang), 
        st.session_state.full_name, 
        st.session_state.kh_sdt_val, 
        st.session_state.kh_ten_val
    ))
    t.start()

# =====================================================================
# 4. LUỒNG ĐIỀU HƯỚNG VÀ XỬ LÝ CHÍNH
# =====================================================================
def main():
    init_states = {
        "last_submit": None, "submit_count": 0, "submitting": False, 
        "logged_in": False, "role": None, "full_name": None, "gio_hang": [], 
        "bill_vua_in": None, "kh_sdt_val": "", "kh_ten_val": "Khách lẻ", 
        "start_time": get_now_vn(), "reset_counter": 0, "tho_chot_val": "",
        "hang_hien_tai": "", "tong_chi_tieu_val": 0.0, "da_load_nhap": False
    }
    for key, val in init_states.items():
        if key not in st.session_state: st.session_state[key] = val

    apply_v15_theme()
    inject_advanced_ui_js()
    settings = get_settings()

    # --- ĐĂNG NHẬP ---
    if not st.session_state["logged_in"]:
        saved_u = st.query_params.get("saved_u", "")
        saved_p = st.query_params.get("saved_p", "")
        with st.container(border=True):
            st.markdown(f"<h2 style='text-align:center; color:{THEME_COLORS['text_title']}; font-weight:800;'>SALON PRO V15</h2>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center; color:{THEME_COLORS['text_muted']}; margin-top:-10px; margin-bottom:20px;'>ĐĂNG NHẬP HỆ THỐNG</p>", unsafe_allow_html=True)
            u = st.text_input("Tài khoản (Số điện thoại)", value=saved_u)
            p = st.text_input("Mật khẩu", type="password", value=saved_p)
            remember_me = st.checkbox("Ghi nhớ mật khẩu", value=bool(saved_u))
            
            if st.button("Xác nhận Đăng Nhập", use_container_width=True, type="primary"):
                if u == "admin" and p == "2026":
                    if remember_me: st.query_params.update({"saved_u": u, "saved_p": p})
                    else: st.query_params.clear()
                    st.session_state.update({"logged_in": True, "role": "Admin", "full_name": "Quản lý", "tho_chot_val": "Quản lý"})
                    st.rerun()
                else:
                    raw_data = get_nhan_vien_data()
                    if len(raw_data) > 0:
                        headers = [str(h).strip().lower() for h in raw_data[0]]
                        col_sdt_idx = next((i for i, h in enumerate(headers) if 'điện thoại' in h or 'sđt' in h or 'tai khoan' in h), -1)
                        col_mk_idx = next((i for i, h in enumerate(headers) if 'mật khẩu' in h or 'mat khau' in h or 'code' in h), -1)
                        col_ten_idx = next((i for i, h in enumerate(headers) if 'tên' in h or 'nhân viên' in h), -1)
                        
                        found_row = next((r for r in raw_data[1:] if len(r) > max(col_sdt_idx, col_mk_idx) and str(r[col_sdt_idx]).strip().lstrip('0') == u.strip().lstrip('0') and str(r[col_mk_idx]).strip() == p.strip() and u.strip()), None)
                                    
                        if found_row:
                            if remember_me: st.query_params.update({"saved_u": u, "saved_p": p})
                            else: st.query_params.clear()
                            ten_that = str(found_row[col_ten_idx]).strip() if col_ten_idx != -1 and col_ten_idx < len(found_row) else "Nhân viên"
                            st.session_state.update({"logged_in": True, "role": "NhanVien", "full_name": ten_that, "tho_chot_val": ten_that})
                            st.rerun()
                        else: st.error("Thông tin số điện thoại hoặc mật khẩu không chính xác.")
                    else: st.error("Hệ thống dữ liệu chưa sẵn sàng.")

    # --- KHU VỰC LÀM VIỆC CHÍNH ---
    else:
        if not st.session_state.da_load_nhap:
            st.session_state.da_load_nhap = True
            _, tam_records = get_bao_cao_va_bill_tam()
            services = get_service_data()
            for r in tam_records:
                if len(r) >= 7 and str(r[3]).strip() == st.session_state.full_name and str(r[6]).strip() == "ĐANG SOẠN":
                    st.session_state.kh_sdt_val = str(r[4]).strip()
                    st.session_state.kh_ten_val = str(r[5]).strip()
                    chi_tiet_dv = str(r[1]).strip()
                    new_gio = []
                    for item in chi_tiet_dv.split(" | "):
                        if item.strip():
                            match = re.match(r"(.+)\s*\(x([\d\.]+)\)", item.strip())
                            if match:
                                t_dv, s_l = match.group(1).strip(), float(match.group(2))
                                info = services.get(t_dv, {"gia": 0.0, "hoa_hong": 0.0})
                                new_gio.append({"dich_vu": t_dv, "so_luong": s_l, "don_gia": info.get("gia", 0.0), "thanh_tien": info.get("gia", 0.0) * s_l, "phan_tram_hh": info.get("hoa_hong", 0.0)})
                    if new_gio:
                        st.session_state.gio_hang = new_gio
                        st.toast("🔄 Đã tự động khôi phục giỏ hàng làm dở trước đó!")
                    break

        tabs = st.tabs(["🏠 Tổng quan", "📄 Lên hóa đơn", "📅 Lịch hẹn", "📊 Báo cáo", "⚙️ Quản trị"], key="main_tabs_v15")
        services = get_service_data()
        dv_list = list(services.keys())
        
        raw_nv = get_nhan_vien_data()
        ds_tho = [str(r[next((i for i, h in enumerate([str(h).strip().lower() for h in raw_nv[0]]) if 'tên' in h or 'nhân viên' in h), -1)]).strip() for r in raw_nv[1:] if len(r) > next((i for i, h in enumerate([str(h).strip().lower() for h in raw_nv[0]]) if 'tên' in h or 'nhân viên' in h), -1)] if len(raw_nv) > 1 else []

        # ==================== TAB 1: TỔNG QUAN ====================
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
                
                # Biểu đồ Doanh Thu Nhanh
                try:
                    bc_values, _ = get_bao_cao_va_bill_tam()
                    if len(bc_values) > 1:
                        df_bc = pd.DataFrame(bc_values[1:], columns=bc_values[0])
                        c_tien = next((c for c in df_bc.columns if 'tiền' in c.lower() or 'tien' in c.lower()), 'Thành tiền')
                        c_ngay = next((c for c in df_bc.columns if 'ngày' in c.lower() or 'ngay' in c.lower()), 'Ngày')
                        
                        df_bc[c_tien] = pd.to_numeric(df_bc[c_tien].astype(str).str.replace(',', '').str.replace('.', ''), errors='coerce').fillna(0)
                        
                        # Xử lý ngày tháng để vẽ biểu đồ 7 ngày gần nhất
                        df_bc['DateObj'] = pd.to_datetime(df_bc[c_ngay], format="%d/%m/%Y", errors='coerce')
                        last_7_days = df_bc.dropna(subset=['DateObj'])
                        last_7_days = last_7_days.groupby('DateObj')[c_tien].sum().reset_index().tail(7)
                        last_7_days['Ngày'] = last_7_days['DateObj'].dt.strftime('%d/%m')
                        
                        if not last_7_days.empty:
                            st.markdown("<div style='margin-top:15px; font-weight:bold;'>📉 Tăng trưởng 7 ngày qua</div>", unsafe_allow_html=True)
                            st.line_chart(last_7_days.set_index('Ngày')[c_tien], color=THEME_COLORS['primary'])
                except: pass

            # TÍCH HỢP LỊCH HẸN RA TỔNG QUAN
            with st.container(border=True):
                st.markdown('<div class="the-quan-ly-flat">📅 LỊCH HẸN HÔM NAY</div>', unsafe_allow_html=True)
                lh_data = get_lich_hen_data()
                if len(lh_data) > 1:
                    df_lh = pd.DataFrame(lh_data[1:], columns=lh_data[0])
                    today_str = get_now_vn().strftime("%Y-%m-%d")
                    # Lọc lịch hẹn của ngày hôm nay
                    if 'Ngày hẹn' in df_lh.columns:
                        df_today_lh = df_bc = df_lh[df_lh['Ngày hẹn'] == today_str]
                        if not df_today_lh.empty:
                            for idx, row in df_today_lh.iterrows():
                                gio = row.get('Giờ hẹn', '--:--')
                                khach = row.get('Tên khách', 'Khách')
                                sdt = row.get('Số điện thoại', '')
                                dv = row.get('Dịch vụ', '')
                                st.markdown(f"""
                                    <div class="lich-hen-item">
                                        <div><span style="color:#d93025; font-weight:800; font-size:16px;">{gio}</span><br><span style="font-size:13px; color:#555;">{khach} - {sdt}</span></div>
                                        <div style="font-size:12px; font-weight:600; color:{THEME_COLORS['primary']};">{dv}</div>
                                    </div>
                                """, unsafe_allow_html=True)
                        else: st.info("Không có lịch hẹn nào được ghi nhận cho hôm nay.")
                else: st.info("Dữ liệu lịch hẹn trống.")

            if st.session_state.get("bill_vua_in"):
                with st.container(border=True):
                    st.markdown('<div class="the-quan-ly-flat">🧾 HOÁ ĐƠN VỪA KHỞI TẠO</div>', unsafe_allow_html=True)
                    st.markdown(st.session_state.bill_vua_in, unsafe_allow_html=True)
                    if st.button("❌ ẨN BILL NÀY", use_container_width=True, type="primary"):
                        st.session_state.bill_vua_in = None
                        st.rerun()

        # ==================== TAB 2: LÊN HÓA ĐƠN ====================
        with tabs[1]:
            with st.container(border=True):
                st.markdown('<div class="the-quan-ly-flat">THÔNG TIN KHÁCH HÀNG</div>', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1: 
                    kh_sdt = st.text_input("Số điện thoại khách", value=st.session_state.kh_sdt_val)
                    if kh_sdt != st.session_state.kh_sdt_val:
                        st.session_state.kh_sdt_val = kh_sdt
                        if kh_sdt.strip(): trigger_auto_save()
                        st.rerun() 
                with c2: 
                    kh_ten = st.text_input("Tên khách hàng", value=st.session_state.kh_ten_val)
                    if kh_ten != st.session_state.kh_ten_val: 
                        st.session_state.kh_ten_val = kh_ten
                        trigger_auto_save()
                        st.rerun()

            with st.container(border=True):
                st.markdown('<div class="the-quan-ly-flat">DANH SÁCH DỊCH VỤ</div>', unsafe_allow_html=True)
                dv_chon = st.multiselect("Chạm chọn dịch vụ...", options=dv_list if dv_list else ["Đang tải..."], key=f"dv_{st.session_state.reset_counter}")
                if st.button("➕ THÊM VÀO GIỎ HÀNG", type="primary", use_container_width=True):
                    if dv_chon:
                        for dv in dv_chon:
                            info_dv = services.get(dv, {"gia": 0.0, "hoa_hong": 0.0})
                            existing = next((item for item in st.session_state.gio_hang if item["dich_vu"] == dv), None)
                            if existing:
                                existing["so_luong"] += 1.0
                                existing["thanh_tien"] = existing["so_luong"] * existing["don_gia"]
                            else:
                                st.session_state.gio_hang.append({"dich_vu": dv, "so_luong": 1.0, "don_gia": info_dv["gia"], "thanh_tien": info_dv["gia"], "phan_tram_hh": info_dv["hoa_hong"]})
                        st.session_state.reset_counter += 1  
                        trigger_auto_save()
                        st.toast("✅ Đã thêm dịch vụ! Đang tự động sao lưu...")
                        time.sleep(0.3)
                        st.rerun()

            t_bill = 0.0
            if st.session_state.gio_hang:
                with st.container(border=True):
                    st.markdown(f'<div class="the-quan-ly-flat">🛒 GIỎ HÀNG ({len(st.session_state.gio_hang)} món)</div>', unsafe_allow_html=True)
                    for idx, item in enumerate(st.session_state.gio_hang):
                        c_sl, c_tt, c_del = st.columns([5, 3, 2])
                        with c_sl:
                            new_sl = st.number_input(f"{item['dich_vu']}:", min_value=0.5, value=float(item['so_luong']), step=0.5, key=f"cart_sl_{idx}")
                            if new_sl != item['so_luong']:
                                item['so_luong'] = new_sl
                                item['thanh_tien'] = new_sl * item['don_gia']
                                trigger_auto_save()
                                st.rerun()
                        with c_tt:
                            st.markdown(f"<div style='margin-top: 30px; font-weight:800; color:{THEME_COLORS['text_main']};'>{item['thanh_tien']:,.0f}đ</div>", unsafe_allow_html=True)
                        with c_del:
                            st.markdown(f"<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
                            if st.button("🗑️", key=f"del_{idx}", use_container_width=True):
                                st.session_state.gio_hang.pop(idx)
                                trigger_auto_save()
                                st.rerun()
                        t_bill += item['thanh_tien']

                    if st.button("💾 LƯU ĐƠN VÀO BILL CHỜ (ĐẨY XUỐNG BẾP/THỢ)", use_container_width=True):
                        if luu_bill_tam(st.session_state.gio_hang, st.session_state.full_name, st.session_state.kh_sdt_val, st.session_state.kh_ten_val):
                            st.session_state.update({"gio_hang": [], "kh_sdt_val": "", "kh_ten_val": "Khách lẻ"})
                            trigger_auto_save()
                            st.toast("✅ Đã đẩy đơn vào danh sách chờ!")
                            time.sleep(1)
                            st.rerun()

            if t_bill > 0:
                with st.container(border=True):
                    st.markdown('<div class="the-quan-ly-flat">THU NGÂN & CHIẾT KHẤU</div>', unsafe_allow_html=True)
                    chot_tho = st.selectbox("Thợ thực hiện:", options=ds_tho if ds_tho else [st.session_state.full_name])
                    
                    # Tách bạch 2 dòng tiền giảm trừ
                    c_km1, c_km2 = st.columns(2)
                    with c_km1: tien_chiet_khau = st.number_input("Chiết khấu ưu đãi (VND)", value=0.0, step=1000.0)
                    with c_km2: tien_khuyen_mai = st.number_input("Trừ khuyến mãi (VND)", value=0.0, step=1000.0)
                    
                    ghi_chu_don = st.text_input("Ghi chú cho đơn hàng (Hiển thị lên Bill):")
                    
                    tong_tru = tien_chiet_khau + tien_khuyen_mai
                    t_khach_tra = max(0.0, t_bill - tong_tru)
                    kh_dua = st.number_input("Số tiền mặt khách trả", value=float(t_khach_tra))
                    t_du = kh_dua - t_khach_tra

                    hs_giam = t_khach_tra / t_bill if t_bill > 0 else 1.0
                    t_cong_tho = sum(item['thanh_tien'] * hs_giam * (item['phan_tram_hh'] / 100.0) for item in st.session_state.gio_hang)

                    st.write("")
                    cb1, cb2, cb3, cb4 = st.columns(4)
                    with cb1: st.markdown(f'<div style="font-size: 11px; font-weight: 600; color: {THEME_COLORS["text_muted"]}; text-align: center;">Tổng bill</div><div class="box-chung">{t_bill:,.0f}</div>', unsafe_allow_html=True)
                    with cb2: st.markdown(f'<div style="font-size: 11px; font-weight: 600; color: {THEME_COLORS["text_muted"]}; text-align: center;">Chiết khấu</div><div class="box-chung chiet-khau-box">{tien_chiet_khau:,.0f}</div>', unsafe_allow_html=True)
                    with cb3: st.markdown(f'<div style="font-size: 11px; font-weight: 600; color: {THEME_COLORS["text_muted"]}; text-align: center;">Khuyến mãi</div><div class="box-chung chiet-khau-box">{tien_khuyen_mai:,.0f}</div>', unsafe_allow_html=True)
                    with cb4: st.markdown(f'<div style="font-size: 11px; font-weight: 600; color: {THEME_COLORS["text_muted"]}; text-align: center;">Thực thu</div><div class="box-chung khach-tra-box">{t_khach_tra:,.0f}</div>', unsafe_allow_html=True)
                    
                    if t_du > 0: st.markdown(f'<div class="tien-thua-box">Tiền thối lại: <span>{t_du:,.0f} VND</span></div>', unsafe_allow_html=True)

                    if st.button("🚀 XUẤT HÓA ĐƠN", use_container_width=True, type="primary"):
                        try:
                            ws = get_google_sheet_workbook().worksheet("BaoCao")
                            ma_hd = f"HD{get_now_vn().strftime('%y%m%d%H%M')}"
                            rows_to_append = []
                            chi_tiet_tele = ""
                            html_items = ""
                            
                            c_ten = st.session_state.kh_ten_val.strip() if st.session_state.kh_ten_val.strip() else "Khách lẻ"
                            c_sdt = st.session_state.kh_sdt_val.strip()
                            # Ghi chú tổng hợp
                            g_chu_full = f"[CK: {tien_chiet_khau:,.0f} | KM: {tien_khuyen_mai:,.0f}] {ghi_chu_don}"

                            for item in st.session_state.gio_hang:
                                hh_dong = item['thanh_tien'] * hs_giam * (item['phan_tram_hh'] / 100.0)
                                rows_to_append.append([
                                    get_now_vn().strftime("%d/%m/%Y"), st.session_state.full_name, 
                                    c_ten, c_sdt,
                                    item['dich_vu'], item['so_luong'], item['don_gia'], item['thanh_tien'],
                                    get_now_vn().strftime("%H:%M:%S"), g_chu_full, hh_dong, ma_hd, kh_dua, t_du, "0 phút", chot_tho
                                ])
                                sl_sach = int(item['so_luong']) if float(item['so_luong']).is_integer() else item['so_luong']
                                html_items += f"""<tr><td style="text-align: left; border: none; padding: 6px 0;"><div style="font-weight: 600; color: #111; font-size: 14px;">{item["dich_vu"]}</div><div style="font-size: 12px; color: #666;">{sl_sach} x {item['don_gia']:,.0f}đ</div></td><td style="text-align: right; border: none; padding: 6px 0; vertical-align: middle;"><div style="font-weight: 700; color: #111; font-size: 14px;">{item["thanh_tien"]:,.0f}đ</div></td></tr>"""
                                chi_tiet_tele += f"\n- {item['dich_vu']} (x{sl_sach}): {item['thanh_tien']:,.0f}đ"
                                
                            ws.append_rows(rows_to_append)
                            st.session_state.update({"gio_hang": [], "kh_sdt_val": "", "kh_ten_val": "Khách lẻ"})
                            trigger_auto_save()
                            
                            nd_mail = f"THÔNG BÁO - Đã thanh toán ✅\n \nMã ĐH: {ma_hd} | {get_now_vn().strftime('%d/%m/%Y %H:%M')}\nKhách: {c_ten} - {c_sdt}\nThu ngân: {st.session_state.full_name}\nThợ: {chot_tho}\n \nDịch vụ:{chi_tiet_tele}\n \nTổng bill: {t_bill:,.0f} đ\nChiết khấu: -{tien_chiet_khau:,.0f} đ\nKhuyến mãi: -{tien_khuyen_mai:,.0f} đ\n \nTHỰC THU: {t_khach_tra:,.0f} đ\n \nGhi chú: {ghi_chu_don}"
                            gui_email_backup(nd_mail)
                            gui_telegram_notification(nd_mail)

                            st.session_state.bill_vua_in = f"""<style>.hoa-don-khung table, .hoa-don-khung tr, .hoa-don-khung td {{border: none !important; background: transparent !important;}}</style>
<div class="hoa-don-khung">
<div style="text-align: center; border-bottom: 1px dashed {THEME_COLORS['border_input']}; padding-bottom: 15px; margin-bottom: 20px;"><div style="font-size: 20px; font-weight: 900; color: {THEME_COLORS['text_main']};">{settings.get('TenTiem', 'SALON KIM HIỀN')}</div><div style="font-size: 13px; color: {THEME_COLORS['text_secondary']}; margin-top:4px;">{settings.get('Diachi', '')}</div><div style="font-size: 13px; color: {THEME_COLORS['text_secondary']};">SĐT: {settings.get('SDT', '')}</div><div style="font-size: 18px; font-weight: 800; color: {THEME_COLORS['text_main']}; margin-top:10px;">HÓA ĐƠN DỊCH VỤ</div><div style="font-size: 12px; color: {THEME_COLORS['text_muted']}; margin-top:5px;">Mã số: {ma_hd}</div></div>
<div style="font-size: 13px; font-weight: 600; color: {THEME_COLORS['text_secondary']}; text-align: left; margin-bottom: 8px; border-bottom: 1px dashed {THEME_COLORS['border_light']}; padding-bottom: 5px;">Thông tin khách hàng:</div>
<div style="border-bottom: 1px solid {THEME_COLORS['border_light']}; padding-bottom: 10px; margin-bottom: 15px; font-size: 14px; color: {THEME_COLORS['text_secondary']};">
    <div style="display: flex; justify-content: space-between; margin-bottom: 6px;"><span>Ngày:</span> <span style="text-align: right;">{get_now_vn().strftime('%d/%m/%Y %H:%M')}</span></div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 6px;"><span>Khách hàng:</span> <span style="font-weight:700; color: {THEME_COLORS['text_main']}; text-align: right;">{c_ten}</span></div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 6px;"><span>Thu ngân:</span> <span style="text-align: right;">{st.session_state.full_name}</span></div>
    <div style="display: flex; justify-content: space-between;"><span>Thợ thực hiện:</span> <span style="font-weight:700; color: {THEME_COLORS['text_main']}; text-align: right;">{chot_tho}</span></div>
</div>
<div style="margin-bottom: 15px;"><div style="font-size: 13px; font-weight: 600; color: {THEME_COLORS['text_secondary']}; text-align: left; margin-bottom: 8px; border-bottom: 1px dashed {THEME_COLORS['border_light']}; padding-bottom: 5px;">Chi tiết dịch vụ:</div>
    <table style="width: 100%; border-collapse: collapse;">{html_items}</table>
</div>
<div style="font-size: 14px; border-bottom: 1px solid {THEME_COLORS['border_light']}; padding-bottom: 10px; margin-bottom: 15px; color: {THEME_COLORS['text_main']};">
    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;"><span>Cộng tiền:</span> <span style="text-align: right; font-weight: 600;">{t_bill:,.0f}</span></div>
    <div style="display: flex; justify-content: space-between; color: {THEME_COLORS['accent_chiet_khau']}; margin-bottom: 8px;"><span>Chiết khấu:</span> <span style="text-align: right; font-weight: 600;">-{tien_chiet_khau:,.0f}</span></div>
    <div style="display: flex; justify-content: space-between; color: {THEME_COLORS['accent_chiet_khau']}; margin-bottom: 8px;"><span>Khuyến mãi:</span> <span style="text-align: right; font-weight: 600;">-{tien_khuyen_mai:,.0f}</span></div>
</div>
<div style="font-size: 13px; font-weight: 600; color: {THEME_COLORS['text_secondary']}; text-align: left; margin-bottom: 8px; border-bottom: 1px dashed {THEME_COLORS['border_light']}; padding-bottom: 5px;">Số tiền cần thanh toán:</div>
<div style="display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 18px; font-weight: 900; color: {THEME_COLORS['text_main']};"><span>TỔNG CỘNG:</span> <span style="text-align: right; color: {THEME_COLORS['accent_chiet_khau']};">{t_khach_tra:,.0f}</span></div>
<div style="text-align: center; margin-top: 15px; font-size: 13px; font-weight: 600; color: #444;">Ghi chú: {ghi_chu_don}</div>
<div style="text-align: center; margin-top: 15px; font-size: 13px; color: {THEME_COLORS['text_muted']}; font-style: italic;">Cảm ơn quý khách đã sử dụng dịch vụ!</div>
</div>"""
                            st.toast("✅ Đã xuất hóa đơn!")
                            time.sleep(1)
                            st.rerun()
                        except Exception as e: st.error(f"Lỗi: {e}")

        # ==================== TAB 3: LỊCH HẸN (HOÀN THIỆN ĐÚNG CỘT) ====================
        with tabs[2]:
            with st.container(border=True):
                st.markdown('<div class="the-quan-ly-flat">📅 TẠO LỊCH HẸN MỚI</div>', unsafe_allow_html=True)
                
                c_hen1, c_hen2 = st.columns(2)
                with c_hen1:
                    hen_ten = st.text_input("Tên khách hàng (Hẹn)")
                    hen_ngay = st.date_input("Ngày hẹn", value=get_now_vn().date())
                with c_hen2:
                    hen_sdt = st.text_input("Số điện thoại (Hẹn)")
                    hen_gio = st.time_input("Giờ hẹn", value=get_now_vn().time())
                
                hen_dv = st.multiselect("Dịch vụ quan tâm", options=dv_list if dv_list else ["Đang tải..."])
                hen_tho = st.selectbox("Thợ yêu cầu (nếu có)", options=["Không yêu cầu"] + ds_tho if ds_tho else ["Không yêu cầu", st.session_state.full_name])
                hen_ghi_chu = st.text_area("Ghi chú thêm (Tình trạng tóc/yêu cầu riêng)")

                if st.button("💾 LƯU LỊCH HẸN", use_container_width=True, type="primary"):
                    if hen_ten and hen_sdt:
                        try:
                            ws_hen = get_google_sheet_workbook().worksheet("LichHen")
                            # Đảm bảo chèn đúng 8 cột: Ngày hẹn, Giờ hẹn, Tên khách, Số điện thoại, Dịch vụ, Nhân viên, Trạng thái, Ghi Chú
                            ws_hen.append_row([
                                str(hen_ngay),
                                str(hen_gio),
                                hen_ten,
                                hen_sdt,
                                ", ".join(hen_dv),
                                hen_tho,
                                "CHỜ XÁC NHẬN",
                                hen_ghi_chu
                            ])
                            get_lich_hen_data.clear()
                            st.toast("✅ Đã lưu lịch hẹn thành công!")
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Lỗi khi lưu lịch hẹn. Đảm bảo sheet 'LichHen' có đủ các cột. Chi tiết: {e}")
                    else:
                        st.warning("Vui lòng nhập Tên và Số điện thoại khách hàng.")

        # ==================== TAB 4: BÁO CÁO (KHÔI PHỤC METRICS) ====================
        with tabs[3]:
            if st.session_state["role"] == "Admin":
                with st.container(border=True):
                    st.markdown('<div class="the-quan-ly-flat">📈 BÁO CÁO DOANH THU & KPI</div>', unsafe_allow_html=True)
                    
                    try:
                        data_bc, data_tam = get_bao_cao_va_bill_tam()
                        if len(data_bc) > 1:
                            df_bc = pd.DataFrame(data_bc[1:], columns=data_bc[0])
                            
                            # Tiền xử lý dữ liệu
                            c_tien = next((c for c in df_bc.columns if 'tiền' in c.lower() or 'tien' in c.lower()), 'Thành tiền')
                            c_ngay = next((c for c in df_bc.columns if 'ngày' in c.lower() or 'ngay' in c.lower()), 'Ngày')
                            c_ma = next((c for c in df_bc.columns if 'mã' in c.lower() or 'hd' in c.lower()), None)
                            
                            df_bc[c_tien] = pd.to_numeric(df_bc[c_tien].astype(str).str.replace(',', '').str.replace('.', ''), errors='coerce').fillna(0)
                            
                            # Metrics
                            today_str = get_now_vn().strftime("%d/%m/%Y")
                            month_str = get_now_vn().strftime("%m/%Y")
                            
                            df_today = df_bc[df_bc[c_ngay] == today_str] if c_ngay in df_bc.columns else pd.DataFrame()
                            df_month = df_bc[df_bc[c_ngay].str.contains(month_str, na=False)] if c_ngay in df_bc.columns else pd.DataFrame()
                            
                            doanh_thu_ngay = df_today[c_tien].sum() if not df_today.empty else 0
                            doanh_thu_thang = df_month[c_tien].sum() if not df_month.empty else 0
                            khach_hom_nay = len([x for x in df_today[c_ma].unique() if str(x).strip()]) if c_ma and not df_today.empty else 0
                            bill_cho = max(0, len(data_tam) - 1)
                            
                            m1, m2, m3, m4 = st.columns(4)
                            m1.metric("💰 DT Hôm nay", f"{doanh_thu_ngay:,.0f}đ")
                            m2.metric("💳 DT Tháng", f"{doanh_thu_thang:,.0f}đ")
                            m3.metric("👥 Khách nay", f"{khach_hom_nay} KH")
                            m4.metric("⏳ Đơn chờ", f"{bill_cho} Bill")
                            
                            # KPI
                            st.markdown("<div style='margin-top:20px; font-weight:bold;'>🏆 KPI THỢ HÔM NAY</div>", unsafe_allow_html=True)
                            if not df_today.empty and len(df_today.columns) >= 16:
                                kpi_df = df_today.groupby(df_today.columns[15])[c_tien].sum().reset_index()
                                kpi_df.columns = ["Tên thợ", "Doanh thu tạo ra"]
                                kpi_df = kpi_df.sort_values(by="Doanh thu tạo ra", ascending=False)
                                kpi_df["Doanh thu tạo ra"] = kpi_df["Doanh thu tạo ra"].apply(lambda x: f"{x:,.0f} đ")
                                st.dataframe(kpi_df, use_container_width=True, hide_index=True)
                            else: st.info("Hôm nay chưa có giao dịch nào hoàn thành.")
                            
                            # Báo cáo Trạng thái Nhân Viên
                            st.markdown("<div style='margin-top:20px; font-weight:bold;'>📍 TRẠNG THÁI NHÂN VIÊN (Phiên làm việc)</div>", unsafe_allow_html=True)
                            nv_status = []
                            for nv in ds_tho:
                                status = "🟢 Đang làm việc" if nv == st.session_state.full_name else "🔴 Offline"
                                nv_status.append({"Tên nhân viên": nv, "Trạng thái": status})
                            st.dataframe(pd.DataFrame(nv_status), use_container_width=True, hide_index=True)

                            st.markdown("<div style='margin-top:20px; font-weight:bold;'>🧾 DỮ LIỆU TỔNG HỢP</div>", unsafe_allow_html=True)
                            c_btn1, c_btn2 = st.columns(2)
                            with c_btn1:
                                if st.button("⏰ Cập nhật dữ liệu", use_container_width=True):
                                    get_bao_cao_va_bill_tam.clear()
                                    st.rerun()
                            with c_btn2:
                                csv_data = convert_df_to_csv(df_bc)
                                st.download_button("📥 Xuất File Excel (CSV)", data=csv_data, file_name=f"DoanhThu_{get_now_vn().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True, type="primary")
                            st.dataframe(df_bc, use_container_width=True)
                        else:
                            st.info("Chưa có dữ liệu báo cáo.")
                            if st.button("⏰ Cập nhật dữ liệu", use_container_width=True):
                                get_bao_cao_va_bill_tam.clear()
                                st.rerun()
                                
                    except Exception as e: 
                        st.error(f"Lỗi tải dữ liệu báo cáo: {e}")
            else:
                st.warning("🔒 Chức năng này chỉ dành cho Quản lý.")

        # ==================== TAB 5: QUẢN TRỊ ====================
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
                                                
                                                if xoa_bill_tam_dong_gốc(sheet_row_idx):
                                                    st.toast("⚡ Đã nạp đơn vào giỏ hàng!")
                                                    time.sleep(0.5)
                                                    st.rerun()
                        else: st.info("Không có đơn chờ duyệt.")
                    except Exception as e: st.error(f"Lỗi đọc đơn chờ: {e}")

                with st.container(border=True):
                    st.markdown('<div class="the-quan-ly-flat">🧪 PHÒNG NGHIÊN CỨU MÀU TÓC</div>', unsafe_allow_html=True)
                    c_lab1, c_lab2 = st.columns(2)
                    with c_lab1:
                        mau_nhuom = st.selectbox("Màu bạn muốn nhuộm:", ["Vàng Đồng (8.43)", "Nâu Lạnh (6.1)", "Khói Xám (8.11)", "Tự phối màu"])
                    with c_lab2:
                        nen_toc = st.selectbox("Nền tóc hiện tại:", ["Level 3 (Đen tự nhiên)", "Level 5 (Nâu sáng)", "Level 7 (Vàng sậm)", "Level 9 (Tẩy sáng)"])
                        
                    if st.button("⚗️ THỬ NGHIỆM CÔNG THỨC & TỶ LỆ", type="primary", use_container_width=True):
                        st.markdown(f"<div style='margin: 15px 0; border-bottom: 2px dashed {THEME_COLORS['primary']};'></div>", unsafe_allow_html=True)
                        
                        # Set data cho màu tóc chuyên nghiệp
                        cong_thuc_data = []
                        loi_khuyen = ""
                        if "Vàng Đồng" in mau_nhuom:
                            cong_thuc_data = [["Màu chủ đạo 8.43", 70.0], ["Màu mix vàng 0.43", 20.0], ["Màu mix tự nhiên 0.00", 10.0], ["Oxy 9%", 100.0]]
                            loi_khuyen = "Phù hợp da trắng. Chải cách chân tóc 2cm. Chờ 30 phút rồi chải chân tóc."
                        elif "Nâu Lạnh" in mau_nhuom:
                            cong_thuc_data = [["Màu chủ đạo 6.1", 80.0], ["Màu mix tro 0.11", 15.0], ["Màu mix xanh rêu 0.22 (khử đỏ)", 5.0], ["Oxy 6%", 100.0]]
                            loi_khuyen = "Màu tệp vào tóc lâu phai. Nếu tóc có ánh đỏ nhiều, cân nhắc tăng 0.22 lên 10%."
                        elif "Khói Xám" in mau_nhuom:
                            cong_thuc_data = [["Màu chủ đạo 8.11", 70.0], ["Màu mix tro 0.11", 20.0], ["Màu mix tím 0.66 (khử vàng)", 10.0], ["Oxy 3%", 100.0]]
                            loi_khuyen = "BẮT BUỘC: Nền tóc phải ở Level 9+. Dùng Oxy thấp để hạt màu khói ngậm sâu vào biểu bì."
                        else:
                            cong_thuc_data = [["Màu chủ đạo", 80.0], ["Màu mix", 20.0], ["Oxy tùy chọn", 100.0]]
                            loi_khuyen = "Theo dõi sát biểu bì tóc."

                        st.markdown(f"<h4 style='color:{THEME_COLORS['text_title']};'>1. Bảng công thức {mau_nhuom} (Tỷ lệ 1:1)</h4>", unsafe_allow_html=True)
                        st.dataframe(pd.DataFrame(cong_thuc_data, columns=["Thành phần (Thuốc + Trợ nhuộm)", "Tỷ lệ % (Gam/ML)"]), use_container_width=True, hide_index=True)
                        
                        st.markdown(f"<h4 style='color:{THEME_COLORS['text_title']}; margin-top: 15px;'>2. Quy trình bôi thuốc chuẩn</h4>", unsafe_allow_html=True)
                        st.markdown(f"""
                        * **Bước 1:** Chuẩn bị bát nhựa, cân tiểu ly điện tử để đong chính xác tỷ lệ màu và Oxy.
                        * **Bước 2:** Đánh đều hỗn hợp thuốc nhuộm và Oxy cho đến khi nhuyễn, không vón cục.
                        * **Bước 3:** Chải thuốc lên thân và ngọn tóc trước (nếu là tóc nguyên thủy chưa nhuộm).
                        * **Bước 4:** Để thời gian lưu thuốc chuẩn (thường từ 35-45 phút). Kích nhiệt nếu cần thiết.
                        """)
                        
                        st.markdown(f"<h4 style='color:{THEME_COLORS['text_title']}; margin-top: 15px;'>3. Lời khuyên kỹ thuật & Đánh giá</h4>", unsafe_allow_html=True)
                        st.success(f"📌 {loi_khuyen}")
                        st.warning("⚠️ **Lưu ý thao tác:** Luôn đeo găng tay. Khách hàng da đầu nhạy cảm cần dùng tinh chất bảo vệ da đầu trước khi vào thuốc.")

                with st.container(border=True):
                    st.markdown('<div class="the-quan-ly-flat">HỆ THỐNG</div>', unsafe_allow_html=True)
                    if st.button("♻️ LÀM MỚI BỘ NHỚ", use_container_width=True, type="primary"):
                        st.cache_data.clear()
                        st.cache_resource.clear() 
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
