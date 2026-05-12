import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- CẤU HÌNH ---
URL_KHO = "https://docs.google.com/spreadsheets/d/1vnbmjqQ-RSVYg3xP4qRzTFMvuVr3kBE-QLGgKzn5LA4/edit?usp=sharing"

st.set_page_config(page_title="Quản Lý Pha Chế V3.0", page_icon="🧪", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

def doc_du_lieu(sheet_name):
    # Đọc dữ liệu và ép kiểu string ngay từ đầu để tránh lỗi định dạng
    df = conn.read(spreadsheet=URL_KHO, worksheet=sheet_name, ttl=0)
    return df.astype(str)

if "auth" not in st.session_state:
    st.session_state.update({"auth": False, "user": ""})

# --- GIAO DIỆN ĐĂNG NHẬP ---
if not st.session_state.auth:
    _, col_login, _ = st.columns([1, 1.5, 1])
    with col_login:
        st.markdown("<h2 style='text-align: center;'>💎 HỆ THỐNG PHA CHẾ</h2>", unsafe_allow_html=True)
        p = st.text_input("Số điện thoại (Tài khoản)")
        pw = st.text_input("Mật khẩu", type="password")
        if st.button("XÁC NHẬN ĐĂNG NHẬP"):
            try:
                df_nv = doc_du_lieu("NhanVien")
                # Làm sạch dữ liệu đầu vào để so sánh chính xác
                p_val = p.strip().lstrip('0') # Bỏ số 0 đầu để khớp với Sheets nếu bị mất
                pw_val = pw.strip()
                
                # Tìm user (So sánh chứa chuỗi để linh hoạt hơn)
                user = df_nv[df_nv['So_dien_thoai'].str.contains(p_val) & (df_nv['Mat_khau'] == pw_val)]
                
                if not user.empty:
                    st.session_state.auth = True
                    st.session_state.user = user.iloc[0]['Ten_nhan_vien']
                    st.rerun()
                else:
                    st.error("Sai tài khoản hoặc mật khẩu rồi ní!")
            except Exception as e:
                st.error(f"Lỗi kết nối: {e}. Ní kiểm tra cột So_dien_thoai trên Sheets nhé!")
    st.stop()

# --- GIAO DIỆN CHÍNH SAU ĐĂNG NHẬP ---
st.sidebar.subheader(f"👤 Chào ní: {st.session_state.user}")
if st.sidebar.button("🔓 Đăng xuất"):
    st.session_state.auth = False
    st.rerun()

tab1, tab2 = st.tabs(["📝 NHẬP MẺ HÀNG", "🕵️ SOÁT SỔ CÁI"])

with tab1:
    try:
        df_dm = doc_du_lieu("DanhMuc")
        sp = st.selectbox("Chọn sản phẩm", df_dm['Tên Sản Phẩm'].tolist())
        
        c1, c2 = st.columns(2)
        rx = c1.number_input("Số lượng RX (Lít)", 0.0)
        tn = c2.number_input("Số lượng TN (Lít)", 0.0)
        
        tong = rx + tn
        p_rx = f"{round((rx/tong)*100,1)}%" if tong > 0 else "0%"
        p_tn = f"{round((tn/tong)*100,1)}%" if tong > 0 else "0%"
        st.info(f"📊 Tỷ lệ mẻ: RX {p_rx} - TN {p_tn}")
        
        d = st.slider("Đánh giá chất lượng (1-10)", 0, 10, 8)
        n = st.text_area("Ghi chú thao tác", "Thực hiện chuẩn quy trình.")
        
        if st.button("🚀 LƯU DỮ LIỆU"):
            new_row = pd.DataFrame([{
                "Ngày": datetime.now().strftime('%d/%m/%Y'),
                "Người làm": st.session_state.user,
                "Sản phẩm": sp, "SL Rửa Xe": rx, "Tỷ lệ RX": p_rx,
                "SL Tẩy Nhôm": tn, "Tỷ lệ TN": p_tn,
                "Đánh giá": f"{d}/10", "Ghi chú": n,
                "Giờ lưu": datetime.now().strftime('%H:%M:%S')
            }])
            df_bc = doc_du_lieu("BaoCao")
            df_final = pd.concat([df_bc, new_row], ignore_index=True)
            conn.update(spreadsheet=URL_KHO, worksheet="BaoCao", data=df_final)
            st.success("✅ ĐÃ ĐỒNG BỘ VỀ KHO!")
            st.balloons()
            
    except Exception as e:
        st.warning("Đang chờ dữ liệu từ Sheets...")

with tab2:
    st.subheader("🔍 Nhật ký tổng kho")
    try:
        st.dataframe(doc_du_lieu("BaoCao"), use_container_width=True)
    except:
        st.info("Chưa có dữ liệu.")
