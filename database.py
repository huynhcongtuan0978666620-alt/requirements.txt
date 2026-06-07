# database.py - BỘ MÁY XỬ LÝ DỮ LIỆU (DATABASE LAYER)
import gspread
import streamlit as st
from google.oauth2.service_account import Credentials
import pandas as pd
import re
from datetime import datetime
import pytz

# --- CẤU HÌNH KẾT NỐI ---
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


@st.cache_resource
def get_google_sheet_workbook():
    try:
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

        creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
        client = gspread.authorize(creds)
        url = secrets.get("spreadsheet", "")
        if not url and "spreadsheet" in st.secrets:
            url = st.secrets["spreadsheet"]
        return client.open_by_key(url) if len(url) < 50 else client.open_by_url(url)
    except Exception as e:
        st.error(f"Lỗi khởi tạo kết nối Sheets: {e}")
        st.stop()


# --- CÁC HÀM TRUY XUẤT DỮ LIỆU ---
def get_now_vn():
    vn_tz = pytz.timezone("Asia/Ho_Chi_Minh")
    return datetime.now(vn_tz)


@st.cache_data(ttl=3600)
def get_settings():
    try:
        sh = get_google_sheet_workbook()
        rows = sh.worksheet("ThietLap").get_all_values()
        return {
            str(row[0]).strip(): str(row[1]).strip() for row in rows if len(row) > 1
        }
    except:
        return {
            "TenTiem": "SALON KIM HIỀN",
            "Diachi": "131, TRẦN BÌNH TRỌNG, LONG XUYÊN",
            "SDT": "0947.58.1516",
        }


@st.cache_data(ttl=3600)
def get_service_data():
    try:
        sh = get_google_sheet_workbook()
        rows = sh.worksheet("DanhMuc").get_all_values()
        danh_sach_dv = {}
        for row in rows[1:]:
            if len(row) >= 2:
                ten_dv = str(row[0]).strip()
                if not ten_dv:
                    continue
                try:
                    gia_goc = float(
                        str(row[1]).replace(".", "").replace(",", "").strip()
                    )
                except:
                    gia_goc = 0.0
                hoa_hong = 0.0
                if len(row) >= 3 and row[2]:
                    try:
                        hoa_hong = float(
                            str(row[2]).replace("%", "").replace(",", ".").strip()
                        )
                    except:
                        hoa_hong = 0.0
                danh_sach_dv[ten_dv] = {"gia": gia_goc, "hoa_hong": hoa_hong}
        return danh_sach_dv
    except:
        return {}


@st.cache_data(ttl=3600)
def get_nhan_vien_data():
    try:
        return get_google_sheet_workbook().worksheet("NhanVien").get_all_values()
    except:
        return []


@st.cache_data(ttl=60)
def get_khach_hang_data():
    try:
        rows = get_google_sheet_workbook().worksheet("KhachHang").get_all_values()
        return {
            str(r[0]).strip().replace(".0", ""): str(r[1]).strip()
            for r in rows[1:]
            if len(r) >= 2 and str(r[0]).strip()
        }
    except:
        return {}


@st.cache_data(ttl=120)
def get_bao_cao_va_bill_tam():
    try:
        sh = get_google_sheet_workbook()
        return (
            sh.worksheet("BaoCao").get_all_values(),
            sh.worksheet("BillTam").get_all_values(),
        )
    except:
        return [], []


@st.cache_data(ttl=60)
def get_lich_hen_data():
    try:
        return get_google_sheet_workbook().worksheet("LichHen").get_all_values()
    except:
        return []


# --- HÀM THAO TÁC DỮ LIỆU ---
def luu_bill_tam(gio_hang, nhan_vien, kh_sdt="", kh_ten="Khách lẻ"):
    try:
        sh = get_google_sheet_workbook()
        ws = sh.worksheet("BillTam")
        chi_tiet = " | ".join(
            [f"{item['dich_vu']} (x{item['so_luong']})" for item in gio_hang]
        )
        tong_tien = sum([item["thanh_tien"] for item in gio_hang])
        ws.append_row(
            [
                get_now_vn().strftime("%Y-%m-%d %H:%M:%S"),
                chi_tiet,
                tong_tien,
                nhan_vien,
                str(kh_sdt).strip(),
                str(kh_ten).strip(),
                "CHỜ XỬ LÝ",
            ]
        )
        get_bao_cao_va_bill_tam.clear()
        return True
    except:
        return False


def xoa_toan_bo_don_da_chot():
    try:
        ws = get_google_sheet_workbook().worksheet("HoaDon")
        all_data = ws.get_all_values()
        if len(all_data) > 1:
            ws.delete_rows(2, len(all_data))
            return True
        return False
    except:
        return False
