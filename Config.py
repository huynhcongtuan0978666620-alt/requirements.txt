# config.py - File lưu trữ các cấu hình chung của App Kim Hiền

# 1. HỆ THỐNG MÀU SẮC (THEME COLORS)
# Ní dùng dictionary này để quản lý toàn bộ giao diện, dễ chỉnh sửa đồng bộ.
THEME_COLORS = {
    # Màu nền chủ đạo
    "bg_app": "#e8f5f3",  # Nền tổng thể toàn trang
    "bg_card": "#ffffff",  # Nền cho các thẻ (cards)
    "bg_box_chung": "#f4f7f6",  # Nền cho các ô chứa nội dung phụ
    "bg_vip_box": "#e3f2fd",  # Nền riêng cho các khu vực VIP
    "bg_shake_box": "#fff3e0",  # Nền cho hiệu ứng lắc/thông báo
    "bg_badge_hang": "#efebe9",  # Nền các nhãn hạng thành viên
    "bg_marquee": "rgba(70, 140, 150, 1)",  # Màu nền cho chữ chạy (marquee)
    # Màu điểm nhấn (Accents)
    "primary": "rgba(70, 140, 150, 1)",  # Màu chính của thương hiệu
    "accent_vip": "#ffff00",  # Màu nổi bật cho VIP
    "accent_danger": "#d32f2f",  # Màu cảnh báo (lỗi/xóa)
    "accent_zalo": "#0068ff",  # Màu xanh biểu tượng Zalo
    "accent_chiet_khau": "#e65100",  # Màu cho con số chiết khấu
    # Màu chữ (Typography)
    "text_main": "#263238",  # Màu chữ chính, dễ đọc
    "text_secondary": "#546e7a",  # Màu chữ phụ, mô tả nhỏ
    "text_muted": "#90a4ae",  # Màu chữ mờ (vô hiệu hóa)
    "text_title": "#0f4c43",  # Màu tiêu đề (đậm, sang)
    "text_badge": "#ffffff",  # Màu chữ trên các nhãn (badge)
    # Màu đường viền & đổ bóng (Borders & Shadows)
    "border_light": "#eaeaea",  # Đường kẻ mảnh
    "border_input": "#cfd8dc",  # Viền khung nhập liệu
    "border_badge": "#b2dfdb",  # Viền nhãn thành viên
    "border_vip": "#4fc3f7",  # Viền trang trí cho VIP
    "shadow_light": "rgba(0, 0, 0, 0.015)",  # Đổ bóng nhẹ
    "shadow_heavy": "rgba(0, 0, 0, 0.04)",  # Đổ bóng nổi rõ
    "shadow_toast": "rgba(0, 0, 0, 0.6)",  # Đổ bóng cho thông báo nổi (toast)
}
