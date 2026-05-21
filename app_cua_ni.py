import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import pytz
import time
import re

# =====================================================================
# TẦNG 1: GIAO DIỆN & STYLE (LUXURY FLAT)
# =====================================================================
st.set_page_config(page_title="LKTV DETAILING - PREMIUM", layout="centered", page_icon="✂️", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');
        html, body, .stApp { font-family: 'Inter', sans-serif !important; background-color: #f8f9fa !important; }
        .stApp { padding-top: 75px !important; padding-bottom: 60px !important; }
        
        /* Ẩn logo hệ thống */
        header, footer, .stAppDeployButton, [data-testid="stStatusWidget"] { display: none !important; }

        /* Component Classes */
        .the-quan-ly-flat { background: #ffffff !important; padding: 15px !important; border-radius: 12px !important; border-left: 6px solid #7d8f15 !important; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1) !important; text-align: center !important; font-weight: 700 !important; margin-bottom: 20px !important; }
        .nhan-tieu-de { font-size: 13px !important; font-weight: 700 !important; text-transform: uppercase !important; margin-bottom: 5px !important; color: #374151; }
        .tong-don-box { background: #fef3c7; color: #b45309; padding: 15px; border-radius: 12px; text-align: center; font-size: 24px; font-weight: 900; border: 2px dashed #fde68a; }
        .cong-tho-box { background: #f3f4f6; color: #1f2937; padding: 15px; border-radius: 12px; text-align: center; font-size: 24px; font-weight: 900; border: 2px dashed #e5e7eb; }
        .tien-thua-box { background: #d1fae5; color: #065f46; padding: 22px; border-radius: 16px; text-align: center; font-size: 26px; font-weight: 900; border: 3px dashed #059669; animation: pulse 2.5s infinite; }
        
        /* Banner & Bill */
        .banner-top { position: fixed; top: 0; left: 0; right: 0; height: 48px; background: #111; color: #f1c40f; display: flex; align-items: center; justify-content: center; font-weight: 800; z-index: 9999; border-bottom: 3px solid #7d8f15; }
        .banner-bottom { position: fixed; bottom: 0; left: 0; right: 0; height: 48px; background: #111; color: #f1c40f; display: flex; align-items: center; padding-left: 20px; font-weight: 800; z-index: 9999; border-top: 3px solid #7d8f15; }
        .hoa-don-khung { background: #fff; padding: 25px; border: 2px solid #111; border-radius: 16px; font-family: monospace; }
        .hd-row { display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 8px; }
        
        @keyframes pulse { 0% {transform: scale(1);} 70% {transform: scale(1.02);} 100% {transform: scale(1);} }
    </style>
    <div class="banner-top" onclick="createFirework(event)">⭐⭐⭐ SALON KIM HIỀN ⭐⭐⭐</div>
    <div class="banner-bottom" onclick="createFirework(event)"> KIM HIỀN 2026 🌹🌹🌹 </div>
    <script>
        function createFirework(e) {
            const colors = ['#f1c40f', '#00ffcc', '#ffcc00'];
            for (let i = 0; i < 20; i++) {
                const p = document.createElement('div');
                p.style.position = 'fixed'; p.style.left = e.clientX + 'px'; p.style.top = e.clientY + 'px';
                p.style.width = '6px'; p.style.height = '6px'; p.style.borderRadius = '50%';
                p.style.background = colors[Math.floor(Math.random() * colors.length)];
                p.style.zIndex = '100000'; document.body.appendChild(p);
                setTimeout(() => p.remove(), 700);
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
