import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import time
import pytz
import hashlib

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN (GIỮ CHUẨN 18.0)
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

        with tabs[0]:
            st.info(f"👤 {st.session_state['user']} ({st.session_state['role']})")
            services = get_service_data()
            with st.form("form_nhap", clear_on_submit=True):
                kh = st.text_input("Tên khách hàng", "Khách lẻ")
                sdt = st.text_input("SĐT khách hàng")
                dv = st.selectbox("Dịch vụ", list(services.keys()))
                sl = st.number_input("Số lượng", 0.5, 10.0, 1.0, 0.5)
                note = st.text_area("Ghi chú thực chiến")
                
                don_gia = services.get(dv, 0)
                thanh_tien = don_gia * sl
                st.write(f"💰 **Thanh toán: {thanh_tien:,.0f} VNĐ**")

                if st.form_submit_button("LƯU DỮ LIỆU", use_container_width=True, type="primary"):
                    cho = 10 - (time.time() - st.session_state["last_submit"])
                    if cho > 0: 
                        st.warning(f"Đợi {int(cho)}s nữa nhé ní!")
                    else:
                        try:
                            client = get_gspread_client()
                            sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
                            ws = sh.worksheet("BaoCao")
                            
                            # Kiểm tra chống trùng dữ liệu cũ nhất
                            last_data = ws.get_all_values()
                            is_duplicate = False
                            if len(last_data) > 1:
                                # Kiểm tra Tên khách (Cột B), SĐT (Cột C), Dịch vụ (Cột D)
                                # Lưu ý: Vì mình sắp xếp DESC (mới nhất ở trên), nên dòng mới nhất là index 1
                                row_check = last_data[1] 
                                if [kh, sdt, dv] == [row_check[1], row_check[2], row_check[3]]:
                                    is_duplicate = True

                            if is_duplicate:
                                st.error("Phiếu này ní vừa nhập xong mà, đừng nhập trùng!")
                            else:
                                now = get_now_vn()
                                # --- CHUẨN HÓA THỨ TỰ CỘT (A đến J) ---
                                # A: Ngày | B: Tên khách | C: SĐT | D: Dịch vụ | E: SL | F: Đơn giá | G: Thành tiền | H: Ghi chú | I: Giờ | J: Người nhập
                                data_row = [
                                    now.strftime("%d/%m/%Y"), # A
                                    kh,                        # B
                                    sdt,                       # C
                                    dv,                        # D
                                    sl,                        # E
                                    don_gia,                   # F
                                    thanh_tien,                # G
                                    note,                      # H
                                    now.strftime("%H:%M:%S"), # I
                                    st.session_state['user']   # J
                                ]
                                
                                ws.append_row(data_row)
                                # Sắp xếp lại để cái mới nhất luôn ở dòng 2 (ngay dưới tiêu đề)
                                ws.sort((1, 'des'), (9, 'des'))
                                
                                st.session_state["last_submit"] = time.time()
                                st.success("Đã ghi sổ đúng cột và sắp xếp gọn gàng! 🎉")
                                st.balloons()
                        except Exception as e:
                            st.error(f"Lỗi rồi ní: {e}")

            if st.button("🚪 ĐĂNG XUẤT"):
                st.session_state.update({"logged_in": False, "role": None})
                st.rerun()

        if st.session_state["role"] == "Admin":
            with tabs[1]:
                st.subheader("📊 Doanh thu LKTV")
                try:
                    client = get_gspread_client()
                    sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
                    df = pd.DataFrame(sh.worksheet("BaoCao").get_all_records())
                    if not df.empty:
                        st.dataframe(df.head(15), use_container_width=True)
                        st.metric("Tổng thu hôm nay", f"{df[df['Ngày']==get_now_vn().strftime('%d/%m/%Y')]['Thành Tiền'].sum():,.0f} VNĐ")
                    else: st.write("Chưa có khách nào hôm nay.")
                except: st.warning("Sheet BaoCao không khớp tiêu đề.")

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

if __name__ == "__main__":
    main()
        
