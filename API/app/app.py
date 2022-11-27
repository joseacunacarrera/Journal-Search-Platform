from flask import *
from wrapper_mariadb import MariaDB
from elasticsearch import Elasticsearch
import firebase_admin
from firebase_admin import credentials, db, auth
import json, time
    
app = Flask(__name__)
config = {
    'databaseURL': "https://journal-search-platform-default-rtdb.firebaseio.com",
    'projectId': "journal-search-platform",
    'storageBucket': "journal-search-platform.appspot.com",
}

cred = credentials.Certificate("API/app/credentials.json")
default_app = firebase_admin.initialize_app(cred, options = config)

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

    response = json.dumps(lis_res)
    return make_response(response)

@app.route('/articulos/obtener', methods=['GET'])
def obtener_articulo():
    search_input = str(request.args.get('search_input'))
    article_title = search_input
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
                                                    "value": article_title,
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
    
    return resp

@app.route('/articulos/like', methods=['POST'])
def likear_articulo():
    article = str(request.args.get('user_input'))
    user_id = str(request.args.get('user_id'))

    data = {'user_id': user_id, 'article': article}

    body = json.dumps(data)
    try:
        ref = db.reference("/likes")
        ref.push(body)
        return make_response('Like registrado')
    except Exception as error:
        return f'Error: {error}'
    
@app.route('/articulos/gustados', methods=['GET'])
def articulos_gustados():
    user_id = request.args.get('user_id')
    try:
        ref = db.reference(f'/likes')

        #likes = res_to_list(ref.get())
        json_likes = ref.order_by_child('user_id').get()
        print(json_likes)
        likes = json.loads(json_likes.items())

        print(likes)

        response = json.dumps(filtrar_likes_usuario(likes=likes, user_id=user_id))

        print(response)

        return make_response(response)
    except Exception as error:

        print("erroooooor")

        return f'Error: {error}'



def filtrar_likes_usuario(likes, user_id):

    lista_likes = []
    for like in likes:
        if like['user_id'] == user_id:
            lista_likes.append(like)

    return lista_likes

def res_to_list(res):
    fb_keys = list(res.keys())

    for fb_key, value in zip(fb_keys, res.values()):
        value['fb_key'] = fb_key

    return list(res.values())

if __name__ == "__main__":
    app.run(host='localhost', port=5000)