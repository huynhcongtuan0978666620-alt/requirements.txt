import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import pytz
import time
import re
import random
import threading
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit.components.v1 as components

# 1. Cấu hình trang tối ưu riêng cho giao diện điện thoại
st.set_page_config(
    page_title="SALON PRO V15",
    layout="wide",
    page_icon="💇‍♀️",
    initial_sidebar_state="collapsed",
)

# CHÈN ĐOẠN NÀY NGAY DƯỚI SET_PAGE_CONFIG ĐỂ KÍCH HOẠT PWA
components.html(
    """
    <script>
      if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js')
        .then(reg => console.log('✅ Service Worker đăng ký thành công!'))
        .catch(err => console.log('❌ Service Worker lỗi:', err));
      }
    </script>
    """,
    height=0,
)



# =====================================================================
# 📍 BỘ THEO DÕI TRẠNG THÁI NHÂN VIÊN TOÀN CỤC
# =====================================================================
@st.cache_resource
def get_global_user_tracker():
    return {}

# =====================================================================
# 🕒 HÀM LẤY GIỜ VIỆT NAM CHUẨN (ĐƯA LÊN ĐẦU ĐỂ PHỤC VỤ THỜI GIAN THỰC)
# =====================================================================
def get_now_vn():
    vn_tz = pytz.timezone("Asia/Ho_Chi_Minh")
    return datetime.now(vn_tz)

# =====================================================================
# 🌟 CẤU HÌNH BẢNG MÀU CHI TIẾT TỪNG THÀNH PHẦN (DESIGN SYSTEM V15 NÂNG CẤP)
# =====================================================================
THEME_DAY = {
    "bg_app": "#e8f5f3",
    "bg_card": "#ffffff",
    "bg_box_chung": "#f4f7f6",
    "bg_vip_box": "#e3f2fd",
    "bg_shake_box": "#fff3e0",
    "bg_badge_hang": "#efebe9",
    "bg_marquee": "#fff9c4",            # Nền chữ chạy ban ngày (Vàng nhạt thanh lịch)
    "text_marquee": "#0f4c43",          # Màu chữ chạy ban ngày độc lập
    "primary": "rgba(70, 140, 150, 1)", 
    "text_primary_btn": "#ffffff",      # Màu chữ của nút Primary ban ngày
    "accent_vip": "#ffb300",            
    "accent_danger": "#d32f2f",         
    "accent_zalo": "#0068ff",           
    "accent_chiet_khau": "#e65100",     
    "text_main": "#263238",             
    "text_secondary": "#546e7a",        
    "text_muted": "#90a4ae",            
    "text_title": "#0f4c43",            
    "text_badge": "#ffffff",            
    "border_light": "#eaeaea",          
    "border_input": "#cfd8dc",          
    "border_badge": "#b2dfdb",          
    "border_vip": "#4fc3f7",            
    "shadow_light": "rgba(0, 0, 0, 0.015)", 
    "shadow_heavy": "rgba(0, 0, 0, 0.04)",  
    "shadow_toast": "rgba(0, 0, 0, 0.6)",   
}

THEME_NIGHT = {
    "bg_app": "#0f1a1c",                # Nền tối sang trọng huyền bí (Không bị đen xì)
    "bg_card": "#162629",               # Nền hộp thẻ ban đêm
    "bg_box_chung": "#1e3337",          
    "bg_vip_box": "#152d42",            
    "bg_shake_box": "#3d2a15",          
    "bg_badge_hang": "#2e2522",         
    "bg_marquee": "#233d41",            # Nền chữ chạy ban đêm độc lập
    "text_marquee": "#ffd54f",          # Màu chữ chạy ban đêm (Vàng neon nổi bật)
    "primary": "#26a69a",               
    "text_primary_btn": "#0f1a1c",      # Màu chữ nút bấm chính ban đêm độc lập
    "accent_vip": "#ffd54f",            
    "accent_danger": "#ff5252",         
    "accent_zalo": "#29b6f6",           
    "accent_chiet_khau": "#ff7043",     
    "text_main": "#eceff1",             
    "text_secondary": "#b0bec5",        
    "text_muted": "#78909c",            
    "text_title": "#4db6ac",            
    "text_badge": "#0f1a1c",            
    "border_light": "#233d41",          
    "border_input": "#37474f",          
    "border_badge": "#004d40",          
    "border_vip": "#0288d1",            
    "shadow_light": "rgba(0, 0, 0, 0.3)",   
    "shadow_heavy": "rgba(0, 0, 0, 0.5)",   
    "shadow_toast": "rgba(0, 0, 0, 0.7)",   
}

# TỰ ĐỘNG CHUYỂN ĐỔI GIAO DIỆN THEO MÚI GIỜ HOẠT ĐỘNG
current_hour = get_now_vn().hour
if 6 <= current_hour < 18:
    THEME_COLORS = THEME_DAY
    THEME_MODE_LABEL = "☀️ CHẾ ĐỘ BAN NGÀY"
else:
    THEME_COLORS = THEME_NIGHT
    THEME_MODE_LABEL = "🌙 CHẾ ĐỘ BAN ĐÊM"

