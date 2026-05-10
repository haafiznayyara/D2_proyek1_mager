import pymysql

def connection_database():
    ports = [3306, 3307]

    for port in ports:
        try:
            connect = pymysql.connect(
                host="localhost",
                port=port,
                user="root",
                password="",
                database="mager_db",
                cursorclass=pymysql.cursors.DictCursor
            )

            # print(f"Berhasil konek ke MySQL port {port}")
            return connect

        except pymysql.MySQLError:
            print(f"Gagal konek ke port {port}")

    raise Exception("Tidak bisa terhubung ke MySQL di port 3306 maupun 3307")