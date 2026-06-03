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


# =====================================================================
# 🌟 TÍNH NĂNG 3 & 4: BÓC TÁCH BẢNG MÀU & ĐỔI GIAO DIỆN THEO MÚI GIỜ (NGÀY/ĐÊM)
# =====================================================================
def get_now_vn():
    vn_tz = pytz.timezone("Asia/Ho_Chi_Minh")
    return datetime.now(vn_tz)


def get_dynamic_theme_colors():
    """
    Tự động bóc tách và chuyển đổi bảng màu thông minh theo thời gian thực tại Việt Nam.
    - Ban ngày (6h - 18h): Tông màu Minimalism Luxury sáng nhẹ nhàng, nhã nhặn.
    - Ban đêm (18h - 6h): Tông màu Luxury Dim/Dark trầm ấm, quý phái (Không dùng trắng/đen mặc định).
    """
    now_vn = get_now_vn()
    hour = now_vn.hour

    if 6 <= hour < 18:
        # GIAO DIỆN BAN NGÀY - TƯƠI SÁNG & SANG TRỌNG
        return {
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
    else:
        # GIAO DIỆN BAN ĐÊM - TRẦM ẤM, ĐẲNG CẤP & DỊU MẮT
        return {
            "bg_app": "#121a1f",
            "bg_card": "#1a242b",
            "bg_box_chung": "#222f38",
            "bg_vip_box": "#163344",
            "bg_shake_box": "#362921",
            "bg_badge_hang": "#2b2d31",
            "bg_marquee": "#424203",
            "primary": "#3a848f",
            "accent_vip": "#e5a900",
            "accent_danger": "#ff4d4d",
            "accent_zalo": "#1a73e8",
            "accent_chiet_khau": "#ff8c00",
            "text_main": "#e1e7eb",
            "text_secondary": "#9aa8b3",
            "text_muted": "#6a7985",
            "text_title": "#4fa396",
            "text_badge": "#ffffff",
            "border_light": "#23303a",
            "border_input": "#2d3d4a",
            "border_badge": "#204652",
            "border_vip": "#2196f3",
            "shadow_light": "rgba(0, 0, 0, 0.2)",
            "shadow_heavy": "rgba(0, 0, 0, 0.4)",
            "shadow_toast": "rgba(0, 0, 0, 0.8)",
        }


# Khởi tạo bảng màu động ngay đầu luồng render
THEME_COLORS = get_dynamic_theme_colors()

# Cấu hình trang tối ưu riêng cho giao diện điện thoại
st.set_page_config(
    page_title="SALON PRO V16",
    layout="wide",
    page_icon="💇‍♀️",
    initial_sidebar_state="collapsed",
)

# KÍCH HOẠT PWA TỰ ĐỘNG
components.html(
    """
    <script>
      if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js')
        .then(reg => console.log('✅ Service Worker kết nối thành công!'))
        .catch(err => console.log('❌ Service Worker lỗi:', err));
      }
    </script>
    """,
    height=0,
)


def set_app_background(colors):
    gradient_css = f"""
    <style>
    .stApp {{
        background: linear-gradient(180deg, {colors['bg_app']} 20%, {colors['bg_app']} 80%);
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(gradient_css, unsafe_allow_html=True)


set_app_background(THEME_COLORS)


# =====================================================================
# 📍 BỘ THEO DÕI TRẠNG THÁI TOÀN CỤC & HIỆU ỨNG GIAO DIỆN NÂNG CAO
# =====================================================================
@st.cache_resource
def get_global_user_tracker():
    return {}


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
        
        const urlParams = new URLSearchParams(window.parent.location.search);
        const activeTabIdx = urlParams.get('tab');
        if (activeTabIdx !== null && parseInt(activeTabIdx) < tabs.length) {{
            if (tabs[activeTabIdx].getAttribute('aria-selected') !== 'true') {{
                tabs[activeTabIdx].click();
            }}
        }}

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
    
    // --- HIỆU ỨNG 3 CLICK NỔ CONFETTI CHÚC MỪNG ---
    if(!parentDoc.body.hasAttribute('data-fw-v16')) {{
        parentDoc.body.setAttribute('data-fw-v16', '1');
        let clicks = 0;
        let timer = null;
        parentDoc.addEventListener('click', (e) => {{
            clicks++;
            clearTimeout(timer);
            timer = setTimeout(() => {{ clicks = 0; }}, 1000); 
            if(clicks >= 3) {{
                clicks = 0;
                showPremiumToast('🎉 CỐ LÊN NHÉ NÍ ƠI! BÃO ĐƠN NÀO! 🎉');
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
    components.html(js_code, height=0, width=0)


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


def apply_v16_theme():
    p = THEME_COLORS["primary"]
    bg = THEME_COLORS["bg_app"]
    card = THEME_COLORS["bg_card"]
    shadow = THEME_COLORS["shadow_light"]
    txt_main = THEME_COLORS["text_main"]
    txt_secondary = THEME_COLORS["text_secondary"]
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
        
        [data-testid="stVerticalBlock"] {{ gap: 14px !important; }}
    
        /* Thanh Tab nguyên bản đẳng cấp phẳng */
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
        }}
        button[data-baseweb="tab"][aria-selected="true"] p {{ 
            color: {p} !important; 
        }}
        div[data-testid="stTabsTabBorder"] {{ 
            background-color: {p} !important;
            height: 2px !important;
        }}
        
        /* Khối thẻ Card phẳng tối giản sang trọng */
        [data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: {card} !important; 
            border: 1px solid {b_light} !important; 
            border-radius: 16px !important;
            box-shadow: 0 4px 16px {shadow} !important;
            padding: 24px !important; 
            margin-bottom: 15px !important;
        }}
        
        /* Chữ chạy viền thuốc tối ưu riêng biệt màu nền */
        .custom-marquee {{
            background-color: {bg_marquee} !important;
            color: {txt_title} !important; 
            padding: 12px 20px !important; 
            height: 48px !important;       
            border-radius: 12px !important; 
            font-weight: 600 !important;
            font-size: 14px !important;
            border: 1px solid rgba(15, 76, 67, 0.1) !important;
            margin-bottom: 20px !important;
            width: 100% !important;
            overflow: hidden !important;
            display: flex !important;
            align-items: center !important;
        }}
        
        /* Tinh chỉnh hệ thống Nút bấm mượt mà */
        div[data-testid="stButton"] button {{ 
            border-radius: 10px !important; 
            font-weight: 600 !important; 
            border: 1px solid {b_light} !important; 
            background: {card} !important; 
            transition: all 0.15s ease !important;
            color: {txt_main} !important;
        }}
        div[data-testid="stButton"] button:hover {{ border-color: {p} !important; color: {p} !important; }}
        
        div[data-testid="stButton"] button[kind="primary"] {{ 
            background-color: {p} !important; 
            color: #ffffff !important; 
            border: none !important; 
        }}
        div[data-testid="stButton"] button[kind="primary"] p {{ color: #ffffff !important; }}
        
        /* Giao diện biểu mẫu bổ trợ */
        .stTextInput>div>div>input, .stNumberInput>div>div>input, .stDateInput>div>div>input, .stTimeInput>div>div>input, .stTextArea>div>div>textarea {{ 
            background-color: {card} !important;
            border-radius: 8px !important; 
            border: 1px solid {b_input} !important; 
            color: {txt_main} !important; 
        }}
        .the-quan-ly-flat {{ color: {txt_title}; font-weight: 800; font-size: 18px; margin-top: 15px !important; margin-bottom: 15px !important; border-bottom: 2px solid {p}; padding-bottom: 8px; text-transform: uppercase; }}
        .box-chung {{ background-color: {THEME_COLORS['bg_box_chung']}; padding: 10px; border-radius: 10px; text-align: center; border: 1px solid {b_light}; font-size: 18px; font-weight: 800; color: {txt_main}; }}
        .chiet-khau-box {{ color: {THEME_COLORS['accent_chiet_khau']} !important; }} 
        .khach-tra-box {{ background-color: {p} !important; color: #ffffff !important; border:none; }}
        .tien-thua-box {{ background-color: {THEME_COLORS['bg_box_chung']}; color: {txt_main}; padding: 15px; border-radius: 10px; text-align: center; font-size: 18px; font-weight: 700; border: 1px dashed {p}; margin: 10px 0; }}
        .hoa-don-khung {{ background-color: {card} !important; color: {txt_main} !important; padding: 20px !important; border-radius: 15px !important; border-top: 6px solid {p} !important; box-shadow: 0 6px 20px {THEME_COLORS['shadow_heavy']}; margin-top: 5px; }}
        .lsc-shake {{ background-color: {THEME_COLORS['bg_shake_box']}; color: {THEME_COLORS['accent_danger']} !important; padding: 10px; border-radius: 8px; text-align: center; font-size: 13px; font-weight:600; margin-bottom: 10px; border-left: 4px solid {THEME_COLORS['accent_danger']}; }}
        .lsc-vip {{ background-color: {THEME_COLORS['bg_vip_box']}; color: {THEME_COLORS['accent_vip']} !important; padding: 8px; border-radius: 8px; text-align: center; font-size: 13px; margin-bottom: 8px; font-weight: 700; border: 1px solid {THEME_COLORS['border_vip']}; }}
        .lich-hen-item {{ background: {card}; padding: 12px; border-radius: 10px; border: 1px solid {b_light}; border-left: 4px solid {p}; margin-bottom: 8px; color: {txt_main}; }}
    </style>
    """,
        unsafe_allow_html=True,
    )


