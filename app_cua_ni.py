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
        /* ẨN THÀNH PHẦN THỪA KHÔNG CẦN THIẾT */
        header, footer, .stAppDeployButton {display: none !important; visibility: hidden !important;}
        [data-testid="stStatusWidget"], [data-testid="stToolbar"] {display: none !important;}
        
        /* BẢNG HIỆU LKTV HOÀF HẢO KHỚP 100% */
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
            font-size: 32px !important; 
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
    </style>
""", unsafe_allow_html=True)

# --- 2. HÀM HỆ THỐNG ---
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

# --- 3. HÀM CHÍNH ---
def main():
    if "last_submit" not in st.session_state: st.session_state.last_submit = None
    if "submit_count" not in st.session_state: st.session_state.submit_count = 0
    if "submitting" not in st.session_state: st.session_state.submitting = False
    if "logged_in" not in st.session_state:
        st.session_state.update({"logged_in": False, "role": None, "full_name": None})
    
    # Khởi tạo giỏ hàng động
    if "gio_hang" not in st.session_state: st.session_state.gio_hang = []

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
            
            if st.button("➕ THÊM VÀO GIỎ ĐƠN", use_container_width=True):
                if box_sl <= 0:
                    st.error("Vui lòng chọn số lượng lớn hơn 0 trước khi thêm vào giỏ!")
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
                st.warning("⚠️ Nhắc nhở: Giỏ hàng đang trống! Vui lòng chọn dịch vụ và bấm 'Thêm vào giỏ đơn' trước khi Lưu.")
            
            if st.session_state.last_submit and can_go:
                tg_cho = (get_now_vn() - st.session_state.last_submit).total_seconds() / 60
                han_muc = 3 if st.session_state.submit_count == 1 else 5 if st.session_state.submit_count >= 2 else 0
                if tg_cho < han_muc:
                    can_go = False
                    st.error(f"🚫 HÀNG RÀO THÉP: Chờ {round(han_muc - tg_cho, 1)} phút.")

            if can_go:
                cam_ket = st.checkbox("XÁC NHẬN ĐƠN KHÔNG TRÙNG LẶP")
                if not st.session_state.submitting:
                    if st.button("🚀 LƯU VÀO ĐỒNG BỘ ĐƠN HÀNG", use_container_width=True, type="primary"):
                        if cam_ket:
                            st.session_state.submitting = True
                            st.rerun()
                        else: st.error("Chưa tích xác nhận!")
                else:
                    st.button("⚙️ ĐANG XỬ LÝ ĐỒNG BỘ...", disabled=True, use_container_width=True)
                    try:
                        cl = get_gspread_client()
                        ws = cl.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"]).worksheet("BaoCao")
                        bay_gio = get_now_vn()
                        
                        # Sinh Mã Đơn Hàng chuẩn chỉnh
                        ma_hd = f"HD-{bay_gio.strftime('%Y%m%d-%H%M%S')}"
                        
                        # KHỚP CHUẨN ĐÚNG 12 CỘT (Cột L là Mã hoá đơn)
                        rows_to_append = []
                        for item in st.session_state.gio_hang:
                            rows_to_append.append([
                                bay_gio.strftime("%d/%m/%Y"),       # A: Ngày
                                st.session_state.full_name,         # B: Người làm
                                kh_ten,                             # C: Tên khách hàng
                                kh_sdt,                             # D: SĐT khách hàng
                                item['dich_vu'],                    # E: Dịch vụ
                                item['so_luong'],                   # F: Số lượng
                                item['don_gia'],                    # G: Đơn giá
                                item['thanh_tien'],                 # H: Thành tiền
                                bay_gio.strftime("%H:%M:%S"),       # I: Giờ lưu
                                ghi_chu,                            # J: Ghi chú
                                item['tiem_cong_tho'],              # K: Tiền công thợ
                                ma_hd                               # L: Mã hoá đơn (Đã đổi chữ thường theo yêu cầu)
                            ])
                        
                        ws.append_rows(rows_to_append)

                        st.session_state.gio_hang = []
                        st.session_state.last_submit = bay_gio
                        st.session_state.submit_count += 1
                        st.session_state.submitting = False
                        st.success("🎉 ĐỒNG BỘ THÀNH CÔNG! MÃ ĐƠN ĐÃ ĐƯỢC CHÈN VÀO CỘT 'Mã hoá đơn'!")
                        time.sleep(1.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Lỗi lưu đơn: {e}")
                        st.session_state.submitting = False

            st.divider()
            if st.button("🚪 THOÁT APP TÀI KHOẢN", use_container_width=True):
                st.session_state.clear()
                st.rerun()

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
                st.markdown("### 👥 QUẢN LÝ NHÂN SỰ")
                with st.expander("🎫 Tạo/Xem mã nhân viên"):
           
