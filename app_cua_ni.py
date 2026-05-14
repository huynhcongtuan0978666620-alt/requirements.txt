import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import pytz
import hashlib
import time

# --- 1. CẤU HÌNH GIAO DIỆN CHUẨN LKTV (KHÔNG XOÁ CŨ) ---
st.set_page_config(
    page_title="LKTV DETAILING - IRONCLAD", 
    layout="centered", 
    page_icon="✂️",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
        /* ẨN CÁC THÀNH PHẦN THỪA */
        header, footer, .stAppDeployButton {display: none !important; visibility: hidden !important;}
        [data-testid="stStatusWidget"], [data-testid="stToolbar"] {display: none !important;}
        
        /* BẢNG HIỆU LKTV V25.5 QUAY TRỞ LẠI */
        .bang-hieu-lktv {
            text-align: center;
            background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
            color: white; 
            padding: 25px; 
            border-radius: 20px;
            margin-bottom: 25px; 
            box-shadow: 0px 10px 30px rgba(0,0,0,0.4);
            border: 1px solid #ffffff20;
        }
        .logo-img { 
            width: 120px; 
            height: 120px; 
            object-fit: cover; 
            border-radius: 50%; 
            border: 4px solid #f1c40f; 
            margin-bottom: 12px; 
            box-shadow: 0 0 15px rgba(241, 196, 15, 0.5);
        }
        .ten-tiem { 
            font-size: 32px; 
            font-weight: 900; 
            color: #ffffff; 
            text-transform: uppercase; 
            margin-bottom: 5px; 
            letter-spacing: 3px;
        }
        .thong-tin-phu { 
            font-size: 16px; 
            color: #ecf0f1; 
            opacity: 0.9; 
            margin-bottom: 4px; 
        }
        .slogan { 
            font-size: 17px; 
            color: #f1c40f; 
            font-weight: 600; 
            font-style: italic; 
            margin-top: 15px; 
            border-top: 1px solid #ffffff20; 
            padding-top: 10px; 
        }
        
        /* CẤU TRÚC TABS V25.5 */
        .stTabs [data-baseweb="tab-list"] { 
            display: flex; 
            justify-content: center; 
            gap: 15px; 
            width: 100%; 
        }
        .stTabs [data-baseweb="tab"] { 
            flex: 1; 
            height: 60px; 
            background-color: #ffffff; 
            border-radius: 15px 15px 0 0; 
            border: 1px solid #dee2e6;
        }
        .stTabs [data-baseweb="tab"] p { 
            color: #1a1a1a !important; 
            font-weight: 800 !important; 
            font-size: 17px; 
            text-align: center;
        }
        .stTabs [data-baseweb="tab"][aria-selected="true"] { 
            background-color: #f1c40f !important; 
            border-bottom: 5px solid #d4ac0d; 
        }

        /* BOX TIỀN THỪA CÓ HIỆU ỨNG PULSE */
        .tien-thua-box {
            background-color: #d4edda; 
            color: #155724; 
            padding: 25px; 
            border-radius: 15px;
            text-align: center; 
            font-size: 26px; 
            font-weight: 800; 
            border: 4px dashed #28a745;
            margin: 20px 0; 
            animation: pulse-steel 2.5s infinite;
        }
        @keyframes pulse-steel { 
            0% {transform: scale(1); box-shadow: 0 0 0 0 rgba(40, 167, 69, 0.4);} 
            70% {transform: scale(1.03); box-shadow: 0 0 0 15px rgba(40, 167, 69, 0);} 
            100% {transform: scale(1);} 
        }
    </style>
""", unsafe_allow_html=True)

# --- 2. HÀM HỆ THỐNG (GIỮ NGUYÊN) ---
def get_now_vn():
    return datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))

def format_drive_link(link):
    if not link or not isinstance(link, str): return ""
    if 'drive.google.com' in link:
        f_id = ""
        if 'file/d/' in link: f_id = link.split('file/d/')[1].split('/')[0]
        elif 'id=' in link: f_id = link.split('id=')[1].split('&')[0]
        if f_id: return f'https://lh3.googleusercontent.com/d/{f_id}'
    return link

def get_gspread_client():
    creds_info = st.secrets["connections"]["gsheets"]
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    return gspread.authorize(creds)

@st.cache_data(ttl=60)
def get_settings():
    try:
        client = get_gspread_client()
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sh = client.open_by_url(url)
        rows = sh.worksheet("ThietLap").get_all_values()
        return {row[0]: row[1] for row in rows if len(row) > 1}
    except Exception:
        return {"TenTiem": "SALON KIM HIỀN", "Diachi": "131 Trần Bình Trọng", "SDT": "0978.888.888"}

@st.cache_data(ttl=60)
def get_service_data():
    try:
        client = get_gspread_client()
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sh = client.open_by_url(url)
        rows = sh.worksheet("DanhMuc").get_all_values()
        return {row[0]: float(row[1]) for row in rows[1:] if len(row) > 1}
    except: return {}

def display_header(settings):
    l_url = format_drive_link(settings.get('LogoURL', ''))
    st.markdown(f"""
        <div class="bang-hieu-lktv">
            <img src="{l_url}" class="logo-img">
            <div class="ten-tiem">{settings.get('TenTiem')}</div>
            <div class="thong-tin-phu">📍 {settings.get('Diachi')}</div>
            <div class="thong-tin-phu">📞 {settings.get('SDT')}</div>
            <div class="slogan">{settings.get('Slogan', 'Đẳng Cấp Chăm Sóc Xe')}</div>
        </div>
    """, unsafe_allow_html=True)

# --- 3. HÀM CHÍNH ---
def main():
    if "last_submit" not in st.session_state: st.session_state.last_submit = None
    if "submit_count" not in st.session_state: st.session_state.submit_count = 0
    if "submitting" not in st.session_state: st.session_state.submitting = False
    if "logged_in" not in st.session_state:
        st.session_state.update({"logged_in": False, "role": None, "full_name": None})

    settings = get_settings()

    if not st.session_state["logged_in"]:
        display_header(settings)
        with st.form("login_section"):
            st.markdown("<h3 style='text-align: center;'>🔐 ĐĂNG NHẬP</h3>", unsafe_allow_html=True)
            u = st.text_input("Tài khoản")
            p = st.text_input("Mật khẩu", type="password")
            if st.form_submit_button("XÁC NHẬN", use_container_width=True):
                if u == "admin" and p == "2026":
                    st.session_state.update({"logged_in": True, "role": "Admin", "full_name": "Chủ Tiệm"})
                    st.rerun()
                else: st.error("Sai thông tin!")
    else:
        display_header(settings)
        t_list = ["📝 NHẬP LIỆU", "📈 BÁO CÁO", "⚙️ CÀI ĐẶT"] if st.session_state["role"] == "Admin" else ["📝 NHẬP LIỆU"]
        tabs = st.tabs(t_list)

        with tabs[0]:
            st.info(f"👨‍🔧 **Nhân viên:** {st.session_state.full_name} | 🕒 **Giờ:** {get_now_vn().strftime('%H:%M')}")
            services = get_service_data()
            
            c1, c2 = st.columns(2)
            with c1: kh_ten = st.text_input("Tên khách hàng", "Khách lẻ")
            with c2: kh_sdt = st.text_input("SĐT")
            
            dv_chon = st.selectbox("Dịch vụ", list(services.keys()))
            dv_sl = st.number_input("Số lượng", 0.5, 100.0, 1.0, 0.5)
            
            gia_goc = services.get(dv_chon, 0)
            t_bill = gia_goc * dv_sl
            
            st.divider()
            st.markdown(f"<h2 style='text-align: center; color: #f1c40f;'>TỔNG: {t_bill:,.0f} đ</h2>", unsafe_allow_html=True)
            
            kh_tra = st.number_input("Tiền khách đưa", 0.0, value=float(t_bill))
            t_du = kh_tra - t_bill
            if t_du > 0:
                st.markdown(f'<div class="tien-thua-box">💵 THỐI LẠI: {t_du:,.0f} đ</div>', unsafe_allow_html=True)

            # --- HÀNG RÀO THÉP (CẤM XOÁ) ---
            can_go = True
            if st.session_state.last_submit:
                tg_cho = (get_now_vn() - st.session_state.last_submit).total_seconds() / 60
                han_muc = 3 if st.session_state.submit_count == 1 else 5 if st.session_state.submit_count >= 2 else 0
                if tg_cho < han_muc:
                    can_go = False
                    st.error(f"🚫 HÀNG RÀO THÉP: Chờ {round(han_muc - tg_cho, 1)} phút.")

            if can_go:
                cam_ket = st.checkbox("XÁC NHẬN ĐƠN KHÔNG TRÙNG LẶP")
                if not st.session_state.submitting:
                    if st.button("🚀 LƯU VÀO SHEET", use_container_width=True, type="primary"):
                        if cam_ket:
                            st.session_state.submitting = True
                            st.rerun()
                        else: st.error("Chưa tích xác nhận!")
                else:
                    st.button("⚙️ ĐANG XỬ LÝ...", disabled=True, use_container_width=True)
                    try:
                        cl = get_gspread_client()
                        ws = cl.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"]).worksheet("BaoCao")
                        bay_gio = get_now_vn()
                        
                        # --- FIX LỖI LỆCH CỘT (TỪ ẢNH 1778781088101.jpg) ---
                        # Tuyệt đối đủ 9 cột để không bị nhảy giờ sang cột thanh toán
                        ws.append_row([
                            bay_gio.strftime("%d/%m/%Y"), # 1. Ngày
                            st.session_state.full_name,   # 2. NV
                            kh_ten,                       # 3. Khách
                            kh_sdt,                       # 4. SĐT
                            dv_chon,                      # 5. Dịch vụ
                            dv_sl,                        # 6. SL
                            gia_goc,                      # 7. Đơn giá
                            t_bill,                       # 8. Thành tiền
                            bay_gio.strftime("%H:%M:%S")  # 9. Giờ lưu (Fix lệch)
                        ])
                        
                        st.session_state.last_submit = bay_gio
                        st.session_state.submit_count += 1
                        st.session_state.submitting = False
                        st.success("🎉 LƯU THÀNH CÔNG!")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Lỗi: {e}")
                        st.session_state.submitting = False

        if st.session_state["role"] == "Admin":
            with tabs[1]:
                st.subheader("📈 DOANH THU THỰC TẾ")
                try:
                    cl = get_gspread_client()
                    ws_bc = cl.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"]).worksheet("BaoCao")
                    du_lieu = ws_bc.get_all_records()
                    if du_lieu:
                        df_bc = pd.DataFrame(du_lieu)
                        st.dataframe(df_bc.tail(50), use_container_width=True)
                        ngay_nay = get_now_vn().strftime("%d/%m/%Y")
                        df_h = df_bc[df_bc['Ngày'] == ngay_nay]
                        
                        c1, c2, c3 = st.columns(3)
                        c1.metric("HÔM NAY", f"{df_h['Thành tiền'].sum():,.0f}")
                        c2.metric("SỐ ĐƠN", len(df_h))
                        c3.metric("TRUNG BÌNH", f"{df_h['Thành tiền'].mean() if len(df_h)>0 else 0:,.0f}")
                    else: st.info("Trống.")
                except Exception as e: st.error(f"Lỗi báo cáo: {e}")

            with tabs[2]:
                st.subheader("⚙️ QUẢN TRỊ")
                with st.expander("🔗 LIÊN KẾT SHEET"):
                    st.markdown(f"[Mở File Google Sheets]({st.secrets['connections']['gsheets']['spreadsheet']})")
                if st.button("🧹 CLEAR CACHE"):
                    st.cache_data.clear()
                    st.rerun()
                st.divider()
                if st.button("🚪 ĐĂNG XUẤT", use_container_width=True):
                    st.session_state.clear()
                    st.rerun()

if __name__ == "__main__":
    main()
    
