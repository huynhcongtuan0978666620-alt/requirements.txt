# database.py
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st

def get_client():
    # Ní bỏ đoạn code gspread.service_account(...) của ní vào đây
    # Nên lưu credentials vào st.secrets để bảo mật ní nhé!
    return gspread.service_account(filename="credentials.json")

def get_data_from_sheet(sheet_name):
    client = get_client()
    sheet = client.open(config.TEN_FILE_SHEET).worksheet(sheet_name)
    return pd.DataFrame(sheet.get_all_records())
  