def set_app_background(colors):
    gradient_css = f"""
    <style>
    .stApp {{
        background: linear-gradient(180deg, {colors['bg_app']} 20%, {colors['bg_box_chung']} 80%);
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(gradient_css, unsafe_allow_html=True)

set_app_background(THEME_COLORS)



def inject_advanced_ui_js():
    js_code = f"""
    <script>
    const parentDoc = window.parent.document;
    
    // --- CHỐNG NGỦ (ANTI-SLEEP PING 30s) ---
    setInterval(() => {{
        fetch('/_stcore/health').catch(()=>{{}});
    }}, 30000); 

    // --- FIX LỖI MẤT TAB KHI F5 & CHUYỂN TAB TỰ ĐỘNG ---
    function initTabObserver() {{
        const tabs = parentDoc.querySelectorAll('button[data-baseweb="tab"]');
        if (tabs.length === 0) {{
            setTimeout(initTabObserver, 500);
            return;
        }}
        
        // Đọc Tab từ URL (query_params) và tự động bấm vào Tab đó
        const urlParams = new URLSearchParams(window.parent.location.search);
        const activeTabIdx = urlParams.get('tab');
        if (activeTabIdx !== null && parseInt(activeTabIdx) < tabs.length) {{
            if (tabs[activeTabIdx].getAttribute('aria-selected') !== 'true') {{
                tabs[activeTabIdx].click();
            }}
        }}

        // Gắn sự kiện: Bấm tab nào thì lưu tab đó lên URL
        tabs.forEach((tab, index) => {{
            tab.addEventListener('click', () => {{
                const url = new URL(window.parent.location);
                url.searchParams.set('tab', index);
                window.parent.history.replaceState({{}}, '', url);
            }});
        }});
    }}
    
    if(!parentDoc.body.hasAttribute('data-tab-observer')) {{
        parentDoc.body.setAttribute('data-tab-observer', '1');
        initTabObserver();
    }}

    function showPremiumToast(text) {{
        let t = parentDoc.createElement('div');
        t.innerText = text;
        t.style.cssText = "position:fixed; top:15%; left:50%; transform:translate(-50%, -50%); background: {THEME_COLORS['primary']}; color:#ffffff; padding:15px 30px; border-radius:12px; font-weight:bold; box-shadow: 0 10px 30px {THEME_COLORS['shadow_toast']}; border-left: 5px solid {THEME_COLORS['accent_vip']}; z-index:9999999; font-size:15px; transition: opacity 0.5s; text-align:center;";
        parentDoc.body.appendChild(t);
        setTimeout(() => {{ t.style.opacity = '0'; setTimeout(()=>t.remove(), 500); }}, 2500);
    }}
    
    // --- HIỆU ỨNG 3 CLICK NỔ CONFETTI ---
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
                showPremiumToast('🎉 CỐ LÊN NHÉ! BÃO ĐƠN NÀO! 🎉');
                for(let i=0; i<60; i++) {{
                    let f = parentDoc.createElement('div');
                    f.style.cssText = `position:fixed; width:8px; height:8px; border-radius:100%; background-color:${{['{THEME_COLORS['primary']}', '{THEME_COLORS['accent_danger']}', '#40a9ff', '{THEME_COLORS['accent_vip']}'][Math.floor(Math.random()*4)]}}; left:50%; top:50%; transform:translate(-50%, -50%); pointer-events:none; z-index:9999998; transition: all 1.5s cubic-bezier(0.25, 1, 0.5, 1);`;
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


def render_balloons_html():
    colors = [
        THEME_COLORS["primary"],
        THEME_COLORS["primary"],
        THEME_COLORS["accent_vip"],
    ]
    html_balloons = '<div class="balloon-container-css" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: 9999998; overflow: hidden;">'
    for i in range(20):
        left_pos = random.uniform(5, 95)
        color = random.choice(colors)
        size_ratio = random.uniform(0.6, 1.0)
        w, h = int(40 * size_ratio), int(55 * size_ratio)
        delay = round(random.uniform(0.0, 2.0), 2)
        duration = round(random.uniform(4.0, 6.0), 2)
        html_balloons += f'<div style="position: absolute; bottom: -100px; border-radius: 50% 50% 50% 50% / 40% 40% 60% 60%; opacity: 0.8; background-color: {color}; left: {left_pos}vw; width: {w}px; height: {h}px; animation: fly-up-skywards-pure {duration}s linear {delay}s forwards; box-shadow: 0 4px 6px {THEME_COLORS["shadow_light"]};"></div>'
    html_balloons += "<style>@keyframes fly-up-skywards-pure { 0% { transform: translateY(110vh); opacity: 0; } 10% { opacity: 0.8; } 90% { opacity: 0.8; } 100% { transform: translateY(-120vh); opacity: 0; } }</style></div>"
    st.markdown(html_balloons, unsafe_allow_html=True)


def apply_v15_theme():
    p = THEME_COLORS["primary"]
    bg = THEME_COLORS["bg_app"]
    card = THEME_COLORS["bg_card"]
    shadow = THEME_COLORS["shadow_light"]
    txt_main = THEME_COLORS["text_main"]
    txt_muted = THEME_COLORS["text_muted"]
    txt_title = THEME_COLORS["text_title"]
    b_light = THEME_COLORS["border_light"]
    b_input = THEME_COLORS["border_input"]
    bg_marquee = THEME_COLORS["bg_marquee"]

    st.markdown(
        f"""
    <style>

    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
        html, body, .stApp {{ font-family: 'Inter', sans-serif !important; background-color: {bg} !important; padding-top: 0px !important; }}
        header, footer, [data-testid='stToolbar'], [data-testid='stDecoration'] {{ display: none !important; }}
        
        [data-testid="stVerticalBlock"] {{ gap: 14px !important; }}
    
        /* 1. Trả lại thanh Tab nguyên bản thanh lịch theo ảnh ní thích */
        [data-testid="stTabs"] [role="tablist"] {{
            background: transparent !important; 
            border-bottom: 1px solid {b_light} !important;
            padding: 0px !important; 
            box-shadow: none !important;
            margin-bottom: 16px !important;
            gap: 24px !important;
        }}
        button[data-baseweb="tab"] {{ 
            background-color: transparent !important; 
            border-radius: 0px !important; 
            margin: 0px !important;
            padding: 10px 4px !important;
        }}
        button[data-baseweb="tab"] p {{ 
            color: {txt_muted} !important; 
            font-weight: 600 !important; 
            font-size: 15px !important; 
        }}
        button[data-baseweb="tab"][aria-selected="true"] {{ 
            background-color: transparent !important;
            color: {THEME_COLORS['primary']} !important;
        }}
        button[data-baseweb="tab"][aria-selected="true"] p {{ 
            color: #ff4b4b !important; 
        }}
        div[data-testid="stTabsTabBorder"] {{ 
            background-color: {THEME_COLORS['primary']} !important;
            height: 2px !important;
        }}
        
        /* 2. Khối thẻ Card tối giản phẳng cao cấp */
        [data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: {card} !important; 
            border: 1px solid {b_light} !important; 
            border-radius: 16px !important;
            box-shadow: 0 4px 16px {shadow} !important;
            padding: 24px !important; 
            margin-bottom: 15px !important;
        }}
        
        /* 3. Khung chữ chạy viên thuốc chuẩn chỉ */
        .custom-marquee {{
            background-color: {bg_marquee} !important;
            color: {THEME_COLORS['primary']} !important; 
            padding: 12px 20px !important; 
            height: 48px !important;       
            border-radius: 12px !important; 
            font-weight: 500 !important;
            font-size: 15px !important;
            border: 1px solid rgba(15, 76, 67, 0.1) !important;
            margin-bottom: 20px !important;
            width: 100% !important;
            box-shadow: none !important;
            overflow: hidden !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }}
        .custom-marquee marquee {{
            margin: 0 !important;
            padding: 0 !important;
            line-height: 48px !important; 
            display: block !important;
            letter-spacing: 0.5px;
        }}
        
        /* 4. Tinh chỉnh hệ thống Nút bấm mượt mà */
        div[data-testid="stButton"] button {{ 
            border-radius: 10px !important; 
            font-weight: 600 !important; 
            border: 1px solid {b_light} !important; 
            background: {card} !important; 
            transition: all 0.15s ease !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
            color: {txt_main} !important;
        }}
        div[data-testid="stButton"] button:hover {{ transform: translateY(-1px) !important; box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important; border-color: {p} !important; color: {p} !important; }}
        div[data-testid="stButton"] button:active {{ transform: scale(0.97) !important; }}
        
        div[data-testid="stButton"] button[kind="primary"] {{ 
            background-color: {p} !important; 
            color: #ffffff !important; 
            border: none !important; 
        }}
        div[data-testid="stButton"] button[kind="primary"] p {{
            color: #ffffff !important;
            font-weight: 600 !important;
        }}
        div[data-testid="stButton"] button[kind="primary"]:hover {{ background-color: #0b3831 !important; color: #ffffff !important; box-shadow: 0 4px 12px rgba(15,76,67,0.15) !important; }}
        
        /* Các thành phần bổ trợ cho tiệm */
        .stTextInput>div>div>input, .stNumberInput>div>div>input, .stDateInput>div>div>input, .stTimeInput>div>div>input, .stTextArea>div>div>textarea {{ border-radius: 8px !important; border: 1px solid {b_input}; color: {txt_main} !important; }}
        .the-quan-ly-flat {{ color: {txt_title}; font-weight: 800; font-size: 18px; margin-top: 15px !important; margin-bottom: 15px !important; border-bottom: 2px solid {p}; padding-bottom: 8px; text-transform: uppercase; }}
        .box-chung {{ background-color: {THEME_COLORS['bg_box_chung']}; padding: 10px; border-radius: 10px; text-align: center; border: 1px solid {b_light}; font-size: 18px; font-weight: 800; color: {txt_main}; }}
        .chiet-khau-box {{ color: {THEME_COLORS['accent_chiet_khau']} !important; }} 
        .khach-tra-box {{ background-color: {p} !important; color: #ffffff !important; border:none; }}
        .tien-thua-box {{ background-color: {THEME_COLORS['bg_box_chung']}; color: {txt_main}; padding: 15px; border-radius: 10px; text-align: center; font-size: 18px; font-weight: 700; border: 1px dashed {p}; margin: 10px 0; }}
        .hoa-don-khung {{ background-color: {card} !important; color: {txt_main} !important; padding: 20px !important; border-radius: 15px !important; border-top: 6px solid {p} !important; box-shadow: 0 6px 20px {THEME_COLORS['shadow_heavy']}; margin-top: 5px; }}
        .lsc-shake {{ background-color: {THEME_COLORS['bg_shake_box']}; color: {THEME_COLORS['accent_danger']} !important; padding: 10px; border-radius: 8px; text-align: center; font-size: 13px; font-weight:600; margin-bottom: 10px; border-left: 4px solid {THEME_COLORS['accent_danger']}; }}
        .lsc-vip {{ background-color: {THEME_COLORS['bg_vip_box']}; color: {THEME_COLORS['accent_vip']} !important; padding: 8px; border-radius: 8px; text-align: center; font-size: 13px; margin-bottom: 8px; font-weight: 700; border: 1px solid {THEME_COLORS['border_vip']}; }}
        .lich-hen-item {{ background: #fff; padding: 12px; border-radius: 10px; border: 1px solid #eee; border-left: 4px solid {p}; margin-bottom: 8px; }}
    </style>
    """,
        unsafe_allow_html=True,
    )


mau_chu = "#FF5733"
ten_dang_nhap = st.session_state.get("full_name", "Quý khách")
marquee_code = f"""
<div class="custom-marquee">
    <marquee scrollamount="4">
        CHÀO MỪNG <span style="color: {mau_chu}; font-weight: bold;">{ten_dang_nhap}</span> ĐẾN VỚI SALON KIM HIỀN! 
        CHÚC MỘT NGÀY BÃO ĐƠN VÀ CHỐT THẬT NHIỀU BILL NHA!
    </marquee>
</div>
"""
st.markdown(marquee_code, unsafe_allow_html=True)


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
            "token_uri": secrets.get(
                "token_uri", "https://oauth2.googleapis.com/token"
            ),
        }

        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        url = secrets.get("spreadsheet", "")
        if not url and "spreadsheet" in st.secrets:
            url = st.secrets["spreadsheet"]
        return client.open_by_key(url) if len(url) < 50 else client.open_by_url(url)
    except Exception as e:
        st.error(f"Lỗi khởi tạo kết nối Sheets: {e}")
        st.stop()
        
def count_orders_today():
    """Tự động quét tấm sheet BaoCao để đếm tổng đơn chốt chuẩn ngày hôm nay"""
    try:
        sh = get_google_sheet_workbook()
        ws = sh.worksheet("BaoCao")
        records = ws.get_all_values()
        if len(records) <= 1:
            return 0
        
        # Nhận diện cột Ngày tự động để tránh lệch cột
        header = records[0]
        c_ngay_idx = -1
        for idx, col in enumerate(header):
            if "ngày" in col.lower() or "ngay" in col.lower():
                c_ngay_idx = idx
                break
        if c_ngay_idx == -1:
            c_ngay_idx = 0
            
        today_str = get_now_vn().strftime("%d/%m/%Y")
        count = 0
        for row in records[1:]:
            if len(row) > c_ngay_idx:
                if str(row[c_ngay_idx]).strip() == today_str:
                    count += 1
        return count
    except Exception:
        return 0

def admin_clear_all_data():
    """Xoá sạch dữ liệu trên sheet LichHen và BaoCao (Giữ lại hàng tiêu đề đầu)"""
    try:
        sh = get_google_sheet_workbook()
        
        # Xoá dọn dẹp LichHen
        try:
            ws_lh = sh.worksheet("LichHen")
            lh_len = len(ws_lh.get_all_values())
            if lh_len > 1:
                ws_lh.delete_rows(2, lh_len)
        except Exception:
            pass
            
        # Xoá dọn dẹp BaoCao
        try:
            ws_bc = sh.worksheet("BaoCao")
            bc_len = len(ws_bc.get_all_values())
            if bc_len > 1:
                ws_bc.delete_rows(2, bc_len)
        except Exception:
            pass
            
        # Làm sạch toàn bộ bộ nhớ đệm giải phóng tài nguyên cho hệ thống
        st.cache_data.clear()
        st.cache_resource.clear()
        return True
    except Exception:
        return False

def format_drive_direct_url(link):
    if not link or not isinstance(link, str):
        return ""
    match = re.search(r"(pires=|/d/|id=)([a-zA-Z0-9-_]{33,40})", link.strip())
    return f"https://lh3.googleusercontent.com/d/{match.group(2)}" if match else ""


@st.cache_data(ttl=3600)
def get_settings():
    try:
        sh = get_google_sheet_workbook()
        rows = sh.worksheet("ThietLap").get_all_values()
        return {
            str(row[0]).strip(): str(row[1]).strip() for row in rows if len(row) > 1
        }
    except Exception:
        return {
            "TenTiem": "SALON KIM HIỀN",
            "Diachi": "131, TRẦN BÌNH TRỌNG, LONG XUYÊN",
            "SDT": "0947.58.1516",
        }


@st.cache_data(ttl=3600)
def get_service_data():
    try:
        sh = get_google_sheet_workbook()
        rows = sh.worksheet("DanhMuc").get_all_values()
        danh_sach_dv = {}
        for row in rows[1:]:
            if len(row) >= 2:
                ten_dv = str(row[0]).strip()
                if not ten_dv:
                    continue
                try:
                    gia_goc = float(
                        str(row[1]).replace(".", "").replace(",", "").strip()
                    )
                except Exception:
                    gia_goc = 0.0
                hoa_hong = 0.0
                if len(row) >= 3 and row[2]:
                    try:
                        hoa_hong = float(
                            str(row[2]).replace("%", "").replace(",", ".").strip()
                        )
                    except Exception:
                        hoa_hong = 0.0
                danh_sach_dv[ten_dv] = {"gia": gia_goc, "hoa_hong": hoa_hong}
        return danh_sach_dv
    except Exception:
        return {}


@st.cache_data(ttl=3600)
def get_nhan_vien_data():
    try:
        return get_google_sheet_workbook().worksheet("NhanVien").get_all_values()
    except Exception:
        return []


@st.cache_data(ttl=60)
def get_khach_hang_data():
    try:
        rows = get_google_sheet_workbook().worksheet("KhachHang").get_all_values()
        return {
            str(r[0]).strip().replace(".0", ""): str(r[1]).strip()
            for r in rows[1:]
            if len(r) >= 2 and str(r[0]).strip()
        }
    except Exception:
        return {}


@st.cache_data(ttl=15)
def get_plkh_data():
    try:
        return get_google_sheet_workbook().worksheet("PLKH").get_all_values()
    except Exception:
        return []


def get_huy_hieu(tong_chi):
    if tong_chi >= 10000000:
        return "DIAMOND"
    elif tong_chi >= 5000000:
        return "GOLD"
    elif tong_chi >= 3000000:
        return "SILVER"
    elif tong_chi >= 1000000:
        return "THÂN THIẾT"
    return "TIỀM NĂNG"


@st.cache_data(ttl=120)
def get_bao_cao_va_bill_tam():
    try:
        sh = get_google_sheet_workbook()
        return (
            sh.worksheet("BaoCao").get_all_values(),
            sh.worksheet("BillTam").get_all_values(),
        )
    except Exception:
        return [], []


@st.cache_data(ttl=60)
def get_lich_hen_data():
    try:
        sh = get_google_sheet_workbook()
        return sh.worksheet("LichHen").get_all_values()
    except Exception:
        return []


@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode("utf-8-sig")


def luu_bill_tam(gio_hang, nhan_vien, kh_sdt="", kh_ten="Khách lẻ"):
    try:
        sh = get_google_sheet_workbook()
        ws = sh.worksheet("BillTam")
        chi_tiet = " | ".join(
            [f"{item['dich_vu']} (x{item['so_luong']})" for item in gio_hang]
        )
        tong_tien = sum([item["thanh_tien"] for item in gio_hang])
        ws.append_row(
            [
                get_now_vn().strftime("%Y-%m-%d %H:%M:%S"),
                chi_tiet,
                tong_tien,
                nhan_vien,
                str(kh_sdt).strip(),
                str(kh_ten).strip(),
                "CHỜ XỬ LÝ",
            ]
        )
        get_bao_cao_va_bill_tam.clear()
        return True
    except Exception:
        return False


def xoa_bill_tam_dong_goc(index_sheet_row):
    try:
        sh = get_google_sheet_workbook()
        sh.worksheet("BillTam").delete_rows(index_sheet_row)
        get_bao_cao_va_bill_tam.clear()
        return True
    except Exception:
        return False


def gui_email_backup(noi_dung):
    try:
        sender_email = "huynhcongtuan0978666620@gmail.com"
        password = "lwui aesw vqal ytcq"
        receiver_emails = ["huynhcongtuan0978666620@gmail.com"]
        gio_vn_mail = get_now_vn().strftime("%d/%m/%Y %H:%M")
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = ", ".join(receiver_emails)
        msg["Subject"] = f"HOÁ ĐƠN DỊCH VỤ - {gio_vn_mail}"
        msg.attach(MIMEText(noi_dung, "plain"))
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_emails, msg.as_string())
        server.quit()
    except Exception:
        pass


