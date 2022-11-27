from wrapper_mariadb import MariaDB
from wrapper_rabbitmq import RabbitMQ
from elasticsearch import Elasticsearch
import elasticsearch.exceptions
import json
import requests
import time
from datetime import datetime, timezone

class DetailsDownloader:

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

    
    def callback(self, ch, method, properties, body):
        # Transforma el json de la cola de entrada en un diccionario de Python
        body_obj = json.loads(body)

        # Crea el cursor de MariaDB y realiza la búsqueda del job y el grupo basado en el id_job y el grp_number
        cursor = self.mariadb_instance.getConnectionMariaDB()

        #Obtiene el job y el grupo de MariaDB
        cursor.execute('SELECT * FROM jobs WHERE id=?',
                        (body_obj['id_job'],))
        job = cursor.fetchone()
        cursor.execute('SELECT * FROM groups WHERE id_job=? AND grp_number=?',
                        (body_obj['id_job'], body_obj['grp_number']))
        group = cursor.fetchone()

        # Actualiza el grupo (stage=details-downloader, status=in-progress)
        cursor.execute('UPDATE groups SET stage="details-downloader", status="in-progress" WHERE id=?',
                        (group['id'],))
        self.mariadb_instance.connection.commit()

        # Agrega información a la tabla de history
        cursor.execute('INSERT INTO history (stage,status,grp_id,component) VALUES ("details-downloader","in-progress",?,?)',
                        (group['id'],self.pod_name))
        self.mariadb_instance.connection.commit()

        # Proceso de descarga documentos
        offset = group['offset']
        group_end = offset + job['grp_size']
        while(offset <= group_end):
            # Busca cada documento con su respectivo rel_id
            rel_id = str(job['id'])+str(group['id']) + str(offset)
            groupsQuery = {"query" : {"term" : {"_id" : rel_id}}}
            resp = self.es_client.search(index="groups", body = groupsQuery)
            rel_site = resp['hits']['hits'][0]['_source']['rel_site']
            rel_site = rel_site.lower()
            rel_doi = resp['hits']['hits'][0]['_source']['rel_doi']

            # Descarga el documento respectivo en base a su rel_doi y rel_site
            r = requests.get(f'https://api.biorxiv.org/details/{rel_site}/{rel_doi}')
            print("https://api.biorxiv.org/details/"+str(rel_site)+"/"+str(rel_doi))
            rel_complete = r.json()['collection'][0]

            # Se crea el diccionario que va a ser utilizado para actualizar el documento con los details
            details = {}
            for key in rel_complete:
                if key not in ['doi','server','title', 'abstract', 'authors', 'author_corresponding', 'author_corresponding_institution']:
                    details[key] = rel_complete[key]
            
            # Hace el update del documento en ES e imprime el resultado de la operación
            respDetails = self.es_client.update(index="groups", id=int(rel_id), doc=details)
            print(respDetails['result'])
            time.sleep(self.SLEEP_TIME)
            offset += 1

        # Actualiza el registro en la tabla history
        completedDatetime = datetime.now(timezone.utc)
        completedDatetime = completedDatetime.strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute('UPDATE history SET status="completed", end=? WHERE grp_id=? AND stage="details-downloader"',
                        (completedDatetime,group['id']))
        self.mariadb_instance.connection.commit()
        
        # actualizar grupo (status=completed)
        cursor.execute('UPDATE groups SET status="completed" WHERE id=?',
                        (group['id'],))
        self.mariadb_instance.connection.commit()
        # agregar mensaje a cola de salida
        ch.basic_publish(exchange='', routing_key=self.rabbit_queue_out, body=body)
        
    def download(self):
        # Obtiene el mensaje de la cola de entrada
        channel = self.rabbitmq_instance.getConnectionRabbitMQ()
        channel.queue_declare(queue=self.rabbit_queue_out)
        channel.basic_consume(queue=self.rabbit_queue_in, on_message_callback=self.callback, auto_ack=True)
        channel.start_consuming()