import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import pytz
import hashlib

# ==========================================
# 1. GIAO DIỆN CHUẨN LKTV - CÂN CHỈNH GIỮA
# ==========================================
st.set_page_config(page_title="LKTV DETAILING - 2026", layout="centered", page_icon="🧼")

st.markdown("""
    <style>
        header, footer, .stAppDeployButton {display: none !important; visibility: hidden !important;}
        [data-testid="stStatusWidget"], [data-testid="stToolbar"] {display: none !important;}
        
        .bang-hieu-lktv {
            text-align: center;
            background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
            color: white; padding: 25px; border-radius: 20px;
            margin-bottom: 20px; box-shadow: 0px 10px 30px rgba(0,0,0,0.3);
            border: 1px solid #ffffff20;
        }
        .logo-img { width: 100px; height: 100px; object-fit: cover; border-radius: 50%; border: 3px solid #f1c40f; margin-bottom: 10px; background: #000; }
        .ten-tiem { font-size: 28px; font-weight: 800; color: #ffffff; text-transform: uppercase; margin-bottom: 5px; }
        .thong-tin-phu { font-size: 15px; color: #ecf0f1; opacity: 0.9; margin-bottom: 2px; }
        .sdt-tiem { font-size: 18px; color: #f1c40f; font-weight: 700; margin-top: 5px; }
        .slogan { font-size: 15px; color: #f1c40f; font-weight: 500; font-style: italic; margin-top: 10px; border-top: 1px solid #ffffff30; padding-top: 10px; }

        /* --- PHẦN QUAN TRỌNG: CÂN GIỮA VÀ DÀN ĐỀU 3 TAB --- */
        .stTabs [data-baseweb="tab-list"] {
            display: flex;
            justify-content: center; /* Căn giữa toàn bộ cụm Tab */
            gap: 10px;
            width: 100%;
        }
        .stTabs [data-baseweb="tab"] {
            flex: 1; /* Chia đều độ rộng cho các Tab */
            height: 50px;
            background-color: #ffffff;
            border-radius: 10px 10px 0 0;
            max-width: 150px; /* Khống chế độ rộng tối đa để không quá bè */
        }
        .stTabs [data-baseweb="tab"] p { 
            color: #000000 !important; 
            font-weight: 700 !important;
            text-align: center;
            width: 100%;
        }
        .stTabs [data-baseweb="tab"][aria-selected="true"] { 
            background-color: #f1c40f !important; 
        }

        .tien-thua-box {
            background-color: #d4edda; color: #155724; padding: 15px; border-radius: 10px;
            text-align: center; font-size: 22px; font-weight: bold; border: 3px dashed #28a745;
            margin: 15px 0;
        }
    </style>
    """, unsafe_allow_html=True)

# --- HÀM HỆ THỐNG GIỮ NGUYÊN 100% ---
def hash_password(password): 
    return hashlib.sha256(str(password).strip().encode()).hexdigest()

def get_now_vn(): 
    return datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))

def format_drive_link(link):
    if not link or not isinstance(link, str): return ""
    if 'drive.google.com' in link:
        file_id = ""
        if 'file/d/' in link: file_id = link.split('file/d/')[1].split('/')[0]
        elif 'id=' in link: file_id = link.split('id=')[1].split('&')[0]
        if file_id: return f'https://lh3.googleusercontent.com/d/{file_id}'
    return link

def get_gspread_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["connections"]["gsheets"], scopes=scope)
    return gspread.authorize(creds)

@st.cache_data(ttl=60)
def get_settings():
    try:
        client = get_gspread_client()
        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        return {row[0]: row[1] for row in sh.worksheet("ThietLap").get_all_values() if len(row) > 1}
    except: return {"TenTiem": "SALON KIM HIỀN"}

@st.cache_data(ttl=60)
def get_service_data():
    try:
        client = get_gspread_client()
        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        return {r['Tên Sản Phẩm']: float(str(r['Đơn Giá']).replace(',','')) for r in sh.worksheet("DanhMuc").get_all_records() if r['Tên Sản Phẩm']}
    except: return {"Cắt tóc": 50000}

def get_all_users():
    try:
        client = get_gspread_client()
        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        return sh.worksheet("Admin").get_all_records()
    except: return []

def display_header(settings):
    logo_url = format_drive_link(settings.get('Logo', ''))
    st.markdown(f"""
        <div class="bang-hieu-lktv">
            <img src="{logo_url}" class="logo-img">
            <div class="ten-tiem">{settings.get('TenTiem', 'SALON KIM HIỀN')}</div>
            <div class="thong-tin-phu">📍 {settings.get('Diachi', '131, TRẦN BÌNH TRỌNG, LONG XUYÊN')}</div>
            <div class="sdt-tiem">📞 {settings.get('SDT', '0978.888.888')}</div>
            <div class="slogan">{settings.get('Slogan', 'Nơi Bạn Đặt Niềm Tin')}</div>
        </div>
    """, unsafe_allow_html=True)

