import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import time
import pytz

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN (UI/UX LKTV DETAILING)
# ==========================================
st.set_page_config(page_title="LKTV DETAILING - 2026", layout="centered", page_icon="🧼")

st.markdown("""
    <style>
        /* Ẩn các thành phần thừa của Streamlit */
        header, footer, .stAppDeployButton {display: none !important; visibility: hidden !important;}
        [data-testid="stStatusWidget"], [data-testid="stToolbar"] {display: none !important;}
        #MainMenu {visibility: hidden !important;}
        
        /* Cấu hình nội dung chính */
        .main .block-container { padding-top: 1rem !important; padding-bottom: 100px !important; }
        
        /* BẢNG HIỆU LKTV CHUYÊN NGHIỆP */
        .bang-hieu-lktv {
            text-align: center;
            background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
            color: white;
            padding: 25px;
            border-radius: 20px;
            margin-bottom: 20px;
            box-shadow: 0px 10px 30px rgba(0,0,0,0.3);
            border: 1px solid #ffffff20;
        }
        .logo-img { 
            width: 100px; height: 100px; 
            object-fit: cover; 
            border-radius: 50%; 
            border: 3px solid #f1c40f; 
            margin-bottom: 10px;
            background-color: #f1c40f10;
        }
        .ten-tiem { font-size: 26px; font-weight: 800; color: #ffffff; letter-spacing: 1px; text-transform: uppercase; margin: 5px 0; }
        .thong-tin-phu { font-size: 14px; opacity: 0.8; line-height: 1.6; }
        .slogan { font-size: 16px; color: #f1c40f; font-weight: 500; margin-top: 10px; font-style: italic; }
    </style>
    """, unsafe_allow_html=True)

# --- HÀM CHUYỂN ĐỔI LINK DRIVE (BẢN FIX LỖI HIỂN THỊ) ---
def format_drive_link(link):
    if not link or not isinstance(link, str): return ""
    if 'drive.google.com' in link:
        file_id = ""
        if 'file/d/' in link:
            file_id = link.split('file/d/')[1].split('/')[0]
        elif 'id=' in link:
            file_id = link.split('id=')[1].split('&')[0]
        
        if file_id:
            # Sử dụng đầu link lh3 để bypass lỗi hiển thị trên Web App
            return f'https://lh3.googleusercontent.com/d/{file_id}'
    return link

def get_now_vn():
    tz = pytz.timezone('Asia/Ho_Chi_Minh')
    return datetime.now(tz)

# ==========================================
# 2. KẾT NỐI DỮ LIỆU GOOGLE SHEETS
# ==========================================
def get_gspread_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["connections"]["gsheets"], scopes=scope)
    return gspread.authorize(creds)

@st.cache_data(ttl=60) # Lưu bộ nhớ tạm 60 giây để app mượt hơn
def get_settings():
    try:
        client = get_gspread_client()
        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        ws = sh.worksheet("ThietLap")
        records = ws.get_all_values()
        # Chuyển dữ liệu từ Sheet (Dọc) thành Dictionary (Ngang)
        return {row[0]: row[1] for row in records if len(row) > 1}
    except:
        return {"TenTiem": "LKTV DETAILING", "Logo": "", "Diachi": "LONG XUYÊN", "SDT": "0978888888", "Slogan": "Nơi Đặt Niềm Tin.."}

def get_service_data():
    try:
        client = get_gspread_client()
        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        worksheet = sh.worksheet("DanhMuc")
        records = worksheet.get_all_records()
        return {r['Tên Sản Phẩm']: float(str(r['Đơn Giá']).replace(',','')) for r in records if r['Tên Sản Phẩm']}
    except: return {"Lỗi kết nối Danh Mục": 0}

# ==========================================
# 3. GIAO DIỆN HIỂN THỊ (BẢNG HIỆU)
# ==========================================
def display_header(settings):
    logo_url = format_drive_link(settings.get('Logo', ''))
    
    st.markdown(f"""
        <div class="bang-hieu-lktv">
            <img src="{logo_url}" class="logo-img" alt="Logo">
            <div class="ten-tiem">{settings.get('TenTiem', 'LKTV DETAILING')}</div>
            <div class="thong-tin-phu">
                📍 {settings.get('Diachi', 'LONG XUYÊN, AN GIANG')} <br>
                📞 {settings.get('SDT', '0978888888')}
            </div>
            <div class="slogan">{settings.get('Slogan', 'Nơi Đặt Niềm Tin..')}</div>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 4. QUẢN LÝ ĐĂNG NHẬP & PHIÊN LÀM VIỆC
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.update({"logged_in": False, "username": "Admin", "login_time": None})

# ==========================================
# 5. MÀN HÌNH CHÍNH (LOGIC APP)
# ==========================================
def main():
    settings = get_settings() # Lấy thông tin từ sheet ThietLap

    if not st.session_state["logged_in"]:
        # --- MÀN HÌNH ĐĂNG NHẬP ---
        display_header(settings)
        with st.container():
            st.markdown("### 🔐 HỆ THỐNG NỘI BỘ")
            u = st.text_input("Tên đăng nhập")
            p = st.text_input("Mật khẩu", type="password")
            if st.button("VÀO NHÀ", use_container_width=True, type="primary"):
                if u == "admin" and p == "2026":
                    st.session_state.update({"logged_in": True, "login_time": time.time()})
                    st.rerun()
                else:
                    st.error("Sai chìa khóa rồi ní ơi!")
    else:
        # --- MÀN HÌNH LÀM VIỆC ---
        display_header(settings)
        st.write(f"👋 Chào mừng ní quay trở lại!")
        
        # Kết nối sheet báo cáo
        client = get_gspread_client()
        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        sheet_bc = sh.worksheet("BaoCao")
        services = get_service_data()
        now_vn = get_now_vn()

        # Dashboard nhanh
        st.divider()
        col1, col2 = st.columns(2)
        col1.metric("Ngày làm việc", now_vn.strftime("%d/%m/%Y"))
        col2.metric("Trạng thái", "Sẵn sàng ✅")

        # Form nhập liệu
        with st.form("form_nhap_lieu", clear_on_submit=True):
            st.subheader("📝 Lập phiếu mới")
            ten_kh = st.text_input("Tên khách hàng", value="Khách lẻ")
            sdt_kh = st.text_input("Số điện thoại")
            dich_vu = st.selectbox("Dịch vụ", list(services.keys()))
            so_luong = st.number_input("Số lượng", min_value=1.0, value=1.0, step=0.5)
            
            don_gia = services.get(dich_vu, 0)
            thanh_tien = don_gia * so_luong
            st.warning(f"Thành tiền dự kiến: {thanh_tien:,.0f} VNĐ")
            
            ghi_chu = st.text_area("Ghi chú thêm")
            
            if st.form_submit_button("LƯU DỮ LIỆU", use_container_width=True):
                new_row = [
                    now_vn.strftime("%d/%m/%Y"), 
                    ten_kh, 
                    sdt_kh, 
                    dich_vu, 
                    so_luong, 
                    don_gia, 
                    thanh_tien, 
                    ghi_chu,
                    now_vn.strftime("%H:%M:%S")
                ]
                sheet_bc.append_row(new_row)
                st.success("Đã ghi sổ thành công!")
                st.balloons()

        # Nút thoát
        if st.button("🚪 Thoát hệ thống", use_container_width=True):
            st.session_state["logged_in"] = False
            st.rerun()

if __name__ == "__main__":
    main()
    
