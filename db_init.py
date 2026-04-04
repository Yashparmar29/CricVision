import pymysql

try:
    connection = pymysql.connect(host='localhost', user='root', password='')
    with connection.cursor() as cursor:
        cursor.execute("CREATE DATABASE IF NOT EXISTS cricvision_db;")
    connection.commit()
    print("Database cricvision_db created or already exists.")
except Exception as e:
    print(f"Error creating database: {e}")
finally:
    if 'connection' in locals() and connection.open:
        connection.close()
