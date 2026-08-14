import streamlit as st

# Không cần gọi st.set_page_config để tránh lỗi phiên bản Python 3.14
st.markdown('<div style="text-align: center; color: #1E3A8A; font-size: 24px; font-weight: bold;">CÔNG TY TNHH ABC QUỐC SỰ</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; color: #4B5563; font-size: 14px; margin-bottom: 20px;">HỆ THỐNG BÁO CÁO VÀ CHĂM SÓC KHÁCH HÀNG</div>', unsafe_allow_html=True)

with st.container(border=True):
    st.text_input("Tên khách hàng", placeholder="Nhập họ tên khách...")
    st.text_input("Số điện thoại khách hàng", placeholder="Ví dụ: 0912345678")
    st.text_area("Nội dung nhu cầu khách hàng", placeholder="Nhập chi tiết yêu cầu...")
    st.feedback("stars")
    st.button("💾 Gửi & Lưu Báo Cáo", use_container_width=True, type="primary")
