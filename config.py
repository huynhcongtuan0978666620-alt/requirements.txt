def get_so_thu_tu_don(client, sheet_name):
    sheet = client.open("Bản sao của BC_DULIEU_DEMO_2026").worksheet(sheet_name)
    data = sheet.get_all_records()
    import pandas as pd

    df = pd.DataFrame(data)

    # BƯỚC QUAN TRỌNG: Loại bỏ khoảng trắng thừa ở tên tất cả các cột
    df.columns = df.columns.str.strip()

    # Giờ thì nó sẽ tìm đúng cột "Tên khách hàng" dù có hay không khoảng trắng
    so_don = df["Tên khách hàng"].nunique()
    return so_don
