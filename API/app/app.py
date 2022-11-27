from flask import *
from wrapper_mariadb import MariaDB
from elasticsearch import Elasticsearch
import json, time

    
app = Flask(__name__)

mariadb_instance = MariaDB('127.0.0.1', 'mypass', 'root', 'mydb')

def addtoMariaDB(size):
    mariaDBcursor = mariadb_instance.getConnectionMariaDB()
    try:
        mariaDBcursor.execute('INSERT INTO jobs (`status`, grp_size) VALUES ("in-progress", ?)', (size,))
        mariadb_instance.connection.commit()
    except Exception as e: 
        print(f"Error: {e}")

@app.route('/', methods=['GET'])
def main_page():
    data = {
                'Pagina': 'Main Page',
                'Mensaje': 'Succesfully loaded the Main Page',
                'Timestamp': time.time()        
            }

    jason_dump = json.dumps(data)  #se pasan los datos a JSON
    return jason_dump

@app.route('/jobs/agregar/', methods=['POST'])
def agregar_jobs():

    print("siu")

    grp_size = int(request.args.get('grp_size'))

    print(grp_size)
    addtoMariaDB(grp_size)
    
    return "Success", 200

@app.route('/articulos/buscar/<string:search_input>', methods=['GET'])
def buscar_articulos(search_input:str):
    user_input = search_input
    ELASTIC_PASSWORD = "<CONTRASEÑA ES>"
    CLOUD_ID = "deployment-name:..."
    es = Elasticsearch(
        cloud_id=CLOUD_ID,
        basic_auth=("elastic", ELASTIC_PASSWORD)
    )
    resp = es.search(index="groups", body={"query": {"match": {"content": str(user_input)}}})
    print("Got %d Hits:" % resp['hits']['total']['value'])
    for hit in resp['hits']['hits']:
        print("%(timestamp)s %(author)s: %(text)s" % hit["_source"])

    return "Success", 200

@app.route('/articulos/obtener', methods=['GET'])
def obtener_articulo():
    return"Obtener Articulo"

@app.route('/articulos/like', methods=['POST'])
def likear_articulo():
    return"Likear Articulo"
    
@app.route('/artuculos/gustados', methods=['GET'])
def articulos_gustados():
    return"Articulos gustados"

if __name__ == "__main__":
    app.run(host='localhost', port=5000)