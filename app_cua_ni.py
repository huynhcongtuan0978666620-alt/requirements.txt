import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import pytz
import time
import re
import random
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# =====================================================================
# CẤU HÌNH GIAO DIỆN VÀ CSS V14 FINAL (Fix toàn bộ 5 lỗi)
# =====================================================================
st.set_page_config(page_title="LKTV DETAILING - VISION 14", layout="centered", page_icon="⚜️", initial_sidebar_state="collapsed")

def get_now_vn():
    vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    return datetime.now(vn_tz)

def inject_advanced_ui_js():
    js_code = """
    <script>
    const parentDoc = window.parent.document;
    
    function showPremiumToast(text) {
        let t = parentDoc.createElement('div');
        t.innerText = text;
        t.style.cssText = "position:fixed; top:15%; left:50%; transform:translate(-50%, -50%); background: linear-gradient(135deg, #1e1e1e, #333333); color:#d4af37; padding:15px 30px; border-radius:8px; font-weight:bold; box-shadow: 0 10px 30px rgba(0,0,0,0.5); z-index:9999999; font-size:15px; text-align:center; border: 1px solid #d4af37;";
        parentDoc.body.appendChild(t);
        setTimeout(() => { t.style.opacity = '0'; t.style.transition = 'opacity 0.5s'; setTimeout(()=>t.remove(), 500); }, 2500);
    }

    // Fix lỗi 4: Đảm bảo JS bắt sự kiện 3 click trên toàn bộ body
    if(!parentDoc.body.hasAttribute('data-fw-v14')) {
        parentDoc.body.setAttribute('data-fw-v14', '1');
        let clicks = 0;
        let timer = null;
        parentDoc.addEventListener('click', (e) => {
            clicks++;
            clearTimeout(timer);
            timer = setTimeout(() => { clicks = 0; }, 1000); // Tăng lên 1 giây để dễ bấm hơn
            if(clicks >= 3) {
                clicks = 0;
                showPremiumToast('🎉 CHÀO MỪNG NÍ ĐẾN VỚI HỆ THỐNG 🎉');
                // Hiệu ứng pháo hoa
                for(let i=0; i<60; i++) {
                    let f = parentDoc.createElement('div');
                    f.style.cssText = `position:fixed; width:8px; height:8px; border-radius:50%; background-color:${['#d4af37', '#ffffff', '#ff4d4f', '#40a9ff', '#52c41a'][Math.floor(Math.random()*5)]}; left:50%; top:50%; transform:translate(-50%, -50%); pointer-events:none; z-index:9999998; transition: all 1.5s cubic-bezier(0.25, 1, 0.5, 1);`;
                    parentDoc.body.appendChild(f);
                    setTimeout(() => {
                        const angle = Math.random() * Math.PI * 2;
                        const dist = 50 + Math.random() * 300;
                        f.style.left = `calc(50% + ${Math.cos(angle)*dist}px)`;
                        f.style.top = `calc(50% + ${Math.sin(angle)*dist}px)`;
                        f.style.opacity = '0';
                    }, 50);
                    setTimeout(()=>f.remove(), 1600);
                }
            }
        });
    }
    </script>
    """
    st.components.v1.html(js_code, height=0, width=0)

