from wrapper_mariadb import MariaDB
from wrapper_rabbitmq import RabbitMQ
import requests
import json
import time

class Loader:

    TIME_SLEEPS = 5

    def __init__(self, 
                url_mariadb,
                pass_mariadb,
                user_mariadb,
                db_name,
                rabbit_pass,
                rabbit_host,
                rabbit_user,
                rabbit_queue_out,
                pod_name
                ) -> None:
        
        self.mariadb_instance = MariaDB(url_mariadb, pass_mariadb, user_mariadb, db_name)
        self.rabbitmq_instance = RabbitMQ(rabbit_pass, rabbit_host, rabbit_user)
        self.rabbit_queue_out = rabbit_queue_out
        self.pod_name = pod_name

    def load(self):
        channel = self.rabbitmq_instance.getConnectionRabbitMQ()
        while True:
            cursor = self.mariadb_instance.getConnectionMariaDB()
            # get 1 pending job
            cursor.execute('SELECT id, created, status, end, loader, grp_size FROM jobs WHERE status = "pending"')
            pending_job = cursor.fetchone() 
            if pending_job is not None:                
                print(pending_job)     
                # agregar la información del pod que lo está procesando
                cursor.execute('UPDATE jobs SET status="in-progress", loader=? WHERE id=?',
                              (self.pod_name, pending_job['id'])) #todo: que el nombre del loader sea el del pod real
                self.mariadb_instance.connection.commit()
                # llamar al endpoint y obtener "messages"
                r = requests.get('https://api.biorxiv.org/covid19/0')
                messages = r.json()['messages'][0]
                # calcular cantidad de groups
                grp_size = pending_job['grp_size']
                group_quantity = messages['total'] / grp_size
                # crear groups 
                id_job = pending_job['id']
                grp_number = 0
                offset = 0
                while grp_number < group_quantity:
                    cursor.execute('INSERT INTO groups (id_job, grp_number, `offset`) VALUES (?,?,?)', 
                                  (id_job, grp_number, offset,))
                    self.mariadb_instance.connection.commit()
                    # publicar en rabbitmq
                    body = json.dumps({"id_job": id_job, "grp_number": grp_number})
                    channel.queue_declare(queue=self.rabbit_queue_out)
                    channel.basic_publish(exchange='', routing_key=self.rabbit_queue_out, body=body)
                    offset += grp_size
                    grp_number += 1
                    time.sleep(50)
            else:
                print("No pending jobs...")
            self.mariadb_instance.connection.close()
            time.sleep(self.TIME_SLEEPS)