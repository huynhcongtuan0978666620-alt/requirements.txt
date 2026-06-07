# database.py
import gspread
import streamlit as st
from google.oauth2.service_account import Credentials

@st.cache_resource
def get_db_connection():
    # 1. Lấy secrets
    secrets = dict(st.secrets["gcp_service_account"])
    secrets["private_key"] = secrets["private_key"].replace("\\n", "\n")
    
    # 2. Tạo credentials
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(secrets, scopes=scope)
    
    # 3. ĐỔI TÊN BIẾN THÀNH 'gc' THAY VÌ 'client'
    gc = gspread.authorize(creds)
    
    # 4. Trả về sheet
    return gc.open("Bản sao của BC_DULIEU_DEMO_2026").sheet1
