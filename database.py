# database.py
import gspread
import streamlit as st
from google.oauth2.service_account import Credentials


@st.cache_resource
def get_db_connection():
    # 1. Lấy thông tin từ secrets
    secrets = dict(st.secrets["gcp_service_account"])

    # 2. Định dạng lại private_key (rất quan trọng)
    secrets["private_key"] = secrets["private_key"].replace("\\n", "\n")

    # 3. Tạo credentials
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(secrets, scopes=scope)

    # 4. Xác thực và mở sheet
    client = gspread.authorize(creds)

    # Ní thay tên file chính xác vào đây
    return client.open("Bản sao của BC_DULIEU_DEMO_2026").sheet1
