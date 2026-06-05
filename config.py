# config.py
# 1. Định nghĩa bảng màu Minimalism Luxury Edition
THEME_COLORS = {
    "bg_app": "#e8f5f3",
    "bg_card": "#ffffff",
    "bg_box_chung": "#f4f7f6",
    "bg_vip_box": "#e3f2fd",
    "bg_shake_box": "#fff3e0",
    "bg_badge_hang": "#efebe9",
    "bg_marquee": "#f0f008",
    "primary": "rgba(70, 140, 150, 1)",
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


def set_app_background(st, colors):
    # Dùng st truyền vào thay vì st toàn cục
    gradient_css = f"""
        <style>
        .stApp {{ background-color: {colors['bg_app']}; }}
        /* ... CSS của ní ... */
        </style>
    """
    st.markdown(gradient_css, unsafe_allow_html=True)
