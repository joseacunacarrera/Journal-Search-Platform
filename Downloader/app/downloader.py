from wrapper_mariadb import MariaDB
from wrapper_rabbitmq import RabbitMQ
from elasticsearch import Elasticsearch
import elasticsearch.exceptions
import json
import requests
import time
from datetime import datetime, timezone

class Downloader:

    REQUEST_PER_SECOND = 100
    SLEEP_TIME = 1 / REQUEST_PER_SECOND

    def __init__(self,
                url_mariadb,
                pass_mariadb,
                user_mariadb,
                db_name,
                rabbit_pass,
                rabbit_host,
                rabbit_user,
                elastic_user,
                elastic_pass,
                elastic_host,
                rabbit_queue_in,
                rabbit_queue_out,
                pod_name) -> None:
        
        self.mariadb_instance = MariaDB(url_mariadb, pass_mariadb, user_mariadb, db_name)
        self.rabbitmq_instance = RabbitMQ(rabbit_pass, rabbit_host, rabbit_user)
        self.es_client = Elasticsearch("https://"+elastic_host+":9200", basic_auth=(elastic_user,elastic_pass), verify_certs = False)
        self.rabbit_queue_in = rabbit_queue_in
        self.rabbit_queue_out = rabbit_queue_out
        self.pod_name = pod_name

    def es_create_index_if_not_exists(self, index):
        """Create the given ElasticSearch index and ignore error if it already exists"""
        try:
            self.es_client.indices.create(index=index)
        except elasticsearch.exceptions.RequestError as ex:
            if ex.error == 'resource_already_exists_exception':
                pass # Index already exists. Ignore.
            else: # Other exception - raise it
                raise ex

    def callback(self, ch, method, properties, body):
        cursor = self.mariadb_instance.getConnectionMariaDB()
        body_obj = json.loads(body)
        # actualizar grupo (stage=downloader, status=in-progress)
        cursor.execute('SELECT * FROM jobs WHERE id=?',
                        (body_obj['id_job'],))
        job = cursor.fetchone()
        cursor.execute('SELECT * FROM groups WHERE id_job=? AND grp_number=?',
                        (body_obj['id_job'], body_obj['grp_number']))
        group = cursor.fetchone()
        cursor.execute('UPDATE groups SET stage="downloader", status="in-progress" WHERE id=?',
                        (group['id'],))
        self.mariadb_instance.connection.commit()
        # agregar history
        cursor.execute('INSERT INTO history (stage,status,grp_id,component) VALUES ("downloader","in-progress",?,?)',
                        (group['id'],self.pod_name))
        self.mariadb_instance.connection.commit()

        # descargar documentos
        offset = group['offset']
        group_end = offset + job['grp_size']
        while(offset <= group_end):
            r = requests.get(f'https://api.biorxiv.org/covid19/{offset}')
            rel_complete = r.json()['collection'][0]
            rel_id = str(job['id'])+str(group['id']) + str(offset)
            # almacenar en elastic
            rel = {"rel_doi": rel_complete["rel_doi"],
                "rel_site": rel_complete["rel_site"],
                "rel_title": rel_complete["rel_title"],
                "rel_abs": rel_complete["rel_abs"],
                "rel_authors": rel_complete["rel_authors"],}
            resp = self.es_client.index(index="groups", id=int(rel_id),document=rel)
            print(resp['result'])
            time.sleep(self.SLEEP_TIME)
            offset += 1

        # Actualiza el registro en la tabla history
        completedDatetime = datetime.now(timezone.utc)
        completedDatetime = completedDatetime.strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute('UPDATE history SET status="completed", end=? WHERE grp_id=? AND stage="downloader"',
                        (completedDatetime,group['id']))

        # actualizar grupo (status=completed)
        cursor.execute('UPDATE groups SET status="completed" WHERE id=?',
                        (group['id'],))
        self.mariadb_instance.connection.commit()
        # agregar mensaje a cola de salida
        ch.basic_publish(exchange='', routing_key=self.rabbit_queue_out, body=body)
        
    def download(self):
        # crear indice grupo si no existe
        self.es_create_index_if_not_exists('groups')
        # obtener el mensaje de la cola de entrada
        channel = self.rabbitmq_instance.getConnectionRabbitMQ()
        channel.queue_declare(queue=self.rabbit_queue_out)
        channel.basic_consume(queue=self.rabbit_queue_in, on_message_callback=self.callback, auto_ack=True)
        channel.start_consuming()
