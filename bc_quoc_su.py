import streamlit as st

# Cấu hình trang tối giản để tránh lỗi phiên bản
st.set_page_config(
    page_title="BC Quốc Sự",
    page_layout="centered"
)

# --- CSS TẠO THẨM MỸ, GIAO DIỆN SANG TRỌNG ---
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        color: #1E3A8A;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .sub-title {
        text-align: center;
        color: #4B5563;
        font-size: 14px;
        margin-bottom: 20px;
    }
    .section-header {
        background-color: #F3F4F6;
        padding: 10px;
        border-radius: 6px;
        color: #1F2937;
        font-weight: bold;
        margin-top: 15px;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# ==================== 1. MÀN HÌNH ĐĂNG NHẬP (GIẢ LẬP KHung Sườn) ====================
# (Khi chạy thật, nếu chưa đăng nhập sẽ hiện form này)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = True  # Tạm thời để True để ní thấy ngay giao diện chính bên dưới

if not st.session_state.logged_in:
    st.markdown('<div class="main-title">ĐĂNG NHẬP HỆ THỐNG</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">BC Quốc Sự - Vui lòng xác thực nhân sự</div>', unsafe_allow_html=True)
    with st.form("login_form"):
        nv_id = st.text_input("Mã hoặc Tên nhân viên")
        submit_login = st.form_submit_button("Đăng Nhập")
        if submit_login:
            if nv_id:
                st.session_state.logged_in = True
                st.session_state.ten_nv = nv_id
                st.rerun()
            else:
                st.warning("Vui lòng nhập tên nhân viên!")
else:
    # ==================== 2. GIAO DIỆN CHÍNH APP ====================
    
    # Thông tin công ty ở phía trên cùng
    st.markdown('<div class="main-title">CÔNG TY TNHH ABC QUỐC SỰ</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">HỆ THỐNG BÁO CÁO VÀ CHĂM SÓC KHÁCH HÀNG</div>', unsafe_allow_html=True)
    
    # Hiển thị nhân viên đang thao tác (Góc trên)
    col_info1, col_info2 = st.columns([3, 1])
    with col_info1:
        st.info("👤 Nhân viên trực: **Nguyễn Văn A** (Demo)")
    with col_info2:
        if st.button("Đăng xuất"):
            st.session_state.logged_in = False
            st.rerun()

    st.markdown("---")

    # Khung nhập liệu thông tin khách hàng
    st.markdown('<div class="section-header">📝 PHIẾU GHI NHẬN THÔNG TIN & NHU CẦU</div>', unsafe_allow_html=True)
    
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Tên khách hàng", placeholder="Nhập họ tên khách...", disabled=True)
        with col2:
            st.text_input("Số điện thoại khách hàng", placeholder="Ví dụ: 0912345678", disabled=True)
            
        st.text_area("Nội dung nhu cầu khách hàng (Tự ghi chép)", placeholder="Nhập chi tiết yêu cầu, thắc mắc hoặc nội dung tư vấn...", height=100, disabled=True)
        
        st.markdown("⭐ **Đánh giá từ khách hàng (1 đến 5 sao):**")
        # Tạo thanh chọn sao trực quan (khung sườn)
        st.feedback("stars") 

        st.text_input("Trạng thái Chốt Sale", placeholder="Ví dụ: Đã chốt / Đang suy nghĩ / Từ chối", disabled=True)
        st.text_area("Ghi chú bổ sung", placeholder="Các lưu ý khác...", height=60, disabled=True)

    # Khu vực các nút chức năng (Action buttons)
    st.markdown("<br>", unsafe_allow_html=True)
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        st.button("💾 Gửi & Lưu Báo Cáo", use_container_width=True, type="primary", disabled=True)
    with col_btn2:
        st.button("🖨️ In 'BC Quốc Sự' (A4 Dọc)", use_container_width=True, disabled=True)

    # Footer nhỏ xinh
    st.markdown("<br><p style='text-align: center; color: #9CA3AF; font-size: 12px;'>Phát triển độc quyền cho đối tác bởi Đội ngũ kỹ thuật Salon Kim Hiền & AI</p>", unsafe_allow_html=True)