apply_v16_theme()

# Hiển thị chữ chạy Marquee chào mừng ở đầu ứng dụng
ten_dang_nhap = st.session_state.get("full_name", "Quý khách")
marquee_code = f"""
<div class="custom-marquee">
    <marquee scrollamount="4">
        CHÀO MỪNG <span style="color: {THEME_COLORS['accent_danger']}; font-weight: bold;">{ten_dang_nhap}</span> ĐẾN VỚI HỆ THỐNG SALON! 
        CHÚC NÍ MỘT NGÀY BÃO ĐƠN VÀ CHỐT THẬT NHIỀU BILL NHA!
    </marquee>
</div>
"""
st.markdown(marquee_code, unsafe_allow_html=True)


# =====================================================================
# 2. CƠ CHẾ KẾT NỐI VÀ HÀM TRUY XUẤT DỮ LIỆU ĐỒNG BỘ GOOGLE SHEETS
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
        return client.open_by_key(url) if len(url) < 50 else client.open_by_url(url)
    except Exception as e:
        st.error(f"Lỗi kết nối bộ cơ sở dữ liệu Sheets: {e}")
        st.stop()


@st.cache_data(ttl=60)
def get_orders_count_today():
    """TÍNH NĂNG 1: Đếm số lượng đơn hàng đã chốt thành công trong ngày hôm nay"""
    try:
        sh = get_google_sheet_workbook()
        rows = sh.worksheet("DoanhThu").get_all_values()
        if len(rows) <= 1:
            return 0

        ngay_hom_nay = get_now_vn().strftime("%d/%m/%Y")
        count = 0
        for row in rows[1:]:
            if len(row) > 0 and str(row[0]).strip() == ngay_hom_nay:
                count += 1
        return count
    except Exception:
        return 0


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


