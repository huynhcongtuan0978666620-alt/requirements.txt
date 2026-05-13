import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# URL FILE MỚI CỦA NÍ
URL_MOI = "https://docs.google.com/spreadsheets/d/1wkWwXtNSY2E9DEm1lG2fRk0WEmNy2XDUUteppiyJgBo/edit?usp=sharing"

st.set_page_config(page_title="Pha Chế DBX 2026", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

st.markdown("<h2 style='text-align: center; color: #007bff;'>🧪 QUẢN LÝ PHA CHẾ THỰC CHIẾN</h2>", unsafe_allow_html=True)

# Lấy danh mục sản phẩm từ tab DanhMuc
try:
    df_dm = conn.read(spreadsheet=URL_MOI, worksheet="DanhMuc", ttl=0)
    danh_sach_sp = df_dm.iloc[:, 0].tolist()
except:
    danh_sach_sp = ["DBX V1.2", "DBX V1.3", "Dung dịch Rửa Xe", "Tẩy Nhôm"]

# --- KHU VỰC NHẬP LIỆU ---
with st.expander("📝 NHẬP THÔNG TIN MẺ HÀNG", expanded=True):
    c1, c2 = st.columns(2)
    with c1:
        sp = st.selectbox("Sản phẩm pha chế", danh_sach_sp)
        rx = st.number_input("Lượng Rửa Xe (Lít)", 0.0, step=0.1)
        tn = st.number_input("Lượng Tẩy Nhôm (Lít)", 0.0, step=0.1)
    with c2:
        dg = st.select_slider("Đánh giá chất lượng (xx/10)", options=list(range(1, 11)), value=8)
        gc = st.text_area("Ghi chú / Hướng dẫn thao tác", "Pha chế tại Lab.")

# Tính tỷ lệ % tự động
tong = rx + tn
if tong > 0:
    tile_rx = f"{(rx/tong)*100:.1f}%"
    tile_tn = f"{(tn/tong)*100:.1f}%"
    st.success(f"📊 Tỷ lệ: RX {tile_rx} - TN {tile_tn} (Tổng: {tong} Lít)")

# --- NÚT LƯU DỮ LIỆU ---
if st.button("🚀 LƯU VÀO SỔ CÁI"):
    try:
        new_row = pd.DataFrame([{
            "Ngày": datetime.now().strftime("%d/%m/%Y"),
            "Người làm": "Chủ tiệm",
            "Sản phẩm": sp,
            "SL Rửa Xe": rx,
            "Tỷ lệ RX": tile_rx if tong > 0 else "0%",
            "SL Tẩy Nhôm": tn,
            "Tỷ lệ TN": tile_tn if tong > 0 else "0%",
            "Đánh giá": f"{dg}/10",
            "Ghi chú": gc,
            "Giờ lưu": datetime.now().strftime("%H:%M:%S")
        }])
        
        # Đọc dữ liệu cũ từ tab BaoCao
        df_old = conn.read(spreadsheet=URL_MOI, worksheet="BaoCao", ttl=0)
        df_updated = pd.concat([df_old, new_row], ignore_index=True)
        
        # Ghi đè lại vào Google Sheets
        conn.update(spreadsheet=URL_MOI, worksheet="BaoCao", data=df_updated)
        st.balloons()
        st.info("✅ Đã lưu thành công mẻ hàng vào file BC_DULIEU_DEMO_2026!")
    except Exception as e:
        st.error(f"Lỗi kết nối: {e}. Ní kiểm tra lại quyền 'Người chỉnh sửa' trên Sheets nhé!")

# Xem lịch sử nhanh
if st.checkbox("🕵️ Hiển thị lịch sử pha chế"):
    try:
        st.dataframe(conn.read(spreadsheet=URL_MOI, worksheet="BaoCao", ttl=0), use_container_width=True)
    except:
        st.warning("Chưa có dữ liệu trong tab BaoCao.")
