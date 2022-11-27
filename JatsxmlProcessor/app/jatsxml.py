from wrapper_mariadb import MariaDB
from wrapper_rabbitmq import RabbitMQ
from elasticsearch import Elasticsearch
import elasticsearch.exceptions
import json
import requests
import time
from datetime import datetime, timezone
import xmltodict

class JatsxmlProcessor:

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
                rabbit_queue_out) -> None:
        
        self.mariadb_instance = MariaDB(url_mariadb, pass_mariadb, user_mariadb, db_name)
        self.rabbitmq_instance = RabbitMQ(rabbit_pass, rabbit_host, rabbit_user)
        self.es_client = Elasticsearch("https://"+elastic_host+":9200", basic_auth=(elastic_user,elastic_pass), verify_certs = False)
        self.rabbit_queue_in = rabbit_queue_in
        self.rabbit_queue_out = rabbit_queue_out

    
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

        # Actualiza el grupo (stage=jatsxml-processor, status=in-progress)
        cursor.execute('UPDATE groups SET stage="jatsxml-processor", status="in-progress" WHERE id=?',
                        (group['id'],))
        self.mariadb_instance.connection.commit()

        # Agrega información a la tabla de history
        cursor.execute('INSERT INTO history (stage,status,grp_id,component) VALUES ("jatsxml-processor","in-progress",?,"component")',
                        (group['id'],))
        self.mariadb_instance.connection.commit()

        # Proceso de descarga documentos
        offset = group['offset']
        group_end = offset + job['grp_size']
        while(offset <= group_end):
            # Busca cada documento con su respectivo rel_id
            rel_id = str(job['id'])+str(group['id']) + str(offset)
            groupsQuery = {"query" : {"term" : {"_id" : rel_id}}}
            resp = self.es_client.search(index="groups", body = groupsQuery)

            dicDocumento= resp['hits']['hits'][0]['_source']

            # Busca si existe el campo de jatsxml en el documento
            jatsxmlURL= ""
            if "jatsxml" in dicDocumento.keys():
                jatsxmlURL=dicDocumento['jatsxml']

            # Descarga del documento jatsxml
            r = requests.get(jatsxmlURL)

            xmlToWrite= open('jats.xml', 'wb')
            xmlToWrite.write(r.content)
            xmlToWrite.close()

            xmlToRead = open('jats.xml', 'rb')
            xmlBytes= xmlToRead.read()
            data_xml_string= xmlBytes.decode('utf8').replace("'", '"')
            
            #data_dict['jatsxmlDoc']= xmltodict.parse(xmlToRead)
            xmlToRead.close()

            data_json= xmltodict.parse(data_xml_string)
            data_json_string= json.dumps(data_json)

            data_dict={}
            data_dict['jatsxmlDoc']= data_json_string

            print(rel_id)
            print(r)

            # Hace el update del documento en ES e imprime el resultado de la operación
            respDetails = self.es_client.update(index="groups", id=int(rel_id), doc=data_dict)
            print(respDetails['result'])

            time.sleep(self.SLEEP_TIME)
            offset += 1

        # Actualiza el registro en la tabla history
        completedDatetime = datetime.now(timezone.utc)
        completedDatetime = completedDatetime.strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute('UPDATE history SET status="completed", end=? WHERE grp_id=? AND stage="jatsxml-processor"',
                        (completedDatetime,group['id']))
        
        # actualizar grupo (status=completed)
        cursor.execute('UPDATE groups SET status="completed" WHERE id=?',
                        (group['id'],))
        self.mariadb_instance.connection.commit()
        # agregar mensaje a cola de salida
        ch.basic_publish(exchange='', routing_key=self.rabbit_queue_out, body=body)
        
    def process(self):
        # Obtiene el mensaje de la cola de entrada
        channel = self.rabbitmq_instance.getConnectionRabbitMQ()
        channel.queue_declare(queue=self.rabbit_queue_out)
        channel.basic_consume(queue=self.rabbit_queue_in, on_message_callback=self.callback, auto_ack=True)
        channel.start_consuming()