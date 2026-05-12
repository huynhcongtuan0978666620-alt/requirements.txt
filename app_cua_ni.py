import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- CẤU HÌNH ĐƯỜNG LINK MỚI CỦA NÍ ---
URL_KHO = "[https://docs.google.com/spreadsheets/d/1vnbmjqQ-RSVYg3xP4qRzTFMvuVr3kBE-QLGgKzn5LA4/edit?usp=sharing](https://docs.google.com/spreadsheets/d/1vnbmjqQ-RSVYg3xP4qRzTFMvuVr3kBE-QLGgKzn5LA4/edit?usp=sharing)"

st.set_page_config(page_title="Quản Lý Pha Chế V3.0", page_icon="🧪", layout="wide")

# Thiết lập kết nối với Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def doc_du_lieu(sheet_name):
    # Đọc dữ liệu từ sheet tương ứng, ttl=0 để luôn lấy dữ liệu mới nhất
    return conn.read(spreadsheet=URL_KHO, worksheet=sheet_name, ttl=0)

# --- KIỂM TRA TRẠNG THÁI ĐĂNG NHẬP ---
if "auth" not in st.session_state:
    st.session_state.update({"auth": False, "user": ""})

if not st.session_state.auth:
    _, col_login, _ = st.columns([1, 1.5, 1])
    with col_login:
        st.markdown("<h2 style='text-align: center;'>💎 ĐĂNG NHẬP HỆ THỐNG</h2>", unsafe_allow_html=True)
        p = st.text_input("Số điện thoại (Tài khoản)")
        pw = st.text_input("Mật khẩu", type="password")
        if st.button("XÁC NHẬN VÀO HỆ THỐNG"):
            try:
                df_nv = doc_du_lieu("NhanVien")
                # Kiểm tra tài khoản và mật khẩu
                user = df_nv[(df_nv['Số điện thoại'].astype(str) == str(p).strip()) & 
                             (df_nv['Mật khẩu'].astype(str) == str(pw).strip())]
                if not user.empty:
                    st.session_state.auth = True
                    st.session_state.user = user.iloc[0]['Tên nhân viên']
                    st.rerun()
                else:
                    st.error("Thông tin đăng nhập không đúng!")
            except Exception as e:
                st.error(f"Lỗi kết nối Sheets: {e}. Ní kiểm tra quyền Chia sẻ (Editor) nhé!")
    st.stop()

# --- GIAO DIỆN CHÍNH SAU KHI ĐĂNG NHẬP ---
st.sidebar.subheader(f"👤 Nhân viên: {st.session_state.user}")
if st.sidebar.button("🔓 Đăng xuất"):
    st.session_state.auth = False
    st.rerun()

tab_nhap, tab_soat = st.tabs(["📝 NHẬP MẺ HÀNG", "🕵️ SOÁT SỔ CÁI"])

# --- TAB 1: NHẬP LIỆU ---
with tab_nhap:
    try:
        df_dm = doc_du_lieu("DanhMuc")
        list_sp = df_dm['Tên Sản Phẩm'].tolist()

        col_trai, col_phai = st.columns([1, 1.2])
        with col_trai:
            st.subheader("Thông tin pha chế")
            sp = st.selectbox("Sản phẩm pha chế", list_sp)
            
            c1, c2 = st.columns(2)
            rx = c1.number_input("Số lượng Rửa Xe (Lít)", 0.0, step=0.1)
            tn = c2.number_input("Số lượng Tẩy Nhôm (Lít)", 0.0, step=0.1)
            
            tong = rx + tn
            p_rx = round((rx/tong)*100, 2) if tong > 0 else 0
            p_tn = round((tn/tong)*100, 2) if tong > 0 else 0
            
            st.info(f"📊 Tỷ lệ mẻ: RX {p_rx}% - TN {p_tn}%")
            
            # Form đánh giá theo yêu cầu của ní
            diem = st.slider("Đánh giá chất lượng (xx/10)", 0, 10, 8)
            note = st.text_area("Hướng dẫn thao tác / Ghi chú sử dụng", "Thao tác chuẩn theo quy trình.")

            if st.button("🚀 GỬI DỮ LIỆU VỀ KHO"):
                # Tạo dòng dữ liệu mới
                new_row = pd.DataFrame([{
                    "Ngày": datetime.now().strftime('%d/%m/%Y'),
                    "Người làm": st.session_state.user,
                    "Sản phẩm": sp,
                    "SL Rửa Xe": rx,
                    "Tỷ lệ RX": f"{p_rx}%",
                    "SL Tẩy Nhôm": tn,
                    "Tỷ lệ TN": f"{p_tn}%",
                    "Đánh giá": f"{diem}/10",
                    "Ghi chú": note,
                    "Giờ lưu": datetime.now().strftime('%H:%M:%S')
                }])
                
                # Đọc dữ liệu cũ, cộng thêm dòng mới và cập nhật
                df_bc = doc_du_lieu("BaoCao")
                df_combined = pd.concat([df_bc, new_row], ignore_index=True)
                conn.update(spreadsheet=URL_KHO, worksheet="BaoCao", data=df_combined)
                st.success("✅ ĐÃ ĐỒNG BỘ DỮ LIỆU THÀNH CÔNG!")
                st.balloons()
                
        with col_phai:
            st.subheader("Lịch sử 5 mẻ gần nhất")
            df_view = doc_du_lieu("BaoCao")
            st.dataframe(df_view.tail(5), use_container_width=True)
            
    except Exception as e:
        st.warning(f"Đang đợi dữ liệu từ Sheets... (Lỗi: {e})")

# --- TAB 2: SOÁT SỔ ---
with tab_soat:
    st.subheader("🔍 Nhật ký tổng kho (Sổ cái)")
    try:
        df_full = doc_du_lieu("BaoCao")
        st.write(f"Tổng số mẻ hàng trong kho: **{len(df_full)}**")
        st.dataframe(df_full, use_container_width=True)
    except:
        st.info("Chưa có dữ liệu trong sổ cái.")
