import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import pytz
import time
import re

# Tầng 1: Cấu hình & Giao diện (Frontend)
st.set_page_config(
    page_title="LKTV DETAILING - PREMIUM", 
    layout="centered", 
    page_icon="✂️",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
        /* 1. ĐỒNG BỘ FONT & NỀN */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
        html, body, .stApp, div, span, p, h1, h2, h3, h4, h5, h6, input, button, select, textarea {
            font-family: 'Inter', sans-serif !important;
        }
        .stApp { padding-top: 75px !important; padding-bottom: 60px !important; background-color: #f8f9fa !important; }

        /* ẨN THÀNH PHẦN HỆ THỐNG */
        header, footer, .stAppDeployButton, [data-testid="stStatusWidget"], [data-testid="stToolbar"] {
            display: none !important; visibility: hidden !important; height: 0 !important; width: 0 !important;
        }

        /* 2. CÁC KHỐI THẺ (CARDS) */
        .the-quan-ly-flat {
            background: #ffffff !important; padding: 15px !important; border-radius: 12px !important;
            border-left: 6px solid #7d8f15 !important; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
            text-align: center !important; font-weight: 700 !important; font-size: 14px !important; margin-bottom: 20px !important;
        }
        .nhan-tieu-de { font-size: 13px !important; font-weight: 700 !important; margin-bottom: 5px !important; text-transform: uppercase !important; }
        
        .tong-don-box { background-color: #fef3c7 !important; color: #b45309 !important; padding: 15px !important; border-radius: 12px !important; text-align: center !important; font-size: 24px !important; font-weight: 900 !important; border: 2px dashed #fde68a !important; }
        .cong-tho-box { background-color: #f3f4f6 !important; color: #1f2937 !important; padding: 15px !important; border-radius: 12px !important; text-align: center !important; font-size: 24px !important; font-weight: 900 !important; border: 2px dashed #e5e7eb !important; }
        .tien-thua-box { background-color: #059669 !important; color: #ffffff !important; padding: 12px !important; border-radius: 12px !important; text-align: center !important; font-size: 16px !important; font-weight: 700 !important; margin-top: 15px !important; box-shadow: 0 4px 10px rgba(5, 150, 105, 0.3) !important; }

        /* 3. BANNER ĐỈNH & ĐÁY */
        .banner-top, .banner-bottom {
            position: fixed !important; left: 0 !important; right: 0 !important; height: 48px !important;
            background: #111111 !important; color: #f1c40f !important; font-size: 15px !important; font-weight: 800 !important;
            display: flex !important; align-items: center !important; cursor: pointer !important; z-index: 999999 !important;
        }
        .banner-top { top: 0 !important; justify-content: center !important; border-bottom: 3px solid #7d8f15 !important; }
        .banner-bottom { bottom: 0 !important; padding-left: 20px !important; border-top: 3px solid #7d8f15 !important; }

        /* 4. TABS & NÚT BẤM */
        [data-testid="stTabs"] [role="tablist"] { display: flex !important; width: 100% !important; justify-content: center !important; gap: 6px !important; padding: 0 !important; margin: 0 auto 15px auto !important; }
        button[data-baseweb="tab"] {
            flex: 1 1 100% !important; height: 54px !important; display: flex !important; align-items: center !important;
            justify-content: center !important; background-color: #e2e8f0 !important; border-radius: 10px !important; border: none !important;
        }
        button[data-baseweb="tab"][aria-selected="true"] { background-color: #f1c40f !important; box-shadow: 0 4px 12px rgba(241, 196, 15, 0.4) !important; }
        button[data-baseweb="tab"] p, button[data-baseweb="tab"] span { color: #334155 !important; font-weight: 700 !important; }
        button[data-baseweb="tab"][aria-selected="true"] p, button[data-baseweb="tab"][aria-selected="true"] span { color: #000000 !important; font-weight: 900 !important; }

        /* 5. HÓA ĐƠN */
        .hoa-don-khung { background-color: #ffffff !important; color: #111111 !important; padding: 25px !important; border-radius: 16px !important; border: 2px solid #111111 !important; font-family: monospace !important; box-shadow: 0px 10px 25px rgba(0,0,0,0.08) !important; margin-top: 20px !important; }
        .hd-row { display: flex !important; justify-content: space-between !important; margin-bottom: 8px !important; font-size: 13px !important; }
    </style>

    <div class="banner-top" onclick="createFirework(event)">⭐⭐⭐ SALON KIM HIỀN ⭐⭐⭐</div>
    <div class="banner-bottom" onclick="createFirework(event)"> KIM HIỀN 2026 🌹🌹🌹 </div>

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
# 3. LUỒNG ĐIỀU HƯỚNG CHÍNH (MAIN APPLICATION LOGIC) - ĐÃ TỐI ƯU
# =====================================================================
def main():
    # 1. Khởi tạo State
    init_states = {"last_submit": None, "submit_count": 0, "submitting": False, "adding_cart": False, "logged_in": False, "role": None, "full_name": None, "gio_hang": [], "bill_vua_in": None}
    for key, val in init_states.items():
        if key not in st.session_state: st.session_state[key] = val

    settings = get_settings()

    # 2. Phân hệ đăng nhập
    if not st.session_state["logged_in"]:
        display_header(settings)
        with st.form("login_section"):
            st.markdown("<h3 style='text-align: center; color: #f1c40f;'>🔐 ĐĂNG NHẬP</h3>", unsafe_allow_html=True)
            u = st.text_input("Tài khoản (SĐT)")
            p = st.text_input("Mật khẩu", type="password")
            if st.form_submit_button("XÁC NHẬN ĐĂNG NHẬP", use_container_width=True):
                # (Phần logic xác thực giữ nguyên của ní)
                if u == "admin" and p == "2026":
                    st.session_state.update({"logged_in": True, "role": "Admin", "full_name": "Chủ Tiệm"}); st.rerun()
                else:
                    # Gọi hàm xác thực từ Google Sheets tại đây...
                    pass

    # 3. Phân hệ hoạt động chính
    else:
        display_header(settings)
        t_list = ["🛒 NHẬP LIỆU", "📈 BÁO CÁO", "⚙️ CÀI ĐẶT"] if st.session_state["role"] == "Admin" else ["🛒 NHẬP LIỆU"]
        tabs = st.tabs(t_list)

        # --- TAB 1: NHẬP LIỆU ---
        with tabs[0]:
            st.info(f"👨‍🔧 **Nhân viên:** {st.session_state.full_name} | 🕒 {get_now_vn().strftime('%H:%M')}")
            st.markdown('<div class="the-quan-ly-flat">📝 NHẬP "ĐƠN HÀNG" BÊN DƯỚI NHÉ!</div>', unsafe_allow_html=True)
            
            # Form chọn dịch vụ
            services = get_service_data()
            c1, c2 = st.columns(2)
            kh_ten = c1.text_input("👤 Tên khách", "Khách lẻ")
            kh_sdt = c2.text_input("📞 SĐT khách")
            
            box_chon_dv = st.selectbox("📌 Dịch vụ", options=list(services.keys()) if services else ["Không có dữ liệu"], index=None)
            box_sl = st.number_input("🔢 Số lượng", min_value=0.0, step=0.5)
            
            if st.button("✅ THÊM VÀO GIỎ ĐƠN", use_container_width=True):
                # ... (Logic thêm vào giỏ hàng giữ nguyên của ní)
                st.rerun()

            # Giỏ hàng & Thanh toán
            if st.session_state.gio_hang:
                # ... (Hiển thị chi tiết đơn và logic tính tiền, chốt đơn)
                pass
            
            if st.session_state.bill_vua_in:
                st.markdown(st.session_state.bill_vua_in, unsafe_allow_html=True)

        # --- TAB 2: BÁO CÁO (CHỈ ADMIN) ---
        if st.session_state["role"] == "Admin":
            with tabs[1]:
                st.markdown("### 📊 DOANH THU REALTIME")
                try:
                    # Gọi dữ liệu BaoCao và hiển thị DataFrame
                    st.dataframe(pd.DataFrame(get_gspread_client().open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"]).worksheet("BaoCao").get_all_records()), use_container_width=True)
                except Exception as e: st.error(f"Lỗi: {e}")

            # --- TAB 3: CÀI ĐẶT (CHỈ ADMIN) ---
            with tabs[2]:
                st.markdown("### ⚙️ HỆ THỐNG QUẢN TRỊ")
                # ... (Logic thêm tài khoản nhân viên của ní)

            st.divider()
            if st.button("🚪 THOÁT HỆ THỐNG", use_container_width=True):
                st.session_state.clear(); st.rerun()

if __name__ == "__main__":
    main()
