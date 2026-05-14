import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import pytz
import hashlib
import time

# ==========================================
# GIAO DIỆN CHUẨN SALON KIM HIỀN - V26.2
# ==========================================
st.set_page_config(page_title="SALON KIM HIỀN", layout="centered", page_icon="✂️")

st.markdown("""
    <style>
        header, footer, .stAppDeployButton {display: none !important; visibility: hidden !important;}
        [data-testid="stStatusWidget"], [data-testid="stToolbar"] {display: none !important;}
        .bang-hieu-kim-hien {
            text-align: center;
            background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
            color: white; padding: 25px; border-radius: 20px;
            margin-bottom: 20px; box-shadow: 0px 10px 30px rgba(0,0,0,0.3);
            border: 1px solid #ffffff20;
        }
        .logo-tron { width: 100px; height: 100px; object-fit: cover; border-radius: 50%; border: 3px solid #f1c40f; margin-bottom: 10px; background: #000; }
        .ten-tiem { font-size: 28px; font-weight: 800; color: #ffffff; text-transform: uppercase; margin-bottom: 5px; }
        .stTabs [data-baseweb="tab-list"] { display: flex; justify-content: center; gap: 10px; width: 100%; }
        .stTabs [data-baseweb="tab"] { flex: 1; height: 50px; background-color: #ffffff; border-radius: 10px 10px 0 0; max-width: 150px; }
        .stTabs [data-baseweb="tab"] p { color: #000000 !important; font-weight: 700 !important; }
        .stTabs [data-baseweb="tab"][aria-selected="true"] { background-color: #f1c40f !important; }
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
        f_id = ""
        if 'file/d/' in link: f_id = link.split('file/d/')[1].split('/')[0]
        elif 'id=' in link: f_id = link.split('id=')[1].split('&')[0]
        if f_id: return f'https://lh3.googleusercontent.com/d/{f_id}'
    return link

def get_gspread_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["connections"]["gsheets"], scopes=scope)
    return gspread.authorize(creds)

@st.cache_data(ttl=60)
def get_gsheet_data(sheet_name):
    try:
        client = get_gspread_client()
        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        return sh.worksheet(sheet_name).get_all_records()
    except: return []

def display_header():
    # Lấy dữ liệu từ Cloud
    settings_data = get_gsheet_data("ThietLap")
    settings = {str(row.get('Mục')).strip(): row.get('Giá trị') for row in settings_data if row.get('Mục')}
    
    # LOGIC LOGO: Ưu tiên Sheets -> Fallback link gốc
    logo_link = settings.get('Logo')
    if not logo_link:
        # Link ảnh gốc từ phiên bản ní đã ưng ý
        logo_url = "https://lh3.googleusercontent.com/d/1X5_t9u-8X5_t9u-8X5_t9u-8X5_t9u" # Thay ID ảnh Drive thực tế của ní vào đây
    else:
        logo_url = format_drive_link(logo_link)

    st.markdown(f"""
        <div class="bang-hieu-kim-hien">
            <img src="{logo_url}" class="logo-tron" onerror="this.src='https://via.placeholder.com/100?text=KIM+HIEN'">
            <div class="ten-tiem">{settings.get('TenTiem', 'SALON KIM HIỀN')}</div>
            <div class="thong-tin-phu">📍 131, TRẦN BÌNH TRỌNG, MỸ XUYÊN, LONG XUYÊN, AN GIANG</div>
            <div class="sdt-tiem">📞 0978.888.888</div>
            <div class="slogan">"Nơi Bạn Đặt Niềm Tin"</div>
        </div>
    """, unsafe_allow_html=True)

def main():
    if "logged_in" not in st.session_state:
        st.session_state.update({"logged_in": False, "role": None, "last_submit": None, "count": 0, "is_saving": False})

    if not st.session_state["logged_in"]:
        display_header()
        with st.form("login_form"):
            u = st.text_input("Tài khoản")
            p = st.text_input("Mật khẩu", type="password")
            if st.form_submit_button("ĐĂNG NHẬP", use_container_width=True):
                if u == "admin" and p == "2026":
                    st.session_state.update({"logged_in": True, "role": "Admin", "full_name": "Chủ Tiệm", "phone": "0978888888"})
                    st.rerun()
                users = get_gsheet_data("Admin")
                p_hashed = hash_password(p)
                for row in users:
                    if str(u).strip() == str(row.get('Tài khoản')).strip() and p_hashed == str(row.get('Mật khẩu')).strip():
                        st.session_state.update({"logged_in": True, "role": row.get('Quyền'), "full_name": row.get('Họ tên'), "phone": row.get('Số điện thoại')})
                        st.rerun()
                st.error("Sai thông tin!")
    else:
        display_header()
        tab_list = ["📝 NHẬP LIỆU", "📈 BÁO CÁO", "⚙️ CÀI ĐẶT"] if st.session_state["role"] == "Admin" else ["📝 NHẬP LIỆU"]
        tabs = st.tabs(tab_list)

        with tabs[0]:
            st.info(f"👷 NV: {st.session_state['full_name']} | 📞 {st.session_state['phone']}")
            
            # KIỂM TRA HÀNG RÀO THỜI GIAN
            can_submit = True
            wait_msg = ""
            if st.session_state.last_submit:
                now = get_now_vn()
                diff = (now - st.session_state.last_submit).total_seconds() / 60
                required = 3 if st.session_state.count == 1 else 5 if st.session_state.count >= 2 else 0
                if diff < required:
                    can_submit = False
                    wait_msg = f"Vui lòng chờ thêm {round(required - diff, 1)} phút để nhập đơn kế tiếp."

            kh = st.text_input("Khách hàng", "Khách lẻ")
            services = {r['Tên Sản Phẩm']: r['Đơn Giá'] for r in get_gsheet_data("DanhMuc")}
            dv = st.selectbox("Dịch vụ", list(services.keys()) if services else ["Cắt tóc"])
            sl = st.number_input("Số lượng", 1.0)
            
            gia = float(str(services.get(dv, 0)).replace(',', '')) if services else 0
            tong = gia * sl
            st.subheader(f"TỔNG: {tong:,.0f} VNĐ")

            if not can_submit:
                st.error(f"🚫 {wait_msg}")
            else:
                st.warning("⚠️ XÁC NHẬN CHỐNG TRÙNG:")
                confirm = st.checkbox("TÔI XÁC NHẬN ĐƠN NÀY KHÔNG TRÙNG ĐƠN") #
                
                if st.session_state.is_saving:
                    st.button("🚀 ĐANG LƯU...", disabled=True, use_container_width=True)
                    try:
                        client = get_gspread_client()
                        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
                        ws = sh.worksheet("BaoCao")
                        now_vn = get_now_vn()
                        ws.append_row([now_vn.strftime("%d/%m/%Y"), f"{st.session_state['full_name']} ({st.session_state['phone']})", kh, "", dv, sl, gia, tong, tong, now_vn.strftime("%H:%M:%S")])
                        st.session_state.update({"last_submit": now_vn, "count": st.session_state.count + 1, "is_saving": False})
                        st.success("✅ ĐÃ LƯU THÀNH CÔNG!")
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
                    except: 
                        st.session_state.is_saving = False
                        st.rerun()
                else:
                    if st.button("🚀 XÁC NHẬN LƯU ĐƠN", use_container_width=True, type="primary"):
                        if confirm:
                            st.session_state.is_saving = True
                            st.rerun()
                        else: st.error("Phải tích xác nhận mới được lưu!")

        if st.session_state["role"] == "Admin":
            with tabs[1]:
                df = pd.DataFrame(get_gsheet_data("BaoCao"))
                if not df.empty: st.dataframe(df.tail(50), use_container_width=True)
            with tabs[2]:
                set_df = pd.DataFrame(get_gsheet_data("ThietLap"))
                if not set_df.empty: st.table(set_df)

        if st.sidebar.button("🚪 Đăng xuất"):
            st.session_state.clear()
            st.rerun()

if __name__ == "__main__": main()
    