def gui_telegram_notification(noi_dung):
    try:
        if "telegram" in st.secrets:
            bot_token = st.secrets["telegram"].get("bot_token")
            chat_id = st.secrets["telegram"].get("chat_id")
            if bot_token and chat_id:
                url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                requests.post(
                    url, json={"chat_id": chat_id, "text": noi_dung}, timeout=10
                )
    except Exception:
        pass


# =====================================================================
# 3. CƠ CHẾ AUTO-SAVE NGẦM
# =====================================================================
def background_save_draft(gio_hang_copy, nhan_vien, kh_sdt, kh_ten):
    try:
        sh = get_google_sheet_workbook()
        ws = sh.worksheet("BillTam")
        records = ws.get_all_values()
        draft_idx = -1
        for i, r in enumerate(records):
            if (
                len(r) >= 7
                and str(r[3]).strip() == nhan_vien
                and str(r[6]).strip() == "ĐANG SOẠN"
            ):
                draft_idx = i + 1
                break

        chi_tiet = " | ".join(
            [f"{item['dich_vu']} (x{item['so_luong']})" for item in gio_hang_copy]
        )
        tong_tien = sum([item["thanh_tien"] for item in gio_hang_copy])

        if not gio_hang_copy and draft_idx != -1:
            ws.delete_rows(draft_idx)
        elif gio_hang_copy and draft_idx != -1:
            ws.update(
                f"A{draft_idx}:G{draft_idx}",
                [
                    [
                        get_now_vn().strftime("%Y-%m-%d %H:%M:%S"),
                        chi_tiet,
                        tong_tien,
                        nhan_vien,
                        kh_sdt,
                        kh_ten,
                        "ĐANG SOẠN",
                    ]
                ],
            )
        elif gio_hang_copy and draft_idx == -1:
            ws.append_row(
                [
                    get_now_vn().strftime("%Y-%m-%d %H:%M:%S"),
                    chi_tiet,
                    tong_tien,
                    nhan_vien,
                    kh_sdt,
                    kh_ten,
                    "ĐANG SOẠN",
                ]
            )
        get_bao_cao_va_bill_tam.clear()
    except Exception:
        pass


def trigger_auto_save():
    t = threading.Thread(
        target=background_save_draft,
        args=(
            list(st.session_state.gio_hang),
            st.session_state.full_name,
            st.session_state.kh_sdt_val,
            st.session_state.kh_ten_val,
        ),
    )
    t.start()


def check_auto_login():
    if not st.session_state.get("logged_in", False):
        u = st.query_params.get("saved_u")
        p = st.query_params.get("saved_p")
        if u and p:
            if u == "Admin" and p == "111":
                st.session_state.update(
                    {
                        "logged_in": True,
                        "role": "Admin",
                        "full_name": "Quản lý",
                        "tho_chot_val": "Quản lý",
                    }
                )
                return True
            else:
                raw_data = get_nhan_vien_data()
                if len(raw_data) > 0:
                    headers = [str(h).strip().lower() for h in raw_data[0]]
                    col_sdt_idx = next(
                        (
                            i
                            for i, h in enumerate(headers)
                            if "điện thoại" in h or "sđt" in h or "tai khoan" in h
                        ),
                        -1,
                    )
                    col_mk_idx = next(
                        (
                            i
                            for i, h in enumerate(headers)
                            if "mật khẩu" in h or "mat khau" in h or "code" in h
                        ),
                        -1,
                    )
                    col_ten_idx = next(
                        (
                            i
                            for i, h in enumerate(headers)
                            if "tên" in h or "nhân viên" in h
                        ),
                        -1,
                    )

                    found_row = next(
                        (
                            r
                            for r in raw_data[1:]
                            if len(r) > max(col_sdt_idx, col_mk_idx)
                            and str(r[col_sdt_idx]).strip().lstrip("0")
                            == u.strip().lstrip("0")
                            and str(r[col_mk_idx]).strip() == p.strip()
                            and u.strip()
                        ),
                        None,
                    )
                    if found_row:
                        ten_that = (
                            str(found_row[col_ten_idx]).strip()
                            if col_ten_idx != -1 and col_ten_idx < len(found_row)
                            else "Nhân viên"
                        )
                        st.session_state.update(
                            {
                                "logged_in": True,
                                "role": "NhanVien",
                                "full_name": ten_that,
                                "tho_chot_val": ten_that,
                            }
                        )
                        return True
    return st.session_state.get("logged_in", False)


apply_v15_theme()


