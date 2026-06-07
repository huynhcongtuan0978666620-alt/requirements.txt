# database.py
import gspread
import streamlit as st
from google.oauth2.service_account import Credentials


@st.cache_resource
def get_db_connection():
    try:
        # Lấy thông tin secrets
        if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
            secrets = dict(st.secrets["connections"]["gsheets"])
        else:
            secrets = dict(st.secrets)

        creds_info = {
            "type": secrets.get("type", "service_account"),
            "project_id": secrets.get("project_id", "hethongphache"),
            "private_key_id": secrets.get("private_key_id", ""),
            "private_key": secrets.get("private_key", "").replace("\\n", "\n"),
            "client_email": secrets.get("client_email", ""),
            "client_id": secrets.get("client_id", ""),
            "token_uri": secrets.get(
                "token_uri", "https://oauth2.googleapis.com/token"
            ),
        }

        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]

        # MỞ KHÓA VÀ KẾT NỐI
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        gc = gspread.authorize(creds)

        url = secrets.get("spreadsheet", "")
        if not url and "spreadsheet" in st.secrets:
            url = st.secrets["spreadsheet"]
            # Ní thay "Trang1" bằng tên Sheet chính xác trong file của ní, hoặc dùng .sheet1 để lấy trang đầu tiên
        return (
            gc.open_by_key(url) if len(url) < 50 else gc.open_by_url(url)
        ).sheet1

        # return gc.open_by_key(url) if len(url) < 50 else gc.open_by_url(url)
    except Exception as e:
        st.error(f"Lỗi khởi tạo kết nối: {e}")
        st.stop()
