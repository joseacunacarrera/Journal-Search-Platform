from wraper_mariadb import MariaDB
import datetime

class Loader:

    def __init__(self, 
                url_mariadb,
                pass_mariadb,
                user_mariadb,
                db_name) -> None:
        
        self.mariadb_instance = MariaDB(url_mariadb, pass_mariadb, user_mariadb, db_name)

    def load(self):

        cursor = self.mariadb_instance.getConnectionMariaDB()
        # get 1 pending job
        cursor.execute('SELECT id, created, status, end, loader, grp_size FROM jobs WHERE status = "pending"')
        pending_job = cursor.fetchone() 
        print(pending_job)     
        # agregar la información del pod que lo está procesando
        cursor.execute('UPDATE jobs SET status="in-progress", loader=? WHERE id=?',("databases-mariadb-0", pending_job['id'])) #todo: que el nombre del loader sea el del pod real
        self.mariadb_instance.connection.commit()
        # llamar al endpoint y obtener "messages"
        
        # calcular cantidad de groups
        # crear groups 
        # publicar en rabbitmq

