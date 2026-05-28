import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import pytz
import time
import re
import random
import math
import smtplib
import requests
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# =====================================================================
# 🌟 MENU ĐIỀU CHỈNH MÀU SẮC (DESIGN SYSTEM) - V14
# =====================================================================
THEME_COLORS = {
    "bg_app": "#EEF4F8",            
    "bg_card": "#ffffff",           
    "bg_box_chung": "#f8f9fa",      
    "bg_vip_box": "#eaf2e6",        
    "bg_shake_box": "#fff1f0",      
    "bg_badge_hang": "#fffbfa",     
    "primary": "#6FA8DC",           
    "accent_vip": "#13c2c2",        
    "accent_danger": "#cf1322",     
    "accent_zalo": "#0068ff",       
    "accent_chiet_khau": "#d93025", 
    "text_main": "#111111",         
    "text_secondary": "#555555",    
    "text_muted": "#888888",        
    "text_title": "#2c3e50",        
    "text_badge": "#d4380d",        
    "border_light": "#eaeaea",      
    "border_input": "#cccccc",      
    "border_badge": "#ffe1df",      
    "border_vip": "#87e8de",        
    "shadow_light": "rgba(0,0,0,0.05)",  
    "shadow_heavy": "rgba(0,0,0,0.08)",  
    "shadow_toast": "rgba(0,0,0,0.1)",   
}

# =====================================================================
# 1. CẤU HÌNH GIAO DIỆN V14
# =====================================================================
st.set_page_config(
    page_title="LKTV CHANNEL V14", 
    layout="centered", 
    page_icon="💎",
    initial_sidebar_state="collapsed"
)

def get_now_vn():
    vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    return datetime.now(vn_tz)

def inject_advanced_ui_js():
    js_code = f"""
    <script>
    const parentDoc = window.parent.document;
    function showPremiumToast(text) {{
        let t = parentDoc.createElement('div');
        t.innerText = text;
        t.style.cssText = "position:fixed; top:15%; left:50%; transform:translate(-50%, -50%); background: {THEME_COLORS['bg_card']}; color:{THEME_COLORS['text_main']}; padding:15px 30px; border-radius:12px; font-weight:bold; box-shadow: 0 10px 30px {THEME_COLORS['shadow_toast']}; border-left: 5px solid {THEME_COLORS['primary']}; z-index:9999999; font-size:15px; transition: opacity 0.5s; text-align:center;";
        parentDoc.body.appendChild(t);
        setTimeout(() => {{ t.style.opacity = '0'; setTimeout(()=>t.remove(), 500); }}, 2500);
    }}
    if(!parentDoc.body.hasAttribute('data-fw-v14')) {{
        parentDoc.body.setAttribute('data-fw-v14', '1');
        let clicks = 0;
        let timer = null;
        parentDoc.addEventListener('click', (e) => {{
            clicks++;
            clearTimeout(timer);
            timer = setTimeout(() => {{ clicks = 0; }}, 1000); 
            if(clicks >= 3) {{
                clicks = 0;
                showPremiumToast('🎉 Chào mừng đến với NHÀ CỦA HIỀN 🎉');
            }}
        }});
    }}
    </script>
    """
    st.components.v1.html(js_code, height=0, width=0)

