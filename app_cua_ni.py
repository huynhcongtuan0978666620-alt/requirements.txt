import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import pytz
import hashlib
import time

# ==========================================
# GIAO DIỆN CHUẨN SALON KIM HIỀN - 2026
# ==========================================
st.set_page_config(page_title="SALON KIM HIỀN - QUẢN LÝ", layout="centered", page_icon="✂️")

st.markdown("""
    <style>
        header, footer, .stAppDeployButton {display: none !important; visibility: hidden !important;}
        [data-testid="stStatusWidget"], [data-testid="stToolbar"] {display: none !important;}
        
        .bang-hieu-lktv {
            text-align: center;
            background: linear-gradient(135deg, #1a2a6c 0%, #b21f1f 50%, #fdbb2d 100%);
            color: white; padding: 25px; border-radius: 20px;
            margin-bottom: 20px; box-shadow: 0px 10px 30px rgba(0,0,0,0.3);
            border: 1px solid #ffffff20;
        }
        .ten-tiem { font-size: 30px; font-weight: 800; text-transform: uppercase; margin-bottom: 5px; }
        .thong-tin-phu { font-size: 15px; color: #ecf0f1; opacity: 0.9; }
        .sdt-tiem { font-size: 18px; color: #ffffff; font-weight: 700; margin-top: 5px; }
        .slogan { font-size: 16px; color: #ffffff; font-weight: 500; font-style: italic; margin-top: 10px; border-top: 1px solid #ffffff30; padding-top: 10px; }

        .stTabs [data-baseweb="tab-list"] { display: flex; justify-content: center; gap: 12px; width: 100%; }
        .stTabs [data-baseweb="tab"] { flex: 1; height: 55px; background-color: #f8f9fa; border-radius: 12px 12px 0 0; max-width: 160px; border: 1px solid #dee2e6; }
        .stTabs [data-baseweb="tab"] p { color: #333333 !important; font-weight: 700 !important; font-size: 16px; }
        .stTabs [data-baseweb="tab"][aria-selected="true"] { background-color: #fdbb2d !important; border: none; }
    </style>
    """, unsafe_allow_html=True)

def hash_password(password): 
    return hashlib.sha256(str(password).strip().encode()).hexdigest()

def get_now_vn(): 
    return datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))

def get_gspread_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["connections"]["gsheets"], scopes=scope)
    return gspread.authorize(creds)

@st.cache_data(ttl=60)
def get_service_data():
    try:
        client = get_gspread_client()
        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        return {r['Tên Sản Phẩm']: float(str(r['Đơn Giá']).replace(',','')) for r in sh.worksheet("DanhMuc").get_all_records() if r['Tên Sản Phẩm']}
    except: return {"Dịch vụ cơ bản": 50000}

def get_all_users():
    try:
        client = get_gspread_client()
        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        return sh.worksheet("Admin").get_all_records()
    except: return []

def main():
    if "is_processing" not in st.session_state:
        st.session_state.is_processing = False
    if "logged_in" not in st.session_state:
        st.session_state.update({"logged_in": False, "role": None, "full_name": None, "phone": None})

    st.markdown("""
        <div class="bang-hieu-lktv">
            <div class="ten-tiem">SALON KIM HIỀN</div>
            <div class="thong-tin-phu">📍 131, TRẦN BÌNH TRỌNG, LONG XUYÊN, AN GIANG</div>
            <div class="sdt-tiem">📞 0978.888.888</div>
            <div class="slogan">"Nơi Bạn Đặt Niềm Tin"</div>
        </div>
    """, unsafe_allow_html=True)

    if not st.session_state["logged_in"]:
        with st.form("login_form"):
            u = st.text_input("Tài khoản")
            p = st.text_input("Mật khẩu", type="password")
            if st.form_submit_button("ĐĂNG NHẬP", use_container_width=True):
                if u == "admin" and p == "2026":
                    st.session_state.update({"logged_in": True, "role": "Admin", "full_name": "Chủ Tiệm", "phone": "0978.888.888"})
                    st.rerun()
                users = get_all_users()
                p_hash = hash_password(p)
                for row in users:
                    if str(u) == str(row.get('Tài khoản')).strip() and p_hash == str(row.get('Mật khẩu')).strip():
                        st.session_state.update({"logged_in": True, "role": row.get('Quyền'), "full_name": row.get('Họ tên'), "phone": row.get('Số điện thoại')})
                        st.rerun()
                st.error("Sai thông tin!")
    else:
        tabs = st.tabs(["📝 NHẬP LIỆU", "📈 BÁO CÁO", "⚙️ CÀI ĐẶT"] if st.session_state["role"] == "Admin" else ["📝 NHẬP LIỆU"])

        with tabs[0]:
            st.info(f"👷 NV: {st.session_state['full_name']} | {st.session_state['phone']}")
            services = get_service_data()
            kh = st.text_input("Khách hàng", "Khách lẻ")
            sdt_kh = st.text_input("SĐT khách")
            dv = st.selectbox("Dịch vụ", list(services.keys()))
            sl = st.number_input("Số lượng", 0.5, 50.0, 1.0, 0.5)
            gia = services.get(dv, 0)
            tong = gia * sl
            st.markdown(f"### TỔNG: `{tong:,.0f} VNĐ`")
            
            # --- KHÓA NÚT CHỐNG TRÙNG TUYỆT ĐỐI ---
            if st.session_state.is_processing:
                st.warning("⚠️ ĐANG LƯU... ĐỪNG BẤM THÊM NÍ ƠI!")
                st.button("🚀 HỆ THỐNG ĐANG XỬ LÝ...", disabled=True, use_container_width=True)
                try:
                    client = get_gspread_client()
                    sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
                    ws = sh.worksheet("BaoCao")
                    now = get_now_vn()
                    nv_label = f"{st.session_state['full_name']} ({st.session_state['phone']})"
                    ws.append_row([now.strftime("%d/%m/%Y"), nv_label, kh, sdt_kh, dv, sl, gia, tong, tong, now.strftime("%H:%M:%S")])
                    st.success("✅ ĐÃ LƯU THÀNH CÔNG!")
                    st.balloons()
                    time.sleep(2)
                    st.session_state.is_processing = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Lỗi: {e}")
                    st.session_state.is_processing = False
                    st.rerun()
            else:
                if st.button("🚀 XÁC NHẬN LƯU ĐƠN", use_container_width=True, type="primary"):
                    st.session_state.is_processing = True
                    st.rerun()

        if st.session_state["role"] == "Admin":
            with tabs[1]:
                if st.button("🔄 Cập nhật"): st.rerun()
                try:
                    client = get_gspread_client()
                    sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
                    df = pd.DataFrame(sh.worksheet("BaoCao").get_all_records())
                    st.dataframe(df.tail(20), use_container_width=True)
                except: st.write("Đang tải dữ liệu...")

        if st.sidebar.button("🚪 Đăng xuất"):
            st.session_state.clear()
            st.rerun()

if __name__ == "__main__":
    main()
    
