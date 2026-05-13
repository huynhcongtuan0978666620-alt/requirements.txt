import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import time

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN & CSS SIÊU CẤP
# ==========================================
st.set_page_config(
    page_title="Hệ Thống Quản Lý Lab 2026",
    layout="centered",
    page_icon="🧪"
)

# Đoạn này xử lý triệt để các icon vương miện/lâu đài và làm sạch giao diện
st.markdown("""
    <style>
        /* Ẩn Header, Footer và nút Deploy */
        header, footer, .stAppDeployButton {
            display: none !important;
            visibility: hidden !important;
        }
        
        /* Ẩn cụm Status Widget (Vương miện/Lâu đài) ở góc dưới */
        [data-testid="stStatusWidget"], [data-testid="stToolbar"] {
            display: none !important;
        }

        /* Tùy chỉnh khung nhập liệu cho chuyên nghiệp */
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 1rem !important;
        }
        
        /* Làm nổi bật các thông báo */
        .stAlert {
            border-radius: 10px;
        }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. KẾT NỐI DỮ LIỆU GOOGLE SHEETS
# ==========================================
def get_gspread_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        creds = Credentials.from_service_account_info(st.secrets["connections"]["gsheets"], scopes=scope)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Lỗi kết nối API: {e}")
        return None

def safe_append_row(sheet, row_data):
    """Hàm lưu dữ liệu có cơ chế thử lại nếu lỗi mạng"""
    for i in range(3):
        try:
            sheet.append_row(row_data)
            return True
        except:
            time.sleep(2)
    return False

# ==========================================
# 3. HÀM XỬ LÝ LOGIC NGHIỆP VỤ
# ==========================================
def get_product_list():
    """Lấy danh mục dịch vụ từ Sheet DanhMuc"""
    try:
        client = get_gspread_client()
        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        sheet_dm = sh.worksheet("DanhMuc")
        # Lấy cột 1, bỏ dòng tiêu đề
        products = sheet_dm.col_values(1)[1:]
        return [p.strip() for p in products if p.strip()]
    except:
        return ["Rửa Xe Tay Ga", "Rửa Xe Số", "Thay Nhớt Shell", "Thay Nhớt Castrol"]

def check_login(user_input, pass_input):
    """Kiểm tra nhân viên đăng nhập từ Sheet NhanVien"""
    try:
        client = get_gspread_client()
        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        sheet_nv = sh.worksheet("NhanVien")
        data_nv = sheet_nv.get_all_records()
        for row in data_nv:
            if str(row['Số Điện Thoại (Login)']).strip() == str(user_input).strip() and \
               str(row['Mật Khẩu']).strip() == str(pass_input).strip():
                return True, row['Tên Nhân Viên']
        return False, None
    except:
        return False, None

# ==========================================
# 4. QUẢN LÝ TRẠNG THÁI HỆ THỐNG (SESSION STATE)
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.update({
        "logged_in": False,
        "role": None,
        "username": None,
        "last_submit": 0  # Thời gian bấm nút lần cuối
    })

# ==========================================
# 5. GIAO DIỆN ĐĂNG NHẬP
# ==========================================
def login_screen():
    st.markdown("<h2 style='text-align: center;'>🧪 LAB SYSTEM LOGIN</h2>", unsafe_allow_html=True)
    with st.container():
        with st.form("login_form"):
            user = st.text_input("Số điện thoại đăng nhập")
            password = st.text_input("Mật khẩu", type="password")
            submit = st.form_submit_button("XÁC NHẬN ĐĂNG NHẬP", use_container_width=True)
            
            if submit:
                if user == "admin" and password == "2026":
                    st.session_state.update({"logged_in": True, "role": "admin", "username": "Chủ tiệm"})
                    st.rerun()
                else:
                    success, full_name = check_login(user, password)
                    if success:
                        st.session_state.update({"logged_in": True, "role": "staff", "username": full_name})
                        st.rerun()
                    else:
                        st.error("Ní nhập sai thông tin rồi, kiểm tra lại nhé!")

# ==========================================
# 6. GIAO DIỆN CHÍNH (MAIN APP)
# ==========================================
def main_app():
    # Khởi tạo kết nối
    client = get_gspread_client()
    sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
    sheet_bc = sh.worksheet("BaoCao")

    # Sidebar quản lý tài khoản
    with st.sidebar:
        st.header("👤 TÀI KHOẢN")
        st.info(f"Đang đăng nhập: **{st.session_state['username']}**")
        if st.button("ĐĂNG XUẤT", use_container_width=True):
            st.session_state["logged_in"] = False
            st.rerun()
        st.divider()
        st.write("Hệ thống thử nghiệm Lab 2026")

    st.title("🚀 NHẬP DỮ LIỆU THỰC CHIẾN")

    # Layout nhập liệu
    with st.expander("📝 THÔNG TIN DỊCH VỤ", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            nguoi_lam = st.text_input("Người thực hiện", value=st.session_state["username"], disabled=True)
            san_pham = st.selectbox("Loại dịch vụ / Sản phẩm", get_product_list())
            diem_so = st.select_slider("Đánh giá chất lượng", options=[f"{i}/10" for i in range(1, 11)], value="9/10")
        
        with col2:
            ngay = st.date_input("Ngày thực hiện", datetime.now())
            so_luong = st.number_input("Số lượng (xe/chai/lần)", min_value=0.0, step=1.0, format="%.0f")
            ghi_chu = st.text_input("Ghi chú thêm", value="Thực hiện tại tiệm.")

    # --- HỆ THỐNG KIỂM SOÁT THÔNG MINH ---
    # 1. Chống bấm nhầm (Double-check)
    show_confirm = False
    try:
        last_rows = sheet_bc.get_all_values()[-3:] # Lấy 3 dòng cuối
        for r in last_rows:
            if r[1] == nguoi_lam and r[2] == san_pham and float(str(r[3]).replace(',','.')) == so_luong:
                show_confirm = True
                break
    except: pass

    # 2. Chống Spam thời gian (Cooldown)
    COOLDOWN = 5 # Chờ 5 giây cho chắc ăn
    time_passed = time.time() - st.session_state["last_submit"]
    
    if show_confirm:
        st.warning("⚠️ Dữ liệu này hình như vừa mới nhập xong. Ní kiểm tra kỹ nhé!")
        confirm = st.checkbox("Tôi xác nhận đây là lượt làm mới, không phải trùng.")
    else:
        confirm = True

    # Nút bấm lưu dữ liệu
    if time_passed < COOLDOWN:
        st.button(f"⏳ VUI LÒNG ĐỢI ({int(COOLDOWN - time_passed)}s)", disabled=True, use_container_width=True)
    else:
        if st.button("🚀 LƯU VÀO SỔ CÁI", type="primary", use_container_width=True, disabled=not confirm):
            if so_luong <= 0:
                st.error("Số lượng phải lớn hơn 0 mới lưu được ní ơi!")
            else:
                with st.status("🔄 Đang đẩy dữ liệu lên Google Sheets...", expanded=True) as status:
                    # Phân loại tự động
                    sl_rua_xe = so_luong if "Nhớt" not in san_pham else 0
                    sl_thay_nhot = so_luong if "Nhớt" in san_pham else 0
                    gio_hien_tai = datetime.now().strftime("%H:%M:%S")
                    
                    row = [
                        ngay.strftime("%d/%m/%Y"), 
                        nguoi_lam, 
                        san_pham, 
                        sl_rua_xe, 
                        sl_thay_nhot, 
                        diem_so, 
                        ghi_chu, 
                        gio_hien_tai
                    ]
                    
                    if safe_append_row(sheet_bc, row):
                        st.session_state["last_submit"] = time.time()
                        status.update(label="✅ ĐÃ LƯU THÀNH CÔNG!", state="complete", expanded=False)
                        st.success(f"Đã ghi nhận mẻ: {san_pham}")
                        st.balloons()
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error("Lỗi mạng, ní bấm thử lại lần nữa xem sao.")

    # Phần dành riêng cho Admin (Xem báo cáo nhanh)
    if st.session_state["role"] == "admin":
        st.divider()
        st.subheader("📊 XEM NHANH 10 GIAO DỊCH CUỐI")
        try:
            data = sheet_bc.get_all_records()
            if data:
                df = pd.DataFrame(data).tail(10)
                st.table(df)
            else:
                st.info("Chưa có dữ liệu trong sổ cái.")
        except:
            st.info("Đang tải dữ liệu từ Sheets...")

# ==========================================
# 7. KHỞI CHẠY ỨNG DỤNG
# ==========================================
if not st.session_state["logged_in"]:
    login_screen()
else:
    main_app()
