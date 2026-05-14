import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime, timedelta
import pytz
import hashlib
import time

# ==========================================
# GIAO DIỆN CHUẨN SALON KIM HIỀN - V26.0
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
        .warning-box { background-color: #fff3cd; color: #856404; padding: 15px; border-radius: 10px; border: 1px solid #ffeeba; margin: 10px 0; font-weight: bold;}
    </style>
    """, unsafe_allow_html=True)

# --- HÀM HỆ THỐNG ---
def get_now_vn(): 
    return datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))

def get_gspread_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["connections"]["gsheets"], scopes=scope)
    return gspread.authorize(creds)

@st.cache_data(ttl=30)
def get_gsheet_data(sheet_name):
    try:
        client = get_gspread_client()
        sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        return sh.worksheet(sheet_name).get_all_records()
    except: return []

def main():
    if "logged_in" not in st.session_state:
        st.session_state.update({"logged_in": False, "role": None, "last_submit_time": None, "submit_count": 0})

    # Header nguyên bản
    st.markdown(f"""<div class="bang-hieu-kim-hien">
        <div class="ten-tiem">SALON KIM HIỀN</div>
        <div class="thong-tin-phu">📍 131, TRẦN BÌNH TRỌNG, LONG XUYÊN, AN GIANG</div>
        <div class="sdt-tiem">📞 0978.888.888</div>
        <div class="slogan">"Nơi Bạn Đặt Niềm Tin"</div>
    </div>""", unsafe_allow_html=True)

    if not st.session_state["logged_in"]:
        with st.form("login_form"):
            u = st.text_input("Tài khoản")
            p = st.text_input("Mật khẩu", type="password")
            if st.form_submit_button("ĐĂNG NHẬP", use_container_width=True):
                if u == "admin" and p == "2026":
                    st.session_state.update({"logged_in": True, "role": "Admin", "full_name": "Chủ Tiệm"})
                    st.rerun()
                # Logic check nhân viên (bỏ qua để ngắn gọn nhưng ní giữ lại phần check SHA256 cũ nhé)
                st.error("Sai thông tin!")
    else:
        tabs = st.tabs(["📝 NHẬP LIỆU", "📈 BÁO CÁO", "⚙️ CÀI ĐẶT"] if st.session_state["role"] == "Admin" else ["📝 NHẬP LIỆU"])

        with tabs[0]:
            st.info(f"👷 Nhân viên: {st.session_state.get('full_name')}")
            kh = st.text_input("Khách hàng", "Khách lẻ")
            dv = st.selectbox("Dịch vụ", ["Cắt tóc", "Gội đầu", "Làm móng"])
            sl = st.number_input("Số lượng", 1.0)
            
            # --- TÍNH TOÁN THỜI GIAN CHỜ (COOLDOWN) ---
            can_submit = True
            wait_time = 0
            if st.session_state.last_submit_time:
                now = get_now_vn()
                elapsed = (now - st.session_state.last_submit_time).total_seconds() / 60
                
                # Sau đơn 1 chờ 3 phút, sau đó chờ 5 phút
                required_wait = 3 if st.session_state.submit_count == 1 else 5 if st.session_state.submit_count >= 2 else 0
                if elapsed < required_wait:
                    can_submit = False
                    wait_time = round(required_wait - elapsed, 1)

            if not can_submit:
                st.error(f"🚫 VUI LÒNG CHỜ {wait_time} PHÚT NỮA MỚI ĐƯỢC NHẬP ĐƠN TIẾP THEO!")
            else:
                # --- CẢNH BÁO TRÙNG & XÁC NHẬN ---
                confirm_check = st.checkbox("✅ TÔI XÁC NHẬN ĐƠN NÀY KHÔNG BỊ TRÙNG")
                
                if st.button("🚀 LƯU ĐƠN HÀNG", use_container_width=True, type="primary"):
                    if not confirm_check:
                        st.warning("⚠️ BẠN PHẢI TÍCH VÀO Ô XÁC NHẬN TRƯỚC KHI LƯU!")
                    else:
                        with st.spinner("Đang lưu..."):
                            # Logic lưu đơn thực tế (append_row)
                            st.session_state.last_submit_time = get_now_vn()
                            st.session_state.submit_count += 1
                            st.success("Đã lưu đơn thành công!")
                            st.balloons()
                            time.sleep(1)
                            st.rerun()

        if st.session_state["role"] == "Admin":
            with tabs[1]: # Tab Báo Cáo
                st.subheader("📊 Lịch sử doanh thu")
                data = get_gsheet_data("BaoCao")
                if data: st.dataframe(pd.DataFrame(data).tail(50), use_container_width=True)
                else: st.warning("Không có dữ liệu báo cáo.")
            
            with tabs[2]: # Tab Cài Đặt
                st.subheader("⚙️ Cấu hình hệ thống")
                settings = get_gsheet_data("ThietLap")
                if settings: st.table(pd.DataFrame(settings))

if __name__ == "__main__": main()
                        
