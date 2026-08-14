import streamlit as st
import datetime

st.markdown('<div style="text-align: center; color: #1E3A8A; font-size: 24px; font-weight: bold;">CÔNG TY TNHH ABC QUỐC SỰ</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; color: #4B5563; font-size: 14px; margin-bottom: 20px;">HỆ THỐNG BÁO CÁO VÀ CHĂM SÓC KHÁCH HÀNG</div>', unsafe_allow_html=True)

with st.container(border=True):
    # Đặt key riêng cho từng ô để tránh xung đột
    ten_kh = st.text_input("Tên khách hàng", placeholder="Nhập họ tên khách...", key="input_ten_kh")
    sdt_kh = st.text_input("Số điện thoại khách hàng", placeholder="Ví dụ: 0912345678", key="input_sdt_kh")
    nhu_cau = st.text_area("Nội dung nhu cầu khách hàng", placeholder="Nhập chi tiết yêu cầu...", key="input_nhu_cau")
    
    # Đánh giá sao có key riêng
    danh_gia = st.feedback("stars", key="feedback_sao")
    
    # Trạng thái chốt sale và ghi chú
    chot_sale = st.text_input("Trạng thái Chốt Sale", placeholder="Ví dụ: Đã chốt / Đang suy nghĩ", key="input_chot_sale")
    ghi_chu = st.text_area("Ghi chú bổ sung", placeholder="Các lưu ý khác...", key="input_ghi_chu")

    # Nút bấm có key định danh riêng biệt để không bao giờ bị lỗi trùng lặp
    if st.button("💾 Gửi & Lưu Báo Cáo", use_container_width=True, type="primary", key="btn_gui_bao_cao"):
        thoi_gian = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.success(f"✅ Đã ghi nhận lúc: {thoi_gian}")
        st.balloons()
