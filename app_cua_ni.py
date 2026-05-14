import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime, timedelta
import pytz
import hashlib
import time

# ==========================================
# GIAO DIỆN CHUẨN SALON KIM HIỀN
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
        .sdt-tiem { font-size: 18px; color: #f1c40f; font-weight: 700; }
        .slogan { font-size: 15px; color: #f1c40f; font-weight: 500; font-style: italic; margin-top: 10px; border-top: 1px solid #ffffff30; padding-top: 10px; }

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
def get_gsheet_data(sheet_name):
    try:
        client = get_gspread_client()
        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        return sh.worksheet(sheet_name).get_all_records()
    except: return []

def display_header(settings):
    logo_url = format_drive_link(settings.get('Logo', ''))
    st.markdown(f"""
        <div class="bang-hieu-kim-hien">
            <img src="{logo_url}" class="logo-tron">
            <div class="ten-tiem">{settings.get('TenTiem', 'SALON KIM HIỀN')}</div>
            <div class="thong-tin-phu">📍 131, TRẦN BÌNH TRỌNG, MỸ XUYÊN, LONG XUYÊN, AN GIANG</div>
            <div class="sdt-tiem">📞 0978.888.888</div>
            <div class="slogan">"Nơi Bạn Đặt Niềm Tin"</div>
        </div>
    """, unsafe_allow_html=True)

def main():
    if "logged_in" not in st.session_state:
        st.session_state.update({"logged_in": False, "role": None, "last_submit": None, "count": 0, "is_saving": False})

    settings_list = get_gsheet_data("ThietLap")
    settings = {row['Mục']: row['Giá trị'] for row in settings_list if 'Mục' in row}

    if not st.session_state["logged_in"]:
        display_header(settings)
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
        display_header(settings)
        tabs = st.tabs(["📝 NHẬP LIỆU", "📈 BÁO CÁO", "⚙️ CÀI ĐẶT"] if st.session_state["role"] == "Admin" else ["📝 NHẬP LIỆU"])

        with tabs[0]:
            st.info(f"👷 NV: {st.session_state['full_name']} | 📞 {st.session_state['phone']}")
            
            # Kiểm tra hàng rào thời gian (Cooldown)
            can_submit = True
            wait_msg = ""
            if st.session_state.last_submit:
                now = get_now_vn()
                diff = (now - st.session_state.last_submit).total_seconds() / 60
                required = 3 if st.session_state.count == 1 else 5 if st.session_state.count >= 2 else 0
                if diff < required:
                    can_submit = False
                    wait_msg = f"Vui lòng chờ thêm {round(required - diff, 1)} phút để nhập đơn kế tiếp."

            kh = st.text_input("Tên khách hàng", "Khách lẻ")
            sdt = st.text_input("SĐT khách")
            services = {r['Tên Sản Phẩm']: r['Đơn Giá'] for r in get_gsheet_data("DanhMuc")}
            dv = st.selectbox("Dịch vụ", list(services.keys()))
            sl = st.number_input("Số lượng", 1.0)
            
            tong = float(str(services.get(dv, 0)).replace(',', '')) * sl
            st.subheader(f"TỔNG: {tong:,.0f} VNĐ")

            if not can_submit:
                st.error(f"🚫 {wait_msg}")
            else:
                st.warning("⚠️ KIỂM TRA TRÙNG ĐƠN:")
                confirm = st.checkbox("TÔI XÁC NHẬN ĐƠN NÀY KHÔNG TRÙNG VÀ ĐÚNG SỐ TIỀN")
                
                if st.session_state.is_saving:
                    st.button("🚀 ĐANG LƯU...", disabled=True, use_container_width=True)
                    try:
                        client = get_gspread_client()
                        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
                        ws = sh.worksheet("BaoCao")
                        now_vn = get_now_vn()
                        ws.append_row([now_vn.strftime("%d/%m/%Y"), f"{st.session_state['full_name']} ({st.session_state['phone']})", kh, sdt, dv, sl, services.get(dv), tong, tong, now_vn.strftime("%H:%M:%S")])
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
                        else: st.error("Vui lòng tích xác nhận chống trùng!")

        if st.session_state["role"] == "Admin":
            with tabs[1]:
                st.dataframe(pd.DataFrame(get_gsheet_data("BaoCao")).tail(50), use_container_width=True)
            with tabs[2]:
                st.table(pd.DataFrame(get_gsheet_data("ThietLap")))

        if st.sidebar.button("🚪 Đăng xuất"):
            st.session_state.clear()
            st.rerun()

if __name__ == "__main__": main()
    
