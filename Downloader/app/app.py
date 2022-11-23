# Librerías necesarias

from configparser import NoSectionError
import pika, os, json, mariadb, sys, math, time
from elasticsearch import Elasticsearch

# Variables de entorno

api_endpoint= os.getenv("APIENDPOINT")
rabbitmq_endpoint = os.getenv("RMQENDPOINT")
mariadb_endpoint = os.getenv("MDBENDPOINT")
elastic_endpoint = os.getenv("ESENDPOINT")

rabbit_user = os.getenv("RMQUSER")
rabbit_pass = os.getenv("RMQPASS")

mariadb_user = os.getenv("MDBUSER")
mariadb_pass = os.getenv("MDBPASS")

elastic_user = os.getenv("ESUSER")
elastic_pass = os.getenv("ESPASS")

elastic_index = os.getenv("ESINDEX")
mariadb_db = os.getenv("MDBDB")

rmq_sourcequeue = os.getenv("RMQSOURCEQUEUE")
rmq_destqueue = os.getenv("RMQDESTQUEUE")
