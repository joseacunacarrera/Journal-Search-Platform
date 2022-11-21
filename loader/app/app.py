from flask import Flask

app = Flask(__name__)

@app.route('/', methods=['GET'])
def hello_wold():
    return "Hello World"

@app.route('/jobs/agregar', methods=['POST'])
def agregar_jobs():
    return "Agregar un Job"

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