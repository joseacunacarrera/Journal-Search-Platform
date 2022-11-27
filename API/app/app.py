from flask import *
from wrapper_mariadb import MariaDB
from elasticsearch import Elasticsearch
import json, time

    
app = Flask(__name__)

mariadb_instance = MariaDB('127.0.0.1', 'mypass', 'root', 'mydb')

def addtoMariaDB(size):
    mariaDBcursor = mariadb_instance.getConnectionMariaDB()
    try:
        mariaDBcursor.execute('INSERT INTO jobs (`status`, grp_size) VALUES ("pending", ?)', (size,))
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

    grp_size = int(request.args.get('grp_size'))

    print(grp_size)
    addtoMariaDB(grp_size)
    
    return "Success", 200

@app.route('/articulos/buscar/', methods=['GET'])
def buscar_articulos():

    search_input = str(request.args.get('search_input'))

    user_input = search_input
    ELASTIC_PASSWORD = "mypass"
    es = Elasticsearch("https://localhost:9200", basic_auth=('elastic',ELASTIC_PASSWORD), verify_certs = False)

    query_body = {
        "query": {
            "bool": {
                "must": [
                    {
                        "span_near": {
                            "clauses": [
                                {
                                    "span_multi": {
                                        "match": {
                                            "fuzzy": {
                                                "rel_title":{
                                                    "value": user_input,
                                                    "fuzziness": "AUTO"
                                                }
                                            }
                                        }
                                    }
                                }
                            ],
                            "slop": 0,
                            "in_order": False
                        }
                    }
                ]
            }
        }
    }
    
    resp = es.search(index="groups", body=query_body, size=100)
    print("Got %d Hits:" % resp['hits']['total']['value'])
    lis_res = []
    for hit in resp['hits']['hits']:
        print(hit["_source"]["rel_title"], hit["_id"])
        lis_res.append({'Title': hit['_source']['rel_title'], 'Id': hit['_id']})

    return lis_res

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