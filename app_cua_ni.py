import streamlit as st
import pandas as pd
import time

# 1. Cấu hình trang tối ưu riêng cho giao diện điện thoại
st.set_page_config(page_title="Salon Kim Hiền - Premium", page_icon="💇", layout="centered")

# 2. Định nghĩa bộ màu thương hiệu sang trọng (Xanh Lục Bảo & Trắng Sữa)
THEME_COLORS = {
    "bg_app": "rgba(235, 245, 241, 0.8)",
    "bg_card": "#ffffff",
    "bg_box_chung": "#f4f8f6",
    "bg_marquee": "#e2f0eb",
    "primary": "#0f4c43",
    "text_main": "#1a2522",
    "text_secondary": "#5a6b66",
    "text_title": "#0f4c43",
}

# 3. Hàm bơm CSS Custom làm mịn và bo tròn các góc Card
def apply_premium_theme():
    custom_css = f"""
    <style>
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    .stApp {{
        background: linear-gradient(to bottom, {THEME_COLORS['bg_app']}, #ffffff) !important;
        background-attachment: fixed;
    }}
    
    /* Ép các khối chứa nội dung bo góc mềm mại */
    div[data-testid="stVerticalBlock"] > div {{
        background-color: {THEME_COLORS['bg_card']} !important;
        border-radius: 20px !important;
        box-shadow: 0 10px 30px rgba(15, 76, 67, 0.05) !important;
        padding: 22px !important;
        border: 1px solid rgba(15, 76, 67, 0.04) !important;
        margin-bottom: 15px;
    }}
    
    /* ĐOẠN CẢI TIẾN 1: Ép thanh thông báo chạy chữ dàn đều 100% chiều ngang */
    .custom-marquee {{
        background-color: {THEME_COLORS['bg_marquee']};
        color: {THEME_COLORS['primary']};
        padding: 12px 20px;
        border-radius: 12px;
        font-weight: 500;
        font-size: 15px;
        border: 1px solid rgba(15, 76, 67, 0.1);
        margin-bottom: 20px;
        width: 100% !important;
    }}
    
    /* ĐOẠN CẢI TIẾN 2: Đổi màu thanh gạch chân bên dưới Tab sang màu Xanh Lục Bảo */
    button[data-baseweb="tab"] {{
        color: {THEME_COLORS['text_secondary']} !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: {THEME_COLORS['primary']} !important;
    }}
    div[data-testid="stTabsTabBorder"] {{
        background-color: {THEME_COLORS['primary']} !important;
    }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

# Kích hoạt chiếc áo mới cho giao diện
apply_premium_theme()

# 4. Hiển thị các thành phần UI mẫu trên màn hình
st.markdown('<div class="custom-marquee"><marquee scrollamount="4">KÍNH CHÀO QUÝ KHÁCH! CHÚC MỘT NGÀY BÃO ĐƠN VÀ CHỐT THẬT NHIỀU BILL NHA KHÁCH ƠI!</marquee></div>', unsafe_allow_html=True)

# Thanh Menu điều hướng tối giản
menu_tabs = st.tabs(["Tổng quan", "Lên hóa đơn", "Lịch hẹn", "Báo cáo"])

with menu_tabs[0]:
    # CARD 1: THÔNG TIN THƯƠNG HIỆU SALON
    st.markdown(
        f"""
        <div style="text-align: center;">
            <div style="display: inline-block; width: 90px; height: 90px; border-radius: 50%; border: 3px solid {THEME_COLORS['primary']}; overflow: hidden; margin-bottom: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.08);">
                <img src="https://images.unsplash.com/photo-1560066984-138dadb4c035?w=150" style="width: 100%; height: 100%; object-fit: cover;" alt="Logo">
            </div>
            <h2 style="margin: 0; font-size: 22px; color: {THEME_COLORS['text_title']}; letter-spacing: 0.5px;">SALON KIM HIỀN</h2>
            <p style="color: {THEME_COLORS['text_secondary']}; font-size: 13px; margin: 6px 0 4px 0;">131, Trần Bình Trọng, Mỹ Xuyên, Long Xuyên, An Giang</p>
            <p style="color: {THEME_COLORS['primary']}; font-weight: 600; font-size: 14px; margin: 0;">Hotline: 0947.58.1516</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    
    # CARD 2: LỜI CHÀO BAN QUẢN LÝ
    st.markdown(
        f"""
        <div style="color: {THEME_COLORS['text_main']};">
            <span style="font-size: 14px; color: {THEME_COLORS['text_secondary']};">Chào chị thân yêu,</span>
            <h3 style="margin: 2px 0 8px 0; font-size: 19px; color: {THEME_COLORS['text_title']};">Nguyễn Thị Hiền</h3>
            <span style="font-size: 13px; color: {THEME_COLORS['text_secondary']};">Hôm nay là ngày: <b>30/05/2026</b></span>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # CARD 3: KHU VỰC HIỂN THỊ BIỂU ĐỒ & CHỈ SỐ DOANH THU
    st.markdown(f"<p style='color:{THEME_COLORS['primary']}; font-weight:700; margin-top:15px; margin-bottom:5px;'>📈 TĂNG TRƯỞNG DOANH THU TRONG NGÀY</p>", unsafe_allow_html=True)
    
    # Giả lập 3 cột chỉ số doanh thu gọn gàng trên mobile
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Tổng thu", "5,400,000đ")
    col_m2.metric("Khách", "12 Người")
    col_m3.metric("Chờ", "2 Bill")