def apply_v14_theme():
    p = THEME_COLORS['primary']
    bg = THEME_COLORS['bg_app']
    card = THEME_COLORS['bg_card']
    shadow = THEME_COLORS['shadow_light']
    txt_main = THEME_COLORS['text_main']
    txt_sub = THEME_COLORS['text_secondary']
    txt_muted = THEME_COLORS['text_muted']
    txt_title = THEME_COLORS['text_title']
    b_light = THEME_COLORS['border_light']
    b_input = THEME_COLORS['border_input']

    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
        html, body, .stApp {{ font-family: 'Inter', sans-serif !important; background-color: {bg} !important; padding-top: 0px !important; }}
        header, footer, [data-testid='stToolbar'], [data-testid='stDecoration'] {{ display: none !important; }}
        [data-testid="stVerticalBlock"] {{ gap: 5px !important; }}
        [data-testid="stTabs"] [role="tablist"] {{
            background: {card}; border-radius: 12px; padding: 5px; box-shadow: 0 4px 6px {shadow}; margin-bottom: 5px !important;
        }}
        button[data-baseweb="tab"] {{ background-color: transparent !important; }}
        button[data-baseweb="tab"] p {{ color: {txt_muted} !important; font-weight: 600 !important; font-size: 14px; }}
        button[data-baseweb="tab"][aria-selected="true"] {{ background-color: {p} !important; border-radius: 8px; }}
        button[data-baseweb="tab"][aria-selected="true"] p {{ color: {txt_main} !important; }}
        [data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: {card} !important; border: none !important; border-radius: 15px !important;
            border-left: 5px solid {p} !important; box-shadow: 2px 2px 10px {shadow} !important;
            padding: 15px !important; margin-bottom: 8px !important;
        }}
        div[data-testid="stButton"] button {{ border-radius: 10px !important; font-weight: 600 !important; border: 1px solid {b_light}; background: {card}; }}
        div[data-testid="stButton"] button[kind="primary"] {{ background-color: {p} !important; color: {txt_main} !important; border: none !important; }}
        .stTextInput>div>div>input, .stNumberInput>div>div>input, .stDateInput>div>div>input, .stTimeInput>div>div>input {{ border-radius: 8px !important; border: 1px solid {b_input}; }}
        .the-quan-ly-flat {{ color: {txt_title}; font-weight: 800; font-size: 18px; margin-bottom: 10px; border-bottom: 2px solid {p}; padding-bottom: 5px; text-transform: uppercase; }}
        .hoa-don-khung {{ background-color: {card} !important; color: {txt_main} !important; padding: 20px !important; border-radius: 15px !important; border-top: 8px solid {p} !important; box-shadow: 0 4px 12px {THEME_COLORS['shadow_heavy']}; margin-top: 5px; }}
    </style>
    """, unsafe_allow_html=True)

# =====================================================================
# 2. CƠ CHẾ KẾT NỐI & DỮ LIỆU CHÍNH
# =====================================================================
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
            "token_uri": secrets.get("token_uri", "https://oauth2.googleapis.com/token"),
        }

        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        url = secrets.get("spreadsheet", "")
        if not url and "spreadsheet" in st.secrets:
            url = st.secrets["spreadsheet"]
        return client.open_by_key(url) if len(url) < 50 else client.open_by_url(url)
    except Exception as e:
        st.error(f"Lỗi khởi tạo kết nối Sheets: {e}")
        st.stop()

@st.cache_data(ttl=3600)
def get_settings():
    try:
        sh = get_google_sheet_workbook()
        rows = sh.worksheet("ThietLap").get_all_values()
        return {str(row[0]).strip(): str(row[1]).strip() for row in rows if len(row) > 1}
    except Exception: return {"TenTiem": "SALON KIM HIỀN", "Diachi": "131, TRẦN BÌNH TRỌNG, LONG XUYÊN", "SDT": "0947.58.1516"}

@st.cache_data(ttl=3600)
def get_service_data():
    try:
        sh = get_google_sheet_workbook()
        rows = sh.worksheet("DanhMuc").get_all_values()
        danh_sach_dv = {}
        for row in rows[1:]:
            if len(row) >= 2:
                ten_dv = str(row[0]).strip()
                if not ten_dv: continue
                try: gia_goc = float(str(row[1]).replace('.', '').replace(',', '').strip())
                except: gia_goc = 0.0
                hoa_hong = 0.0
                if len(row) >= 3 and row[2]:
                    try: hoa_hong = float(str(row[2]).replace('%', '').replace(',', '.').strip())
                    except: hoa_hong = 0.0
                danh_sach_dv[ten_dv] = {"gia": gia_goc, "hoa_hong": hoa_hong}
        return danh_sach_dv
    except Exception: return {}

@st.cache_data(ttl=3600)
def get_nhan_vien_data():
    try: return get_google_sheet_workbook().worksheet("NhanVien").get_all_values()
    except Exception: return []

@st.cache_data(ttl=300)
def get_bao_cao_va_bill_tam():
    try:
        sh = get_google_sheet_workbook()
        return sh.worksheet("BaoCao").get_all_values(), sh.worksheet("BillTam").get_all_values()
    except Exception: return [], []

@st.cache_data
def convert_df_to_csv(df):
    # Xuất định dạng utf-8-sig để đọc tiếng Việt chuẩn trên Excel 2010
    return df.to_csv(index=False).encode('utf-8-sig')

def luu_bill_tam(gio_hang, nhan_vien, kh_sdt="", kh_ten="Khách lẻ"):
    try:
        sh = get_google_sheet_workbook()
        ws = sh.worksheet("BillTam")
        chi_tiet = " | ".join([f"{item['dich_vu']} (x{item['so_luong']})" for item in gio_hang])
        tong_tien = sum([item['thanh_tien'] for item in gio_hang])
        ws.append_row([get_now_vn().strftime("%Y-%m-%d %H:%M:%S"), chi_tiet, tong_tien, nhan_vien, str(kh_sdt).strip(), str(kh_ten).strip(), "CHỜ XỬ LÝ"])
        get_bao_cao_va_bill_tam.clear()
        return True
    except Exception: return False

# =====================================================================
# 3. CƠ CHẾ AUTO-SAVE NGẦM (BACKGROUND THREADING)
# =====================================================================
def background_save_draft(gio_hang_copy, nhan_vien, kh_sdt, kh_ten):
    try:
        sh = get_google_sheet_workbook()
        ws = sh.worksheet("BillTam")
        records = ws.get_all_values()
        draft_idx = -1
        for i, r in enumerate(records):
            if len(r) >= 7 and str(r[3]).strip() == nhan_vien and str(r[6]).strip() == "ĐANG SOẠN":
                draft_idx = i + 1 
                break
                
        chi_tiet = " | ".join([f"{item['dich_vu']} (x{item['so_luong']})" for item in gio_hang_copy])
        tong_tien = sum([item['thanh_tien'] for item in gio_hang_copy])
        
        if not gio_hang_copy and draft_idx != -1:
            ws.delete_rows(draft_idx)
        elif gio_hang_copy and draft_idx != -1:
            ws.update(f"A{draft_idx}:G{draft_idx}", [[get_now_vn().strftime("%Y-%m-%d %H:%M:%S"), chi_tiet, tong_tien, nhan_vien, kh_sdt, kh_ten, "ĐANG SOẠN"]])
        elif gio_hang_copy and draft_idx == -1:
            ws.append_row([get_now_vn().strftime("%Y-%m-%d %H:%M:%S"), chi_tiet, tong_tien, nhan_vien, kh_sdt, kh_ten, "ĐANG SOẠN"])
        get_bao_cao_va_bill_tam.clear()
    except Exception: pass

def trigger_auto_save():
    t = threading.Thread(target=background_save_draft, args=(
        list(st.session_state.gio_hang), 
        st.session_state.full_name, 
        st.session_state.kh_sdt_val, 
        st.session_state.kh_ten_val
    ))
    t.start()

# =====================================================================
# 4. LUỒNG ĐIỀU HƯỚNG VÀ XỬ LÝ CHÍNH
# =====================================================================
def main():
    init_states = {
        "last_submit": None, "submit_count": 0, "submitting": False, 
        "logged_in": False, "role": None, "full_name": None, "gio_hang": [], 
        "bill_vua_in": None, "kh_sdt_val": "", "kh_ten_val": "Khách lẻ", 
        "start_time": get_now_vn(), "reset_counter": 0, "tho_chot_val": "",
        "hang_hien_tai": "", "tong_chi_tieu_val": 0.0, "da_load_nhap": False
    }
    for key, val in init_states.items():
        if key not in st.session_state: st.session_state[key] = val

    apply_v14_theme()
    inject_advanced_ui_js()
    settings = get_settings()

    # --- ĐĂNG NHẬP ---
    if not st.session_state["logged_in"]:
        saved_u = st.query_params.get("saved_u", "")
        saved_p = st.query_params.get("saved_p", "")
        with st.container(border=True):
            st.markdown(f"<h2 style='text-align:center; color:{THEME_COLORS['text_title']}; font-weight:800;'>ECO TIME V14</h2>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center; color:{THEME_COLORS['text_muted']}; margin-top:-10px; margin-bottom:20px;'>ĐĂNG NHẬP HỆ THỐNG</p>", unsafe_allow_html=True)
            u = st.text_input("Tài khoản (Số điện thoại)", value=saved_u)
            p = st.text_input("Mật khẩu", type="password", value=saved_p)
            remember_me = st.checkbox("Ghi nhớ mật khẩu", value=bool(saved_u))
            
            if st.button("Xác nhận Đăng Nhập", use_container_width=True, type="primary"):
                if u == "admin" and p == "2026":
                    if remember_me: st.query_params.update({"saved_u": u, "saved_p": p})
                    else: st.query_params.clear()
                    st.session_state.update({"logged_in": True, "role": "Admin", "full_name": "Quản lý", "tho_chot_val": "Quản lý"})
                    st.rerun()
                else:
                    raw_data = get_nhan_vien_data()
                    if len(raw_data) > 0:
                        headers = [str(h).strip().lower() for h in raw_data[0]]
                        col_sdt_idx = next((i for i, h in enumerate(headers) if 'điện thoại' in h or 'sđt' in h or 'tai khoan' in h), -1)
                        col_mk_idx = next((i for i, h in enumerate(headers) if 'mật khẩu' in h or 'mat khau' in h or 'code' in h), -1)
                        col_ten_idx = next((i for i, h in enumerate(headers) if 'tên' in h or 'nhân viên' in h), -1)
                        
                        found_row = next((r for r in raw_data[1:] if len(r) > max(col_sdt_idx, col_mk_idx) and str(r[col_sdt_idx]).strip().lstrip('0') == u.strip().lstrip('0') and str(r[col_mk_idx]).strip() == p.strip() and u.strip()), None)
                                    
                        if found_row:
                            if remember_me: st.query_params.update({"saved_u": u, "saved_p": p})
                            else: st.query_params.clear()
                            ten_that = str(found_row[col_ten_idx]).strip() if col_ten_idx != -1 and col_ten_idx < len(found_row) else "Nhân viên"
                            st.session_state.update({"logged_in": True, "role": "NhanVien", "full_name": ten_that, "tho_chot_val": ten_that})
                            st.rerun()
                        else: st.error("Thông tin số điện thoại hoặc mật khẩu không chính xác.")
                    else: st.error("Hệ thống dữ liệu chưa sẵn sàng.")

    # --- KHU VỰC LÀM VIỆC CHÍNH ---
    else:
        if not st.session_state.da_load_nhap:
            st.session_state.da_load_nhap = True
            _, tam_records = get_bao_cao_va_bill_tam()
            services = get_service_data()
            for r in tam_records:
                if len(r) >= 7 and str(r[3]).strip() == st.session_state.full_name and str(r[6]).strip() == "ĐANG SOẠN":
                    st.session_state.kh_sdt_val = str(r[4]).strip()
                    st.session_state.kh_ten_val = str(r[5]).strip()
                    chi_tiet_dv = str(r[1]).strip()
                    new_gio = []
                    for item in chi_tiet_dv.split(" | "):
                        if item.strip():
                            match = re.match(r"(.+)\s*\(x([\d\.]+)\)", item.strip())
                            if match:
                                t_dv, s_l = match.group(1).strip(), float(match.group(2))
                                info = services.get(t_dv, {"gia": 0.0, "hoa_hong": 0.0})
                                new_gio.append({"dich_vu": t_dv, "so_luong": s_l, "don_gia": info.get("gia", 0.0), "thanh_tien": info.get("gia", 0.0) * s_l, "phan_tram_hh": info.get("hoa_hong", 0.0)})
                    if new_gio:
                        st.session_state.gio_hang = new_gio
                        st.toast("🔄 Đã tự động khôi phục giỏ hàng làm dở trước đó!")
                    break

        tabs = st.tabs(["🏠 Tổng quan", "📄 Lên hóa đơn", "📅 Lịch hẹn", "📊 Báo cáo", "⚙️ Thêm"], key="main_tabs_v14")
        services = get_service_data()
        dv_list = list(services.keys())
        
        raw_nv = get_nhan_vien_data()
        ds_tho = [str(r[next((i for i, h in enumerate([str(h).strip().lower() for h in raw_nv[0]]) if 'tên' in h or 'nhân viên' in h), -1)]).strip() for r in raw_nv[1:] if len(r) > next((i for i, h in enumerate([str(h).strip().lower() for h in raw_nv[0]]) if 'tên' in h or 'nhân viên' in h), -1)] if len(raw_nv) > 1 else []

        # ==================== TAB 1: TỔNG QUAN ====================
        with tabs[0]:
            with st.container(border=True):
                st.markdown(f"""
                    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center;">
                        <div style="font-size: 22px; font-weight: 900; color: {THEME_COLORS['text_main']}; text-transform: uppercase; letter-spacing: 1px;">{settings.get('TenTiem', 'SALON KIM HIỀN')}</div>
                        <div style="font-size: 13px; color: {THEME_COLORS['text_muted']}; margin-top: 5px; text-align: center;">
                            <div>{settings.get('Diachi', '131, TRẦN BÌNH TRỌNG, LONG XUYÊN')}</div>
                            <div style="margin-top: 3px;">Hotline: {settings.get('SDT', '0947.58.1516')}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            with st.container(border=True):
                st.markdown(f"**Chào mừng, {st.session_state.full_name}!**")
                st.markdown(f"<span style='color:{THEME_COLORS['text_muted']}; font-size:13px;'>Hôm nay là: {get_now_vn().strftime('%d/%m/%Y')}</span>", unsafe_allow_html=True)

            if st.session_state.get("bill_vua_in"):
                with st.container(border=True):
                    st.markdown('<div class="the-quan-ly-flat">🧾 HOÁ ĐƠN VỪA KHỞI TẠO</div>', unsafe_allow_html=True)
                    st.markdown(st.session_state.bill_vua_in, unsafe_allow_html=True)
                    if st.button("❌ ẨN BILL NÀY", use_container_width=True, type="primary"):
                        st.session_state.bill_vua_in = None
                        st.rerun()

        # ==================== TAB 2: LÊN HÓA ĐƠN ====================
        with tabs[1]:
            with st.container(border=True):
                st.markdown('<div class="the-quan-ly-flat">THÔNG TIN KHÁCH HÀNG</div>', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1: 
                    kh_sdt = st.text_input("Số điện thoại khách", value=st.session_state.kh_sdt_val)
                    if kh_sdt != st.session_state.kh_sdt_val:
                        st.session_state.kh_sdt_val = kh_sdt
                        if kh_sdt.strip(): trigger_auto_save()
                        st.rerun() 
                with c2: 
                    kh_ten = st.text_input("Tên khách hàng", value=st.session_state.kh_ten_val)
                    if kh_ten != st.session_state.kh_ten_val: 
                        st.session_state.kh_ten_val = kh_ten
                        trigger_auto_save()
                        st.rerun()

            with st.container(border=True):
                st.markdown('<div class="the-quan-ly-flat">DANH SÁCH DỊCH VỤ</div>', unsafe_allow_html=True)
                dv_chon = st.multiselect("Chạm chọn dịch vụ...", options=dv_list if dv_list else ["Đang tải..."], key=f"dv_{st.session_state.reset_counter}")
                if st.button("➕ THÊM VÀO GIỎ HÀNG", type="primary", use_container_width=True):
                    if dv_chon:
                        for dv in dv_chon:
                            info_dv = services.get(dv, {"gia": 0.0, "hoa_hong": 0.0})
                            existing = next((item for item in st.session_state.gio_hang if item["dich_vu"] == dv), None)
                            if existing:
                                existing["so_luong"] += 1.0
                                existing["thanh_tien"] = existing["so_luong"] * existing["don_gia"]
                            else:
                                st.session_state.gio_hang.append({"dich_vu": dv, "so_luong": 1.0, "don_gia": info_dv["gia"], "thanh_tien": info_dv["gia"], "phan_tram_hh": info_dv["hoa_hong"]})
                        st.session_state.reset_counter += 1  
                        trigger_auto_save()
                        st.toast("✅ Đã thêm dịch vụ! Đang tự động sao lưu...")
                        time.sleep(0.3)
                        st.rerun()

            t_bill = 0.0
            if st.session_state.gio_hang:
                with st.container(border=True):
                    st.markdown(f'<div class="the-quan-ly-flat">🛒 GIỎ HÀNG ({len(st.session_state.gio_hang)} món)</div>', unsafe_allow_html=True)
                    for idx, item in enumerate(st.session_state.gio_hang):
                        c_sl, c_tt, c_del = st.columns([5, 3, 2])
                        with c_sl:
                            new_sl = st.number_input(f"{item['dich_vu']}:", min_value=0.5, value=float(item['so_luong']), step=0.5, key=f"cart_sl_{idx}")
                            if new_sl != item['so_luong']:
                                item['so_luong'] = new_sl
                                item['thanh_tien'] = new_sl * item['don_gia']
                                trigger_auto_save()
                                st.rerun()
                        with c_tt:
                            st.markdown(f"<div style='margin-top: 30px; font-weight:800; color:{THEME_COLORS['text_main']};'>{item['thanh_tien']:,.0f}đ</div>", unsafe_allow_html=True)
                        with c_del:
                            st.markdown(f"<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
                            if st.button("🗑️", key=f"del_{idx}", use_container_width=True):
                                st.session_state.gio_hang.pop(idx)
                                trigger_auto_save()
                                st.rerun()
                        t_bill += item['thanh_tien']

                    if st.button("💾 LƯU ĐƠN VÀO BILL CHỜ (ĐẨY XUỐNG BẾP/THỢ)", use_container_width=True):
                        if luu_bill_tam(st.session_state.gio_hang, st.session_state.full_name, st.session_state.kh_sdt_val, st.session_state.kh_ten_val):
                            st.session_state.update({"gio_hang": [], "kh_sdt_val": "", "kh_ten_val": "Khách lẻ"})
                            trigger_auto_save()
                            st.toast("✅ Đã đẩy đơn vào danh sách chờ!")
                            time.sleep(1)
                            st.rerun()

            if t_bill > 0:
                with st.container(border=True):
                    st.markdown('<div class="the-quan-ly-flat">THU NGÂN & CHIẾT KHẤU</div>', unsafe_allow_html=True)
                    chot_tho = st.selectbox("Thợ thực hiện:", options=ds_tho if ds_tho else [st.session_state.full_name])
                    tien_giam = st.number_input("Chiết khấu (VND)", value=0.0, step=1000.0)
                    t_khach_tra = max(0.0, t_bill - tien_giam)
                    kh_dua = st.number_input("Số tiền mặt khách trả", value=float(t_khach_tra))
                    
                    if st.button("🚀 XUẤT HÓA ĐƠN", use_container_width=True, type="primary"):
                        try:
                            ws = get_google_sheet_workbook().worksheet("BaoCao")
                            ma_hd = f"HD{get_now_vn().strftime('%y%m%d%H%M')}"
                            rows_to_append = []
                            for item in st.session_state.gio_hang:
                                rows_to_append.append([
                                    get_now_vn().strftime("%d/%m/%Y"), st.session_state.full_name, 
                                    st.session_state.kh_ten_val, st.session_state.kh_sdt_val,
                                    item['dich_vu'], item['so_luong'], item['don_gia'], item['thanh_tien'],
                                    get_now_vn().strftime("%H:%M:%S"), f"CK: {tien_giam:,.0f}", 
                                    item['thanh_tien'] * (item['phan_tram_hh'] / 100.0), ma_hd, kh_dua, kh_dua - t_khach_tra, "0 phút", chot_tho
                                ])
                            ws.append_rows(rows_to_append)
                            st.session_state.update({"gio_hang": [], "kh_sdt_val": "", "kh_ten_val": "Khách lẻ"})
                            trigger_auto_save()
                            st.toast("✅ Đã xuất hóa đơn!")
                            time.sleep(1)
                            st.rerun()
                        except Exception as e: st.error(f"Lỗi: {e}")

        # ==================== TAB 3: LỊCH HẸN (HOÀN THIỆN) ====================
        with tabs[2]:
            with st.container(border=True):
                st.markdown('<div class="the-quan-ly-flat">📅 TẠO LỊCH HẸN MỚI</div>', unsafe_allow_html=True)
                
                c_hen1, c_hen2 = st.columns(2)
                with c_hen1:
                    hen_ten = st.text_input("Tên khách hàng (Hẹn)")
                    hen_ngay = st.date_input("Ngày hẹn", value=get_now_vn().date())
                with c_hen2:
                    hen_sdt = st.text_input("Số điện thoại (Hẹn)")
                    hen_gio = st.time_input("Giờ hẹn", value=get_now_vn().time())
                
                hen_dv = st.multiselect("Dịch vụ quan tâm", options=dv_list if dv_list else ["Đang tải..."])
                hen_tho = st.selectbox("Thợ yêu cầu (nếu có)", options=["Không yêu cầu"] + ds_tho if ds_tho else ["Không yêu cầu", st.session_state.full_name])
                hen_ghi_chu = st.text_area("Ghi chú thêm (Tình trạng xe/yêu cầu riêng)")

                if st.button("💾 LƯU LỊCH HẸN", use_container_width=True, type="primary"):
                    if hen_ten and hen_sdt:
                        try:
                            # Yêu cầu ní tạo sẵn Sheet có tên "LichHen" trên Google Sheets nhé
                            ws_hen = get_google_sheet_workbook().worksheet("LichHen")
                            ws_hen.append_row([
                                get_now_vn().strftime("%Y-%m-%d %H:%M:%S"),
                                str(hen_ngay),
                                str(hen_gio),
                                hen_ten,
                                hen_sdt,
                                ", ".join(hen_dv),
                                hen_tho,
                                hen_ghi_chu,
                                "CHỜ XÁC NHẬN"
                            ])
                            st.toast("✅ Đã lưu lịch hẹn thành công!")
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Lỗi khi lưu lịch hẹn. Đảm bảo ní đã tạo Sheet 'LichHen' nhé. Chi tiết: {e}")
                    else:
                        st.warning("Vui lòng nhập Tên và Số điện thoại khách hàng.")

        # ==================== TAB 4: BÁO CÁO (HOÀN THIỆN) ====================
        with tabs[3]:
            if st.session_state["role"] == "Admin":
                with st.container(border=True):
                    st.markdown('<div class="the-quan-ly-flat">📈 BÁO CÁO DOANH THU TỔNG QUAN</div>', unsafe_allow_html=True)
                    
                    try:
                        data_bc, _ = get_bao_cao_va_bill_tam()
                        if len(data_bc) > 1:
                            df_bc = pd.DataFrame(data_bc[1:], columns=data_bc[0])
                            
                            c_btn1, c_btn2 = st.columns(2)
                            with c_btn1:
                                if st.button("⏰ Cập nhật dữ liệu", use_container_width=True):
                                    get_bao_cao_va_bill_tam.clear()
                                    st.rerun()
                            with c_btn2:
                                # Chuyển CSV sang utf-8-sig để Excel bản cũ hiển thị Tiếng Việt không lỗi
                                csv_data = convert_df_to_csv(df_bc)
                                st.download_button(
                                    label="📥 Xuất File Excel (CSV)", 
                                    data=csv_data, 
                                    file_name=f"DoanhThu_{get_now_vn().strftime('%Y%m%d')}.csv", 
                                    mime="text/csv", 
                                    use_container_width=True,
                                    type="primary"
                                )
                            
                            st.markdown(f"**Tổng số giao dịch đã ghi nhận:** {len(df_bc)}")
                            st.dataframe(df_bc, use_container_width=True)
                        else:
                            st.info("Chưa có dữ liệu báo cáo.")
                            if st.button("⏰ Cập nhật dữ liệu", use_container_width=True):
                                get_bao_cao_va_bill_tam.clear()
                                st.rerun()
                                
                    except Exception as e: 
                        st.error(f"Lỗi tải dữ liệu báo cáo: {e}")
            else:
                st.warning("🔒 Chức năng này chỉ dành cho Quản lý.")

        # ==================== TAB 5: QUẢN TRỊ & HỆ THỐNG ====================
        with tabs[4]:
            if st.session_state["role"] == "Admin":
                with st.container(border=True):
                    st.markdown('<div class="the-quan-ly-flat">QUẢN LÝ BILL CHỜ</div>', unsafe_allow_html=True)
                    try:
                        _, data_tam = get_bao_cao_va_bill_tam()
                        rows_tam = [r for r in data_tam[1:] if len(r) >= 7 and r[6].strip() == "CHỜ XỬ LÝ"]
                        if rows_tam:
                            for i, row in enumerate(rows_tam):
                                st.write(f"📝 {row[5]} ({row[4]}) - {row[2]}đ")
                        else: st.info("Không có đơn chờ duyệt.")
                    except Exception as e: st.error(f"Lỗi: {e}")

                with st.container(border=True):
                    st.markdown('<div class="the-quan-ly-flat">🧪 QUẢN LÝ PHÒNG LAB</div>', unsafe_allow_html=True)
                    c_lab1, c_lab2 = st.columns(2)
                    with c_lab1:
                        ma_ct = st.selectbox("Mã công thức", ["DBX 1.3", "DBX 1.2", "Formula Custom"])
                    with c_lab2:
                        the_tich = st.number_input("Thể tích mẻ (Lít)", min_value=3.0, value=3.0, step=1.0)
                        
                    if st.button("⚗️ TÍNH TOÁN CÔNG THỨC & QUY TRÌNH", type="primary", use_container_width=True):
                        st.markdown(f"<div style='margin: 15px 0; border-bottom: 2px dashed {THEME_COLORS['primary']};'></div>", unsafe_allow_html=True)
                        st.markdown(f"<h4 style='color:{THEME_COLORS['text_title']};'>1. Công thức hoàn chỉnh (Mẻ {the_tich} Lít)</h4>", unsafe_allow_html=True)
                        st.dataframe(pd.DataFrame({"Thành phần": ["Dung môi gốc", "Chất HĐBM", "Phụ gia làm sạch", "Chất bảo quản/Hương liệu"], "Tỷ lệ (%)": [70.0, 15.0, 10.0, 5.0], "Khối lượng/Thể tích": [f"{the_tich * 0.7:.2f} L", f"{the_tich * 0.15:.2f} L", f"{the_tich * 0.10:.2f} L", f"{the_tich * 0.05:.2f} L"]}), use_container_width=True, hide_index=True)
                        st.markdown(f"<h4 style='color:{THEME_COLORS['text_title']}; margin-top: 15px;'>2. Quy trình pha chế chuẩn</h4>", unsafe_allow_html=True)
                        st.info("💡 Hệ thống vận hành: Dàn 3 máy khuấy song song.")
                        st.markdown(f"""* **Bước 1:** Bơm `{the_tich * 0.7:.2f} L` dung môi gốc vào bồn. Kích hoạt máy khuấy số 1 (chạy chậm).\n* **Bước 2:** Nạp từ từ Chất HĐBM. Bật tiếp máy khuấy số 2 để tạo dòng xoáy trợ lực.\n* **Bước 3:** Thêm Phụ gia làm sạch. Đóng điện cho **toàn bộ 3 máy khuấy** chạy hết công suất để nhũ hóa sâu.\n* **Bước 4:** Thêm Hương liệu ở phút cuối, giảm tốc độ và tắt máy.""")
                        st.markdown(f"<h4 style='color:{THEME_COLORS['text_title']}; margin-top: 15px;'>3. Đánh giá: 9.5/10 điểm</h4>", unsafe_allow_html=True)
                        st.success("Hệ form mới bám rất sát thể tích lớn. Lực đánh bù trừ qua lại của 3 trục khuấy giúp dung dịch không bị tách lớp, độ đồng nhất cực kỳ cao.")
                        st.markdown(f"<h4 style='color:{THEME_COLORS['text_title']}; margin-top: 15px;'>4. Hướng dẫn thao tác / Hướng dẫn sử dụng</h4>", unsafe_allow_html=True)
                        st.warning("- **An toàn điện:** Chú ý quan sát nguồn cấp, tuyệt đối không để sụt áp khi ép cả 3 tải chạy max tốc cùng lúc.\n- **Vệ sinh:** Xả bồn và rửa cánh khuấy ngay sau khi chiết rót xong.\n- **Bảo quản:** Sang chiết dung dịch vào can tối màu, để nơi thoáng mát.")

                with st.container(border=True):
                    st.markdown('<div class="the-quan-ly-flat">HỆ THỐNG</div>', unsafe_allow_html=True)
                    if st.button("♻️ LÀM MỚI BỘ NHỚ", use_container_width=True, type="primary"):
                        st.cache_data.clear()
                        st.cache_resource.clear() 
                        st.rerun()
                    if st.button("🚪 Đăng xuất Admin", use_container_width=True):
                        st.session_state.clear()
                        st.rerun()
            else:
                with st.container(border=True):
                    st.markdown('<div class="the-quan-ly-flat">HỆ THỐNG</div>', unsafe_allow_html=True)
                    if st.button("🚪 Đăng xuất", use_container_width=True, type="primary"):
                        st.session_state.clear()
                        st.rerun()

if __name__ == "__main__":
    main()
