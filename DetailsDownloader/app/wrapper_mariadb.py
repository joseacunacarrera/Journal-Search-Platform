import mariadb

class MariaDB:
    
    def __init__(self, 
                url_mariadb,
                pass_mariadb,
                user_mariadb,
                db_name) -> None:
        self.connection = None
        self.url_mariadb = url_mariadb
        self.pass_mariadb = pass_mariadb
        self.user_mariadb = user_mariadb
        self.db_name = db_name

    def getConnectionMariaDB(self):
        try:
            self.connection = mariadb.connect(
                host = self.url_mariadb,
                user = self.user_mariadb,
                password = self.pass_mariadb,
                port = 3306,
                database = self.db_name,
            )
            cursor = self.connection.cursor(dictionary=True)
            return cursor
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")