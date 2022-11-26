from flask import *
import json, time


app = Flask(__name__)

@app.route('/', methods=['GET'])
def main_page():
    
    data = {
                'Pagina': 'Main Page',
                'Mensaje': 'Succesfully loaded the Main Page',
                'Timestamp': time.time()        
            }

    jason_dump = json.dumps(data)  #se pasan los datos a JSON
    return jason_dump

@app.route('/jobs/agregar/', methods=['POST'])  # /jobs/agregar/?url_elas=[URL]&user=[USER]&password=[PASSWORD]&id_elas=[ID]
def agregar_jobs():

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

@app.route('/articulos/buscar', methods=['GET'])
def buscar_articulos():
    return "Buscar Articulos"

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