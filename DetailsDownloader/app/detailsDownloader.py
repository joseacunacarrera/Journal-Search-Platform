from wrapper_mariadb import MariaDB
from wrapper_rabbitmq import RabbitMQ
from elasticsearch import Elasticsearch
import elasticsearch.exceptions
import json
import requests

class DetailsDownloader:

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
                rabbit_queue_out) -> None:
        
        self.mariadb_instance = MariaDB(url_mariadb, pass_mariadb, user_mariadb, db_name)
        self.rabbitmq_instance = RabbitMQ(rabbit_pass, rabbit_host, rabbit_user)
        self.es_client = Elasticsearch("https://"+elastic_host+":9200", basic_auth=(elastic_user,elastic_pass), verify_certs = False)
        self.rabbit_queue_in = rabbit_queue_in
        self.rabbit_queue_out = rabbit_queue_out

    
    def callback(self, ch, method, properties, body):
        # Transforma el json de la cola de entrada en un diccionario de Python
        body_obj = json.loads(body)

        # Crea el cursor de MariaDB y realiza la búsqueda del grupo basado en el id_job y el grp_number
        cursor = self.mariadb_instance.getConnectionMariaDB()
        cursor.execute('SELECT * FROM groups WHERE id_job=? AND grp_number=?',
                        (body_obj['id_job'], body_obj['grp_number']))
        group = cursor.fetchone()

        # Actualiza el grupo (stage=details-downloader, status=in-progress)
        cursor.execute('UPDATE groups SET stage="details-downloader", status="in-progress" WHERE id=?',
                        (group['id'],))
        self.mariadb_instance.connection.commit()

        resp = self.es_client.search(index="groups", query={"match_all": {}})
        #print("Got %d Hits:" % resp['hits']['total']['value'])
        print(resp['hits']['hits'])
        



        
        # Agrega información a la tabla de history
        cursor.execute('INSERT INTO history (stage,status,grp_id,component) VALUES ("details-downloader","in-progress",?,"component")',
                        (group['id'],))
        self.mariadb_instance.connection.commit()
        
        '''# descargar documentos
        r = requests.get(f'https://api.biorxiv.org/covid19/{group["grp_number"]}')
        rel_complete = r.json()['collection']
        print(rel_complete)'''

        #rel_complete = r.json()['collection'][0]
        
        # Almacena en elastic
        '''
        rel = {"rel_doi": rel_complete["rel_doi"],
               "rel_site": rel_complete["rel_site"],
               "rel_title": rel_complete["rel_title"],
               "rel_abs": rel_complete["rel_abs"],
               "rel_authors": rel_complete["rel_authors"],}
        resp = self.es_client.index(index="groups", id=group['id'],document=rel)
        print(resp['result'])
        '''
        
        # actualizar grupo (status=completed)
        '''
        cursor.execute('UPDATE groups SET status="completed" WHERE id=?',
                        (group['id'],))
        self.mariadb_instance.connection.commit()
        # agregar mensaje a cola de salida
        ch.basic_publish(exchange='', routing_key=self.rabbit_queue_out, body=body)
        '''
        
    def download(self):
        # Obtiene el mensaje de la cola de entrada
        channel = self.rabbitmq_instance.getConnectionRabbitMQ()
        channel.queue_declare(queue=self.rabbit_queue_out)
        channel.basic_consume(queue=self.rabbit_queue_in, on_message_callback=self.callback, auto_ack=True)
        channel.start_consuming()