@st.cache_data(ttl=30)
def get_lich_hen_data():
    try:
        sh = get_google_sheet_workbook()
        return sh.worksheet("LichHen").get_all_records()
    except Exception:
        return []


# =====================================================================
# 4. LUỒNG ĐIỀU HƯỚNG VÀ GIAO DIỆN CHỨC NĂNG CHÍNH
# =====================================================================
def main():
    inject_advanced_ui_js()

    # Khởi tạo trạng thái mặc định cho ứng dụng
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = True
        st.session_state.role = "Admin"
        st.session_state.full_name = "Huỳnh Công Tuấn"

    # PHÂN QUYỀN GIAO DIỆN ADMIN
    if st.session_state.role == "Admin":
        st.markdown(
            '<div class="the-quan-ly-flat">⚙️ BẢNG ĐIỀU KHIỂN HỆ THỐNG QUẢN TRỊ</div>',
            unsafe_allow_html=True,
        )

        # --- TÍNH NĂNG 1: HIỂN THỊ BỘ ĐẾM SỐ ĐƠN HÀNG TRONG NGÀY ---
        total_don_hang = get_orders_count_today()
        st.metric(
            label="📊 Tổng số hóa đơn đã chốt hôm nay",
            value=f"{total_don_hang} đơn hàng",
            delta="Cập nhật thời gian thực",
        )

    # HIỂN THỊ KHU VỰC LỊCH HẸN HÔM NAY
    st.markdown(
        '<div class="the-quan-ly-flat">📅 DANH SÁCH LỊCH HẸN</div>',
        unsafe_allow_html=True,
    )

    lich_hen_list = get_lich_hen_data()

    if not lich_hen_list:
        st.info("Hiện tại chưa có lịch hẹn nào mới được ghi nhận.")
    else:
        for idx, row in enumerate(lich_hen_list):
            tt_val = str(row.get("Trạng thái", "")).strip()
            if tt_val.upper() == "ĐÃ CHỐT ĐƠN":
                continue

            gio = row.get("Giờ", "--:--")
            khach = row.get("Tên Khách", "Khách Lẻ")
            sdt = row.get("Số Điện Thoại", "-------")
            dv = row.get("Dịch Vụ", "Chưa đăng ký")

            # Tối ưu giao diện hiển thị danh sách dạng hàng ngang
            col_info, col_action = st.columns([7, 3])

            with col_info:
                st.markdown(
                    f"""
                    <div class="lich-hen-item">
                        <div style="flex: 1;">
                            <span style="color:{THEME_COLORS['accent_danger']}; font-weight:800; font-size:16px;">⏰ {gio}</span><br>
                            <span style="font-size:13px; font-weight:bold;">👤 {khach} - {sdt}</span><br>
                            <span style="font-size:12px; font-weight:600; color:{THEME_COLORS['primary']};">💇‍♀️ {dv}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with col_action:
                # --- TÍNH NĂNG 2: BỘ ĐÔI NÚT CHỐT NHANH / XÓA LỊCH HẸN TRỰC TIẾP ---
                st.write("")  # Căn chỉnh lề dọc để khớp với thẻ thông tin
                sub_col1, sub_col2 = st.columns(2)

                with sub_col1:
                    if st.button(
                        "✅ Chốt", key=f"btn_chot_{idx}", use_container_width=True
                    ):
                        try:
                            sh = get_google_sheet_workbook()
                            ws = sh.worksheet("LichHen")
                            # Đổi trạng thái lịch hẹn trên Google Sheets thành "Đã chốt đơn"
                            ws.update_cell(idx + 2, 5, "Đã chốt đơn")
                            st.toast(
                                f"🎉 Đã chuyển trạng thái chốt đơn cho khách {khach}!"
                            )
                            st.cache_data.clear()
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Lỗi xử lý: {e}")

                with sub_col2:
                    if st.button(
                        "❌ Xóa", key=f"btn_xoa_{idx}", use_container_width=True
                    ):
                        try:
                            sh = get_google_sheet_workbook()
                            ws = sh.worksheet("LichHen")
                            # Xóa hẳn dòng lịch hẹn đó ra khỏi bộ lưu trữ đám mây Google Sheets
                            ws.delete_rows(idx + 2)
                            st.toast(f"🗑️ Đã xóa lịch hẹn của {khach} thành công!")
                            st.cache_data.clear()
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Lỗi xử lý: {e}")


if __name__ == "__main__":
    main()
