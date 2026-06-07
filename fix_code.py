# fix_code.py
# Ní chạy file này để thay thế THEME_COLORS bằng config.THEME_COLORS

file_name = 'app_cua_ni1.py' # Ní nhớ kiểm tra xem tên file chính xác là gì nhé

try:
    with open(file_name, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Thực hiện thay thế
    new_content = content.replace('THEME_COLORS', 'config.THEME_COLORS')
    
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print("Xong rồi ní ơi! Đã thay thế xong tất cả.")
except Exception as e:
    print(f"Có lỗi rồi ní ơi: {e}")
  