# =====================================================================
# 4. LUỒNG ĐIỀU HƯỚNG VÀ XỬ LÝ CHÍNH
# =====================================================================
def main():
    init_states = {
        "last_submit": None,
        "submit_count": 0,
        "submitting": False,
        "logged_in": False,
        "role": None,
        "full_name": None,
        "gio_hang": [],
        "bill_vua_in": None,
        "kh_sdt_val": "",
        "kh_ten_val": "",
        "start_time": get_now_vn(),
        "reset_counter": 0,
        "tho_chot_val": "",
        "hang_hien_tai": "",
        "tong_chi_tieu_val": 0.0,
        "da_load_nhap": False,
        "trigger_balloons": False,
        "lh_sdt_val": "",
        "lh_ten_val": "",
        "current_lh_idx": None,
    }
    for key, val in init_states.items():
        if key not in st.session_state:
            st.session_state[key] = val

    apply_v15_theme()
    inject_advanced_ui_js()
    settings = get_settings()

    if not st.session_state["logged_in"]:
        is_auto_logged = check_auto_login()
        if is_auto_logged:
            st.session_state.logged_in = True
            st.session_state.trigger_balloons = True
            st.rerun()

    if st.session_state.get("trigger_balloons"):
        render_balloons_html()
        st.session_state.trigger_balloons = False

    if st.session_state["logged_in"]:
        global_tracker = get_global_user_tracker()
        global_tracker[st.session_state.full_name] = time.time()

    # --- GIAO DIỆN ĐĂNG NHẬP BAN ĐẦU ---
    if not st.session_state["logged_in"]:
        with st.container(border=True):
            st.markdown(
                f"<h2 style='text-align:center; color:{THEME_COLORS['text_title']}; font-weight:800;'>SALON PRO V15</h2>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<p style='text-align:center; color:{THEME_COLORS['text_muted']}; margin-top:-10px; margin-bottom:20px;'>ĐĂNG NHẬP HỆ THỐNG</p>",
                unsafe_allow_html=True,
            )
            u = st.text_input("Tài khoản (Số điện thoại)")
            p = st.text_input("Mật khẩu", type="password")
            remember_me = st.checkbox("Ghi nhớ mật khẩu cho lần sau", value=True)

            if st.button(
                "Xác nhận Đăng Nhập", use_container_width=True, type="primary"
            ):
                if u == "Admin" and p == "111":
                    if remember_me:
                        st.query_params["saved_u"] = u
                        st.query_params["saved_p"] = p
                    st.session_state.update(
                        {
                            "logged_in": True,
                            "role": "Admin",
                            "full_name": "Quản lý",
                            "tho_chot_val": "Quản lý",
                            "trigger_balloons": True,
                        }
                    )
                    st.rerun()
                else:
                    raw_data = get_nhan_vien_data()
                    if len(raw_data) > 0:
                        headers = [str(h).strip().lower() for h in raw_data[0]]
                        col_sdt_idx = next(
                            (
                                i
                                for i, h in enumerate(headers)
                                if "điện thoại" in h or "sđt" in h or "tai khoan" in h
                            ),
                            -1,
                        )
                        col_mk_idx = next(
                            (
                                i
                                for i, h in enumerate(headers)
                                if "mật khẩu" in h or "mat khau" in h or "code" in h
                            ),
                            -1,
                        )
                        col_ten_idx = next(
                            (
                                i
                                for i, h in enumerate(headers)
                                if "tên" in h or "nhân viên" in h
                            ),
                            -1,
                        )

                        found_row = next(
                            (
                                r
                                for r in raw_data[1:]
                                if len(r) > max(col_sdt_idx, col_mk_idx)
                                and str(r[col_sdt_idx]).strip().lstrip("0")
                                == u.strip().lstrip("0")
                                and str(r[col_mk_idx]).strip() == p.strip()
                                and u.strip()
                            ),
                            None,
                        )
                        if found_row:
                            if remember_me:
                                st.query_params["saved_u"] = u
                                st.query_params["saved_p"] = p
                            ten_that = (
                                str(found_row[col_ten_idx]).strip()
                                if col_ten_idx != -1 and col_ten_idx < len(found_row)
                                else "Nhân viên"
                            )
                            st.session_state.update(
                                {
                                    "logged_in": True,
                                    "role": "NhanVien",
                                    "full_name": ten_that,
                                    "tho_chot_val": ten_that,
                                    "trigger_balloons": True,
                                }
                            )
                            st.rerun()
                        else:
                            st.error(
                                "Thông tin số điện thoại hoặc mật khẩu không chính xác."
                            )
                    else:
                        st.error("Hệ thống dữ liệu chưa sẵn sàng.")
                        st.stop()

    # --- KHU VỰC LÀM VIỆC CHÍNH ---
    else:
        if not st.session_state.da_load_nhap:
            st.session_state.da_load_nhap = True
            _, tam_records = get_bao_cao_va_bill_tam()
            services = get_service_data()
            for r in tam_records:
                if (
                    len(r) >= 7
                    and str(r[3]).strip() == st.session_state.full_name
                    and str(r[6]).strip() == "ĐANG SOẠN"
                ):
                    st.session_state.kh_sdt_val = str(r[4]).strip()
                    st.session_state.kh_ten_val = str(r[5]).strip()
                    chi_tiet_dv = str(r[1]).strip()
                    new_gio = []
                    for item in chi_tiet_dv.split(" | "):
                        if item.strip():
                            match = re.match(r"(.+)\s*\(x([\d\.]+)\)", item.strip())
                            if match:
                                t_dv, s_l = match.group(1).strip(), float(
                                    match.group(2)
                                )
                                info = services.get(t_dv, {"gia": 0.0, "hoa_hong": 0.0})
                                new_gio.append(
                                    {
                                        "dich_vu": t_dv,
                                        "so_luong": s_l,
                                        "don_gia": info.get("gia", 0.0),
                                        "thanh_tien": info.get("gia", 0.0) * s_l,
                                        "phan_tram_hh": info.get("hoa_hong", 0.0),
                                    }
                                )
                    if new_gio:
                        st.session_state.gio_hang = new_gio
                        st.toast("🔄 Đã tự động khôi phục giỏ hàng làm dở trước đó!")
                    break

        tabs = st.tabs(
            [
                "🏠 Tổng quan",
                "📄 Lên hóa đơn",
                "📅 Lịch hẹn",
                "📊 Báo cáo",
                "⚙️ Quản trị & Mở rộng",
            ]
        )
        services = get_service_data()
        dv_list = list(services.keys())

        raw_nv = get_nhan_vien_data()
        ds_tho = (
            [
                str(
                    r[
                        next(
                            (
                                i
                                for i, h in enumerate(
                                    [str(h).strip().lower() for h in raw_nv[0]]
                                )
                                if "tên" in h or "nhân viên" in h
                            ),
                            -1,
                        )
                    ]
                ).strip()
                for r in raw_nv[1:]
                if len(r) > 0
            ]
            if len(raw_nv) > 1
            else [st.session_state.full_name]
        )

        # ==================== TAB 1: TỔNG QUAN ====================
        with tabs[0]:
            with st.container(border=True):
                direct_logo_url = format_drive_direct_url(settings.get("Logo", ""))
                fallback_gif = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
                st.markdown(
                    f"""
                    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center;">
                        <img src="{direct_logo_url}" style="width: 85px; height: 85px; border-radius: 50%; border: 3px solid {THEME_COLORS['primary']}; object-fit: cover; margin-bottom: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);" onerror="this.onerror=null;this.src='{fallback_gif}';">
                        <div style="font-size: 22px; font-weight: 900; color: {THEME_COLORS['text_main']}; text-transform: uppercase; letter-spacing: 1px;">{settings.get('TenTiem', 'SALON KIM HIỀN')}</div>
                        <div style="font-size: 13px; color: {THEME_COLORS['text_muted']}; margin-top: 5px; text-align: center;">
                            <div>{settings.get('Diachi', '131, TRẦN BÌNH TRỌNG, LONG XUYÊN')}</div>
                            <div style="margin-top: 3px;">Hotline: {settings.get('SDT', '0947.58.1516')}</div>
                        </div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )

            with st.container(border=True):
                st.markdown(f"👋 **Xin chào, {st.session_state.full_name}!**")
                st.markdown(
                    f"<span style='color:{THEME_COLORS['text_muted']}; font-size:13px;'>Hôm nay là: {get_now_vn().strftime('%d/%m/%Y')}</span>",
                    unsafe_allow_html=True,
                )

                try:
                    bc_values, _ = get_bao_cao_va_bill_tam()
                    if len(bc_values) > 1:
                        df_bc = pd.DataFrame(bc_values[1:], columns=bc_values[0])
                        c_tien = next(
                            (
                                c
                                for c in df_bc.columns
                                if "tiền" in c.lower() or "tien" in c.lower()
                            ),
                            "Thành tiền",
                        )
                        c_ngay = next(
                            (
                                c
                                for c in df_bc.columns
                                if "ngày" in c.lower() or "ngay" in c.lower()
                            ),
                            "Ngày",
                        )
                        df_bc[c_tien] = pd.to_numeric(
                            df_bc[c_tien]
                            .astype(str)
                            .str.replace(",", "")
                            .str.replace(".", ""),
                            errors="coerce",
                        ).fillna(0)
                        df_bc["DateObj"] = pd.to_datetime(
                            df_bc[c_ngay], format="%d/%m/%Y", errors="coerce"
                        )
                        last_7_days = df_bc.dropna(subset=["DateObj"])
                        last_7_days = (
                            last_7_days.groupby("DateObj")[c_tien]
                            .sum()
                            .reset_index()
                            .tail(7)
                        )
                        last_7_days["Ngày"] = last_7_days["DateObj"].dt.strftime(
                            "%d/%m"
                        )

                        if not last_7_days.empty:
                            st.markdown(
                                f"<div style='margin-top:25px; margin-bottom:10px; font-weight:bold; font-size:15px; color:{THEME_COLORS['text_title']}; letter-spacing:0.5px;'>📉 BÁO CÁO DOANH THU 7 NGÀY QUA</div>",
                                unsafe_allow_html=True,
                            )
                            st.line_chart(
                                last_7_days.set_index("Ngày")[c_tien],
                                color=THEME_COLORS["primary"],
                            )
                except Exception:
                    pass

            with st.container(border=True):
                lh_data = get_lich_hen_data()
                if len(lh_data) > 1:
                    df_lh = pd.DataFrame(lh_data[1:], columns=lh_data[0])
                    today_str = get_now_vn().strftime("%d/%m/%Y")
                    c_ngay_lh = next(
                        (
                            c
                            for c in df_lh.columns
                            if "ngày" in c.lower() or "ngay" in c.lower()
                        ),
                        None,
                    )
                    c_gio_lh = next(
                        (
                            c
                            for c in df_lh.columns
                            if "giờ" in c.lower() or "gio" in c.lower()
                        ),
                        None,
                    )
                    c_ten_lh = next(
                        (
                            c
                            for c in df_lh.columns
                            if "tên" in c.lower() or "khách" in c.lower()
                        ),
                        None,
                    )
                    c_sdt_lh = next(
                        (
                            c
                            for c in df_lh.columns
                            if "điện thoại" in c.lower()
                            or "sđt" in c.lower()
                            or "sdt" in c.lower()
                        ),
                        None,
                    )
                    c_dv_lh = next(
                        (
                            c
                            for c in df_lh.columns
                            if "dịch" in c.lower() or "dich" in c.lower()
                        ),
                        None,
                    )
                    c_tt_lh = next(
                        (
                            c
                            for c in df_lh.columns
                            if "trạng thái" in c.lower() or "trang thai" in c.lower()
                        ),
                        None,
                    )
                    c_tho_lh = next(
                        (
                            c
                            for c in df_lh.columns
                            if "nhân viên" in c.lower() or "nhan vien" in c.lower()
                        ),
                        None,
                    )

                    if c_ngay_lh:
                        df_today_lh = df_lh[
                            df_lh[c_ngay_lh]
                            .astype(str)
                            .str.contains(today_str, na=False)
                        ]

                        # Fix Bug 2: Đếm số lượng đơn hẹn
                        so_luong_hen = len(df_today_lh)
                        st.markdown(
                            f'<div class="the-quan-ly-flat">📅 LỊCH HẸN HÔM NAY ({so_luong_hen})</div>',
                            unsafe_allow_html=True,
                        )

                        has_items = False
                        if not df_today_lh.empty:
                            for i, row in df_today_lh.iterrows():
                                idx_sheet = i + 2
                                gio = (
                                    row.get(c_gio_lh, "--:--") if c_gio_lh else "--:--"
                                )
                                khach = (
                                    row.get(c_ten_lh, "Khách") if c_ten_lh else "Khách"
                                )
                                sdt = row.get(c_sdt_lh, "") if c_sdt_lh else ""
                                dv = row.get(c_dv_lh, "") if c_dv_lh else ""
                                tt_val = (
                                    row.get(c_tt_lh, "CHỜ PHỤC VỤ")
                                    if c_tt_lh
                                    else "CHỜ PHỤC VỤ"
                                )
                                tho_yc = (
                                    row.get(c_tho_lh, "Không yêu cầu")
                                    if c_tho_lh
                                    else "Không yêu cầu"
                                )

                                if (
                                    st.session_state["role"] == "NhanVien"
                                    and tho_yc != "Không yêu cầu"
                                    and tho_yc != st.session_state.full_name
                                ):
                                    continue

                                has_items = True

                                st.markdown(
                                    f"""
                                    <div class="lich-hen-item">
                                        <div style="flex: 1;"><span style="color:#d93025; font-weight:800; font-size:16px;">{gio}</span><br><span style="font-size:13px; color:#555; font-weight:bold;">{khach} - {sdt}</span><br><span style="font-size:12px; font-weight:600; color:{THEME_COLORS['primary']};">{dv}</span></div>
                                    </div>
                                """,
                                    unsafe_allow_html=True,
                                )

                                if tt_val.strip().upper() == "ĐÃ CHỐT ĐƠN":
                                    st.markdown(
                                        f"<div style='text-align:right; font-weight:bold; font-size:14px; color:#28a745; margin-bottom:10px;'>✅ ĐÃ CHỐT ĐƠN</div>",
                                        unsafe_allow_html=True,
                                    )
                                    if st.session_state["role"] == "Admin":
                                        if st.button(
                                            "🗑️ Xóa lịch hẹn",
                                            key=f"del_lh_home_{idx_sheet}",
                                        ):
                                            try:
                                                get_google_sheet_workbook().worksheet(
                                                    "LichHen"
                                                ).delete_rows(idx_sheet)
                                                get_lich_hen_data.clear()
                                                st.toast(
                                                    "✅ Đã xóa lịch hẹn khỏi hệ thống!"
                                                )
                                                time.sleep(0.5)
                                                st.rerun()
                                            except Exception:
                                                pass
                                else:
                                    if st.button(
                                        "📝 Nạp & Lên Đơn",
                                        key=f"lh_home_{idx_sheet}",
                                        use_container_width=True,
                                    ):
                                        # Fix Bug 1: Nạp cả danh sách Dịch Vụ từ lịch hẹn vào Giỏ Hàng
                                        new_gio = []
                                        if dv:
                                            for d_v in dv.split(", "):
                                                d_v_clean = d_v.strip()
                                                if d_v_clean in services:
                                                    inf = services[d_v_clean]
                                                    new_gio.append(
                                                        {
                                                            "dich_vu": d_v_clean,
                                                            "so_luong": 1.0,
                                                            "don_gia": inf["gia"],
                                                            "thanh_tien": inf["gia"],
                                                            "phan_tram_hh": inf[
                                                                "hoa_hong"
                                                            ],
                                                        }
                                                    )

                                        st.session_state.update(
                                            {
                                                "gio_hang": new_gio,
                                                "kh_sdt_val": str(sdt),
                                                "kh_ten_val": str(khach),
                                                "tho_chot_val": (
                                                    str(tho_yc)
                                                    if tho_yc != "Không yêu cầu"
                                                    else st.session_state.full_name
                                                ),
                                                "current_lh_idx": idx_sheet,
                                            }
                                        )

                                        try:
                                            col_idx = (
                                                df_lh.columns.get_loc(c_tt_lh) + 1
                                                if c_tt_lh
                                                else 7
                                            )
                                            get_google_sheet_workbook().worksheet(
                                                "LichHen"
                                            ).update_cell(
                                                idx_sheet, col_idx, "ĐANG XỬ LÝ"
                                            )
                                            get_lich_hen_data.clear()
                                        except Exception:
                                            pass

                                        trigger_auto_save()
                                        st.toast(
                                            "✅ Đã nạp thông tin. Đang chuyển sang Tab Lên Hóa Đơn!"
                                        )
                                        time.sleep(0.3)
                                        st.query_params["tab"] = (
                                            "1"  # Búng sang Tab 2 tự động
                                        )
                                        st.rerun()
                                st.markdown(
                                    "<hr style='margin:8px 0; border:none;'>",
                                    unsafe_allow_html=True,
                                )
                        if not has_items:
                            st.info("Không có lịch hẹn nào của bạn cho hôm nay.")
                else:
                    st.markdown(
                        '<div class="the-quan-ly-flat">📅 LỊCH HẸN HÔM NAY (0)</div>',
                        unsafe_allow_html=True,
                    )
                    st.info("Dữ liệu lịch hẹn trống.")

            if st.session_state.get("bill_vua_in"):
                with st.container(border=True):
                    st.markdown(
                        '<div class="the-quan-ly-flat">🧾 HOÁ ĐƠN VỪA KHỞI TẠO</div>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(st.session_state.bill_vua_in, unsafe_allow_html=True)
                    if st.button(
                        "❌ ẨN BILL NÀY", use_container_width=True, type="primary"
                    ):
                        st.session_state.bill_vua_in = None
                        st.rerun()

        # ==================== TAB 2: LÊN HÓA ĐƠN ====================
        with tabs[1]:
            with st.container(border=True):
                st.markdown(
                    '<div class="the-quan-ly-flat">THÔNG TIN KHÁCH HÀNG</div>',
                    unsafe_allow_html=True,
                )
                c1, c2 = st.columns(2)
                with c1:
                    kh_sdt = st.text_input(
                        "Số điện thoại khách", value=st.session_state.kh_sdt_val
                    )
                    if kh_sdt != st.session_state.kh_sdt_val:
                        st.session_state.kh_sdt_val = kh_sdt
                        if kh_sdt.strip():
                            sdt_clean = kh_sdt.strip()
                            ds_kh = get_khach_hang_data()
                            s_k_0 = (
                                sdt_clean[1:]
                                if sdt_clean.startswith("0")
                                else sdt_clean
                            )
                            s_c_0 = (
                                "0" + sdt_clean
                                if not sdt_clean.startswith("0")
                                else sdt_clean
                            )

                            if sdt_clean in ds_kh:
                                st.session_state.kh_ten_val = ds_kh[sdt_clean]
                            elif s_k_0 in ds_kh:
                                st.session_state.kh_ten_val = ds_kh[s_k_0]
                            elif s_c_0 in ds_kh:
                                st.session_state.kh_ten_val = ds_kh[s_c_0]
                            else:
                                st.session_state.kh_ten_val = ""
                            trigger_auto_save()
                        else:
                            st.session_state.kh_ten_val = ""
                        st.rerun()
                with c2:
                    kh_ten = st.text_input(
                        "Tên khách hàng",
                        value=st.session_state.kh_ten_val,
                        placeholder="Khách lẻ",
                    )
                    if kh_ten != st.session_state.kh_ten_val:
                        st.session_state.kh_ten_val = kh_ten
                        trigger_auto_save()
                        st.rerun()

            with st.container(border=True):
                st.markdown(
                    '<div class="the-quan-ly-flat">DANH SÁCH DỊCH VỤ</div>',
                    unsafe_allow_html=True,
                )
                max_dv = 3 if st.session_state.get("role") == "NhanVien" else None
                pholder_text = (
                    "Chọn tối đa 3 dịch vụ..." if max_dv else "Chọn dịch vụ..."
                )

                dv_chon = st.multiselect(
                    "Chạm chọn dịch vụ...",
                    options=dv_list if dv_list else ["Đang tải..."],
                    max_selections=max_dv,
                    placeholder=pholder_text,
                    key=f"dv_{st.session_state.reset_counter}",
                )
                if st.button(
                    "➕ THÊM VÀO GIỎ HÀNG", type="primary", use_container_width=True
                ):
                    if dv_chon:
                        for dv in dv_chon:
                            info_dv = services.get(dv, {"gia": 0.0, "hoa_hong": 0.0})
                            existing = next(
                                (
                                    item
                                    for item in st.session_state.gio_hang
                                    if item["dich_vu"] == dv
                                ),
                                None,
                            )
                            if existing:
                                existing["so_luong"] += 1.0
                                existing["thanh_tien"] = (
                                    existing["so_luong"] * existing["don_gia"]
                                )
                            else:
                                st.session_state.gio_hang.append(
                                    {
                                        "dich_vu": dv,
                                        "so_luong": 1.0,
                                        "don_gia": info_dv["gia"],
                                        "thanh_tien": info_dv["gia"],
                                        "phan_tram_hh": info_dv["hoa_hong"],
                                    }
                                )
                        st.session_state.reset_counter += 1
                        trigger_auto_save()
                        st.toast("✅ Đã thêm dịch vụ! Đang tự động sao lưu...")
                        time.sleep(0.3)
                        st.rerun()

            t_bill = 0.0
            if st.session_state.gio_hang:
                with st.container(border=True):
                    st.markdown(
                        f'<div class="the-quan-ly-flat">🛒 GIỎ HÀNG ({len(st.session_state.gio_hang)} món)</div>',
                        unsafe_allow_html=True,
                    )
                    max_sl = (
                        2.0 if st.session_state.get("role") == "NhanVien" else 1000.0
                    )

                    for idx, item in enumerate(st.session_state.gio_hang):
                        c_sl, c_tt, c_del = st.columns([5, 3, 2])
                        with c_sl:
                            new_sl = st.number_input(
                                f"{item['dich_vu']}:",
                                min_value=0.5,
                                max_value=max_sl,
                                value=float(item["so_luong"]),
                                step=0.5,
                                key=f"cart_sl_{idx}",
                            )
                            if new_sl != item["so_luong"]:
                                item["so_luong"] = new_sl
                                item["thanh_tien"] = new_sl * item["don_gia"]
                                trigger_auto_save()
                                st.rerun()
                        with c_tt:
                            st.markdown(
                                f"<div style='margin-top: 30px; font-weight:800; color:{THEME_COLORS['text_main']};'>{item['thanh_tien']:,.0f}đ</div>",
                                unsafe_allow_html=True,
                            )
                        with c_del:
                            st.markdown(
                                f"<div style='margin-top: 30px;'></div>",
                                unsafe_allow_html=True,
                            )
                            if st.button(
                                "🗑️ Xoá dịch vụ",
                                key=f"del_{idx}",
                                use_container_width=True,
                            ):
                                st.session_state.gio_hang.pop(idx)
                                trigger_auto_save()
                                st.rerun()
                        t_bill += item["thanh_tien"]

                    if st.button("💾 LƯU ĐƠN VÀO BILL CHỜ", use_container_width=True):
                        if luu_bill_tam(
                            st.session_state.gio_hang,
                            st.session_state.full_name,
                            st.session_state.kh_sdt_val,
                            st.session_state.kh_ten_val,
                        ):
                            st.session_state.update(
                                {"gio_hang": [], "kh_sdt_val": "", "kh_ten_val": ""}
                            )
                            trigger_auto_save()
                            st.toast("✅ Đã đẩy đơn vào danh sách chờ thành công!")
                            time.sleep(0.5)
                            st.rerun()

            if t_bill > 0:
                with st.container(border=True):
                    st.markdown(
                        '<div class="the-quan-ly-flat">THU NGÂN & THANH TOÁN</div>',
                        unsafe_allow_html=True,
                    )

                    opts_tho = ds_tho if ds_tho else [st.session_state.full_name]
                    try:
                        default_idx = opts_tho.index(st.session_state.tho_chot_val)
                    except Exception:
                        default_idx = 0
                    chot_tho = st.selectbox(
                        "Thợ thực hiện:", options=opts_tho, index=default_idx
                    )

                    c_km1, c_km2 = st.columns(2)
                    with c_km1:
                        tien_chiet_khau = st.number_input(
                            "Chiết khấu ưu đãi (VND)", value=0.0, step=1000.0
                        )
                    with c_km2:
                        tien_khuyen_mai = st.number_input(
                            "Trừ khuyến mãi (VND)", value=0.0, step=1000.0
                        )

                    ghi_chu_don = st.text_input(
                        "Ghi chú cho đơn hàng (Hiển thị lên Bill):"
                    )

                    tong_tru = tien_chiet_khau + tien_khuyen_mai
                    t_khach_tra = max(0.0, t_bill - tong_tru)
                    kh_dua = st.number_input(
                        "Số tiền mặt khách trả", value=float(t_khach_tra)
                    )
                    t_du = kh_dua - t_khach_tra
                    hs_giam = t_khach_tra / t_bill if t_bill > 0 else 1.0

                    st.write("")
                    cb1, cb2, cb3, cb4 = st.columns(4)
                    with cb1:
                        st.markdown(
                            f'<div style="font-size: 11px; font-weight: 600; color: {THEME_COLORS["text_muted"]}; text-align: left;">Tổng bill</div><div class="box-chung">{t_bill:,.0f}</div>',
                            unsafe_allow_html=True,
                        )
                    with cb2:
                        st.markdown(
                            f'<div style="font-size: 11px; font-weight: 600; color: {THEME_COLORS["text_muted"]}; text-align: left;">Chiết khấu</div><div class="box-chung chiet-khau-box">{tien_chiet_khau:,.0f}</div>',
                            unsafe_allow_html=True,
                        )
                    with cb3:
                        st.markdown(
                            f'<div style="font-size: 11px; font-weight: 600; color: {THEME_COLORS["text_muted"]}; text-align: left;">Khuyến mãi</div><div class="box-chung chiet-khau-box">{tien_khuyen_mai:,.0f}</div>',
                            unsafe_allow_html=True,
                        )
                    with cb4:
                        st.markdown(
                            f'<div style="font-size: 11px; font-weight: 600; color: {THEME_COLORS["text_muted"]}; text-align: left;">Thực thu</div><div class="box-chung khach-tra-box">{t_khach_tra:,.0f}</div>',
                            unsafe_allow_html=True,
                        )

                    if t_du > 0:
                        st.markdown(
                            f'<div class="tien-thua-box">Tiền thối lại: <span>{t_du:,.0f} VND</span></div>',
                            unsafe_allow_html=True,
                        )

                    st.markdown(
                        f"""
                        <div style="background-color: #eaf2e6; border: 1px solid #87e8de; border-left: 5px solid #13c2c2; padding: 12px; border-radius: 10px; text-align: center; margin: 15px 0 5px 0; font-weight: 700; color: #111; font-size: 14px;">
                            👉 XÁC NHẬN SỐ TIỀN THỰC THU: <span style="color:#cf1322; font-size:35px;text-align: right;">{t_khach_tra:,.0f}đ</span><br>
                            <span style="font-weight:400; font-size:12px; color:#555;text-align: center;">(Hệ thống đang kiểm tra....)</span>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )

                    cam_ket = st.checkbox("Xác nhận đã chính xác")

                    if not st.session_state.submitting:
                        if st.button(
                            "🚀 XUẤT HÓA ĐƠN", use_container_width=True, type="primary"
                        ):
                            if cam_ket:
                                st.session_state.submitting = True
                                st.rerun()
                            else:
                                st.warning(
                                    "⚠️ Vui lòng check ô Xác nhận thông tin đơn hàng trước khi xuất!"
                                )
                    else:
                        st.button(
                            "Đang đồng bộ...", disabled=True, use_container_width=True
                        )
                        try:
                            ws = get_google_sheet_workbook().worksheet("BaoCao")
                            ma_hd = f"HD{get_now_vn().strftime('%y%m%d%H%M')}"
                            rows_to_append = []
                            chi_tiet_tele = ""
                            html_items = ""

                            c_ten = (
                                st.session_state.kh_ten_val.strip()
                                if st.session_state.kh_ten_val.strip()
                                else "Khách lẻ"
                            )
                            c_sdt = st.session_state.kh_sdt_val.strip()
                            g_chu_full = f"[CK: {tien_chiet_khau:,.0f} | KM: {tien_khuyen_mai:,.0f}] {ghi_chu_don}"

                            for item in st.session_state.gio_hang:
                                hh_dong = (
                                    item["thanh_tien"]
                                    * hs_giam
                                    * (item["phan_tram_hh"] / 100.0)
                                )
                                rows_to_append.append(
                                    [
                                        get_now_vn().strftime("%d/%m/%Y"),
                                        st.session_state.full_name,
                                        c_ten,
                                        c_sdt,
                                        item["dich_vu"],
                                        item["so_luong"],
                                        item["don_gia"],
                                        item["thanh_tien"],
                                        get_now_vn().strftime("%H:%M:%S"),
                                        g_chu_full,
                                        hh_dong,
                                        ma_hd,
                                        kh_dua,
                                        t_du,
                                        "0 phút",
                                        chot_tho,
                                    ]
                                )
                                sl_sach = (
                                    int(item["so_luong"])
                                    if float(item["so_luong"]).is_integer()
                                    else item["so_luong"]
                                )
                                html_items += f"""<tr><td style="text-align: left; border: none; padding: 6px 0;"><div style="font-weight: 600; color: #111; font-size: 14px;">{item["dich_vu"]}</div><div style="font-size: 12px; color: #666;">{sl_sach} x {item['don_gia']:,.0f}đ</div></td><td style="text-align: right; border: none; padding: 6px 0; vertical-align: middle;"><div style="font-weight: 700; color: #111; font-size: 14px;">{item["thanh_tien"]:,.0f}đ</div></td></tr>"""
                                chi_tiet_tele += f"\n- {item['dich_vu']} (x{sl_sach}): {item['thanh_tien']:,.0f}đ"

                            ws.append_rows(rows_to_append)

                            if st.session_state.get("current_lh_idx"):
                                try:
                                    get_google_sheet_workbook().worksheet(
                                        "LichHen"
                                    ).update_cell(
                                        st.session_state.current_lh_idx,
                                        7,
                                        "ĐÃ CHỐT ĐƠN",
                                    )
                                    get_lich_hen_data.clear()
                                except Exception:
                                    pass
                                st.session_state.current_lh_idx = None

                            st.session_state.update(
                                {
                                    "gio_hang": [],
                                    "kh_sdt_val": "",
                                    "kh_ten_val": "",
                                    "submitting": False,
                                }
                            )
                            trigger_auto_save()

                            nd_mail = f"THÔNG BÁO\nĐH ĐÃ THANH TOÁN ✅\n \nMã ĐH: {ma_hd} | {get_now_vn().strftime('%d/%m/%Y %H:%M')}\nKhách: {c_ten} - {c_sdt}\nThu ngân: {st.session_state.full_name}\nThợ: {chot_tho}\n \n===============\n \nChi tiết dịch vụ:{chi_tiet_tele}\n \n===============\n \nTổng bill: {t_bill:,.0f} đ\nChiết khấu: -{tien_chiet_khau:,.0f} đ\nKhuyến mãi: -{tien_khuyen_mai:,.0f} đ\n \nGHI CHÚ: {ghi_chu_don} \n \n===============\n \nTHỰC THU: {t_khach_tra:,.0f} đ\n \n===============\n \nChi tiết xin liên hệ Hotline 0947.58.1516 \nHỗ trợ 24/7.\nCảm ơn quý khách đã sử dụng dịch vụ!\n"

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
    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;"><span>Tổng tiền dịch vụ:</span> <span style="text-align: right; font-weight: 600;">{t_bill:,.0f}</span></div>
    <div style="display: flex; justify-content: space-between; color: {THEME_COLORS['accent_chiet_khau']}; margin-bottom: 8px;"><span>Chiết khấu:</span> <span style="text-align: right; font-weight: 600;">-{tien_chiet_khau:,.0f}</span></div>
    <div style="display: flex; justify-content: space-between; color: {THEME_COLORS['accent_chiet_khau']}; margin-bottom: 8px;"><span>Khuyến mãi:</span> <span style="text-align: right; font-weight: 600;">-{tien_khuyen_mai:,.0f}</span></div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;"><span>Tiền khách đưa:</span> <span style="text-align: right; font-weight: 600;">{kh_dua:,.0f}</span></div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;"><span>Tiền thối lại:</span> <span style="text-align: right; font-weight: 600;">{t_du:,.0f}</span></div>
