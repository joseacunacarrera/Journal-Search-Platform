from flask import *
from wrapper_mariadb import MariaDB
from elasticsearch import Elasticsearch
import json, time

class API:
    
    app = Flask(__name__)
    def __init__(self,
                url_mariadb,
                pass_mariadb,
                user_mariadb,
                db_name) -> None:
        
        self.mariadb_instance = MariaDB(url_mariadb, pass_mariadb, user_mariadb, db_name)

    def addtoMariaDB(self, size):
        mariaDBcursor = self.mariadb_instance.getConnectionMariaDB()
        try:
            mariaDBcursor.execute('INSERT INTO jobs (status,grp_size) VALUES (?,?)', ('in-progess',size))
            self.mariadb_instance.connection.commit()
        except mariaDBcursor.Error as e: 
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

    @app.route('/jobs/agregar/<int:grp_size>', methods=['POST'])  # /jobs/agregar/?url_elas=[URL]&user=[USER]&password=[PASSWORD]&id_elas=[ID]
    def agregar_jobs(self, grp_size: int):
        print(grp_size)
        self.addtoMariaDB(grp_size)
        
        URL_elas = str(request.args.get('url_elas')) #URL de elasticsearch
        user = str(request.args.get('user'))         #Usuario de elasticsearch
        password = str(request.args.get('password')) #Password de elasticsearch
        id_elas = str(request.args.get('id_elas'))   #Indice de elasticsearch

        data = {
                    'Pagina': 'Agregar Job',
                    'URL': f'{URL_elas}',
                    'USER': f'{user}',
                    'PASSWORD': f'{password}',
                    'ID': f'{id_elas}',
                    'Timestamp': time.time()        
                }

        json_dump = json.dumps(data)  #se pasan los datos a JSON
        
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