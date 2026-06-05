def get_so_thu_tu_don(client, sheet_name):
    # 1. Đọc dữ liệu từ sheet
    sheet = client.open("Bản sao của BC_DULIEU_DEMO_2026").worksheet(BaoCao)
    data = sheet.get_all_records()
    
    # 2. Chuyển thành DataFrame cho dễ lọc
    import pandas as pd
    df = pd.DataFrame(data)
    
    # 3. Lọc khách hàng duy nhất (Giả sử cột chứa tên khách là 'TenKhach')
    # Ní nhớ đổi 'TenKhach' thành tên cột chính xác trong sheet của ní
    so_don = df['Tên khách hàng'].nunique()
    
    return so_don
    
