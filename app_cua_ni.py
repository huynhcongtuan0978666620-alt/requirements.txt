import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import pytz
import time
import re

# =====================================================================
# TẦNG 1: GIAO DIỆN & STYLE (FULL NGUYÊN BẢN CỦA NÍ)
# =====================================================================
st.set_page_config(page_title="LKTV DETAILING - PREMIUM", layout="centered", page_icon="✂️", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
        html, body, [class*="css"], .stApp, div, span, p, h1, h2, h3, h4, h5, h6, input, button, select, textarea {
            font-family: 'Inter', '-apple-system', BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
        }
        .stApp { padding-top: 75px !important; padding-bottom: 60px !important; background-color: #f8f9fa !important; }
        header, footer, .stAppDeployButton, [data-testid="stStatusWidget"], [data-testid="stToolbar"], div[class*="stAppViewerToolbar"], div[data-testid="stAppViewerToolbar"], footer + div { display: none !important; visibility: hidden !important; height: 0 !important; width: 0 !important; opacity: 0 !important; pointer-events: none !important; }

        .the-quan-ly-flat { background-color: #ffffff !important; padding: 15px !important; border-radius: 12px !important; border-left: 6px solid #7d8f15 !important; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important; text-align: center !important; font-weight: 700 !important; font-size: 14px !important; margin-bottom: 20px !important; }
        .nhan-tieu-de { font-size: 13px !important; font-weight: 700 !important; margin-bottom: 5px !important; text-transform: uppercase !important; text-align: center; color: #374151; letter-spacing: 1px; }
        
        .tong-don-box { background-color: #fef3c7 !important; color: #b45309 !important; padding: 16px !important; border-radius: 16px !important; text-align: center !important; font-size: 24px !important; font-weight: 900 !important; border: 3px dashed #d97706 !important; box-shadow: 0px 4px 10px rgba(0,0,0,0.02) !important; }
        .cong-tho-box { background-color: #f3f4f6 !important; color: #1f2937 !important; padding: 16px !important; border-radius: 16px !important; text-align: center !important; font-size: 24px !important; font-weight: 900 !important; border: 3px dashed #4b5563 !important; box-shadow: 0px 4px 10px rgba(0,0,0,0.02) !important; }
        .tien-thua-box { background-color: #d1fae5 !important; color: #065f46 !important; padding: 22px !important; border-radius: 16px !important; text-align: center !important; font-size: 26px !important; font-weight: 900 !important; border: 3px dashed #059669 !important; margin: 20px 0 !important; animation: pulse-steel 2.5s infinite !important; }
        @keyframes pulse-steel { 0% {transform: scale(1); box-shadow: 0 0 0 0 rgba(5, 150, 105, 0.4);} 70% {transform: scale(1.02); box-shadow: 0 0 0 12px rgba(5, 150, 105, 0);} 100% {transform: scale(1);} }

        .banner-top { position: fixed !important; left: 0 !important; right: 0 !important; top: 0px !important; height: 48px !important; background: #111111 !important; color: #f1c40f !important; font-size: 15px !important; font-weight: 800 !important; letter-spacing: 1px !important; display: flex !important; align-items: center !important; justify-content: center !important; cursor: pointer !important; user-select: none !important; z-index: 999999 !important; border-bottom: 3px solid #7d8f15 !important; box-shadow: 0px 4px 15px rgba(0,0,0,0.3) !important; }
        .banner-bottom { position: fixed !important; left: 0 !important; right: 0 !important; height: 48px !important; background: #111111 !important; color: #f1c40f !important; font-size: 15px !important; font-weight: 800 !important; letter-spacing: 1px !important; display: flex !important; align-items: center !important; cursor: pointer !important; user-select: none !important; z-index: 99999 !important; bottom: 0 !important; top: auto !important; border-top: 3px solid #7d8f15 !important; justify-content: flex-start !important; padding-left: 20px !important; }

        .bang-hieu-lktv { text-align: center; margin-bottom: 25px !important; padding: 25px !important; border-radius: 24px !important; background: linear-gradient(135deg, #111827 0%, #1f2937 100%) !important; color: white !important; box-shadow: 0px 15px 35px rgba(0,0,0,0.25) !important; border: 1px solid rgba(255, 255, 255, 0.08) !important; }
        .logo-img { width: 110px !important; height: 110px !important; object-fit: cover !important; border-radius: 50% !important; border: 4px solid #f1c40f !important; margin: 0 auto 15px auto !important; display: block !important; box-shadow: 0 0 20px rgba(241, 196, 15, 0.4) !important; }
        .ten-tiem { font-size: 24px !important; font-weight: 900 !important; color: #ffffff !important; text-transform: uppercase !important; margin-bottom: 6px !important; letter-spacing: 2px !important; }
        .thong-tin-phu { font-size: 12px !important; color: #9ca3af !important; margin: 5px 0 !important; font-weight: 400; }
        .slogan { font-size: 15px !important; color: #f1c40f !important; font-weight: 600 !important; font-style: italic !important; margin-top: 15px !important; border-top: 1px solid rgba(255,255,255,0.1) !important; padding-top: 12px !important; }

        [data-testid="stTabs"] [role="tablist"] { display: flex !important; width: 100% !important; justify-content: center !important; align-items: center !important; gap: 6px !important; padding: 0 !important; margin: 0 auto 15px auto !important; }
        button[data-baseweb="tab"] { flex: 1 1 100% !important; height: 54px !important; display: flex !important; align-items: center !important; justify-content: center !important; background-color: #e2e8f0 !important; border-radius: 10px !important; border: none !important; }
        button[data-baseweb="tab"][aria-selected="true"] { background-color: #f1c40f !important; box-shadow: 0 4px 12px rgba(241, 196, 15, 0.4) !important; }
        button[data-baseweb="tab"][aria-selected="true"] p, button[data-baseweb="tab"][aria-selected="true"] span, button[data-baseweb="tab"][aria-selected="true"] div[data-testid="stMarkdownContainer"] { color: #000000 !important; font-weight: 900 !important; font-size: 16px !important; }

        .hoa-don-khung { background-color: #ffffff !important; color: #111111 !important; padding: 25px !important; border-radius: 16px !important; border: 2px solid #111111 !important; font-family: monospace !important; box-shadow: 0px 10px 25px rgba(0,0,0,0.08) !important; margin-top: 20px !important; position: relative; }
        .hd-row { display: flex !important; justify-content: space-between !important; align-items: center !important; margin-bottom: 8px !important; font-size: 13px !important; }
        .firework-particle { position: fixed !important; width: 6px; height: 6px; border-radius: 50%; pointer-events: none !important; z-index: 100000 !important; }
    </style>

    <div class="banner-top" onclick="createFirework(event)">⭐⭐⭐ SALON KIM HIỀN ⭐⭐⭐</div>
    <div class="banner-bottom" onclick="createFirework(event)"> KIM HIỀN 2026 🌹🌹🌹 </div>

    <script>
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
# TẦNG 2: SERVICE LAYER (Kết nối & Data)
# =====================================================================
def get_now_vn(): return datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))

def get_gspread_client():
    creds = Credentials.from_service_account_info(st.secrets["connections"]["gsheets"], scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
    return gspread.authorize(creds)

@st.cache_data(ttl=5)
def get_settings():
    try:
        rows = get_gspread_client().open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"]).worksheet("ThietLap").get_all_values()
        return {str(row[0]).strip(): str(row[1]).strip() for row in rows if len(row) > 1}
    except: return {"TenTiem": "SALON KIM HIỀN", "Diachi": "131, TRẦN BÌNH TRỌNG, MỸ XUYÊN", "SDT": "0947.58.1516"}

@st.cache_data(ttl=60)
def get_service_data():
    try:
        rows = get_gspread_client().open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"]).worksheet("DanhMuc").get_all_values()
        data = {}
        for row in rows[1:]:
            if len(row) >= 2:
                gia = float(str(row[1]).replace('.', '').replace(',', '').strip()) if row[1] else 0
                hh = float(str(row[2]).replace('%', '').replace(',', '.').strip()) if len(row) >= 3 and row[2] else 0
                data[str(row[0]).strip()] = {"gia": gia, "hoa_hong": hh}
        return data
    except: return {}

# =====================================================================
# TẦNG 3: LOGIC LAYER (Main Application)
# =====================================================================
def main():
    # Khởi tạo session state
    states = {"logged_in": False, "role": None, "full_name": None, "gio_hang": [], "bill_vua_in": None}
    for k, v in states.items():
        if k not in st.session_state: st.session_state[k] = v

    settings = get_settings()
    
    if not st.session_state["logged_in"]:
        # Logic Đăng nhập (tương tự code cũ của ní)
        # ... (Tui giữ nguyên phần kiểm tra User của ní ở đây)
        pass 
    else:
        # Giao diện chính sau khi đăng nhập
        tabs = st.tabs(["🛒 NHẬP LIỆU", "📈 BÁO CÁO", "⚙️ CÀI ĐẶT"]) if st.session_state["role"] == "Admin" else st.tabs(["🛒 NHẬP LIỆU"])
        # ... (Phần hiển thị đơn hàng & xuất bill của ní)

if __name__ == "__main__":
    main()
