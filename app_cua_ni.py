import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import time
import pytz
import hashlib

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN (PHONG CÁCH 18.0)
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
        .ten-tiem { font-size: 26px; font-weight: 800; color: #ffffff; text-transform: uppercase; }
        .slogan { font-size: 16px; color: #f1c40f; font-weight: 500; font-style: italic; }
        .stTabs [data-baseweb="tab-list"] { gap: 10px; }
        .stTabs [data-baseweb="tab"] { height: 50px; background-color: #f0f2f6; border-radius: 10px 10px 0 0; }
    </style>
    """, unsafe_allow_html=True)

# --- HÀM HỆ THỐNG ---
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

# ==========================================
# 2. KẾT NỐI GOOGLE SHEETS
# ==========================================
def get_gspread_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["connections"]["gsheets"], scopes=scope)
    return gspread.authorize(creds)

@st.cache_data(ttl=60)
def get_settings():
    try:
        client = get_gspread_client()
        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        ws = sh.worksheet("ThietLap")
        records = ws.get_all_values()
        return {row[0]: row[1] for row in records if len(row) > 1}
    except: return {"TenTiem": "LKTV DETAILING"}

def get_all_users():
    try:
        client = get_gspread_client()
        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        ws = sh.worksheet("Admin")
        return ws.get_all_records()
    except: return []

@st.cache_data(ttl=60)
def get_service_data():
    try:
        client = get_gspread_client()
        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        ws = sh.worksheet("DanhMuc")
        records = ws.get_all_records()
        return {r['Tên Sản Phẩm']: float(str(r['Đơn Giá']).replace(',','')) for r in records if r['Tên Sản Phẩm']}
    except: return {"Rửa xe": 50000}

# ==========================================
# 3. GIAO DIỆN & LOGIC CHÍNH
# ==========================================
def display_header(settings):
    logo_url = format_drive_link(settings.get('Logo', ''))
    st.markdown(f"""
        <div class="bang-hieu-lktv">
            <img src="{logo_url}" class="logo-img">
            <div class="ten-tiem">{settings.get('TenTiem', 'LKTV DETAILING')}</div>
            <div class="thong-tin-phu">📍 {settings.get('Diachi', 'LONG XUYÊN')}</div>
            <div class="slogan">{settings.get('Slogan', 'Nơi Đặt Niềm Tin..')}</div>
        </div>
    """, unsafe_allow_html=True)

def main():
    settings = get_settings()
    if "logged_in" not in st.session_state:
        st.session_state.update({"logged_in": False, "role": None, "user": None, "last_submit": 0})

    if not st.session_state["logged_in"]:
        display_header(settings)
        with st.form("login_form"):
            st.markdown("### 🔐 XÁC THỰC CHỦ TIỆM")
            u_input = st.text_input("Tên đăng nhập")
            p_input = st.text_input("Mật khẩu", type="password")
            if st.form_submit_button("VÀO NHÀ", use_container_width=True, type="primary"):
                if u_input == "admin" and p_input == "2026":
                    st.session_state.update({"logged_in": True, "role": "Admin", "user": "Chủ Tiệm"})
                    st.rerun()
                users = get_all_users()
                p_hashed = hash_password(p_input)
                for row in users:
                    if str(u_input) == str(row.get('Tài khoản')).strip() and p_hashed == str(row.get('Mật khẩu')).strip():
                        st.session_state.update({"logged_in": True, "role": row.get('Quyền', 'Nhân viên'), "user": u_input})
                        st.rerun()
                st.error("Chìa khóa sai rồi ní ơi!")
    else:
        display_header(settings)
        tab_list = ["📝 NHẬP LIỆU", "📈 BÁO CÁO", "⚙️ CÀI ĐẶT"] if st.session_state["role"] == "Admin" else ["📝 NHẬP LIỆU"]
        tabs = st.tabs(tab_list)

        # --- TAB NHẬP LIỆU ---
        with tabs[0]:
            st.info(f"👤 {st.session_state['user']} ({st.session_state['role']})")
            services = get_service_data()
            with st.form("form_nhap", clear_on_submit=True):
                kh = st.text_input("Tên khách hàng", "Khách lẻ")
                sdt = st.text_input("SĐT khách hàng")
                dv = st.selectbox("Dịch vụ", list(services.keys()))
                sl = st.number_input("Số lượng", 0.5, 10.0, 1.0, 0.5)
                
                don_gia = services.get(dv, 0)
                thanh_tien = don_gia * sl
                st.write(f"💰 **Thành tiền: {thanh_tien:,.0f} VNĐ**")

                if st.form_submit_button("LƯU DỮ LIỆU", use_container_width=True, type="primary"):
                    cho = 10 - (time.time() - st.session_state["last_submit"])
                    if cho > 0: st.warning(f"Đợi {int(cho)}s nữa nhé!")
                    else:
                        try:
                            client = get_gspread_client()
                            sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
                            ws = sh.worksheet("BaoCao")
                            all_rows = ws.get_all_values()
                            # Check trùng cột C (Khách) và D (SĐT)
                            if len(all_rows) > 1 and [kh, sdt] == [all_rows[1][2], all_rows[1][3]]:
                                st.error("Phiếu này vừa nhập xong ní ơi!")
                            else:
                                now = get_now_vn()
                                data_row = [
                                    now.strftime("%d/%m/%Y"), st.session_state['user'], kh, sdt, 
                                    dv, sl, don_gia, thanh_tien, thanh_tien, now.strftime("%H:%M:%S")
                                ]
                                ws.append_row(data_row)
                                ws.sort((1, 'des'), (10, 'des'))
                                st.session_state["last_submit"] = time.time()
                                st.success("Ghi sổ thành công! 🎉")
                                st.balloons()
                        except Exception as e: st.error(f"Lỗi: {e}")

            if st.button("🚪 ĐĂNG XUẤT"):
                st.session_state.update({"logged_in": False, "role": None})
                st.rerun()

        # --- TAB BÁO CÁO (ADMIN) ---
        if st.session_state["role"] == "Admin":
            with tabs[1]:
                st.subheader("📊 Lịch sử giao dịch")
                try:
                    client = get_gspread_client()
                    sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
                    df = pd.DataFrame(sh.worksheet("BaoCao").get_all_records())
                    if not df.empty:
                        st.dataframe(df.head(15), use_container_width=True)
                        st.metric("Doanh thu hôm nay", f"{df[df['Ngày']==get_now_vn().strftime('%d/%m/%Y')]['Thành Tiền'].sum():,.0f} VNĐ")
                    else: st.write("Chưa có dữ liệu.")
                except: st.warning("Sheet BaoCao không khớp.")

            # --- TAB CÀI ĐẶT (MỚI) ---
            with tabs[2]:
                st.subheader("⚙️ HỆ THỐNG QUẢN TRỊ")
                
                # Phần 1: Thông tin tiệm
                with st.expander("🏠 Thông tin cửa hàng", expanded=True):
                    st.write(f"**Tên tiệm:** {settings.get('TenTiem')}")
                    st.write(f"**Địa chỉ:** {settings.get('Diachi')}")
                    st.write(f"**Slogan:** {settings.get('Slogan')}")
                    st.caption("Chỉnh sửa các thông tin này trực tiếp tại Sheet 'ThietLap'")

                # Phần 2: Quản lý nhân sự (Mã hóa pass)
                with st.expander("🔐 Công cụ bảo mật nhân viên"):
                    st.markdown("Nhập mật khẩu muốn đặt cho nhân viên vào đây để lấy mã dán vào cột **Mật khẩu** trong sheet **Admin**.")
                    new_pass = st.text_input("Mật khẩu mới", type="password", key="new_pass_input")
                    if new_pass:
                        hashed = hash_password(new_pass)
                        st.code(hashed, language="text")
                        st.success("Copy dòng mã trên và dán vào Google Sheet ní nhé!")

                # Phần 3: Trạng thái kết nối
                with st.expander("📡 Kiểm tra kết nối"):
                    if st.button("Kiểm tra ngay"):
                        try:
                            get_gspread_client()
                            st.success("Kết nối Google Sheets: OK ✅")
                            st.info(f"Thời gian hệ thống: {get_now_vn().strftime('%H:%M:%S %d/%m/%Y')}")
                        except:
                            st.error("Kết nối thất bại! Kiểm tra lại Secrets.")

if __name__ == "__main__":
    main()
    
