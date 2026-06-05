def get_so_thu_tu_don(client, sheet_name):
    try:
        sheet = client.open("Bản sao của BC_DULIEU_DEMO_2026").worksheet(sheet_name)
        data = sheet.get_all_records()
        import pandas as pd

        df = pd.DataFrame(data)

        # In ra các cột để kiểm tra xem mình có đọc đúng tên không
        # st.write(df.columns) # Ní bỏ comment dòng này nếu vẫn lỗi để xem nó thấy cột gì

        so_don = df["Tên khách hàng"].nunique()
        return so_don
    except Exception as e:
        return f"Lỗi: {e}"  # Nó sẽ hiện lỗi cụ thể ra hóa đơn cho ní thấy
