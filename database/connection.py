import pymysql

def connection_database():
    connect = pymysql.connect(
            host="localhost",
            user="root",
            password="",
            database="mager_db",
            cursorclass=pymysql.cursors.DictCursor
        )
    return connect