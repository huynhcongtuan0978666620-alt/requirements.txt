import streamlit as st
import datetime
import gspread
from google.oauth2.service_account import Credentials

# --- HÀM KẾT NỐI GOOGLE SHEET ---
def get_google_sheet_connection():
    try:
        # Lấy thông tin xác thực từ secrets của Streamlit
        scope = ["https://www.spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        
        # Mở file Google Sheet bằng Link hoặc Tên (Ở đây ta mở bằng Link Trang Tính của ní)
        sheet_url = "https://docs.google.com/spreadsheets/d/16lkyLMwb8OTdrFpSdZHIjWOd4Oyqjs7VKYS814n7Svs/edit"
        sheet = client.open_by_url(sheet_url).sheet1 # Lấy sheet đầu tiên
        return sheet
    except Exception as e:
        st.error(f"Lỗi kết nối Google Sheet: {e}")
        return None

# --- GIAO DIỆN APP ---
st.markdown('<div style="text-align: center; color: #1E3A8A; font-size: 24px; font-weight: bold;">CÔNG TY TNHH ABC QUỐC SỰ</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; color: #4B5563; font-size: 14px; margin-bottom: 20px;">HỆ THỐNG BÁO CÁO VÀ CHĂM SÓC KHÁCH HÀNG</div>', unsafe_allow_html=True)

with st.container(border=True):
    ten_kh = st.text_input("Tên khách hàng", placeholder="Nhập họ tên khách...", key="input_ten_kh")
    sdt_kh = st.text_input("Số điện thoại khách hàng", placeholder="Ví dụ: 0912345678", key="input_sdt_kh")
    nhu_cau = st.text_area("Nội dung nhu cầu khách hàng", placeholder="Nhập chi tiết yêu cầu...", key="input_nhu_cau")
    
    danh_gia = st.feedback("stars", key="feedback_sao")
    # Đổi giá trị sao từ dạng số đếm sang text sao (ví dụ: 5 sao -> "⭐⭐⭐⭐⭐")
    sao_text = "⭐" * (danh_gia + 1) if danh_gia is not None else "Chưa đánh giá"
    
    chot_sale = st.text_input("Trạng thái Chốt Sale", placeholder="Ví dụ: Đã chốt / Đang suy nghĩ", key="input_chot_sale")
    ghi_chu = st.text_area("Ghi chú bổ sung", placeholder="Các lưu ý khác...", key="input_ghi_chu")

    if st.button("💾 Gửi & Lưu Báo Cáo", use_container_width=True, type="primary", key="btn_gui_bao_cao"):
        if not ten_kh or not sdt_kh:
            st.warning("⚠️ Vui lòng nhập đầy đủ Tên khách hàng và Số điện thoại!")
        else:
            sheet = get_google_sheet_connection()
            if sheet:
                try:
                    # Lấy số thứ tự tự động dựa trên số dòng hiện có trong sheet
                    existing_data = sheet.get_all_values()
                    stt = len(existing_data) if len(existing_data) > 0 else 1
                    
                    # Lấy thời gian hiện tại
                    thoi_gian = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Tên nhân viên (Tạm để mặc định, sau này gắn form đăng nhập)
                    ten_nv = "Nhân viên trực"
                    
                    # Chuẩn bị dòng dữ liệu đúng thứ tự 8 cột:
                    # (1) STT, (2) Tên NV, (3) Khách hàng, (4) SĐT khách hàng, (5) Nhu cầu, (6) Thời gian, (7) Chốt Sale, (8) Ghi chú
                    row_data = [
                        stt,
                        ten_nv,
                        ten_kh,
                        str(sdt_kh),
                        nhu_cau,
                        thoi_gian,
                        chot_sale,
                        f"Đánh giá: {sao_text} | Ghi chú: {ghi_chu}"
                    ]
                    
                    # Đẩy dữ liệu vào Google Sheet
                    sheet.append_row(row_data)
                    
                    st.success(f"✅ Đã lưu báo cáo thành công vào Trang tính lúc {thoi_gian}!")
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ Không thể ghi dữ liệu vào Sheet: {e}")
