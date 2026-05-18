import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import pytz
import time
import re

# --- 1. CẤU HÌNH GIAO DIỆN CHUẨN LKTV V25.0 NGUYÊN BẢN ---
st.set_page_config(
    page_title="LKTV DETAILING - IRONCLAD", 
    layout="centered", 
    page_icon="✂️",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
        /* ========================================================= */
        /* 🎨 HỘP CLONE MANAGE APP - SỬA LỖI ĐỒNG SIZE TUYỆT ĐỐI V6    */
        /* ========================================================= */

        /* 1. ẨN THÀNH PHẦN THỪA KHÔNG LIÊN QUAN */
        header, footer, .stAppDeployButton {
            display: none !important;
            visibility: hidden !important;
        }
        [data-testid="stStatusWidget"], [data-testid="stToolbar"] {
            display: none !important;
        }

        /* 2. ĐẢM BẢO KHÔNG GIAN FULL MÀN HÌNH */
        html, body, .stApp {
            height: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        /* 3. ĐỒNG BỘ SIZE THEO TỌA ĐỘ SÁT ĐÁY (FIX HỦT CHIỀU CAO) */
        body::after {
            content: "KIM HIỀN SALON  >" !important;
            position: fixed !important;
            
            /* 💥 TUYỆT CHIÊU: KHÓA CHẶT ĐỈNH VÀ ĐÁY THEO KHUNG HỆ THỐNG GỐC */
            bottom: 0 !important;       
            top: auto !important;
            height: auto !important;    /* Tháo bỏ chiều cao cố định cũ */
            
            /* Đồng bộ khoảng cách đệm từ chân màn hình lên y hệt thanh gốc */
            padding-top: 10px !important;    
            padding-bottom: 12px !important; /* Tràn khít mép dưới điện thoại */
            
            left: 0 !important;         /* Ghim góc trái */
            width: calc(100% - 150px) !important; /* Chừa đúng khoảng cho Manage app */
            
            /* Màu nền và bo góc chuẩn chỉ */
            background-color: #131824 !important; 
            border-top-right-radius: 4px !important; 
            
            /* Phông chữ, cỡ chữ, màu sắc đồng điệu 100% */
            color: #e0e0e0 !important;   
            font-family: Source Sans Pro, -apple-system, BlinkMacSystemFont, sans-serif !important; 
            font-size: 14px !important;  
            font-weight: 400 !important; 
            
            /* Canh chữ nằm ngay ngắn giữa hộp */
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            box-sizing: border-box !important;
            
            border: none !important;
            box-shadow: none !important;
            
            z-index: 9999 !important;
        }



        /* BẢNG HIỆU LKTV HOÀN HẢO KHỚP 100% */
        .bang-hieu-lktv {
            text-align: center;
            background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%) !important;
            color: white !important; 
            padding: 25px !important; 
            border-radius: 20px !important;
            margin-bottom: 25px !important; 
            box-shadow: 0px 10px 30px rgba(0,0,0,0.4) !important;
            border: 1px solid #ffffff20 !important;
        }
        .logo-img { 
            width: 120px !important; 
            height: 120px !important; 
            object-fit: cover !important; 
            border-radius: 50% !important; 
            border: 4px solid #f1c40f !important; 
            margin: 0 auto 12px auto !important; 
            display: block !important;
            box-shadow: 0 0 15px rgba(241, 196, 15, 0.5) !important;
        }
        .ten-tiem { 
            font-size: 26px !important; 
            font-weight: 900 !important; 
            color: #ffffff !important; 
            text-transform: uppercase !important; 
            margin-bottom: 5px !important; 
            letter-spacing: 3px !important;
        }
        .thong-tin-phu { 
            font-size: 16px !important; 
            color: #ecf0f1 !important; 
            opacity: 0.9 !important; 
            margin: 4px 0 !important; 
        }
        .slogan { 
            font-size: 17px !important; 
            color: #f1c40f !important; 
            font-weight: 600 !important; 
            font-style: italic !important; 
            margin-top: 15px !important; 
            border-top: 1px solid #ffffff20 !important; 
            padding-top: 10px !important; 
        }
        
        /* TABS ĐỒNG BỘ */
        .stTabs [data-baseweb="tab-list"] { display: flex; justify-content: center; gap: 15px; width: 100%; }
        .stTabs [data-baseweb="tab"] { flex: 1; height: 60px; background-color: #ffffff; border-radius: 15px 15px 0 0; border: 1px solid #dee2e6;}
        .stTabs [data-baseweb="tab"] p { color: #1a1a1a !important; font-weight: 800 !important; font-size: 17px; text-align: center;}
        .stTabs [data-baseweb="tab"][aria-selected="true"] { background-color: #f1c40f !important; border-bottom: 5px solid #d4ac0d; }

        /* TIÊU ĐỀ NHÃN PHÍA TRÊN BOX ĐÓNG KHUNG */
        .nhan-tieu-de {
            text-align: center; font-size: 16px; font-weight: 800; text-transform: uppercase; margin-bottom: 8px; color: #ffffff;
        }

        /* NÂNG CẤP ĐỒNG BỘ BOX TRỰC QUAN ÔM TRỌN SỐ TIỀN */
        .tong-don-box {
            background-color: #fff3cd; color: #856404; padding: 15px; border-radius: 15px;
            text-align: center; border: 4px dashed #ffc107; font-size: 24px; font-weight: 900;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
        }
        .cong-tho-box {
            background-color: #e2e3e5; color: #28a745; padding: 15px; border-radius: 15px;
            text-align: center; border: 4px dashed #6c757d; font-size: 24px; font-weight: 900;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
        }
        .tien-thua-box {
            background-color: #d4edda; color: #155724; padding: 25px; border-radius: 15px;
            text-align: center; font-size: 26px; font-weight: 800; border: 4px dashed #28a745;
            margin: 20px 0; animation: pulse-steel 2.5s infinite;
        }
        @keyframes pulse-steel { 
            0% {transform: scale(1); box-shadow: 0 0 0 0 rgba(40, 167, 69, 0.4);} 
            70% {transform: scale(1.03); box-shadow: 0 0 0 15px rgba(40, 167, 69, 0);} 
            100% {transform: scale(1);} 
        }

        /* THIẾT KẾ PHÔI HOÁ ĐƠN ĐIỆN TỬ LKTV CỔ ĐIỂN */
        .hoa-don-khung {
            background-color: #ffffff !important; color: #000000 !important; padding: 22px !important;
            border-radius: 12px !important; border: 2px solid #ccc !important; font-family: 'monospace', 'Courier New', Courier !important;
            box-shadow: 0px 4px 15px rgba(0,0,0,0.1) !important; margin-top: 20px !important;
        }
        .hd-header { text-align: center; font-weight: bold; border-bottom: 2px dashed #000; padding-bottom: 10px; margin-bottom: 15px; }
        .hd-title { font-size: 22px; text-transform: uppercase; margin-top: 5px; letter-spacing: 1px; }
        
        /* CẤU TRÚC ĐÒNG BỘ ÉP CHẶT 1 HÀNG KHÔNG CHO XUỐNG DÒNG */
        .hd-row { 
            display: flex !important; 
            justify-content: space-between !important; 
            align-items: center !important;
            margin-bottom: 8px !important; 
            font-size: 13px !important; 
            white-space: nowrap !important; 
            overflow: hidden !important;
            width: 100% !important;
        }
        .hd-row span:first-child {
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            padding-right: 5px !important;
        }
        .hd-items { border-bottom: 1px dashed #000; padding-bottom: 10px; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. HÀM HỆ THỐNG ĐỒNG BỘ ---
def get_now_vn():
    return datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))

def get_gspread_client():
    creds_info = st.secrets["connections"]["gsheets"]
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    return gspread.authorize(creds)

def format_drive_direct_url(link):
    if not link or not isinstance(link, str): return ""
    link = link.strip()
    match = re.search(r'(pires=|/d/|id=)([a-zA-Z0-9-_]{33,40})', link)
    if match:
        f_id = match.group(2)
        return f"https://lh3.googleusercontent.com/d/{f_id}"
    return ""

@st.cache_data(ttl=5)
def get_settings():
    try:
        client = get_gspread_client()
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sh = client.open_by_url(url)
        rows = sh.worksheet("ThietLap").get_all_values()
        return {str(row[0]).strip(): str(row[1]).strip() for row in rows if len(row) > 1}
    except Exception:
        return {
            "TenTiem": "SALON KIM HIỀN", 
            "Diachi": "131, TRẦN BÌNH TRỌNG, MỸ XUYÊN, LONG XUYÊN, AN GIANG (AG CŨ)", 
            "SDT": "0978888888",
            "Slogan": "\"Nơi Bạn Đặt Niềm Tin\"",
            "Logo": ""
        }
        # =====================================================================
# 👉 ĐOẠN 2 BẮT ĐẦU TỪ ĐÂY (DÁN SÁT LỀ TRÁI, NỐI TIẾP NGAY DƯỚI ĐOẠN 1)
# =====================================================================
@st.cache_data(ttl=60)
def get_service_data():
    try:
        client = get_gspread_client()
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sh = client.open_by_url(url)
        rows = sh.worksheet("DanhMuc").get_all_values()
        
        danh_sach_dv = {}
        for row in rows[1:]:
            if len(row) >= 2:
                ten_dv = str(row[0]).strip()
                try:
                    gia_goc = float(str(row[1]).replace(',', '').strip())
                except:
                    gia_goc = 0.0
                
                hoa_hong = 0.0
                if len(row) >= 3 and row[2]:
                    try:
                        raw_hh = str(row[2]).replace('%', '').replace(',', '.').strip()
                        hoa_hong = float(raw_hh)
                        if hoa_hong < 1.0 and hoa_hong > 0:
                            hoa_hong = hoa_hong * 100
                    except:
                        hoa_hong = 0.0
                
                danh_sach_dv[ten_dv] = {
                    "gia": gia_goc,
                    "hoa_hong": hoa_hong
                }
        return danh_sach_dv
    except Exception as e: 
        return {}

def display_header(settings):
    raw_logo = settings.get('Logo', '')
    direct_logo_url = format_drive_direct_url(raw_logo)
    fallback_gif = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"

    st.markdown(f"""
        <div class="bang-hieu-lktv">
            <img src="{direct_logo_url}" class="logo-img" onerror="this.onerror=null;this.src='{fallback_gif}';">
            <div class="ten-tiem">{settings.get('TenTiem', 'SALON KIM HIỀN')}</div>
            <div class="thong-tin-phu">📍 {settings.get('Diachi', '131, TRẦN BÌNH TRỌNG, MỸ XUYÊN, LONG XUYÊN, AN GIANG (AG CŨ)')}</div>
            <div class="thong-tin-phu">📞 {settings.get('SDT', '0978888888')}</div>
            <div class="slogan">{settings.get('Slogan', '"Nơi Bạn Đặt Niềm Tin"')}</div>
        </div>
    """, unsafe_allow_html=True)

def main():
    if "last_submit" not in st.session_state: st.session_state.last_submit = None
    if "submit_count" not in st.session_state: st.session_state.submit_count = 0
    if "submitting" not in st.session_state: st.session_state.submitting = False
    if "adding_cart" not in st.session_state: st.session_state.adding_cart = False
    if "logged_in" not in st.session_state:
        st.session_state.update({"logged_in": False, "role": None, "full_name": None})
    
    if "gio_hang" not in st.session_state: st.session_state.gio_hang = []
    if "bill_vua_in" not in st.session_state: st.session_state.bill_vua_in = None

    settings = get_settings()

    if not st.session_state["logged_in"]:
        display_header(settings)
        with st.form("login_section"):
            st.markdown("<h3 style='text-align: center;'>🔐 ĐĂNG NHẬP</h3>", unsafe_allow_html=True)
            u = st.text_input("Tài khoản (SĐT)")
            p = st.text_input("Mật khẩu", type="password")
            if st.form_submit_button("XÁC NHẬN", use_container_width=True):
                if u == "admin" and p == "2026":
                    st.session_state.update({"logged_in": True, "role": "Admin", "full_name": "Chủ Tiệm"})
                    st.rerun()
                else:
                    try:
                        cl = get_gspread_client()
                        sh = cl.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
                        ws_user = sh.worksheet("NhanVien")
                        user_list = ws_user.get_all_records()
                        
                        found_user = None
                        for row in user_list:
                            sdt_sheet = str(row.get('Số Điện Thoại', '')).strip()
                            sdt_nhap = str(u).strip()
                            if sdt_nhap.lstrip('0') == sdt_sheet.lstrip('0') and sdt_nhap.lstrip('0') != "":
                                pass_sheet = str(row.get('Mật Khẩu', '')).strip()
                                if p.strip() == pass_sheet:
                                    found_user = row
                                    break

                        if found_user:
                            ten_that = found_user.get('Tên Nhân Viên', 'Nhân viên')
                            st.session_state.update({
                                "logged_in": True, 
                                "role": "NhanVien", 
                                "full_name": ten_that
                            })
                            st.success(f"Chào mừng {ten_that}!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("SĐT hoặc Mật khẩu không đúng!")
                    except Exception as e:
                        st.error(f"Lỗi đăng nhập: {e}")

    else:
        display_header(settings)
        t_list = ["📝 NHẬP LIỆU", "📈 BÁO CÁO", "⚙️ CÀI ĐẶT"] if st.session_state["role"] == "Admin" else ["📝 NHẬP LIỆU"]
        tabs = st.tabs(t_list)

        with tabs[0]:
            st.info(f"👨‍🔧 **Nhân viên:** {st.session_state.full_name} | 🕒 **Giờ:** {get_now_vn().strftime('%H:%M')}")
                    
            services = get_service_data()
            dv_list = list(services.keys())
            
            c1, c2 = st.columns(2)
            with c1: kh_ten = st.text_input("Tên khách hàng", "Khách lẻ")
            with c2: kh_sdt = st.text_input("SĐT")
            
            st.markdown("#### 🛒 CHỌN DỊCH VỤ THÊM VÀO ĐƠN")
            box_chon_dv = st.selectbox("Dịch vụ", dv_list if dv_list else ["Không có dữ liệu"])
            box_sl = st.number_input("Số lượng", min_value=0.0, max_value=100.0, value=0.0, step=0.5)
            
            if st.session_state.adding_cart:
                st.button("⏳ ĐANG THÊM VÀO GIỎ...", disabled=True, use_container_width=True)
            else:
                if st.button("➕ THÊM VÀO GIỎ ĐƠN", use_container_width=True):
                    if box_sl <= 0:
                        st.error("Vui lòng chọn số lượng lớn hơn 0 trước khi thêm vào giỏ!")
                    else:
                        st.session_state.adding_cart = True
                        da_co = False
                        for item in st.session_state.gio_hang:
                            if item["dich_vu"] == box_chon_dv:
                                da_co = True
                                break
                        
                        if da_co:
                            st.error(f"🚫 CẢNH BÁO: Dịch vụ '{box_chon_dv}' đã có trong giỏ đơn này rồi ní ơi! Không thể thêm trùng lặp.")
                            st.session_state.adding_cart = False
                        else:
                            info_dv = services.get(box_chon_dv, {"gia": 0.0, "hoa_hong": 0.0})
                            gia_goc = info_dv.get("gia", 0.0)
                            phan_tram_hh = info_dv.get("hoa_hong", 0.0)
                            t_bill_item = gia_goc * box_sl
                            t_cong_tho_item = t_bill_item * (phan_tram_hh / 100.0)
                            
                            st.session_state.gio_hang.append({
                                "dich_vu": box_chon_dv,
                                "so_luong": box_sl,
                                "don_gia": gia_goc,
                                "thanh_tien": t_bill_item,
                                "phan_tram_hh": phan_tram_hh,
                                "tiem_cong_tho": t_cong_tho_item
                            })
                            st.success(f"Đã thêm {box_sl} x {box_chon_dv} vào giỏ hàng thành công!")
                            st.session_state.bill_vua_in = None
                            st.session_state.adding_cart = False
                            time.sleep(0.2)
                            st.rerun()
        # =====================================================================
# 👉 ĐOẠN 3 BẮT ĐẦU TỪ ĐÂY (DÁN SÁT LỀ TRÁI, NỐI TIẾP NGAY DƯỚI ĐOẠN 2)
# =====================================================================
            t_bill = 0.0
            t_cong_tho = 0.0
            
            if len(st.session_state.gio_hang) > 0:
                st.markdown("---")
                st.markdown(f"📋 **CHI TIẾT ĐƠN HÀNG CHỜ LƯU ({len(st.session_state.gio_hang)} món)**")
                
                for idx, item in enumerate(st.session_state.gio_hang):
                    col_item1, col_item2, col_item3 = st.columns([5, 3, 2])
                    with col_item1:
                        st.markdown(f"**{idx+1}. {item['dich_vu']}** (SL: {item['so_luong']})")
                    with col_item2:
                        st.markdown(f"{item['thanh_tien']:,.0f} đ (Công: {item['tiem_cong_tho']:,.0f} đ)")
                    with col_item3:
                        if st.button("❌ Xóa", key=f"del_{idx}", use_container_width=True):
                            st.session_state.gio_hang.pop(idx)
                            st.session_state.bill_vua_in = None
                            st.rerun()
                    
                    t_bill += item['thanh_tien']
                    t_cong_tho += item['tiem_cong_tho']
            
            ghi_chu = st.text_input("Ghi chú tổng đơn (nếu có)", placeholder="Ví dụ: Khách hàng rất hài lòng")
            st.divider()
            
            col_bill1, col_bill2 = st.columns(2)
            with col_bill1:
                st.markdown(f"""
                    <div class="nhan-tieu-de" style="color: #ffc107;">Tổng Đơn Khách</div>
                    <div class="tong-don-box">{t_bill:,.0f} đ</div>
                """, unsafe_allow_html=True)
            with col_bill2:
                st.markdown(f"""
                    <div class="nhan-tieu-de" style="color: #a0a5a9;">Tiền công thợ tổng</div>
                    <div class="cong-tho-box">{t_cong_tho:,.0f} đ</div>
                """, unsafe_allow_html=True)
            
            st.write("")
            kh_tra = st.number_input("Tiền khách đưa", 0.0, value=float(t_bill))
            t_du = kh_tra - t_bill
            if t_du > 0:
                st.markdown(f'<div class="tien-thua-box">💵 THỐI LẠI: {t_du:,.0f} đ</div>', unsafe_allow_html=True)

            can_go = True
            if len(st.session_state.gio_hang) == 0:
                can_go = False
                if st.session_state.bill_vua_in is None:
              
