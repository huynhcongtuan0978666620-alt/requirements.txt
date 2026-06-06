# utils.py
from datetime import datetime
import pytz
import config


def get_now_vn():
    return datetime.now(pytz.timezone("Asia/Ho_Chi_Minh"))
