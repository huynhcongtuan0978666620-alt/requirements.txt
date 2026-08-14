import streamlit as st
import pandas as pd

# Cấu hình trang tối ưu cho hiển thị Mobile
st.set_page_config(page_title="Salon Kim Hiền - Premium UI", page_icon="💇", layout="centered")

# --- 1. BỘ MÀU HOÀNG GIA CHO SALON (THEME_COLORS) ---
THEME_COLORS = {
    "bg_app": "rgba(235, 245, 241, 0.8)",       # Nền tổng thể xanh mint nhạt hoàng gia
    "bg_card": "#ffffff",                       # Nền card trắng tinh khôi
    "bg_box_chung": "#f4f8f6",                  # Khung thông tin phụ nhẹ nhàng
    "bg_marquee": "#e2f0eb",                    # Nền thanh thông báo chạy chữ
    "primary": "#0f4c43",                       # Xanh lục bảo đậm (Deep Emerald) - Cực sang
    "text_main": "#1a2522",                     # Chữ chính màu than đá sắc nét
    "text_secondary": "#5a6b66",                # Chữ phụ thanh lịch
    "text_title": "#0f4c43",                    # Tiêu đề đồng bộ với primary
}

# --- 2. HÀM BƠM CSS CUSTOM - BIẾN APP BÌNH DÂN THÀNH CAO CẤP ---
def apply_premium_theme():
    custom_css = f"""
    <style>
    /* Nền Gradient mượt mà tạo khoảng thở */
    .stApp {{
        background: linear-gradient(to bottom, {THEME_COLORS['bg_app']}, #ffffff) !important;
        background-attachment: fixed;
    }}
    
    /* Thiết kế khung Card bo góc mềm mại, đổ bóng khói sang trọng */
    div[data-testid="stVerticalBlock"] > div {{
        background-color: {THEME_COLORS['bg_card']} !important;
        border-radius: 20px !important;
        box-shadow: 0 10px 30px rgba(15, 76, 67, 0.05) !important;
        padding: 24px !important;
        border: 1px solid rgba(15, 76, 67, 0.04) !important;
        margin-bottom: 15px;
    }}
    
    /* Định dạng thanh thông báo chữ chạy tinh tế */
    .custom-marquee {{
        background-color: {THEME_COLORS['bg_marquee']};
        color: {THEME_COLORS['primary']};
        padding: 10px 15px;
        border-radius: 30px;
        font-weight: 500;
        font-size: 14px;
        border: 1px solid rgba(15, 76, 67, 0.1);
        margin-bottom: 20px;
    }}
    
    /* Làm mượt font chữ tiêu đề */
    h1, h2, h3 {{
        color: {THEME_COLORS['text_title']} !important;
        font-family: 'Inter', sans-serif;
        font-weight: 700 !important;
    }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

apply_premium_theme()

# --- 3. HIỂN THỊ GIAO DIỆN MÔ PHỎNG ---

# Thanh thông báo chạy chữ kiểu mới (Gọn, mỏng, sang)
st.markdown('<div class="custom-marquee"><marquee scrollamount="4">KÍNH CHÀO QUÝ KHÁCH! CHÚC MỘT NGÀY BÃO ĐƠN VÀ CHỐT THẬT NHIỀU BILL NHA KHÁCH ƠI!</marquee></div>', unsafe_allow_html=True)

# Thanh điều hướng Menu tối giản (Bỏ emoji quê mùa)
menu_tabs = st.tabs(["Tổng quan", "Lên hóa đơn", "Lịch hẹn", "Báo cáo"])

with menu_tabs[0]:
    # --- CARD 1: THÔNG TIN SALON (ĐỒNG BỘ VÀ TINH TẾ) ---
    st.markdown(
        f"""
        <div style="text-align: center;">
            <div style="display: inline-block; width: 100px; height: 100px; border-radius: 50%; border: 3px solid {THEME_COLORS['primary']}; overflow: hidden; margin-bottom: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
                <img src="https://via.placeholder.com/100" style="width: 100%; height: 100%; object-fit: cover;" alt="Logo">
            </div>
            <h2 style="margin: 0; font-size: 24px; letter-spacing: 1px;">SALON KIM HIỀN</h2>
            <p style="color: {THEME_COLORS['text_secondary']}; font-size: 13px; margin: 8px 0 4px 0;">131, Trần Bình Trọng, Mỹ Xuyên, Long Xuyên, An Giang</p>
            <p style="color: {THEME_COLORS['primary']}; font-weight: 600; font-size: 14px; margin: 0;">Hotline: 0947.58.1516</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    st.markdown("---") # Đường chia nhẹ nhàng
    
    # --- CARD 2: LỜI CHÀO KHÁCH HÀNG THÂN THIỆN ---
    st.markdown(
        f"""
        <div style="color: {THEME_COLORS['text_main']};">
            <span style="font-size: 15px; color: {THEME_COLORS['text_secondary']};">Chào chị thân yêu,</span>
            <h3 style="margin: 2px 0 10px 0; font-size: 20px;">Nguyễn Thị Hiền</h3>
            <span style="font-size: 13px; color: {THEME_COLORS['text_secondary']};">Hôm nay là ngày: <b>30/05/2026</b></span>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Giả lập biểu đồ hoặc chỉ số
    st.markdown(f"<p style='color:{THEME_COLORS['primary']}; font-weight:700; margin-top:15px;'>📈 TĂNG TRƯỞNG DOANH THU TRONG NGÀY</p>", unsafe_allow_html=True)
    st.info("Hệ thống hiển thị biểu đồ mượt mà tại đây...")
