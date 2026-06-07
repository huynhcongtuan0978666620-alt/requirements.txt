# database.py
import gspread
import streamlit as st
from google.oauth2.service_account import Credentials


@st.cache_resource
def get_db_connection():
    # Ní dùng đúng cách ní đang dùng trong file chính để kết nối
            # ... (đoạn trên ní giữ nguyên)

        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        
        # SỬA ĐOẠN NÀY (Bỏ dấu # ở đầu dòng)
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        
        url = secrets.get("spreadsheet", "")
        # ... (đoạn dưới ní giữ nguyên)
    