def main():
    settings = get_settings()
    if "logged_in" not in st.session_state:
        st.session_state.update({"logged_in": False, "role": None, "user": None, "full_name": None, "phone": None})

    if not st.session_state["logged_in"]:
        display_header(settings)
        with st.form("login_form"):
            st.markdown("### 🔐 ĐĂNG NHẬP")
            u_input = st.text_input("Tên đăng nhập")
            p_input = st.text_input("Mật khẩu", type="password")
            if st.form_submit_button("XÁC NHẬN", use_container_width=True, type="primary"):
                if u_input == "admin" and p_input == "2026":
                    st.session_state.update({"logged_in": True, "role": "Admin", "user": "admin", "full_name": "Chủ Tiệm", "phone": settings.get('SDT', '')})
                    st.rerun()
                
                users = get_all_users()
                p_hashed = hash_password(p_input)
                for row in users:
                    if str(u_input) == str(row.get('Tài khoản')).strip() and p_hashed == str(row.get('Mật khẩu')).strip():
                        st.session_state.update({
                            "logged_in": True, 
                            "role": row.get('Quyền', 'Nhân viên'), 
                            "user": u_input,
                            "full_name": row.get('Họ tên', u_input),
                            "phone": row.get('Số điện thoại', 'N/A')
                        })
                        st.rerun()
                st.error("Thông tin đăng nhập không đúng!")
    else:
        display_header(settings)
        # Tab list hiển thị theo quyền
        tab_list = ["📝 NHẬP LIỆU", "📈 BÁO CÁO", "⚙️ CÀI ĐẶT"] if st.session_state["role"] == "Admin" else ["📝 NHẬP LIỆU"]
        tabs = st.tabs(tab_list)

        with tabs[0]:
            st.success(f"👷 **Nhân sự trực:** {st.session_state['full_name']} | 📞 {st.session_state['phone']}")
            services = get_service_data()
            kh = st.text_input("Tên khách hàng", "Khách lẻ")
            sdt_kh = st.text_input("SĐT khách hàng")
            dv = st.selectbox("Dịch vụ", list(services.keys()))
            sl = st.number_input("Số lượng", 0.5, 100.0, 1.0, 0.5)
            
            don_gia = services.get(dv, 0)
            tong_bill = don_gia * sl
            st.divider()
            st.markdown(f"### 🧾 TỔNG THANH TOÁN: `{tong_bill:,.0f} VNĐ`")
            
            khach_dua = st.number_input("Khách thanh toán (VNĐ)", min_value=0.0, value=float(tong_bill), step=1000.0)
            tien_thua = khach_dua - tong_bill
            if tien_thua > 0:
                st.markdown(f'<div class="tien-thua-box">💵 Trả lại khách: {tien_thua:,.0f} VNĐ</div>', unsafe_allow_html=True)

            if st.button("🚀 LƯU ĐƠN HÀNG", use_container_width=True, type="primary"):
                try:
                    client = get_gspread_client()
                    sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
                    ws = sh.worksheet("BaoCao")
                    now = get_now_vn()
                    nv_info = f"{st.session_state['full_name']} ({st.session_state['phone']})"
                    ws.append_row([now.strftime("%d/%m/%Y"), nv_info, kh, sdt_kh, dv, sl, don_gia, tong_bill, tong_bill, now.strftime("%H:%M:%S")])
                    st.success(f"Đã lưu đơn thành công cho {st.session_state['full_name']}!")
                    st.balloons()
                except Exception as e: st.error(f"Lỗi: {e}")

        if st.session_state["role"] == "Admin":
            with tabs[1]:
                st.subheader("📊 Lịch sử doanh thu")
                try:
                    client = get_gspread_client()
                    sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
                    df = pd.DataFrame(sh.worksheet("BaoCao").get_all_records())
                    if not df.empty:
                        st.dataframe(df.tail(30), use_container_width=True)
                except: st.warning("Đang tải dữ liệu...")
            
            with tabs[2]:
                st.subheader("⚙️ QUẢN TRỊ NHÂN SỰ")
                with st.expander("🔑 TRÌNH TẠO MÃ BẢO MẬT", expanded=True):
                    new_pass = st.text_input("Nhập mật khẩu cấp cho nhân viên", type="password")
                    if new_pass:
                        st.code(hash_password(new_pass), language="text")
                        st.caption("Dán mã này vào cột 'Mật khẩu' trên Google Sheets.")

                with st.expander("👥 DANH SÁCH NHÂN SỰ"):
                    users_data = get_all_users()
                    if users_data:
                        df_users = pd.DataFrame(users_data)
                        st.table(df_users[['Tài khoản', 'Quyền', 'Họ tên', 'Số điện thoại']])

        if st.sidebar.button("🚪 Đăng xuất"):
            st.session_state.update({"logged_in": False})
            st.rerun()

if __name__ == "__main__": main()
    
