# Importación de las librerías

from configparser import NoSectionError
import pika, os, json, mariadb, sys, math, time
from elasticsearch import Elasticsearch

# Extracción de variables de entorno

rabbitmq = os.getenv("RABBITMQ")
rabbitpass = os.getenv("RABBITPASS")
rabbit_queue = os.getenv("RABBITQUEUE")
elastic_Endpoint = os.getenv("ESENDPOINT")

####### Creación de funciones Python

# Cambio de estado del JSON

def changeStatus(jsonDoc):
    jsonDoc["status"] = "In-Progress"
    return jsonDoc

def getDataSourceDetails(data):
    for i in data["data_sources"]:
        if i["name"] == data['source']['data_source']:
            return i

def getSourceExpression(data):
    expression = "SELECT COUNT(1) FROM (" + data["source"]["expression"] + ") sub1"
    return expression

def getGroups(num, jsonDoc):
    grpSize = jsonDoc["source"]["grp_size"]
    total = math.ceil(num / int(grpSize))
    return total

def sendJSONGroups(totalGroups, jsonDoc, clientES):
    jobId = jsonDoc["job_id"]
    channel.queue_declare(queue = rabbit_queue)
    for i in range(totalGroups):
        groupId=jobId+"-"+str(i)
        groupJson = { "job_id" : jobId, "group_id" : groupId}
        print(groupJson)
        clientES.index(index = "groups", refresh = "wait_for", document = groupJson)
        print("Se envio a Elastic")
        groupJsonFormat = json.dumps(groupJson)
        print(groupJsonFormat)
        channel.basic_publish(exchange = '', routing_key = rabbit_queue, body = groupJsonFormat)
        print("Se envio a Rabbit")

####### Conexiones con entidades externas

# Conexión con RabbitMQ

credentials = pika.PlainCredentials('user', rabbitpass)
parameters = pika.ConnectionParameters(host=rabbitmq, credentials=credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

# Conexión a mariaDB

def mariaConnection(details):
    try:
        connection = mariadb.connect(
            host = "databases-mariadb",
            user = "root", # Se consigue con details['user']
            password = "t1", # Se consigue con details['password']
            port = 3306,
            database = details['name']

        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)
    #Cursor para manejar la conexión
    cur = connection.cursor(dictionary=True)
    return cur

# Conexión con Elasticsearch

client = Elasticsearch("https://" + elastic_Endpoint + ":9200", basic_auth = ("elastic", "mypass"), verify_certs = False)

####### Main

# Extracción del job

while (True):
    try:
        inicio = time.time()
        jobQuery = {"query" : {"term" : {"status" : "new"}}}
        jobId = client.search(index = "jobs", body = jobQuery)['hits']['hits'][0]['_id']
        print("Encontro Id")
        jsonData = client.get(index = "jobs", id = jobId)
        jsonData = jsonData["_source"]
        print("Obtuvo el json")
        jsonData = changeStatus(jsonData)
        print("Cambio el estado")
        client.index(index = "jobs", id = jobId, refresh = "wait_for", document = jsonData)
        print("Publico el job en Elastic")
        details = getDataSourceDetails(jsonData)
        print("Obtuvo detalles")
        expression = getSourceExpression(jsonData)
        print("Obtuvo la expresion")
        mariaDBCursor = mariaConnection(details)
        mariaDBCursor.execute(expression)
        print("Realizo el query a MariaDB")
        totalGroups = getGroups(mariaDBCursor.fetchall()[0]["COUNT(1)"], jsonData)
        print("Obtuvo el total de grupos")
        sendJSONGroups(totalGroups, jsonData, client)
        print("Envio los json a Elastic y Rabbit")
        final = time.time()
        metrics = str(final - inicio)
        archivo = open("../appmetrics/metrics.txt", "w")
        archivo.write(metrics)
        archivo.close()
        
    except Exception as e:
        print(e)
        print("No entro")
        continue

