import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import time

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN & CSS (GIỮ NGUYÊN & CẬP NHẬT)
# ==========================================
st.set_page_config(page_title="Hệ Thống Lab 2026", layout="centered", page_icon="🧪")

st.markdown("""
    <style>
        header, footer, .stAppDeployButton {display: none !important; visibility: hidden !important;}
        [data-testid="stStatusWidget"], [data-testid="stToolbar"] {display: none !important;}
        .block-container {padding-top: 1.5rem !important; padding-bottom: 1rem !important;}
        #MainMenu {visibility: hidden !important;}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. KẾT NỐI GOOGLE SHEETS (GIỮ NGUYÊN)
# ==========================================
def get_gspread_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["connections"]["gsheets"], scopes=scope)
    return gspread.authorize(creds)

def safe_append_row(sheet, row_data):
    for i in range(3):
        try:
            sheet.append_row(row_data)
            return True
        except:
            time.sleep(2)
    return False

# ==========================================
# 3. HÀM XỬ LÝ LOGIC (GIỮ NGUYÊN)
# ==========================================
def get_product_list():
    try:
        client = get_gspread_client()
        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        return [p.strip() for p in sh.worksheet("DanhMuc").col_values(1)[1:] if p.strip()]
    except:
        return ["Rửa Xe Tay Ga", "Rửa Xe Số", "Thay Nhớt"]

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
# 4. QUẢN LÝ TRẠNG THÁI (SESSION STATE) - CẬP NHẬT LOGIC THỜI GIAN
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.update({
        "logged_in": False,
        "role": None,
        "username": None,
        "history": {} # Dùng để theo dõi số lần trùng và thời gian cho từng dịch vụ
    })

# ==========================================
# 5. MÀN HÌNH ĐĂNG NHẬP (GIỮ NGUYÊN)
# ==========================================
def login_screen():
    st.markdown("<h2 style='text-align: center;'>🔐 ĐĂNG NHẬP HỆ THỐNG</h2>", unsafe_allow_html=True)
    with st.form("login_form"):
        user = st.text_input("Tên đăng nhập (SĐT)")
        password = st.text_input("Mật khẩu", type="password")
        if st.form_submit_button("XÁC NHẬN ĐĂNG NHẬP", use_container_width=True):
            if user == "admin" and password == "2026":
                st.session_state.update({"logged_in": True, "role": "admin", "username": "Chủ tiệm"})
                st.rerun()
            else:
                success, name = check_login(user, password)
                if success:
                    st.session_state.update({"logged_in": True, "role": "staff", "username": name})
                    st.rerun()
                else: st.error("Sai thông tin rồi ní ơi!")

# ==========================================
# 6. GIAO DIỆN CHÍNH & LOGIC THIẾT QUÂN LUẬT (CẬP NHẬT MỚI)
# ==========================================
def main_app():
    client = get_gspread_client()
    sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
    sheet_bc = sh.worksheet("BaoCao")

    with st.sidebar:
        st.success(f"🟢 {st.session_state['username']}")
        if st.button("ĐĂNG XUẤT"):
            st.session_state["logged_in"] = False
            st.rerun()

    st.title("🧪 QUẢN LÝ DỊCH VỤ")
    danh_sach_sp = get_product_list()

    with st.expander("📝 NHẬP DỮ LIỆU", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            nguoi_lam = st.text_input("Người thực hiện", value=st.session_state["username"], disabled=True)
            san_pham = st.selectbox("Dịch vụ", danh_sach_sp)
            diem_so = st.select_slider("Đánh giá", options=[f"{i}/10" for i in range(1, 11)], value="9/10")
        with col2:
            ngay = st.date_input("Ngày thực hiện", datetime.now())
            so_luong = st.number_input("Số lượng", min_value=0.0, step=1.0, format="%.0f")
            ghi_chu = st.text_input("Ghi chú", value="Thực hiện tại tiệm.")

    # --- HỆ THỐNG KIỂM SOÁT THIẾT QUÂN LUẬT (0-2-5-KHÓA) ---
    is_duplicate = False
    try:
        # Kiểm tra 5 dòng cuối trong Google Sheets xem có trùng y hệt không
        last_rows = sheet_bc.get_all_values()[-5:]
        for r in last_rows:
            if r[1] == nguoi_lam and r[2] == san_pham and float(str(r[3]).replace(',','.')) == so_luong:
                is_duplicate = True
                break
    except: pass

    # Khởi tạo lịch sử cho sản phẩm nếu chưa có
    if san_pham not in st.session_state["history"]:
        st.session_state["history"][san_pham] = {"count": 0, "last_time": 0}

    # Tính toán thời gian chờ
    count = st.session_state["history"][san_pham]["count"]
    last_time = st.session_state["history"][san_pham]["last_time"]
    wait_time = 0
    
    if is_duplicate:
        if count == 1: wait_time = 120    # Trùng lần 2: chờ 2 phút
        elif count == 2: wait_time = 300  # Trùng lần 3: chờ 5 phút
        elif count >= 3: wait_time = 999999 # Trùng lần 4: Khóa vĩnh viễn

    elapsed = time.time() - last_time
    
    # Hiển thị nút bấm dựa trên logic thời gian
    if is_duplicate and count >= 3:
        st.error("🚫 ĐÃ QUÁ SỐ LẦN TRÙNG CHO PHÉP. KHÔNG THỂ LƯU THÊM!")
        st.button("🚀 NÚT BỊ KHÓA VĨNH VIỄN", disabled=True, use_container_width=True)
    elif is_duplicate and elapsed < wait_time:
        con_lai = int(wait_time - elapsed)
        st.warning(f"⚠️ Phát hiện trùng lần {count + 1}! Vui lòng đợi {con_lai//60}p {con_lai%60}s để tiếp tục.")
        st.button(f"⏳ HỆ THỐNG ĐANG KHÓA ({con_lai}s)", disabled=True, use_container_width=True)
    else:
        # Nút bấm lưu chính
        nut_label = "🚀 LƯU VÀO SỔ CÁI" if not is_duplicate else f"🚀 XÁC NHẬN LƯU (TRÙNG LẦN {count + 1})"
        if st.button(nut_label, type="primary", use_container_width=True):
            if so_luong <= 0:
                st.error("Số lượng phải lớn hơn 0!")
            else:
                with st.status("🔄 Đang xử lý dữ liệu..."):
                    sl_rx = so_luong if "Nhớt" not in san_pham else 0
                    sl_tn = so_luong if "Nhớt" in san_pham else 0
                    gio = datetime.now().strftime("%H:%M:%S")
                    row = [ngay.strftime("%d/%m/%Y"), nguoi_lam, san_pham, sl_rx, sl_tn, diem_so, ghi_chu, gio]
                    
                    if safe_append_row(sheet_bc, row):
                        # Cập nhật lịch sử
                        if is_duplicate:
                            st.session_state["history"][san_pham]["count"] += 1
                        else:
                            st.session_state["history"][san_pham]["count"] = 1 # Reset về 1 nếu là lượt mới
                        
                        st.session_state["history"][san_pham]["last_time"] = time.time()
                        
                        st.success("Đã lưu thành công!"); st.balloons(); time.sleep(1); st.rerun()
                    else:
                        st.error("Lỗi kết nối mạng!")

    # Báo cáo Admin (Giữ nguyên)
    if st.session_state["role"] == "admin":
        st.divider(); st.subheader("📊 BÁO CÁO NHANH")
        try:
            df = pd.DataFrame(sheet_bc.get_all_records())
            st.table(df.tail(10))
        except: st.info("Đang tải dữ liệu...")

# --- KHỞI CHẠY ---
if not st.session_state["logged_in"]:
    login_screen()
else:
    main_app()
            
