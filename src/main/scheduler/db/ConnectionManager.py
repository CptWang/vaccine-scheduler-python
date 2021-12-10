import pymssql
import os


class ConnectionManager:

    def __init__(self):
        self.server_name = os.getenv("Server")
        self.db_name = os.getenv("DBName")
        self.user = os.getenv("UserID")
        self.password = os.getenv("Password")
        self.conn = None

    def create_connection(self):
        try:
            self.conn = pymssql.connect(server=self.server_name, user=self.user, password=self.password, database=self.db_name)
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL connection processing! ")
            sqlrc = str(db_err.args[0])
            print("Exception code: " + str(sqlrc))
        return self.conn

    def close_connection(self):
        try:
            self.conn.close()
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL connection processing! ")
            sqlrc = str(db_err.args[0])
            print("Exception code: " + str(sqlrc))

# cm = ConnectionManager()
# conn = cm.create_connection()
# cursor = conn.cursor()

# # example 1: getting all names and available doses in the vaccine table
# get_all_vaccines = "SELECT Name, Doses FROM vaccines"
# try:
#     cursor.execute(get_all_vaccines)
#     for row in cursor:
#         print("name:" + str(row['Name']) + ", available_doses: " + str(row['Doses']))
# except pymssql.Error:
#     print("Error occurred when getting details from Vaccines")

# # example 2: getting all records where the name matches “Pfizer”
# get_pfizer = "SELECT * FROM vaccine WHERE name = %s"
# try:
#     cursor.execute(get_pfizer)
#     for row in cursor:
#         print("name:" + str(row['Name']) + ", available_doses: " + str(row['Doses']))
# except pymssql.Error:
#     print("Error occurred when getting pfizer from Vaccines")