def generate_css_animations(theme="light", role=None):
    is_dark = (theme == "dark")
    bg_app = "#121212" if is_dark else "#f8f9fa"
    bg_box = "#1e1e1e" if is_dark else "#ffffff"
    text_color = "#ffffff" if is_dark else "#111111"
    border_color = "#333333" if is_dark else "#e0e0e0"
    sub_text = "#aaaaaa" if is_dark else "#666666"
    
    dev_style = "footer { display: none !important; }" if role == "Admin" else "header, footer, #MainMenu, .stAppDeployButton, [data-testid='stStatusWidget'], [data-testid='stToolbar'], [data-testid='stDecoration'] { display: none !important; }"
    
    return f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
        html, body, .stApp {{ font-family: 'Inter', sans-serif !important; background-color: {bg_app} !important; color: {text_color} !important; }}
        * {{ color: {text_color}; text-decoration: none !important; }}
        
        .stApp {{ padding-top: 50px !important; padding-bottom: 75px !important; }}
        {dev_style}
        
        /* Fix lỗi 3: Phục hồi Banner */
        .banner-top, .banner-bottom {{ position: fixed !important; left: 0 !important; right: 0 !important; height: 40px !important; background: {"#1e1e1e" if is_dark else "#ffffff"} !important; color: {text_color} !important; font-size: 13px !important; font-weight: 700 !important; display: flex !important; align-items: center !important; justify-content: center !important; z-index: 999999 !important; border-bottom: 1px solid {border_color} !important; }}
        .banner-top {{ top: 0px !important; }}
        .banner-bottom {{ bottom: 0 !important; top: auto !important; border-top: 1px solid {border_color} !important; justify-content: center !important; border-bottom: none !important; }}
        
        /* Fix lỗi 2: Ép cứng màu viền và chữ nút bấm (Chống mù màu) */
        div[data-testid="stButton"] button {{
            color: {text_color} !important; 
            border: 1px solid {border_color} !important; 
            background-color: transparent !important;
        }}
        div[data-testid="stButton"] button[kind="primary"] {{ 
            background-color: #d4af37 !important; /* Vàng Gold nổi bật */
            color: #111111 !important; /* Chữ đen luôn thấy rõ */
            border: none !important;
            font-weight: 800 !important;
        }}

        .the-quan-ly-flat {{ font-weight: 800; font-size: 16px; margin-bottom: 15px; border-bottom: 1px solid {border_color}; padding-bottom: 8px; text-align: center; text-transform: uppercase; }}
        .the-quan-ly-phu {{ text-align: right; font-size: 12px; color: {sub_text}; font-weight: 500; margin-top: -10px; margin-bottom: 15px; }}
        
        .nhan-tieu-de {{ font-size: 11px !important; font-weight: 600 !important; margin-bottom: 8px !important; color: {sub_text} !important; text-align: center; }}
        .box-chung {{ background-color: {bg_box}; padding: 15px 10px; border-radius: 8px; text-align: center; border: 1px solid {border_color}; font-size: 18px; font-weight: 800; color: {text_color}; }}
        .chiet-khau-box {{ color: #d93025 !important; }} 
        .khach-tra-box {{ background-color: {text_color} !important; color: {bg_app} !important; }}
        .tien-thua-box {{ background-color: {"#2a2a2a" if is_dark else "#f8f9fa"}; color: {text_color}; padding: 18px; border-radius: 8px; text-align: center; font-size: 18px; font-weight: 700; border: 1px solid {border_color}; margin: 20px 0; }}
        
        .hoa-don-khung {{ background-color: {bg_box} !important; color: {text_color} !important; padding: 30px 25px !important; border-radius: 12px !important; border: 1px solid {border_color} !important; margin-top: 20px !important; box-shadow: 0 8px 24px rgba(0,0,0,0.04); }}
        
        /* ẨN DEFAULT UNDERLINES STREAMLIT */
        .stMarkdown a {{ text-decoration: none !important; }}
    </style>
    """

# =====================================================================
# HỆ THỐNG KẾT NỐI (Rút gọn để tập trung UI, giữ nguyên Logic gốc)
# =====================================================================
@st.cache_resource
def get_google_sheet_workbook():
    try:
        secrets = dict(st.secrets["connections"]["gsheets"]) if "connections" in st.secrets else dict(st.secrets)
        creds_info = { "type": secrets.get("type", "service_account"), "project_id": secrets.get("project_id", "hethongphache"), "private_key_id": secrets.get("private_key_id", ""), "private_key": secrets.get("private_key", "").replace("\\n", "\n"), "client_email": secrets.get("client_email", ""), "client_id": secrets.get("client_id", ""), "auth_uri": secrets.get("auth_uri", "https://accounts.google.com/o/oauth2/auth"), "token_uri": secrets.get("token_uri", "https://oauth2.googleapis.com/token"), "auth_provider_x509_cert_url": secrets.get("auth_provider_x509_cert_url", "https://www.googleapis.com/oauth2/v1/certs"), "client_x509_cert_url": secrets.get("client_x509_cert_url", "") }
        creds = Credentials.from_service_account_info(creds_info, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
        client = gspread.authorize(creds)
        url = secrets.get("spreadsheet", "") or st.secrets.get("spreadsheet", "")
        return client.open_by_key(url) if len(url) < 50 else client.open_by_url(url)
    except Exception as e:
        st.error(f"Lỗi khởi tạo kết nối Google Sheets: {e}"); st.stop()

def format_drive_direct_url(link):
    if not link or not isinstance(link, str): return ""
    match = re.search(r'(pires=|/d/|id=)([a-zA-Z0-9-_]{33,40})', link.strip())
    return f"https://lh3.googleusercontent.com/d/{match.group(2)}" if match else ""

@st.cache_data(ttl=3600)
def get_settings():
    try:
        sh = get_google_sheet_workbook()
        return {str(row[0]).strip(): str(row[1]).strip() for row in sh.worksheet("ThietLap").get_all_values() if len(row) > 1}
    except: return {"TenTiem": "SALON KIM HIỀN", "Diachi": "131, TRẦN BÌNH TRỌNG, LONG XUYÊN", "SDT": "0947.58.1516"}

@st.cache_data(ttl=3600)
def get_service_data():
    try:
        danh_sach_dv = {}
        for row in get_google_sheet_workbook().worksheet("DanhMuc").get_all_values()[1:]:
            if len(row) >= 2 and str(row[0]).strip():
                try: gia_goc = float(str(row[1]).replace('.', '').replace(',', '').strip())
                except: gia_goc = 0.0
                hoa_hong = float(str(row[2]).replace('%', '').replace(',', '.').strip()) if len(row) >= 3 and row[2] else 0.0
                danh_sach_dv[str(row[0]).strip()] = {"gia": gia_goc, "hoa_hong": hoa_hong * 100 if 0 < hoa_hong < 1.0 else hoa_hong}
        return danh_sach_dv
    except: return {}

@st.cache_data(ttl=3600)
def get_nhan_vien_data():
    try: return get_google_sheet_workbook().worksheet("NhanVien").get_all_values()
    except: return []

@st.cache_data(ttl=60)
def get_khach_hang_data():
    try: return {str(r[0]).strip().replace(".0", ""): str(r[1]).strip() for r in get_google_sheet_workbook().worksheet("KhachHang").get_all_values()[1:] if len(r) >= 2 and str(r[0]).strip()}
    except: return {}

@st.cache_data(ttl=15)
def get_plkh_data():
    try: return get_google_sheet_workbook().worksheet("PLKH").get_all_values()
    except: return []

def get_huy_hieu(tong_chi):
    if tong_chi >= 10000000: return "💎 DIAMOND"
    elif tong_chi >= 5000000: return "🥇 GOLD"
    elif tong_chi >= 3000000: return "🥈 SILVER"
    elif tong_chi >= 1000000: return "🥉 THÂN THIẾT"
    return "🌱 TIỀM NĂNG"

@st.cache_data(ttl=300)
def get_bao_cao_va_bill_tam():
    try: sh = get_google_sheet_workbook(); return sh.worksheet("BaoCao").get_all_values(), sh.worksheet("BillTam").get_all_values()
    except: return [], []

def luu_bill_tam(gio_hang, nhan_vien, kh_sdt="", kh_ten="Khách lẻ"):
    try:
        get_google_sheet_workbook().worksheet("BillTam").append_row([get_now_vn().strftime("%Y-%m-%d %H:%M:%S"), " | ".join([f"{i['dich_vu']} (x{i['so_luong']})" for i in gio_hang]), sum([i['thanh_tien'] for i in gio_hang]), nhan_vien, str(kh_sdt).strip(), str(kh_ten).strip(), "CHỜ XỬ LÝ"])
        get_bao_cao_va_bill_tam.clear(); return True
    except: return False

def main():
    if "logged_in" not in st.session_state: st.session_state.update({"logged_in": False, "role": None, "full_name": None, "gio_hang": [], "bill_vua_in": None, "kh_sdt_val": "", "kh_ten_val": "Khách lẻ", "theme": "light", "reset_counter": 0, "tho_chot_val": ""})
    
    st.markdown(generate_css_animations(st.session_state.theme, st.session_state.get("role")), unsafe_allow_html=True)
    inject_advanced_ui_js()
    st.markdown("""<div class="banner-top">QUẢN LÝ DỊCH VỤ</div><div class="banner-bottom">SALON KIM HIỀN © 2026 - VISION 14 FINAL</div>""", unsafe_allow_html=True)

    settings = get_settings()

    # =================================================================
    # Fix lỗi 1: Bảng hiệu sắp xếp từ trên xuống dưới (Dàn dọc)
    # =================================================================
    bg_box = "#1e1e1e" if st.session_state.theme == "dark" else "#ffffff"
    text_color = "#ffffff" if st.session_state.theme == "dark" else "#111111"
    border_color = "#333333" if st.session_state.theme == "dark" else "#e0e0e0"
    sub_text = "#aaaaaa" if st.session_state.theme == "dark" else "#666666"
    
    direct_logo_url = format_drive_direct_url(settings.get('Logo', ''))
    fallback_gif = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
    
    st.markdown(f"""
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; background-color: {bg_box}; border: 1px solid {border_color}; border-radius: 12px; padding: 25px 15px; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
            <img src="{direct_logo_url}" style="width: 85px; height: 85px; border-radius: 50%; border: 2px solid {border_color}; object-fit: cover; margin-bottom: 12px;" onerror="this.onerror=null;this.src='{fallback_gif}';">
            <div style="font-size: 22px; font-weight: 900; color: {text_color}; text-transform: uppercase; letter-spacing: 1px;">{settings.get('TenTiem', 'SALON KIM HIỀN')}</div>
            <div style="font-size: 13px; color: {sub_text}; margin-top: 8px; text-align: center;">
                <div>📍 {settings.get('Diachi', '131, TRẦN BÌNH TRỌNG, LONG XUYÊN')}</div>
                <div style="margin-top: 3px;">📞 Hotline: {settings.get('SDT', '0947.58.1516')}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        if st.button("☀️ Đổi màu nền (Sáng/Tối)", use_container_width=True):
            st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"; st.rerun()
    with c_btn2:
        if st.session_state["logged_in"] and st.button("🚪 Đăng xuất", use_container_width=True):
            st.session_state.clear(); st.rerun()

    if not st.session_state["logged_in"]:
        with st.form("login_section"):
            st.markdown("<div class='the-quan-ly-flat' style='border:none;'>ĐĂNG NHẬP</div>", unsafe_allow_html=True)
            u = st.text_input("Tài khoản (SĐT)")
            p = st.text_input("Mật khẩu", type="password")
            if st.form_submit_button("Xác nhận Đăng Nhập", use_container_width=True, type="primary"):
                if u == "admin" and p == "2026":
                    st.session_state.update({"logged_in": True, "role": "Admin", "full_name": "Quản lý", "tho_chot_val": "Quản lý"}); st.rerun()
                else: st.error("Sai thông tin đăng nhập!")
    else:
        services = get_service_data()
        dv_list = list(services.keys())
        
        st.markdown('<div class="the-quan-ly-flat">THÔNG TIN KHÁCH HÀNG</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1: 
            kh_sdt = st.text_input("SĐT Khách", value=st.session_state.kh_sdt_val)
            if kh_sdt != st.session_state.kh_sdt_val: st.session_state.kh_sdt_val = kh_sdt; st.rerun()
        with c2: 
            kh_ten = st.text_input("Tên Khách", value=st.session_state.kh_ten_val)
            if kh_ten != st.session_state.kh_ten_val: st.session_state.kh_ten_val = kh_ten

        st.markdown('<div class="the-quan-ly-flat" style="margin-top:20px;">CHỌN DỊCH VỤ</div>', unsafe_allow_html=True)
        dv_chon = st.multiselect("Chạm chọn dịch vụ...", options=dv_list, key=f"dv_{st.session_state.reset_counter}")
        
        # Nút nhấn Primary luôn Vàng Gold, chữ Đen (Fix Lỗi 2)
        if st.button("➕ THÊM VÀO GIỎ HÀNG", type="primary", use_container_width=True):
            if dv_chon:
                for dv in dv_chon:
                    st.session_state.gio_hang.append({"dich_vu": dv, "so_luong": 1.0, "don_gia": services.get(dv, {}).get("gia", 0.0), "thanh_tien": services.get(dv, {}).get("gia", 0.0), "phan_tram_hh": services.get(dv, {}).get("hoa_hong", 0.0)})
                st.session_state.reset_counter += 1; st.rerun()
            else: st.warning("Chọn ít nhất 1 dịch vụ!")

        t_bill = sum(i['thanh_tien'] for i in st.session_state.gio_hang)
        if t_bill > 0:
            st.write(f"🛒 **GIỎ HÀNG:** {len(st.session_state.gio_hang)} món | Tổng: {t_bill:,.0f} đ")
            if st.button("Xóa giỏ hàng"): st.session_state.gio_hang = []; st.rerun()
            
            cn1, cn2 = st.columns(2)
            with cn1: tien_giam = st.number_input("Chiết khấu", 0.0, step=1000.0)
            with cn2: kh_dua = st.number_input("Khách đưa", 0.0, value=float(t_bill - tien_giam))
            
            t_khach_tra = t_bill - tien_giam
            
            if st.button("🚀 XÁC NHẬN & XUẤT HÓA ĐƠN", use_container_width=True, type="primary"):
                ma_hd = f"HD{get_now_vn().strftime('%y%m%d%H%M')}"
                html_items = "".join([f"<tr><td style='padding:5px 0;'>{i['dich_vu']}</td><td style='text-align:right;'>{i['thanh_tien']:,.0f}đ</td></tr>" for i in st.session_state.gio_hang])
                
                # Fix lỗi 5: Ép text-align: left cho nhãn Số tiền cần thanh toán
                st.session_state.bill_vua_in = f"""
<div class="hoa-don-khung" style="background: {bg_box}; padding: 20px; border-radius: 10px; border: 1px solid {border_color}; margin-top:20px;">
    <h3 style="text-align:center; margin-bottom: 5px;">HÓA ĐƠN DỊCH VỤ</h3>
    <div style="text-align:center; font-size:12px; color:{sub_text}; margin-bottom: 15px;">Mã: {ma_hd}</div>
    <div style="font-size:14px; margin-bottom: 10px;">Khách: <b>{st.session_state.kh_ten_val}</b></div>
    <table style="width:100%; font-size:14px; margin-bottom: 15px;">{html_items}</table>
    <hr style="border-top:1px dashed {border_color};">
    
    <!-- FIX LỖI 5 Ở DÒNG DƯỚI ĐÂY -->
    <div style="text-align: left !important; font-size: 13px; font-weight: 600; color: {sub_text}; margin-bottom: 5px;">Số tiền cần thanh toán:</div>
    <div style="font-size: 20px; font-weight: 900; color: {text_color}; display: flex; justify-content: space-between;">
        <span>TỔNG CỘNG:</span> <span>{t_khach_tra:,.0f} đ</span>
    </div>
</div>"""
                st.session_state.gio_hang = []; st.rerun()

        if st.session_state.bill_vua_in:
            st.markdown(st.session_state.bill_vua_in, unsafe_allow_html=True)
            if st.button("❌ Ẩn Bill"): st.session_state.bill_vua_in = None; st.rerun()

if __name__ == "__main__":
    main()
