# database.py
import gspread
import streamlit as st
from google.oauth2.service_account import Credentials

@st.cache_resource
def get_db_connection():
    # Ní dùng đúng cách ní đang dùng trong file chính để kết nối
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], 
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    client = gspread.authorize(creds)
    # Ní nhớ điền đúng tên file Google Sheet của ní ở đây
    return client.open("Bản sao của BC_DULIEU_DEMO_2026").sheet1