</div>
<div style="font-size: 13px; font-weight: 600; color: {THEME_COLORS['text_secondary']}; text-align: left; margin-bottom: 8px; border-bottom: 1px dashed {THEME_COLORS['border_light']}; padding-bottom: 5px;">Số tiền cần thanh toán cuối cùng:</div>
<div style="display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 18px; font-weight: 900; color: {THEME_COLORS['text_main']};"><span>TỔNG CỘNG:</span> <span style="text-align: right; color: {THEME_COLORS['accent_chiet_khau']};">{t_khach_tra:,.0f}</span></div>
<div style="text-align: left; margin-top: 15px; font-size: 13px; font-weight: 600; color: #444;">Ghi Chú: {ghi_chu_don}</div>
<div style="font-size: 13px; font-weight: 600; color: {THEME_COLORS['text_secondary']}; text-align: left; margin-bottom: 8px; border-bottom: 1px dashed {THEME_COLORS['border_light']}; padding-bottom: 5px;"></div>
<div style="text-align: left; margin-top: 15px; font-size: 13px; color: {THEME_COLORS['text_muted']}; font-style: italic;">Mọi chi tiết xin liên hệ:</div>
<div style="text-align: left; margin-top: 15px; font-size: 13px; color: {THEME_COLORS['text_muted']}; font-style: italic;">Salon: KIM HIỀN.</div>
<div style="text-align: left; margin-top: 15px; font-size: 13px; color: {THEME_COLORS['text_muted']}; font-style: italic;">Hotline: 0947.58.1516.</div>
<div style="text-align: left; margin-top: 15px; font-size: 13px; color: {THEME_COLORS['text_muted']}; font-style: italic;">Facebook: Kim Hiền Tóc.</div>
<div style="text-align: left; margin-top: 15px; font-size: 13px; color: {THEME_COLORS['text_muted']}; font-style: italic;">Zalo: 0947.58.1516 - Kim Hiền Tóc.</div>
<div style="text-align: left; margin-top: 15px; font-size: 13px; color: {THEME_COLORS['text_muted']}; font-style: italic;">Đc: 131 Trần Bình Trọng, Mỹ Xuyên, Long Xuyên, AG (Cũ).</div>
<div style="text-align: left; margin-top: 15px; font-size: 13px; color: {THEME_COLORS['text_muted']}; font-style: italic;">Dịch vụ thêm: Có nhận Make-up tiệc tại nhà.</div>
<div style="font-size: 13px; font-weight: 600; color: {THEME_COLORS['text_secondary']}; text-align: left; margin-bottom: 8px; border-bottom: 1px dashed {THEME_COLORS['border_light']}; padding-bottom: 5px;"></div>
<div style="text-align: center; margin-top: 15px; font-size: 13px; color: {THEME_COLORS['text_muted']}; font-style: italic;">Cảm ơn quý khách đã sử dụng dịch vụ!</div>
</div>"""
                            st.balloons()
                            st.toast("✅ Đã xuất hóa đơn thành công!")
                            time.sleep(1.5)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Lỗi hệ thống: {e}")
                            st.session_state.submitting = False

        # ==================== TAB 3: LỊCH HẸN & CHỨC NĂNG LÊN ĐƠN KHÁCH HẸN ====================
        with tabs[2]:
            with st.container(border=True):
                st.markdown(
                    '<div class="the-quan-ly-flat">📅 TẠO LỊCH HẸN MỚI</div>',
                    unsafe_allow_html=True,
                )

                c_hen1, c_hen2 = st.columns(2)
                with c_hen2:
                    hen_sdt = st.text_input(
                        "Số điện thoại (Hẹn)", value=st.session_state.lh_sdt_val
                    )
                    if hen_sdt != st.session_state.lh_sdt_val:
                        st.session_state.lh_sdt_val = hen_sdt
                        if hen_sdt.strip():
                            sdt_clean = hen_sdt.strip()
                            ds_kh = get_khach_hang_data()
                            s_k_0 = (
                                sdt_clean[1:]
                                if sdt_clean.startswith("0")
                                else sdt_clean
                            )
                            s_c_0 = (
                                "0" + sdt_clean
                                if not sdt_clean.startswith("0")
                                else sdt_clean
                            )
                            if sdt_clean in ds_kh:
                                st.session_state.lh_ten_val = ds_kh[sdt_clean]
                            elif s_k_0 in ds_kh:
                                st.session_state.lh_ten_val = ds_kh[s_k_0]
                            elif s_c_0 in ds_kh:
                                st.session_state.lh_ten_val = ds_kh[s_c_0]
                            else:
                                st.session_state.lh_ten_val = ""
                        else:
                            st.session_state.lh_ten_val = ""
                        st.rerun()
                    hen_gio = st.time_input("Giờ hẹn", value=get_now_vn().time())
                with c_hen1:
                    hen_ngay = st.date_input("Ngày hẹn", value=get_now_vn().date())
                    hen_ten = st.text_input(
                        "Tên khách hàng (Hẹn)", value=st.session_state.lh_ten_val
                    )
                    if hen_ten != st.session_state.lh_ten_val:
                        st.session_state.lh_ten_val = hen_ten
                        st.rerun()

                hen_dv = st.multiselect(
                    "Dịch vụ quan tâm", options=dv_list if dv_list else ["Đang tải..."]
                )
                hen_tho = st.selectbox(
                    "Thợ yêu cầu (nếu có)",
                    options=(
                        ["Không yêu cầu"] + ds_tho
                        if ds_tho
                        else ["Không yêu cầu", st.session_state.full_name]
                    ),
                )
                hen_ghi_chu = st.text_area(
                    "Ghi chú thêm (Tình trạng tóc/yêu cầu riêng)"
                )

                if st.button(
                    "💾 LƯU LỊCH HẸN", use_container_width=True, type="primary"
                ):
                    if hen_ten and hen_sdt:
                        try:
                            ws_hen = get_google_sheet_workbook().worksheet("LichHen")
                            ws_hen.append_row(
                                [
                                    str(hen_ngay.strftime("%d/%m/%Y")),
                                    str(hen_gio.strftime("%H:%M")),
                                    hen_ten,
                                    hen_sdt,
                                    ", ".join(hen_dv),
                                    hen_tho,
                                    "CHỜ PHỤC VỤ",
                                    hen_ghi_chu,
                                ]
                            )
                            get_lich_hen_data.clear()
                            st.session_state.lh_sdt_val = ""
                            st.session_state.lh_ten_val = ""
                            st.toast("✅ Đã lưu lịch hẹn thành công!")
                            time.sleep(0.5)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Lỗi khi lưu lịch hẹn: {e}")
                    else:
                        st.warning("Vui lòng nhập Tên và Số điện thoại khách hàng.")

            with st.container(border=True):
                st.markdown(
                    '<div class="the-quan-ly-flat">📋 ĐIỀU PHỐI LỊCH HẸN</div>',
                    unsafe_allow_html=True,
                )
                lh_records = get_lich_hen_data()
                if len(lh_records) > 1:
                    df_lh_full = pd.DataFrame(lh_records[1:], columns=lh_records[0])
                    c_ngay_lh = next(
                        (
                            c
                            for c in df_lh_full.columns
                            if "ngày" in c.lower() or "ngay" in c.lower()
                        ),
                        None,
                    )
                    c_gio_lh = next(
                        (
                            c
                            for c in df_lh_full.columns
                            if "giờ" in c.lower() or "gio" in c.lower()
                        ),
                        None,
                    )
                    c_ten_lh = next(
                        (
                            c
                            for c in df_lh_full.columns
                            if "tên" in c.lower() or "khách" in c.lower()
                        ),
                        None,
                    )
                    c_sdt_lh = next(
                        (
                            c
                            for c in df_lh_full.columns
                            if "điện thoại" in c.lower()
                            or "sđt" in c.lower()
                            or "sdt" in c.lower()
                        ),
                        None,
                    )
                    c_dv_lh = next(
                        (
                            c
                            for c in df_lh_full.columns
                            if "dịch" in c.lower() or "dich" in c.lower()
                        ),
                        None,
                    )
                    c_tt_lh = next(
                        (
                            c
                            for c in df_lh_full.columns
                            if "trạng thái" in c.lower() or "trang thai" in c.lower()
                        ),
                        None,
                    )
                    c_tho_lh = next(
                        (
                            c
                            for c in df_lh_full.columns
                            if "nhân viên" in c.lower() or "nhan vien" in c.lower()
                        ),
                        None,
                    )

                    if c_ngay_lh:
                        df_lh_hien_thi = df_lh_full.tail(15)
                        has_items = False

                        for i, row in df_lh_hien_thi.iterrows():
                            idx_sheet = i + 2
                            gio = row.get(c_gio_lh, "--:--") if c_gio_lh else "--:--"
                            khach = row.get(c_ten_lh, "Khách") if c_ten_lh else "Khách"
                            sdt = row.get(c_sdt_lh, "") if c_sdt_lh else ""
                            dv = row.get(c_dv_lh, "") if c_dv_lh else ""
                            ngay = row.get(c_ngay_lh, "")
                            tt_val = (
                                row.get(c_tt_lh, "CHỜ PHỤC VỤ")
                                if c_tt_lh
                                else "CHỜ PHỤC VỤ"
                            )
                            tho_yc = (
                                row.get(c_tho_lh, "Không yêu cầu")
                                if c_tho_lh
                                else "Không yêu cầu"
                            )

                            if (
                                st.session_state["role"] == "NhanVien"
                                and tho_yc != "Không yêu cầu"
                                and tho_yc != st.session_state.full_name
                            ):
                                continue

                            has_items = True

                            c_info, c_btn = st.columns([7, 3])
                            with c_info:
                                st.markdown(
                                    f"**{ngay} {gio}** | 👤 {khach} ({sdt})<br>✂️ {dv}",
                                    unsafe_allow_html=True,
                                )
                            with c_btn:
                                if tt_val.strip().upper() == "ĐÃ CHỐT ĐƠN":
                                    st.markdown(
                                        f"<div style='text-align:right; font-weight:bold; font-size:14px; color:#28a745; margin-top:10px;'>✅ ĐÃ CHỐT ĐƠN</div>",
                                        unsafe_allow_html=True,
                                    )
                                    if st.session_state["role"] == "Admin":
                                        if st.button(
                                            "🗑️ Xóa lịch",
                                            key=f"del_lh_tab3_{idx_sheet}",
                                        ):
                                            try:
                                                get_google_sheet_workbook().worksheet(
                                                    "LichHen"
                                                ).delete_rows(idx_sheet)
                                                get_lich_hen_data.clear()
                                                st.toast(
                                                    "✅ Đã xóa lịch hẹn khỏi hệ thống!"
                                                )
                                                time.sleep(0.5)
                                                st.rerun()
                                            except Exception:
                                                pass
                                else:
                                    if st.button(
                                        "📝 Lên Đơn",
                                        key=f"lh_tab3_{idx_sheet}",
                                        use_container_width=True,
                                    ):
                                        new_gio = []
                                        if dv:
                                            for d_v in dv.split(", "):
                                                d_v_clean = d_v.strip()
                                                if d_v_clean in services:
                                                    inf = services[d_v_clean]
                                                    new_gio.append(
                                                        {
                                                            "dich_vu": d_v_clean,
                                                            "so_luong": 1.0,
                                                            "don_gia": inf["gia"],
                                                            "thanh_tien": inf["gia"],
                                                            "phan_tram_hh": inf[
                                                                "hoa_hong"
                                                            ],
                                                        }
                                                    )

                                        st.session_state.update(
                                            {
                                                "gio_hang": new_gio,
                                                "kh_sdt_val": sdt,
                                                "kh_ten_val": khach,
                                                "tho_chot_val": (
                                                    tho_yc
                                                    if tho_yc != "Không yêu cầu"
                                                    else st.session_state.full_name
                                                ),
                                                "current_lh_idx": idx_sheet,
                                            }
                                        )

                                        try:
                                            col_idx = (
                                                df_lh_full.columns.get_loc(c_tt_lh) + 1
                                                if c_tt_lh
                                                else 7
                                            )
                                            get_google_sheet_workbook().worksheet(
                                                "LichHen"
                                            ).update_cell(
                                                idx_sheet, col_idx, "ĐANG XỬ LÝ"
                                            )
                                            get_lich_hen_data.clear()
                                        except Exception:
                                            pass

                                        trigger_auto_save()
                                        st.toast(
                                            "⚡ Chuyển dữ liệu lịch hẹn ra giỏ hàng thành công!"
                                        )
                                        time.sleep(0.3)
                                        st.query_params["tab"] = (
                                            "1"  # Búng tự động qua Tab 2
                                        )
                                        st.rerun()
                            st.markdown(
                                "<hr style='margin: 5px 0;'>", unsafe_allow_html=True
                            )
                        if not has_items:
                            st.info("Hiện tại chưa có danh sách lịch hẹn nào.")
                else:
                    st.info("Hiện tại chưa có dữ liệu danh sách lịch hẹn.")

        # ==================== TAB 4: BÁO CÁO ====================
        with tabs[3]:
            if st.session_state["role"] == "Admin":
                with st.container(border=True):

                    # --- KHU VỰC ĐẾM KIỂM SOÁT ĐƠN CHO ADMIN ---
    if st.session_state.get("role") == "Admin":
        total_today = count_orders_today()
        st.markdown(
            f"""
            <div class="box-chung" style="background-color: {THEME_COLORS['bg_vip_box']}; border-left: 6px solid {THEME_COLORS['primary']}; padding: 15px; margin-bottom: 20px; text-align: left; font-size: 15px;">
                📊 <span style="color: {THEME_COLORS['text_title']}; font-weight: 700;">HỆ THỐNG KIỂM SOÁT ĐƠN:</span> 
                Hôm nay hệ thống tiệm đã chốt thành công <span style="color: {THEME_COLORS['accent_danger']}; font-size: 24px; font-weight: 800;">{total_today}</span> đơn hàng dịch vụ.
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.session_state.get("role") == "Admin":
                with st.container(border=True):
                    st.markdown(
                        f'<div class="the-quan-ly-flat" style="color:{THEME_COLORS["accent_danger"]}; border-bottom: 2px solid {THEME_COLORS["accent_danger"]}; padding-bottom: 8px;">🛠️ ĐIỀU HÀNH TỐI CAO ADMIN</div>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(f"<p style='color:{THEME_COLORS['text_main']}; font-weight:600; font-size:14px;'>Múi giờ hệ thống đang nhận diện: <span style='color:{THEME_COLORS['primary']};'>{THEME_MODE_LABEL}</span></p>", unsafe_allow_html=True)
                    st.error("⚠️ LƯU Ý NGUY HIỂM: Nút bấm dưới đây sẽ quét và dọn sạch TOÀN BỘ danh sách lịch hẹn cùng toàn bộ báo cáo đơn hàng đã chốt trên Google Sheets gốc của hệ thống!")
                    
                    if st.button("🔥 KÍCH HOẠT XOÁ TỔNG LỊCH HẸN & KẾT QUẢ ĐÃ CHỐT", type="primary", use_container_width=True):
                        with st.spinner("Đang thực hiện lệnh xoá tổng dữ liệu và dọn dẹp bộ nhớ đệm..."):
                            if admin_clear_all_data():
                                st.toast("✅ Đã xoá sạch toàn bộ lịch hẹn và kết quả chốt trên hệ thống thành công!", icon="✅")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Lỗi! Không thể ghi hoặc xoá dữ liệu trên Google Sheets.")

                    st.write("") # Dãn khoảng cách

    st.markdown(
        '<div class="the-quan-ly-flat">📊 THỐNG KÊ DOANH THU CHUNG</div>',
        unsafe_allow_html=True,
    )
                    st.markdown(
                        '<div style="color:#2c3e50; font-weight:800; font-size:18px; margin-top:10px; margin-bottom:15px; border-bottom:2px solid #6FA8DC; padding-bottom:8px; text-transform:uppercase;">📈 THỐNG KÊ DOANH THU CHUNG</div>',
                        unsafe_allow_html=True,
                    )

                    try:
                        data_bc, data_tam = get_bao_cao_va_bill_tam()
                        if len(data_bc) > 1:
                            df_bc = pd.DataFrame(data_bc[1:], columns=data_bc[0])
                            c_tien = next(
                                (
                                    c
                                    for c in df_bc.columns
                                    if "tiền" in c.lower() or "tien" in c.lower()
                                ),
                                "Thành tiền",
                            )
                            c_ngay = next(
                                (
                                    c
                                    for c in df_bc.columns
                                    if "ngày" in c.lower() or "ngay" in c.lower()
                                ),
                                "Ngày",
                            )
                            c_ma = next(
                                (
                                    c
                                    for c in df_bc.columns
                                    if "mã" in c.lower() or "hd" in c.lower()
                                ),
                                None,
                            )

                            df_bc[c_tien] = pd.to_numeric(
                                df_bc[c_tien]
                                .astype(str)
                                .str.replace(",", "")
                                .str.replace(".", ""),
                                errors="coerce",
                            ).fillna(0)
                            today_str = get_now_vn().strftime("%d/%m/%Y")
                            month_str = get_now_vn().strftime("%m/%Y")

                            df_bc[c_ngay] = df_bc[c_ngay].astype(str).str.strip()
                            df_today = (
                                df_bc[df_bc[c_ngay] == today_str]
                                if c_ngay in df_bc.columns
                                else pd.DataFrame()
                            )
                            df_month = (
                                df_bc[df_bc[c_ngay].str.contains(month_str, na=False)]
                                if c_ngay in df_bc.columns
                                else pd.DataFrame()
                            )

                            doanh_thu_ngay = (
                                df_today[c_tien].sum() if not df_today.empty else 0
                            )
                            doanh_thu_thang = (
                                df_month[c_tien].sum() if not df_month.empty else 0
                            )
                            khach_hom_nay = (
                                len(
                                    [
                                        x
                                        for x in df_today[c_ma].unique()
                                        if str(x).strip()
                                    ]
                                )
                                if c_ma and not df_today.empty
                                else 0
                            )
                            bill_cho = max(0, len(data_tam) - 1)
                            tb_don = (
                                doanh_thu_ngay / khach_hom_nay
                                if khach_hom_nay > 0
                                else 0
                            )

                            m1, m2, m3, m4, m5 = st.columns(5)
                            m1.metric(
                                "💰 TỔNG DOANH THU HÔM NAY", f"{doanh_thu_ngay:,.0f}đ"
                            )
                            m2.metric(
                                "💳 TỔNG DOANH THU TRONG THÁNG",
                                f"{doanh_thu_thang:,.0f}đ",
                            )
                            m3.metric("📈 DOANH THU TRUNG BÌNH", f"{tb_don:,.0f}đ")
                            m4.metric(
                                "👥 KHÁCH ĐÃ PHỤC VỤ HÔM NAY", f"{khach_hom_nay} Khách"
                            )
                            m5.metric("⏳ TỔNG ĐƠN CHỜ HIỆN TẠI", f"{bill_cho} Bill")

                            st.markdown(
                                '<div style="color:#2c3e50; font-weight:800; font-size:18px; margin-top:35px; margin-bottom:15px; border-bottom:2px solid #6FA8DC; padding-bottom:8px; text-transform:uppercase;">🏆 KPI THỢ HÔM NAY</div>',
                                unsafe_allow_html=True,
                            )
                            if not df_today.empty:
                                if "Thợ phụ trách" in df_today.columns:
                                    col_tho_name = "Thợ phụ trách"
                                else:
                                    col_tho_name = next(
                                        (
                                            c
                                            for c in df_today.columns
                                            if (
                                                "thợ" in c.lower()
                                                or "tho" in c.lower()
                                                or "thực hiện" in c.lower()
                                            )
                                            and "tiền" not in c.lower()
                                        ),
                                        None,
                                    )

                                if col_tho_name:
                                    kpi_df = (
                                        df_today.groupby(col_tho_name)[c_tien]
                                        .sum()
                                        .reset_index()
                                    )
                                    kpi_df.columns = ["Tên thợ", "Doanh thu tạo ra"]
                                    kpi_df = kpi_df.sort_values(
                                        by="Doanh thu tạo ra", ascending=False
                                    )
                                    kpi_df["Doanh thu tạo ra"] = kpi_df[
                                        "Doanh thu tạo ra"
                                    ].apply(lambda x: f"{x:,.0f} đ")
                                    st.dataframe(
                                        kpi_df,
                                        use_container_width=True,
                                        hide_index=True,
                                    )
                                else:
                                    st.warning(
                                        "Hệ thống chưa dò thấy cột thông tin Thợ Thực Hiện trong dữ liệu sheet BaoCao."
                                    )
                            else:
                                st.info(
                                    "Hôm nay chưa ghi nhận dữ liệu giao dịch hoàn thành để tính KPI."
                                )

                            st.markdown(
                                '<div style="color:#2c3e50; font-weight:800; font-size:18px; margin-top:35px; margin-bottom:15px; border-bottom:2px solid #6FA8DC; padding-bottom:8px; text-transform:uppercase;">📍 TRẠNG THÁI NHÂN VIÊN TRỰC TUYẾN</div>',
                                unsafe_allow_html=True,
                            )
                            nv_status = []
                            current_time = time.time()
                            global_tracker = get_global_user_tracker()

                            for nv in ds_tho:
                                if nv in global_tracker and (
                                    current_time - global_tracker[nv] < 900
                                ):
                                    status = "🟢 Đang làm việc (Online)"
                                elif nv == st.session_state.full_name:
                                    status = "🟢 Đang làm việc (Online)"
                                else:
                                    status = "🔴 Offline"
                                nv_status.append(
                                    {"Tên nhân viên": nv, "Trạng thái hệ thống": status}
                                )
                            st.dataframe(
                                pd.DataFrame(nv_status),
                                use_container_width=True,
                                hide_index=True,
                            )

                            st.markdown(
                                '<div style="color:#2c3e50; font-weight:800; font-size:18px; margin-top:35px; margin-bottom:15px; border-bottom:2px solid #6FA8DC; padding-bottom:8px; text-transform:uppercase;">🧾 DỮ LIỆU TỔNG HỢP CHI TIẾT</div>',
                                unsafe_allow_html=True,
                            )
                            c_btn1, c_btn2 = st.columns(2)
                            with c_btn1:
                                if st.button(
                                    "⏰ Cập nhật dữ liệu", use_container_width=True
                                ):
                                    get_bao_cao_va_bill_tam.clear()
                                    st.rerun()
                            with c_btn2:
                                csv_data = convert_df_to_csv(df_bc)
                                st.download_button(
                                    "📥 Xuất File Excel (CSV)",
                                    data=csv_data,
                                    file_name=f"DoanhThu_{get_now_vn().strftime('%Y%m%d')}.csv",
                                    mime="text/csv",
                                    use_container_width=True,
                                    type="primary",
                                )
                            st.dataframe(df_bc, use_container_width=True)
                        else:
                            st.info("Chưa có dữ liệu báo cáo.")
                            if st.button(
                                "⏰ Cập nhật dữ liệu", use_container_width=True
                            ):
                                get_bao_cao_va_bill_tam.clear()
                                st.rerun()

                    except Exception as e:
                        st.error(f"Lỗi tải dữ liệu báo cáo: {e}")
            else:
                st.warning("🔒 Chức năng này chỉ dành cho tài khoản có quyền Quản lý.")

        # ==================== TAB 5: QUẢN TRỊ & MỞ RỘNG ====================
        with tabs[4]:
            if st.session_state["role"] == "Admin":
                with st.container(border=True):
                    st.markdown(
                        '<div style="color:#2c3e50; font-weight:800; font-size:18px; margin-top:10px; margin-bottom:15px; border-bottom:2px solid #6FA8DC; padding-bottom:8px; text-transform:uppercase;">QUẢN LÝ DANH SÁCH BILL CHỜ</div>',
                        unsafe_allow_html=True,
                    )
                    if st.button(
                        "🔄 Làm mới dữ liệu bill chờ", use_container_width=True
                    ):
                        get_bao_cao_va_bill_tam.clear()
                        st.rerun()

                    st.write("")
                    try:
                        _, data_tam = get_bao_cao_va_bill_tam()
                        if len(data_tam) > 1:
                            rows_tam = data_tam[1:]
                            has_pending = False
                            for i, row in enumerate(rows_tam):
                                sheet_row_idx = i + 2
                                cleaned = [str(c).strip() for c in row]
                                valid = [
                                    idx for idx, c in enumerate(cleaned) if c != ""
                                ]
                                if not valid:
                                    continue
                                real_data = cleaned[valid[0] :]

                                if len(real_data) >= 7 and real_data[6] == "CHỜ XỬ LÝ":
                                    has_pending = True
                                    t_tao_str = (
                                        real_data[0] if len(real_data) > 0 else ""
                                    )
                                    chi_tiet_dv = (
                                        real_data[1] if len(real_data) > 1 else ""
                                    )
                                    t_tien_str = (
                                        real_data[2] if len(real_data) > 2 else "0"
                                    )
                                    tho_lam = (
                                        real_data[3]
                                        if len(real_data) > 3
                                        else "Chưa rõ"
                                    )
                                    sdt_kh = real_data[4] if len(real_data) > 4 else ""
                                    ten_kh = (
                                        real_data[5]
                                        if len(real_data) > 5
                                        else "Khách lẻ"
                                    )

                                    with st.container(border=True):
                                        col_info, col_act = st.columns([7, 3])
                                        with col_info:
                                            st.markdown(
                                                f"👤 **Khách:** {ten_kh} ({sdt_kh})"
                                            )
                                            st.markdown(
                                                f"🛠 **Chi tiết:** `{chi_tiet_dv}`"
                                            )
                                            try:
                                                st.markdown(
                                                    f"💰 **Tạm tính:** `{float(t_tien_str.replace(',','').replace('.','')):,.0f}đ` | 🤝 **Thợ:** {tho_lam}"
                                                )
                                            except Exception:
                                                st.markdown(
                                                    f"💰 **Tạm tính:** `{t_tien_str}đ` | 🤝 **Thợ:** {tho_lam}"
                                                )
                                        with col_act:
                                            st.write("")
                                            if st.button(
                                                "🛒 Nạp ra giỏ",
                                                key=f"load_{sheet_row_idx}",
                                                use_container_width=True,
                                                type="primary",
                                            ):
                                                with st.spinner("Đang nạp..."):
                                                    new_gio = []
                                                    for item in chi_tiet_dv.split(
                                                        " | "
                                                    ):
                                                        if item.strip():
                                                            match = re.match(
                                                                r"(.+)\s*\(x([\d\.]+)\)",
                                                                item.strip(),
                                                            )
                                                            if match:
                                                                t_dv, s_l = match.group(
                                                                    1
                                                                ).strip(), float(
                                                                    match.group(2)
                                                                )
                                                                info = services.get(
                                                                    t_dv,
                                                                    {
                                                                        "gia": 0.0,
                                                                        "hoa_hong": 0.0,
                                                                    },
                                                                )
                                                                new_gio.append(
                                                                    {
                                                                        "dich_vu": t_dv,
                                                                        "so_luong": s_l,
                                                                        "don_gia": info.get(
                                                                            "gia", 0.0
                                                                        ),
                                                                        "thanh_tien": info.get(
                                                                            "gia", 0.0
                                                                        )
                                                                        * s_l,
                                                                        "phan_tram_hh": info.get(
                                                                            "hoa_hong",
                                                                            0.0,
                                                                        ),
                                                                    }
                                                                )

                                                    st.session_state.update(
                                                        {
                                                            "gio_hang": new_gio,
                                                            "kh_sdt_val": sdt_kh,
                                                            "kh_ten_val": ten_kh,
                                                            "tho_chot_val": tho_lam,
                                                            "bill_vua_in": None,
                                                        }
                                                    )

                                                    if xoa_bill_tam_dong_goc(
                                                        sheet_row_idx
                                                    ):
                                                        st.toast(
                                                            "⚡ Đã nạp đơn chờ vào giỏ hàng thành công!"
                                                        )
                                                        time.sleep(0.3)
                                                        st.query_params["tab"] = "1"
                                                        st.rerun()
                            if not has_pending:
                                st.info("Không có đơn chờ duyệt nào hiện tại.")
                        else:
                            st.info("Không có đơn chờ duyệt nào hiện tại.")
                    except Exception as e:
                        st.error(f"Lỗi đọc đơn chờ: {e}")

                st.markdown(
                    "<div style='margin-top: 25px;'></div>", unsafe_allow_html=True
                )
                with st.container(border=True):
                    st.markdown(
                        '<div class="the-quan-ly-flat">🧪 PHÒNG NGHIÊN CỨU MÀU TÓC</div>',
                        unsafe_allow_html=True,
                    )
                    c_lab1, c_lab2 = st.columns(2)
                    with c_lab1:
                        mau_nhuom = st.selectbox(
                            "Màu bạn muốn nhuộm:",
                            [
                                "Vàng Đồng (8.43)",
                                "Nâu Lạnh (6.1)",
                                "Khói Xám (8.11)",
                                "Tự phối màu",
                            ],
                        )
                    with c_lab2:
                        nen_toc = st.selectbox(
                            "Nền tóc hiện tại:",
                            [
                                "Level 3 (Đen tự nhiên)",
                                "Level 5 (Nâu sáng)",
                                "Level 7 (Vàng sậm)",
                                "Level 9 (Tẩy sáng)",
                            ],
                        )

                    if st.button(
                        "⚗️ THỬ NGHIỆM CÔNG THỨC & TỶ LỆ",
                        type="primary",
                        use_container_width=True,
                    ):
                        st.markdown(
                            f"<div style='margin: 15px 0; border-bottom: 2px dashed {THEME_COLORS['primary']};'></div>",
                            unsafe_allow_html=True,
                        )

                        cong_thuc_data = []
                        loi_khuyen = ""
                        diem_so = "9.0/10"
                        if "Vàng Đồng" in mau_nhuom:
                            cong_thuc_data = [
                                ["Màu chủ đạo 8.43", 70.0],
                                ["Màu mix đồng 0.43", 20.0],
                                ["Màu mix tự nhiên 0.00", 10.0],
                                ["Oxy 9%", 100.0],
                            ]
                            loi_khuyen = "Phù hợp da trắng. Chải thuốc thân và ngọn, chải cách chân tóc 2cm. Chờ 30 phút rồi chải tiếp phần chân tóc."
                            diem_so = "9.2/10"
                        elif "Nâu Lạnh" in mau_nhuom:
                            cong_thuc_data = [
                                ["Màu chủ đạo 6.1", 80.0],
                                ["Màu mix tro 0.11", 15.0],
                                ["Màu mix xanh rêu 0.22 (khử đỏ)", 5.0],
                                ["Oxy 6%", 100.0],
                            ]
                            loi_khuyen = "Màu tệp vào tóc lâu phai. Nếu nền tóc cũ của khách có ánh đỏ/cam nhiều, cân nhắc tăng 0.22 lên 10% để triệt đỏ."
                            diem_so = "9.5/10"
                        elif "Khói Xám" in mau_nhuom:
                            cong_thuc_data = [
                                ["Màu chủ đạo 8.11", 70.0],
                                ["Màu mix tro 0.11", 20.0],
                                ["Màu mix tím 0.66 (khử vàng)", 10.0],
                                ["Oxy 3%", 100.0],
                            ]
                            loi_khuyen = "BẮT BUỘC: Nền tóc phải ở Level 9+. Dùng Oxy thấp (3% hoặc 6%) để hạt màu khói ngậm sâu vào biểu bì, tránh tuột màu nhanh."
                            diem_so = "8.8/10"
                        else:
                            cong_thuc_data = [
                                ["Màu chủ đạo", 80.0],
                                ["Màu mix", 20.0],
                                ["Oxy tùy chọn", 100.0],
                            ]
                            loi_khuyen = "Theo dõi sát biểu bì tóc để xả nước kịp thời."
                            diem_so = "8.5/10"

                        st.markdown(
                            f"<h4 style='color:{THEME_COLORS['text_title']};'>1. Bảng công thức hoàn chỉnh (Tỷ lệ %)</h4>",
                            unsafe_allow_html=True,
                        )
                        st.dataframe(
                            pd.DataFrame(
                                cong_thuc_data,
                                columns=[
                                    "Thành phần (Thuốc + Trợ nhuộm)",
                                    "Tỷ lệ % (Gam/ML)",
                                ],
                            ),
                            use_container_width=True,
                            hide_index=True,
                        )

                        st.markdown(
                            f"<h4 style='color:{THEME_COLORS['text_title']}; margin-top: 15px;'>2. Quy trình pha chế / bôi thuốc chuẩn</h4>",
                            unsafe_allow_html=True,
                        )
                        st.markdown(f"""
                        * **Bước 1:** Chuẩn bị bát nhựa sạch, dùng cân tiểu ly điện tử đong chính xác các thành phần theo bảng tỷ lệ %.
                        * **Bước 2:** Đánh hỗn hợp thuốc nhuộm và Oxy thật đều tay cho đến khi dung dịch nhuyễn mịn hoàn toàn.
                        * **Bước 3:** Chia tóc làm 4 phần đồng đều. Tiến hành chải thuốc lên thân và ngọn tóc một cách đồng đều.
                        * **Bước 4:** Để thời gian lưu thuốc ổn định trên tóc từ 35-45 phút tùy thuộc vào độ thẩm thấu của sợi tóc.
                        """)

                        st.markdown(
                            f"<h4 style='color:{THEME_COLORS['text_title']}; margin-top: 15px;'>3. Đánh giá chuyên gia chuyên môn</h4>",
                            unsafe_allow_html=True,
                        )
                        st.info(
                            f"🏆 **Điểm số chất lượng công thức nhuộm:** {diem_so} điểm."
                        )

                        st.markdown(
                            f"<h4 style='color:{THEME_COLORS['text_title']}; margin-top: 15px;'>4. Hướng dẫn thao tác / Hướng dẫn sử dụng</h4>",
                            unsafe_allow_html=True,
                        )
                        st.markdown(f"""
                        * **Chuẩn bị trước khi thao tác:** Đeo găng tay bạt bảo hộ đầy đủ cho thợ và áo choàng bảo vệ cho khách hàng. Thoa một lớp mỏng Vaseline quanh các viền chân tóc (trán, mang tai, sau gáy) để ngăn thuốc nhuộm dính bám vào da.
                        * **Kỹ thuật vào thuốc:** Chia toàn bộ tóc thành các tép nhỏ từ 1-2cm. Đi cọ dứt khoát, trải đều thuốc từ thân đến ngọn hoặc cách chân tùy thuộc vào nền tóc thực tế. Chú ý bôi thuốc đẫm, tránh đọng thuốc cục bộ dễ gây loang lổ.
                        * **Xả tóc & Khóa màu:** Theo dõi độ lên màu liên tục, khi đạt thời gian lưu thuốc chuẩn (35-45 phút), tiến hành xả sạch hoàn toàn bằng nước ấm cho đến khi nước trong. Sử dụng dầu xả hoặc dầu hấp chuyên dụng khử kiềm để đóng chặt biểu bì tóc, khóa hạt màu lâu phai và tạo độ bóng mượt.
                        """)


if __name__ == "__main__":
    main()
