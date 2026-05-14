import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import time
import pytz 

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN & CSS (CHIẾN THUẬT ĐẨY NỘI DUNG)
# ==========================================
st.set_page_config(page_title="Hệ Thống Lab 2026", layout="centered", page_icon="🧪")

st.markdown("""
    <style>
        /* 1. Ẩn tối đa các thành phần thừa của hệ thống */
        header, footer, .stAppDeployButton {display: none !important; visibility: hidden !important;}
        [data-testid="stStatusWidget"], [data-testid="stToolbar"] {display: none !important;}
        
        /* 2. Đẩy nội dung lên sát mép trên và tạo khoảng trống ở dưới đáy */
        .main .block-container {
            padding-top: 1rem !important; 
            padding-bottom: 250px !important; 
        }

        /* 3. Vô hiệu hóa kích thước mọi iframe (Manage app) và button quản trị */
        iframe[title="manage-app"], .stActionButton, div[data-testid="stConnectionStatus"] {
            display: none !important;
            height: 0px !important;
            width: 0px !important;
        }
        
        /* 4. Tối ưu hóa giao diện cho điện thoại */
        #MainMenu {visibility: hidden !important;}
        [data-testid="stExpander"] { margin-bottom: 1.5rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- HÀM LẤY GIỜ CHUẨN VIỆT NAM ---
def get_now_vn():
    tz = pytz.timezone('Asia/Ho_Chi_Minh')
    return datetime.now(tz)

# ==========================================
# 2. KẾT NỐI GOOGLE SHEETS
# ==========================================
def get_gspread_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["connections"]["gsheets"], scopes=scope)
    return gspread.authorize(creds)

# ==========================================
# 3. HÀM XỬ LÝ LOGIC DỮ LIỆU (KHỚP 100% VỚI HÌNH NÍ GỬI)
# ==========================================
def get_service_data():
    """Lấy danh sách sản phẩm và đơn giá từ Sheet DanhMuc"""
    try:
        client = get_gspread_client()
        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        worksheet = sh.worksheet("DanhMuc")
        records = worksheet.get_all_records()
        # Tra cứu theo cột 'Tên Sản Phẩm' và 'Đơn Giá' từ hình 1778728124490.jpg
        return {r['Tên Sản Phẩm']: float(str(r['Đơn Giá']).replace(',','')) for r in records if r['Tên Sản Phẩm']}
    except:
        # Trường hợp lỗi hoặc chưa có dữ liệu
        return {"Lỗi kết nối Sheet": 0}

def check_login(user_input, pass_input):
    try:
        client = get_gspread_client()
        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        sheet_nv = sh.worksheet("NhanVien")
        for row in sheet_nv.get_all_records():
            if str(row['Số Điện Thoại (Login)']).strip() == str(user_input).strip() and \
               str(row['Mật Khẩu']).strip() == str(pass_input).strip():
                return True, row['Tên Nhân Viên']
        return False, None
    except: return False, None

# ==========================================
# 4. QUẢN LÝ TRẠNG THÁI (SESSION STATE)
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.update({
        "logged_in": False, 
        "role": None, 
        "username": None, 
        "history": {}
    })

# ==========================================
# 5. MÀN HÌNH ĐĂNG NHẬP (HIỆU ỨNG PHÁO HOA & DELAY)
# ==========================================
def login_screen():
    st.markdown("<h2 style='text-align: center;'>🔐 ĐĂNG NHẬP HỆ THỐNG</h2>", unsafe_allow_html=True)
    with st.form("login_form"):
        user = st.text_input("Tên đăng nhập (SĐT)")
        password = st.text_input("Mật khẩu", type="password")
        submit = st.form_submit_button("XÁC NHẬN ĐĂNG NHẬP", use_container_width=True)
        
        if submit:
            if user == "admin" and password == "2026":
                st.success("✨ Chúc mừng bạn đã đăng nhập thành công")
                st.balloons()
                time.sleep(2) # Đợi 2 giây theo ý ní
                st.session_state.update({"logged_in": True, "role": "admin", "username": "Chủ tiệm"})
                st.rerun()
            else:
                success, name = check_login(user, password)
                if success:
                    st.success("✨ Chúc mừng bạn đã đăng nhập thành công")
                    st.balloons()
                    time.sleep(2)
                    st.session_state.update({"logged_in": True, "role": "staff", "username": name})
                    st.rerun()
                else:
                    st.error("😔 Bạn đã nhập sai rồi, kiểm tra lại đi nhé")

# ==========================================
# 6. GIAO DIỆN CHÍNH (PHÂN QUYỀN & TỰ ĐỘNG TÍNH TIỀN)
# ==========================================
def main_app():
    client = get_gspread_client()
    sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
    sheet_bc = sh.worksheet("BaoCao")
    service_dict = get_service_data()
    now_vn = get_now_vn()

    with st.sidebar:
        st.success(f"🟢 {st.session_state['username']}")
        if st.button("ĐĂNG XUẤT"):
            st.session_state["logged_in"] = False
            st.rerun()

    st.title("🧪 QUẢN LÝ TIỆM & LAB")

    # --- PHẦN NHẬP LIỆU: Nhân viên & Admin đều dùng chung ---
    with st.expander("📝 LẬP HÓA ĐƠN MỚI", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            ten_kh = st.text_input("Tên khách hàng", value="Khách vãng lai")
            sdt_kh = st.text_input("SĐT khách hàng")
            san_pham = st.selectbox("Chọn dịch vụ", list(service_dict.keys()))
        with col2:
            so_luong = st.number_input("Số lượng", min_value=1.0, step=1.0, value=1.0)
            # Tự động lấy đơn giá từ Dictionary ní đã lập trong Sheet
            don_gia = service_dict.get(san_pham, 0)
            thanh_tien = don_gia * so_luong
            st.info(f"Đơn giá: {don_gia:,.0f}đ")
            st.warning(f"Thành tiền: {thanh_tien:,.0f}đ")

        st.divider()
        col3, col4 = st.columns(2)
        with col3:
            st.markdown(f"**TỔNG TIỀN:** `{thanh_tien:,.0f}đ`")
            st.markdown(f"**CẦN THANH TOÁN:** `{thanh_tien:,.0f}đ`")
        with col4:
            da_thanh_toan = st.number_input("Số tiền đã thanh toán (VNĐ)", min_value=0.0, value=float(thanh_tien))

    # --- NÚT XÁC NHẬN (NHÂN VIÊN CHỈ ĐƯỢC BẤM NÀY) ---
    if st.button("🚀 XÁC NHẬN NHẬP LIỆU", type="primary", use_container_width=True):
        with st.status("🔄 Đang ghi dữ liệu vào sổ cái..."):
            gio_vn = now_vn.strftime("%H:%M:%S")
            # Dòng dữ liệu chuẩn để lưu vào Sheet BaoCao
            row = [
                now_vn.strftime("%d/%m/%Y"), 
                st.session_state["username"], 
                ten_kh, 
                sdt_kh, 
                san_pham, 
                so_luong, 
                don_gia, 
                thanh_tien, 
                da_thanh_toan, 
                gio_vn
            ]
            sheet_bc.append_row(row)
            st.success("Đã lưu thành công!"); st.balloons(); time.sleep(1); st.rerun()

    # --- PHẦN DÀNH RIÊNG CHO CHỦ TIỆM (ADMIN) ---
    if st.session_state["role"] == "admin":
        st.divider()
        st.subheader("📊 KHU VỰC QUẢN TRỊ (CHỈ ADMIN)")
        tab1, tab2 = st.tabs(["Xem Sổ Cái", "Chỉnh Sửa"])
        
        with tab1:
            try:
                data = sheet_bc.get_all_records()
                if data:
                    df = pd.DataFrame(data)
                    st.dataframe(df.tail(20), use_container_width=True)
                else:
                    st.info("Chưa có dữ liệu trong sổ cái.")
            except:
                st.error("Không thể tải báo cáo. Ní kiểm tra lại tiêu đề trong Sheet BaoCao nhé.")
        
        with tab2:
            st.info("Ní là Chủ tiệm nên có toàn quyền sửa file gốc.")
            st.link_button("👉 MỞ FILE GOOGLE SHEET ĐỂ SỬA", st.secrets["connections"]["gsheets"]["spreadsheet"])

# --- KHỞI CHẠY HỆ THỐNG ---
if not st.session_state["logged_in"]:
    login_screen()
else:
    main_app()
    
