import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import pytz
import time
import re

# =====================================================================
# 1. CẤU HÌNH GIAO DIỆN & STYLE CSS THỜI TRANG HIGH-END (LUXURY FLAT)
# =====================================================================
st.set_page_config(
    page_title="LKTV DETAILING - PREMIUM", 
    layout="centered", 
    page_icon="✂️",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
        /* -----------------------------------------------------------------
            1. ĐỒNG BỘ FONT CHỮ & NỀN TẢNG HỆ THỐNG
        ----------------------------------------------------------------- */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght=300;400;500;600;700;800;900&display=swap');

        html, body, [class*="css"], .stApp, div, span, p, h1, h2, h3, h4, h5, h6, input, button, select, textarea {
            font-family: 'Inter', '-apple-system', BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
        }

        .stApp {
            padding-top: 75px !important; 
            padding-bottom: 60px !important;
            background-color: #f8f9fa !important;
        }

        /* -----------------------------------------------------------------
            2. HỆ THỐNG HIỆU ỨNG KHỐI HỘP TÍNH TIỀN & CHỈ DẪN FLAT PREMIUM
        ----------------------------------------------------------------- */
        .the-quan-ly-flat {
            background-color: #ffffff !important;
            padding: 15px !important;
            border-radius: 12px !important;
            border-left: 6px solid #7d8f15 !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
            text-align: center !important;
            font-weight: 700 !important;
            font-size: 14px !important;
            margin-bottom: 20px !important;
        }
        
        .nhan-tieu-de {
            font-size: 13px !important;
            font-weight: 700 !important;
            margin-bottom: 5px !important;
            text-transform: uppercase !important;
        }

        /* -----------------------------------------------------------------
           3. HỆ THỐNG HIỆU ỨNG KHỐI HỘP TÍNH TIỀN & CHỈ DẪN FLAT PREMIUM
        ----------------------------------------------------------------- */
        .the-quan-ly-flat {
            background-color: #ffffff !important;
            padding: 15px !important;
            border-radius: 12px !important;
            border-left: 6px solid #7d8f15 !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
            text-align: center !important;
            font-weight: 700 !important;
            font-size: 14px !important;
            margin-bottom: 20px !important;
        }
        
        .nhan-tieu-de {
            font-size: 13px !important;
            font-weight: 700 !important;
            margin-bottom: 5px !important;
            text-transform: uppercase !important;
        }

        .tong-don-box {
            background-color: #fef3c7 !important;
            color: #b45309 !important;
            padding: 15px !important;
            border-radius: 12px !important;
            text-align: center !important;
            font-size: 24px !important;
            font-weight: 900 !important;
            border: 2px dashed #fde68a !important;
        }

        .cong-tho-box {
            background-color: #f3f4f6 !important;
            color: #1f2937 !important;
            padding: 15px !important;
            border-radius: 12px !important;
            text-align: center !important;
            font-size: 24px !important;
            font-weight: 900 !important;
            border: 2px dashed #e5e7eb !important;
        }

        .tien-thua-box {
            background-color: #059669 !important;
            color: #ffffff !important;
            padding: 12px !important;
            border-radius: 12px !important;
            text-align: center !important;
            font-size: 16px !important;
            font-weight: 700 !important;
            margin-top: 15px !important;
            box-shadow: 0 4px 10px rgba(5, 150, 105, 0.3) !important;
        }


        /* -----------------------------------------------------------------
           4. KHỐI BANNER CỐ ĐỊNH ĐỈNH & ĐÁY (ĐÃ SỬA VỊ TRÍ MOBILE)
        ----------------------------------------------------------------- */
        .banner-top {
            position: fixed !important; 
            left: 0 !important; 
            right: 0 !important; 
            top: 0px !important; 
            height: 48px !important;
            background: #111111 !important; 
            color: #f1c40f !important;
            font-size: 15px !important; 
            font-weight: 800 !important; 
            letter-spacing: 1px !important;
            display: flex !important; 
            align-items: center !important; 
            justify-content: center !important; /* Lệnh này giúp chữ ở ĐỈNH căn giữa */
            cursor: pointer !important; 
            user-select: none !important; 
            z-index: 999999 !important; 
            border-bottom: 3px solid #7d8f15 !important;
            box-shadow: 0px 4px 15px rgba(0,0,0,0.3) !important;
            -webkit-tap-highlight-color: transparent;
        }
        
        .banner-bottom { 
            position: fixed !important; left: 0 !important; right: 0 !important; height: 48px !important;
            background: #111111 !important; color: #f1c40f !important;
            font-size: 15px !important; font-weight: 800 !important; letter-spacing: 1px !important;
            display: flex !important; align-items: center !important; 
            cursor: pointer !important; user-select: none !important; z-index: 99999 !important;
            bottom: 0 !important; 
            top: auto !important;
            border-top: 3px solid #7d8f15 !important; 
            border-bottom: none !important;
            box-shadow: 0px -4px 15px rgba(0,0,0,0.2) !important; 
            justify-content: flex-start !important; 
            padding-left: 20px !important; 
            -webkit-tap-highlight-color: transparent;
        }


        .firework-particle { position: fixed !important; width: 6px; height: 6px; border-radius: 50%; pointer-events: none !important; z-index: 100000 !important; }

        /* -----------------------------------------------------------------
           5. BẢNG HIỆU ĐIỆN TỬ CỦA TIỆM (LUXURY GLOW)
        ----------------------------------------------------------------- */
        .bang-hieu-lktv {
            text-align: center; margin-bottom: 25px !important; padding: 25px !important; border-radius: 24px !important;
            background: linear-gradient(135deg, #111827 0%, #1f2937 100%) !important;
            color: white !important; box-shadow: 0px 15px 35px rgba(0,0,0,0.25) !important; 
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
        }
        .logo-img { 
            width: 110px !important; height: 110px !important; object-fit: cover !important; border-radius: 50% !important; 
            border: 4px solid #f1c40f !important; margin: 0 auto 15px auto !important; display: block !important;
            box-shadow: 0 0 20px rgba(241, 196, 15, 0.4) !important;
        }
        .ten-tiem { font-size: 24px !important; font-weight: 900 !important; color: #ffffff !important; text-transform: uppercase !important; margin-bottom: 6px !important; letter-spacing: 2px !important; }
        .thong-tin-phu { font-size: 12px !important; color: #9ca3af !important; margin: 5px 0 !important; font-weight: 400; }
        .slogan { font-size: 15px !important; color: #f1c40f !important; font-weight: 600 !important; font-style: italic !important; margin-top: 15px !important; border-top: 1px solid rgba(255,255,255,0.1) !important; padding-top: 12px !important; }
        
        /* -----------------------------------------------------------------
           4. ĐIỀU CHỈNH TABS THỜI TRANG CAO CẤP
        ----------------------------------------------------------------- */
        .stTabs [data-baseweb="tab-list"] { display: flex; justify-content: center; gap: 12px; width: 100%; border-bottom: 2px solid #e5e7eb; }
        .stTabs [data-baseweb="tab"] { flex: 1; height: 54px; background-color: #f3f4f6; border-radius: 14px 14px 0 0; border: 1px solid #e5e7eb; transition: all 0.2s ease; }
        .stTabs [data-baseweb="tab"] p { color: #4b5563 !important; font-weight: 700 !important; font-size: 15px; text-align: center; }
        .stTabs [data-baseweb="tab"][aria-selected="true"] { background-color: #111827 !important; border-color: #111827; }
        .stTabs [data-baseweb="tab"][aria-selected="true"] p { color: #f1c40f !important; }

        .nhan-tieu-de { text-align: center; font-size: 14px; font-weight: 800; text-transform: uppercase; margin-bottom: 8px; color: #374151; letter-spacing: 1px; }

        /* KHỐI THÈ HƯỚNG DẪN FLAT PANEL CÓ CHỨA TEXT CHỈ DẪN */
        .the-quan-ly-flat {
            background: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            border-left: 6px solid #7d8f15 !important;
            padding: 14px 16px !important;
            border-radius: 12px !important;
            font-size: 14px !important;
            font-weight: 700 !important;
            color: #1e293b !important; /* Màu chữ xám tối thanh lịch */
            margin-top: 10px !important;
            margin-bottom: 15px !important;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.03) !important;
            text-align: center !important; /* Căn giữa chữ hướng dẫn */
        }
        /* -----------------------------------------------------------------
           6. ĐỒNG BỘ HIỂN THỊ 3 TAB: CHIA ĐỀU 100% MÀN HÌNH - CHỮ CĂN GIỮA
        ----------------------------------------------------------------- */
        /* KHỬ TUYỆT ĐỐI ĐƯỜNG VIỀN ĐỎ CAM CHẠY THEO DƯỚI CHÂN CÁC TAB */
        [data-testid="stTabs"] [role="tablist"] div {
            height: 0px !important;
            background-color: transparent !important;
            border: none !important;
        }

        /* ÉP THANH CHỨA TAB CHẠY HẾT 100% CHIỀU NGANG, KHÔNG ĐỂ TRỐNG */
        [data-testid="stTabs"] [role="tablist"] {
            display: flex !important;
            width: 100% !important;
            justify-content: space-between !important;
            gap: 4px !important; /* Tạo khoảng cách nhỏ vừa phải giữa các nút */
        }

        /* CẤU HÌNH NÚT TAB: CHIA ĐỀU 1/3 MÀN HÌNH VÀ CĂN CHỮ CHÍNH GIỮA */
        button[data-baseweb="tab"] {
            flex: 1 1 0% !important; /* Thần chú ép 3 nút tự động chia đều diện tích màn hình */
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important; /* Ép chữ và icon ra ngay chính giữa tâm nút */
            text-align: center !important;
            background-color: #f1f3f5 !important; /* Nền xám nhạt tinh tế khi chưa chọn */
            color: #495057 !important; /* Chữ xám tối */
            border-radius: 8px !important; /* Bo tròn đều 4 góc cho ra dáng nút bấm hiện đại */
            padding: 10px 4px !important; /* Giảm padding ngang xuống tối thiểu để chữ không bị tràn */
            font-size: 13px !important; /* Kích thước chữ tối ưu cho mobile */
            border: none !important; 
            outline: none !important;
            white-space: nowrap !important; /* Ngăn không cho chữ tự động xuống dòng bậy bạ */
            transition: all 0.2s ease-in-out !important;
        }

        /* HIỆU ỨNG KHI ẤN CHỌN TAB: ĐỔI MÀU NỀN PHẲNG MỊN PREMIUM */
        button[data-baseweb="tab"][aria-selected="true"] {
            background-color: #f1c40f !important; /* Màu xanh rêu thương hiệu của tiệm */
            color: #f1c40f !important; /* Chữ trắng sáng bừng */
            font-weight: 800 !important; /* Chữ đậm lên trông thấy */
            border: none !important;
            outline: none !important;
            box-shadow: 0 4px 8px rgba(125, 143, 21, 0.2) !important; /* Đổ bóng rêu nhẹ luxury */
        }

        /* Khử hoàn toàn các đường viền phát sinh khi Hover/Focus chạm ngón tay vào */
        button[data-baseweb="tab"]:focus, button[data-baseweb="tab"]:active, button[data-baseweb="tab"]:hover {
            border: none !important;
            outline: none !important;
        }

        /* KHỐI NỀN ĐỔ MÀU CHO FORM/NỘI DUNG PHÍA DƯỚI THẺ QUẢN LÝ */
        .khung-noi-dung-mo-rong {
            background-color: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            padding: 20px !important;
            border-radius: 16px !important;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.03) !important;
            margin-bottom: 25px !important;
        }

        /* -----------------------------------------------------------------
            7. ĐỒNG BỘ HIỂN THỊ 3 TAB: TO CAO, CHỮ NẰM NGAY CHÍNH GIỮA TÂM
        ----------------------------------------------------------------- */
        /* Khử tuyệt đối đường viền đỏ cam chạy theo dưới chân các tab */
        [data-testid="stTabs"] [role="tablist"] div {
            height: 0px !important;
            background-color: transparent !important;
            border: none !important;
        }

        /* Ép thanh chứa Tab dàn hàng ngang khít 100% khung hình, không lo lệch */
        [data-testid="stTabs"] [role="tablist"] {
            display: flex !important;
            width: 100% !important;
            justify-content: center !important;
            align-items: center !important;
            gap: 6px !important; 
            padding: 0 !important;
            margin: 0 auto 15px auto !important;
        }

        /* ĐỘ LẠI NÚT TAB: ÉP TOÀN BỘ CÁC LỚP THẺ PHẢI CĂN GIỮA TUYỆT ĐỐI */
        button[data-baseweb="tab"] {
            flex: 1 1 100% !important; 
            height: 54px !important; 
            display: flex !important;
            align-items: center !important;
            justify-content: center !important; 
            text-align: center !important;
            background-color: #e2e8f0 !important; 
            border-radius: 10px !important; 
            padding: 10px 4px !important; 
            border: none !important; 
            outline: none !important;
            white-space: nowrap !important; 
            transition: all 0.2s ease-in-out !important;
        }

        /* THẦN CHÚ DIỆT LỆCH KHUNG: ÉP TẤT CẢ THẺ CHỮ CON PHẢI RA GIỮA */
        button[data-baseweb="tab"] p, 
        button[data-baseweb="tab"] span, 
        button[data-baseweb="tab"] div[data-testid="stMarkdownContainer"] {
            color: #334155 !important; 
            font-size: 16px !important; 
            font-weight: 700 !important; 
            text-align: center !important;
            justify-content: center !important;
            align-items: center !important;
            display: flex !important;
            margin: 0 auto !important; 
            width: 100% !important;
        }

        /* HIỆU ỨNG KHI ẤN CHỌN TAB: NỀN VÀNG RỰC RỠ - CHỮ ĐEN MUN SÁNG BỪNG */
        button[data-baseweb="tab"][aria-selected="true"] {
            background-color: #f1c40f !important; 
            border: none !important;
            outline: none !important;
            box-shadow: 0 4px 12px rgba(241, 196, 15, 0.4) !important; 
        }
        
        /* Ép chữ của Tab KHI ĐƯỢC CHỌN sang đen mun và siêu đậm để chống lóa */
        button[data-baseweb="tab"][aria-selected="true"] p,
        button[data-baseweb="tab"][aria-selected="true"] span,
        button[data-baseweb="tab"][aria-selected="true"] div[data-testid="stMarkdownContainer"] {
            color: #000000 !important; 
            font-weight: 900 !important; 
            font-size: 16px !important;
        }

        /* Khử hoàn toàn các đường viền phát sinh khi chạm ngón tay vào */
        button[data-baseweb="tab"]:focus, button[data-baseweb="tab"]:active, button[data-baseweb="tab"]:hover {
            border: none !important;
            outline: none !important;
        }

        .khung-noi-dung-mo-rong {
            background-color: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            padding: 20px !important;
            border-radius: 16px !important;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.03) !important;
            margin-bottom: 25px !important;
        }
        
        /* -----------------------------------------------------------------
           8. CÁC KHỐI HIỂN THỊ TIỀN TỆ TRỰC QUAN
        ----------------------------------------------------------------- */
        .tong-don-box { background-color: #fef3c7; color: #b45309; padding: 16px; border-radius: 16px; text-align: center; border: 3px dashed #d97706; font-size: 24px; font-weight: 900; box-shadow: 0px 4px 10px rgba(0,0,0,0.02); }
        .cong-tho-box { background-color: #f3f4f6; color: #1f2937; padding: 16px; border-radius: 16px; text-align: center; border: 3px dashed #4b5563; font-size: 24px; font-weight: 900; box-shadow: 0px 4px 10px rgba(0,0,0,0.02); }
        .tien-thua-box { background-color: #d1fae5; color: #065f46; padding: 22px; border-radius: 16px; text-align: center; font-size: 26px; font-weight: 900; border: 3px dashed #059669; margin: 20px 0; animation: pulse-steel 2.5s infinite; }
        @keyframes pulse-steel { 0% {transform: scale(1); box-shadow: 0 0 0 0 rgba(5, 150, 105, 0.4);} 70% {transform: scale(1.02); box-shadow: 0 0 0 12px rgba(5, 150, 105, 0);} 100% {transform: scale(1);} }

        /* -----------------------------------------------------------------
           9. PHÔI HÓA ĐƠN LKTV CHUẨN IN (VINTAGE WHITE)
        ----------------------------------------------------------------- */
        .hoa-don-khung { background-color: #ffffff !important; color: #111111 !important; padding: 25px !important; border-radius: 16px !important; border: 2px solid #111111 !important; font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace !important; box-shadow: 0px 10px 25px rgba(0,0,0,0.08) !important; margin-top: 20px !important; position: relative; }
        .hoa-don-khung::before { content: ""; position: absolute; left: 0; right: 0; top: -5px; height: 10px; background-size: 16px 16px; }
        .hd-header { text-align: center; font-weight: bold; border-bottom: 2px dashed #111111; padding-bottom: 12px; margin-bottom: 15px; }
        .hd-title { font-size: 22px; text-transform: uppercase; margin-top: 6px; letter-spacing: 1px; font-weight: 900; color: #111111; }
        .hd-row { display: flex !important; justify-content: space-between !important; align-items: center !important; margin-bottom: 8px !important; font-size: 13px !important; white-space: nowrap !important; overflow: hidden !important; width: 100% !important; }
        .hd-row span:first-child { overflow: hidden !important; text-overflow: ellipsis !important; padding-right: 5px !important; }
        .hd-items { border-bottom: 2px dashed #111111; padding-bottom: 12px; margin-bottom: 12px; }
    </style>

    <div class="banner-top" onclick="createFirework(event)">⭐⭐⭐ SALON KIM HIỀN ⭐⭐⭐</div>
    <div class="banner-bottom" onclick="createFirework(event)"> KIM HIỀN 2026 🌹🌹🌹 </div>

    <script>
        // Ép buộc giao diện về Light Mode
        const style = document.createElement('style');
        style.innerHTML = `
            @media (prefers-color-scheme: dark) {
                :root {
                    --st-background-color: #ffffff;
                    --st-primary-color: #f1c40f;
                    --st-text-color: #000000;
                }
            }
        `;
        document.head.appendChild(style);
    </script>
    
    <script>
        if (!window.fireworkStylesAdded) {
            const style = document.createElement('style');
            style.innerHTML = `@keyframes explode { 0% { transform: translate(0, 0) scale(1); opacity: 1; } 100% { transform: translate(var(--x), var(--y)) scale(0.2); opacity: 0; } }`;
            document.head.appendChild(style);
            window.fireworkStylesAdded = true;
        }
        function createFirework(e) {
            const clickX = e.clientX, clickY = e.clientY, particleCount = 40;
            const colors = ['#f1c40f', '#00ffcc', '#ffcc00', '#ff6600', '#ffffff'];
            for (let i = 0; i < particleCount; i++) {
                const particle = document.createElement('div');
                particle.className = 'firework-particle';
                particle.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
                particle.style.left = clickX + 'px'; particle.style.top = clickY + 'px';
                particle.style.animation = 'explode 0.7s ease-out forwards';
                const angle = Math.random() * Math.PI * 2, velocity = Math.random() * 120 + 40; 
                particle.style.setProperty('--x', (Math.cos(angle) * velocity) + 'px');
                particle.style.setProperty('--y', (Math.sin(angle) * velocity) + 'px');
                document.body.appendChild(particle);
                setTimeout(() => { particle.remove(); }, 700);
            }
        }
    </script>
""", unsafe_allow_html=True)
# =====================================================================
# 2. HÀM CORE HỆ THỐNG ĐỒNG BỘ & TRUY XUẤT DATA
# =====================================================================
def get_now_vn():
    return datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))

def get_gspread_client():
    creds_info = st.secrets["connections"]["gsheets"]
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    return gspread.authorize(Credentials.from_service_account_info(creds_info, scopes=scope))

def format_drive_direct_url(link):
    if not link or not isinstance(link, str): 
        return ""
    match = re.search(r'(pires=|/d/|id=)([a-zA-Z0-9-_]{33,40})', link.strip())
    return f"https://lh3.googleusercontent.com/d/{match.group(2)}" if match else ""

@st.cache_data(ttl=5)
def get_settings():
    try:
        client = get_gspread_client()
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        rows = client.open_by_url(url).worksheet("ThietLap").get_all_values()
        return {str(row[0]).strip(): str(row[1]).strip() for row in rows if len(row) > 1}
    except Exception:
        return {
            "TenTiem": "SALON KIM HIỀN", 
            "Diachi": "131, TRẦN BÌNH TRỌNG, MỸ XUYÊN, LONG XUYÊN, AN GIANG (AG CŨ)", 
            "SDT": "0947.58.1516", "Slogan": "\"Nơi Bạn Đặt Niềm Tin\"", "Logo": ""
        }

@st.cache_data(ttl=60)
def get_service_data():
    try:
        client = get_gspread_client()
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        rows = client.open_by_url(url).worksheet("DanhMuc").get_all_values()
        
        danh_sach_dv = {}
        for row in rows[1:]:
            if len(row) >= 2:
                ten_dv = str(row[0]).strip()
                if not ten_dv:
                    continue
                try: 
                    gia_goc = float(str(row[1]).replace('.', '').replace(',', '').strip())
                except: 
                    gia_goc = 0.0
                
                hoa_hong = 0.0
                if len(row) >= 3 and row[2]:
                    try:
                        raw_hh = str(row[2]).replace('%', '').replace(',', '.').strip()
                        hoa_hong = float(raw_hh)
                        if 0 < hoa_hong < 1.0: 
                            hoa_hong *= 100
                    except: 
                        hoa_hong = 0.0
                
                danh_sach_dv[ten_dv] = {"gia": gia_goc, "hoa_hong": hoa_hong}
        return danh_sach_dv
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
            <div class="thong-tin-phu">📞 {settings.get('SDT', '0947.58.1516')}</div>
            <div class="slogan">{settings.get('Slogan', '"Nơi Bạn Đặt Niềm Tin"')}</div>
        </div>
    """, unsafe_allow_html=True)


# =====================================================================
# 3. LUỒNG ĐIỀU HƯỚNG CHÍNH (MAIN APPLICATION LOGIC)
# =====================================================================
def main():
    init_states = {"last_submit": None, "submit_count": 0, "submitting": False, "adding_cart": False, "logged_in": False, "role": None, "full_name": None, "gio_hang": [], "bill_vua_in": None}
    for key, val in init_states.items():
        if key not in st.session_state: 
            st.session_state[key] = val

    settings = get_settings()

    # --- PHÂN HỆ ĐĂNG NHẬP ---
    if not st.session_state["logged_in"]:
        display_header(settings)
        with st.form("login_section"):
            st.markdown("<h3 style='text-align: center;'>🔐 ĐĂNG NHẬP</h3>", unsafe_allow_html=True)
            u = st.text_input("Tài khoản (SĐT)")
            p = st.text_input("Mật khẩu", type="password")
            if st.form_submit_button("XÁC NHẬN ĐĂNG NHẬP", use_container_width=True):
                if u == "admin" and p == "2026":
                    st.session_state.update({"logged_in": True, "role": "Admin", "full_name": "Chủ Tiệm"})
                    st.rerun()
                else:
                    try:
                        cl = get_gspread_client()
                        sh = cl.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
                        user_sheet = sh.worksheet("NhanVien")
                        
                        raw_data = user_sheet.get_all_values()
                        if len(raw_data) > 0:
                            headers = [str(h).strip() for h in raw_data[0]]
                            
                            col_sdt_idx = next((i for i, h in enumerate(headers) if 'số điện thoại' in h.lower() or 'sđt' in h.lower() or 'tai khoan' in h.lower()), -1)
                            col_mk_idx = next((i for i, h in enumerate(headers) if 'mật khẩu' in h.lower() or 'mat khau' in h.lower() or 'code' in h.lower()), -1)
                            col_ten_idx = next((i for i, h in enumerate(headers) if 'tên' in h.lower() or 'nhân viên' in h.lower()), -1)
                            
                            if col_sdt_idx == -1 or col_mk_idx == -1:
                                user_list = user_sheet.get_all_records()
                                found_user = None
                                for row in user_list:
                                    sdt_sheet = str(row.get('Số Điện Thoại', row.get('SĐT', ''))).strip().lstrip('0')
                                    sdt_nhap = str(u).strip().lstrip('0')
                                    if sdt_nhap == sdt_sheet and sdt_nhap != "":
                                        if p.strip() == str(row.get('Mật Khẩu', row.get('Mật khẩu', ''))).strip():
                                            found_user = row
                                            break
                                if found_user:
                                    ten_that = found_user.get('Tên Nhân Viên', found_user.get('Tên nhân viên', 'Nhân viên'))
                                    st.session_state.update({"logged_in": True, "role": "NhanVien", "full_name": ten_that})
                                    st.success(f"Chào mừng {ten_that}!")
                                    time.sleep(0.5)
                                    st.rerun()
                                else:
                                    st.error("Tài khoản hoặc Mật khẩu không chính xác!")
                            else:
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
                                    st.session_state.update({"logged_in": True, "role": "NhanVien", "full_name": ten_that})
                                    st.success(f"Chào mừng {ten_that}!")
                                    time.sleep(0.5)
                                    st.rerun()
                                else:
                                    st.error("Tài khoản hoặc Mật khẩu không chính xác!")
                        else:
                            st.error("Bảng dữ liệu Nhân Viên trên Google Sheets đang trống!")
                    except Exception as e:
                        st.error(f"Lỗi cổng kết nối: {e}")

    # --- PHÂN HỆ HOẠT ĐỘNG CHÍNH ---
    else:
        display_header(settings)
        t_list = ["🛒 NHẬP LIỆU", "📈 BÁO CÁO", "⚙️ CÀI ĐẶT"] if st.session_state["role"] == "Admin" else ["🛒 NHẬP LIỆU"]
        tabs = st.tabs(t_list)

        # TAB 1: NHẬP LIỆU & LÊN ĐƠN HÀNG
        with tabs[0]:
            st.info(f"👨‍🔧 **Nhân viên:** {st.session_state.full_name} | 🕒 **Giờ hiện tại:** {get_now_vn().strftime('%H:%M')}")
            
            # HIỂN THỊ CHỮ HƯỚNG DẪN TRONG KHUNG TRỐNG TAB 1
            st.markdown('<div class="the-quan-ly-flat">📝 NHẬP "ĐƠN HÀNG" BÊN DƯỚI NHÉ!</div>', unsafe_allow_html=True)
            services = get_service_data()
            dv_list = list(services.keys())
            
            c1, c2 = st.columns(2)
            with c1: kh_ten = st.text_input("👤 Tên khách hàng", "Khách lẻ")
            with c2: kh_sdt = st.text_input("📞 SĐT khách")
            
            st.markdown("#### ✂️ CHỌN DỊCH VỤ THÊM VÀO ĐƠN")
            
            box_chon_dv = st.selectbox(
                "📌 Dịch vụ", 
                options=dv_list if dv_list else ["Không có dữ liệu"],
                index=None,
                placeholder="Gõ chữ để tìm nhanh... (Ví dụ: 'combo 60', 'cắt')"
            )
            box_sl = st.number_input("🔢 Số lượng", min_value=0.0, max_value=100.0, value=0.0, step=0.5)
            
            if st.session_state.adding_cart:
                st.button("⏳ ĐANG THÊM VÀO GIỎ...", disabled=True, use_container_width=True)
            else:
                if st.button("✅ THÊM VÀO GIỎ ĐƠN", use_container_width=True):
                    if not box_chon_dv or box_chon_dv == "Không có dữ liệu":
                        st.error("🚫 Vui lòng gõ và chọn một dịch vụ cụ thể trước khi thêm vào giỏ nhen ní!")
                    elif box_sl <= 0:
                        st.error("Vui lòng chọn số lượng lớn hơn 0 trước khi thêm vào giỏ!")
                    else:
                        st.session_state.adding_cart = True
                        if any(item["dich_vu"] == box_chon_dv for item in st.session_state.gio_hang):
                            st.error(f"🚫 CẢNH BÁO: Dịch vụ '{box_chon_dv}' đã tồn tại trong giỏ đơn này rồi nhen!")
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
                            st.success(f"Đã thêm {box_sl} x {box_chon_dv} thành công!")
                            st.session_state.bill_vua_in = None
                            st.session_state.adding_cart = False
                            time.sleep(0.2)
                            st.rerun()
            st.markdown('</div>', unsafe_allow_html=True) # ĐÓNG KHUNG CHUẨN: Sau khi các nút và ô nhập liệu đã xuất hiện xong

            # -----------------------------------------------------------------
            # KHỐI HIỂN THỊ GIỎ HÀNG CHỜ LƯU (ĐÃ XOÁ SẠCH KHUNG TRỐNG DƯ THỪA)
            # -----------------------------------------------------------------
            t_bill, t_cong_tho = 0.0, 0.0
            if st.session_state.gio_hang:
                st.markdown("---")
                st.markdown(f"📦 **CHI TIẾT ĐƠN HÀNG CHỜ LƯU ({len(st.session_state.gio_hang)} món)**")
                
                # CHÚ Ý: Đã loại bỏ hoàn toàn thẻ div khung trống rỗng ở đây để giao diện liền mạch
                for idx, item in enumerate(st.session_state.gio_hang):
                    col_item1, col_item2, col_item3 = st.columns([5.0, 3.5, 1.5])
                    with col_item1: 
                        st.markdown(f"**{idx+1}. {item['dich_vu']}** (SL: {item['so_luong']})")
                    with col_item2: 
                        st.markdown(f"{item['thanh_tien']:,.0f}đ (Công: {item['tiem_cong_tho']:,.0f}đ)")
                    with col_item3:
                        if st.button("Xóa", key=f"del_{idx}", use_container_width=True):
                            st.session_state.gio_hang.pop(idx)
                            st.session_state.bill_vua_in = None
                            st.rerun()
                    t_bill += item['thanh_tien']
                    t_cong_tho += item['tiem_cong_tho']

            # -----------------------------------------------------------------
            # KHỐI LOGIC THANH TOÁN & ĐỒNG BỘ GOOGLE SHEETS HỢP NHẤT CHUẨN XÁC
            # -----------------------------------------------------------------
            if t_bill > 0:
                ghi_chu = st.text_input("📝 Ghi chú tổng đơn (nếu có)", placeholder="Ví dụ: Khách làm kỹ, xe dơ nhiều...")
                st.divider()
                
                # Khối hiển thị số tiền trực quan
                col_bill1, col_bill2 = st.columns(2)
                with col_bill1: 
                    st.markdown(f'<div class="nhan-tieu-de" style="color: #b45309;">💰 Tổng Đơn Khách</div><div class="tong-don-box">{t_bill:,.0f} đ</div>', unsafe_allow_html=True)
                with col_bill2: 
                    st.markdown(f'<div class="nhan-tieu-de" style="color: #4b5563;">🛠️ Tiền công thợ tổng</div><div class="cong-tho-box">{t_cong_tho:,.0f} đ</div>', unsafe_allow_html=True)
                
                st.write("")
                kh_tra = st.number_input("💵 Tiền khách đưa", 0.0, value=float(t_bill))
                t_du = kh_tra - t_bill
                if t_du > 0:
                    st.markdown(f'<div class="tien-thua-box">💵 THỐI LẠI TIỀN: {t_du:,.0f} đ</div>', unsafe_allow_html=True)

                can_go = True
                if st.session_state.last_submit:
                    tg_cho = (get_now_vn() - st.session_state.last_submit).total_seconds() / 60
                    han_muc = 3 if st.session_state.submit_count == 1 else 5 if st.session_state.submit_count >= 2 else 0
                    if tg_cho < han_muc:
                        can_go = False
                        st.error(f"🚫 HÀNG RÀO THÉP CHỐNG TRÙNG: Vui lòng đợi thêm {round(han_muc - tg_cho, 1)} phút.")

                if can_go:
                    cam_ket = st.checkbox("✅ XÁC NHẬN ĐƠN KHÔNG TRÙNG LẶP")
                    if not st.session_state.submitting:
                        if st.button("🚀 CHỐT ĐƠN HÀNG & ĐỒNG BỘ", use_container_width=True, type="primary"):
                            if cam_ket:
                                st.session_state.submitting = True
                                st.rerun()
                            else: 
                                st.error("Chưa tích chọn ô xác nhận cam kết!")
                    else:
                        st.button("⏳ ĐANG XỬ LÝ ĐỒNG BỘ...", disabled=True, use_container_width=True)
                        try:
                            cl = get_gspread_client()
                            ws = cl.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"]).worksheet("BaoCao")
                            bay_gio = get_now_vn()
                            ma_hd = f"HD-{bay_gio.strftime('%Y%m%d-%H%M%S')}"
                            
                            rows_to_append = []
                            html_items = ""
                            for idx, item in enumerate(st.session_state.gio_hang):
                                rows_to_append.append([
                                    bay_gio.strftime("%d/%m/%Y"), b_name:=st.session_state.full_name, kh_ten, kh_sdt,
                                    item['dich_vu'], item['so_luong'], item['don_gia'], item['thanh_tien'],
                                    bay_gio.strftime("%H:%M:%S"), ghi_chu, item['tiem_cong_tho'], ma_hd
                                ])
                                html_items += f'<div class="hd-row"><span>{idx+1}. {item["dich_vu"]} (x{item["so_luong"]})</span><span>{item["thanh_tien"]:,.0f} đ</span></div>'
                            
                            ws.append_rows(rows_to_append)

                            st.session_state.bill_vua_in = f"""
                            <div class="hoa-don-khung">
                                <div class="hd-header">
                                    <div style="font-size: 16px; font-weight: 900;">{settings.get('TenTiem', 'SALON KIM HIỀN')}</div>
                                    <div style="font-size: 11px;">📍 {settings.get('Diachi', 'AN GIANG')}</div>
                                    <div style="font-size: 11px;">📞 {settings.get('SDT', '0947.58.1516')}</div>
                                    <div class="hd-title">🧾 PHIẾU THANH TOÁN</div>
                                    <div style="font-size: 11px; margin-top:5px;">Mã đơn: {ma_hd}</div>
                                </div>
                                <div style="border-bottom: 1px dashed #111111; padding-bottom: 5px; margin-bottom: 10px; font-size: 13px;">
                                    <div class="hd-row"><span>Ngày lập:</span> <span>{bay_gio.strftime('%d/%m/%Y %H:%M')}</span></div>
                                    <div class="hd-row"><span>Khách hàng:</span> <span>{kh_ten}</span></div>
                                    <div class="hd-row"><span>Nhân viên:</span> <span>{b_name}</span></div>
                                </div>
                                <div class="hd-items">{html_items}</div>
                                <div style="font-size: 14px; font-weight: bold;">
                                    <div class="hd-row"><span>TỔNG CẦN THANH TOÁN:</span> <span>{t_bill:,.0f} đ</span></div>
                                    <div class="hd-row" style="font-weight: normal; font-size: 13px;"><span>Khách đưa:</span> <span>{kh_tra:,.0f} đ</span></div>
                                    <div class="hd-row" style="color: #059669;"><span>TIỀN THỐI LẠI:</span> <span>{t_du:,.0f} đ</span></div>
                                </div>
                                <div style="text-align: center; margin-top: 20px; font-size: 12px; font-style: italic; border-top: 1px dashed #111111; padding-top: 10px;">
                                    {settings.get('Slogan', '"Nơi Bạn Đặt Niềm Tin"')} <br> ♥️ Cảm ơn quý khách! ♥️
                                </div>
                            </div>"""

                            st.session_state.update({"gio_hang": [], "last_submit": bay_gio, "submit_count": st.session_state.submit_count + 1, "submitting": False})
                            st.success("🎉 ĐỒNG BỘ THÀNH CÔNG! ĐÃ XUẤT HOÁ ĐƠN ĐIỆN TỬ!")
                            time.sleep(0.5)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Lỗi lưu dữ liệu: {e}")
                            st.session_state.submitting = False
            else:
                # Trả về thông báo nhắc nhở khi tổng tiền bằng 0đ
                st.warning("⚠️ Giỏ hàng hiện đang trống nhen ní. Vui lòng chọn dịch vụ phía trên và bấm 'Thêm vào giỏ đơn' để lên đơn tính tiền.")

            if st.session_state.bill_vua_in:
                st.markdown("---")
                st.markdown("### 🧾 HOÁ ĐƠN VỪA LẬP (Chụp màn hình gửi khách)")
                st.markdown(st.session_state.bill_vua_in, unsafe_allow_html=True)

            st.divider()
            if st.button("🚪 THOÁT APP", use_container_width=True):
                st.session_state.clear()
                st.rerun()

# PHÂN HỆ DÀNH RIÊNG CHO TÀI KHOẢN ADMIN (CHỦ TIỆM)
        if st.session_state["role"] == "Admin":
            # TAB 2: DOANH THU REALTIME
            with tabs[1]:
                st.markdown("### 📊 DOANH THU THỰC TẾ REALTIME")
            # HIỂN THỊ CHỮ HƯỚNG DẪN TRONG KHUNG TRỐNG TAB 2
                st.markdown('<div class="the-quan-ly-flat">📊 Vui lòng xem lại “BÁO CÁO“ nhé!</div>', unsafe_allow_html=True)

                try:
                    cl = get_gspread_client()
                    ws_bc = cl.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"]).worksheet("BaoCao")
                    du_lieu = ws_bc.get_all_records()
                    if du_lieu:
                        df_bc = pd.DataFrame(du_lieu)
                        
                        # Tách 50 dòng cuối và xử lý chỉ mục hiển thị
                        df_hien_thi = df_bc.tail(50).copy()
                        df_hien_thi.index = range(1, len(df_hien_thi) + 1)
                        
                        # Đặt tên tiêu đề cho cột số thứ tự là "Stt"
                        df_hien_thi.index.name = "Stt"
                        
                        # Hiển thị bảng dữ liệu sạch sẽ lên giao diện
                        st.dataframe(df_hien_thi, use_container_width=True)
                        
                        # Lọc tính toán doanh thu hôm nay dựa trên bảng gốc đầy đủ
                        ngay_nay = get_now_vn().strftime("%d/%m/%Y")
                        df_h = df_bc[df_bc['Ngày'] == ngay_nay]
                        
                        c1, c2, c3 = st.columns(3)
                        c1.metric("📊 TỔNG DOANH THU HÔM NAY", f"{df_h['Thành tiền'].sum():,.0f} đ")
                        c2.metric("🧾 TỔNG ĐƠN HÀNG", len(df_h))
                        c3.metric("💎 TRUNG BÌNH", f"{df_h['Thành tiền'].mean() if len(df_h)>0 else 0:,.0f} đ")
                    else: 
                        st.info("Chưa có dữ liệu báo cáo đơn hàng.")
                except Exception as e: 
                    st.error(f"Lỗi truy xuất báo cáo: {e}")
                st.markdown('</div>', unsafe_allow_html=True)

            # TAB 3: QUẢN TRỊ NHÂN SỰ & THIẾT LẬP (MÀU NỀN TOÀN KHỐI FLAT PANEL)
            with tabs[2]:
                st.markdown("### ⚙️ HỆ THỐNG QUẢN TRỊ CAO CẤP")
                
                # Khối 1: Google Sheets có màu nền đổ bóng sang trọng
                st.markdown('<div class="the-quan-ly-flat">🔗 LIÊN KẾT GOOGLE SHEET GỐC</div>', unsafe_allow_html=True)
                
                st.markdown(f"👉 **Đường dẫn quản lý:** [Bấm để mở file dữ liệu trên Google Sheets]({st.secrets['connections']['gsheets']['spreadsheet']})")
                st.write("")
                if st.button("♻️ LÀM SẠCH BỘ NHỚ ĐỆM (CLEAR CACHE)"):
                    st.cache_data.clear()
                    st.rerun()
                st.markdown('<div class="the-quan-ly-flat">✍️ĐĂNG KÝ TK “NHÂN VIÊN“</div>', unsafe_allow_html=True)
                
                # Khối 2: Nhân sự có màu nền đổ bóng đầy đủ.
                try:
                    cl = get_gspread_client()
                    sh = cl.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
                    ws_user = sh.worksheet("NhanVien")
                    
                    with st.form("add_user_form", clear_on_submit=True):
                        st.markdown("**➕ Thêm tài khoản nhân viên mới:**")
                        new_sdt = st.text_input("📱 Số điện thoại nhân viên (Tài khoản)")
                        new_code = st.text_input("🔑 Mã đăng nhập (Mật khẩu)")
                        new_name = st.text_input("🏷️ Tên nhân viên hiển thị")
                        
                        if st.form_submit_button("👌 CẤP MÃ MỚI"):
                            if new_sdt and new_code and new_name:
                                ws_user.append_row([new_sdt.strip(), new_code.strip(), new_name.strip()])
                                st.success(f"Đã tạo tài khoản cho {new_name}!")
                                st.cache_data.clear()
                                time.sleep(0.5)
                                r_count = st.rerun()
                            else: st.error("Vui lòng không để trống thông tin!")
                    
                    st.write("---")
                    st.write("📋 **Danh sách nhân sự hiện tại:**")
                    user_data = ws_user.get_all_records()
                    if user_data: 
                        st.table(pd.DataFrame(user_data))
                except Exception as e:
                    st.error(f"Lỗi hệ thống nhân sự: {e}")
                st.markdown('</div>', unsafe_allow_html=True)
                
                st.divider()
                if st.button("🚪 THOÁT KHỎI HỆ THỐNG QUẢN TRỊ", use_container_width=True):
                    st.session_state.clear()
                    st.rerun()

if __name__ == "__main__":
    main()
