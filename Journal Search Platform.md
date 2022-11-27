<p align = 'center'; style = "font-size:20px">
    <b>Instituto Tecnológico de Costa Rica</b>
    <br></br>
</p>

<p align = 'center'; style = "font-size:20px">
    <b>Bases de Datos II</b>
    <br></br>
</p>

<p align = 'center'; style = "font-size:20px">
    <b>Proyecto II - Journal Search Platform</b>
    <br></br>
</p>

<p align = 'center'; style = "font-size:20px">
    <b>Estudiantes:</b>
    <p align = 'center'>
    José Acuña Carrera 
    </p>
    <p align = 'center'>
    Valeria Sell Sáenz 
    </p>
    <p align = 'center'>
    Israel Antonio Herrera Campos 
    </p>
    <p align = 'center'>
    Luis Diego Delgado Muñoz
    </p>
    <p align = 'center'>
    Alexander Brenes Garita 
    </p>
    <br></br>
</p>

<p align = 'center'; style = "font-size:20px">
    <b>Profesor:</b>
    <p align = 'center'>
    Gerardo Nereo Campos Araya
    </p>
    <br></br>
</p>

<p align = 'center'; style = "font-size:20px">
    <b>Fecha de entrega:</b>
    <p align = 'center'>
        25/11/2022
    </p>
    <br></br>
</p>

<p align = 'center'; style = "font-size:20px">
    <b>II Semestre, 2022</b>
</p>

<div style="page-break-after: always;"></div>

# Instrucciones de como ejecutar el proyecto.
### Aplicación Móvil
- Se deberá crear una cuenta en thunkable siguiendo el link: https://x.thunkable.com/
- Debe descargar la aplicación móvil de thunkable para iOS o Android.
- Luego deberá accesar al siguiente link: https://x.thunkable.com/copy/abbacaab8d33043640ab4bf679cfd278.
- Una vez con el proyecto agregado a sus proyectos, podrá probar la aplicación desde la aplicación movil de thunkable.
- Ya en la aplicación, las siguientes son las funcionalidades de esta:
- Crear usuario: Se podrá crear un usario el cual se almacenará en la base de datos Fireship.
- Iniciar sesión: Se iniciará sesión con su usuario creado anteriormente.
- Buscar articulo: En la ventana de buscar articulo podrá buscar por nombre un articulo científico de la página: http://connect.biorxiv.org/relate/content/181.
- Seleccionar articulo: Se podrá seleccionar un articulo de la lista de resultados, lo que le llevará a una pantalla en la que verá el nombre del articulo, sus autores y el abstract de este.
- Likear un articulo: Se podrá dar "me gusta" a los articulos desde la pestaña de un articulo individual, además, se podrá ver los articulos a los que se le ha dado like.

### Helm Charts
Requisitos:
- Tener instalado Docker, Kubernetes y Helm.
- Estár corriendo Docker Desktop (Windows) y tener activada la opción "Enable Kubernetes" en la configuración.
- Asegurarse de tener los recursos de memoria principal necesarios para correr todos los servicios, se recomienda contar con mas de 16GB.
- Clonar el repositorio en su computadora.

Pasos:

- Abrir una terminal en la direccion `./charts` desde el root de la carperta del proyecto y escribir los siguientes comandos en este orden:
- `cd dependencies`
- `helm dependency update`
- `cd ..`
- `cd monitoring`
- `helm dependency update`
- `cd ..`
- `cd databases`
- `helm dependency update`
- `cd ..`
- `cd applications`
- `helm dependency update`
- `cd ..`
- `helm install dependencies dependencies`
- `helm install monitoring monitoring`
- `helm install databases databases`
- `helm install aplications aplications`

Con esto ya debería de estar corriendo todos los servicios en Kubernetes, los cuales son las bases de datos (Elasticsearch, RabbitMQ y MariaDB) y los componentes de la aplicación implementados en Python (API, Loader, Downloader, Details-Downloader, Jatsxml Procesor).

### API

Con el API se necesitan varios pasos extra ya que este necesita ser expuesto fuera del cluster y encima de esto se publica en la web por medio de ngrok.

Pasos:

- Con el deployment de API ya corriendo en Kubernetes, escriba el siguiente comando en su terminal:
- `kubectl port-forward {nombre del pod del api} 3000:3000`
- Una alternativa a este metodo es utilizando la aplicación "Lens":
- Se abre la aplicación y se selecciona el cluster "docker-desktop"
- En la pestaña de pods, seleccione un pod que su nombre inicie con "api"
- En la sección "ports" del sidebar que se despliega, seleccione la opción "Forward"
- En el campo "Local port to forward from:", introduzca 3000 y presione el boton "Start"
- Ya con el port forward hecho de cualquiera de las dos maneras antes mencionadas, abra la aplicacion de Ngrok y escriba el comando `ngrok.exe http 3000`
- Copie el primer link del campo forwarding (se vera algo parecido a: https://2436-190-113-114-40.ngrok.io) y peguelo en la variable "url" de la aplicación de Thunkable.
- Para cada componente que requiera una llamada al API, para realizar el paso de variables se debe incluir ese URL y las variables a utilizar. 
# Recomendaciones. 
- Utilizar los helm charts de bitnami para la creación de las bases de datos en Kubernetes ya que estos están listos para usarse, tienen una extensa documentación que se puede consultar y son muy usados, por lo que si se da un error este se puede buscar en internet y probablemente se encuentre alguien que se haya encontrado con el mismo.
- Contar con una computadoras con al menos 16GB de memoria principal para correr el proyecto, ya que los pods en  Kubernetes terminan haciendo que Docker Desktop consuma hasta 5GB de memoria o mas.
- Encapsular en clases "wraper" las conexiones con MariaDB y RabbitMQ ya que esto nos permite no repetir código e isolar el código de estas conexiones del código de los componentes que las usan, haciendolo mas legible y mantenible.
- Encapsular en clases los componentes implementados en Python y llamarlos desde un "main". Esto genera codigo mas limpio y legible, ademas de modularizar la aplicacion.
- Hacer debug de manera local a la hora de desarrollar los componentes y cuando estos están listos subir la imagen a DockerHub y crear sus deployments. Esto ya que hacer debug con los componentes siendo pods es tedioso y consume mucho tiempo.
- Utilizar variables de entorno para automatizar el uso de ciertos datos como credenciales o los host de las bases de datos.

# Conclusiones.
- Docker es una herramienta muy útil ya que nos permite hacer pequeñas maquinas virtuales con programas (hechos por uno o por otros) y usarlas en cualquier sistema. Esto fue útil a la hora de crear las imagenes de los componentes realizados en Python.
- Kubernetes es una herramienta que aporta mucho valor ya que nos permite manejar los contenedores de docker en clusters y darnos una arquitectura de microservicios "out-of-the-box".
- Helm es una herramienta muy útil para automatizar la creación de depoyments de Kubernetes, dandonós la capacidad de correr unos pocos comandos y ya tener los deployments listos para las bases de datos y los componentes desarrollados en Python.
- Utilizar una estructura de archivos definida para todos los componentes nos dió facilidad para navegar las diferentes partes de cada uno.
- Utilizar un acercamiento orientado a objetos para el código de los componentes nos dió ventajas como: tener menos código repetido, modularizar las diferentes partes de los componentes y facilitarlos cambios en el código.
- Python es un buen lenguaje para implementar este tipo de componentes ya que es fácil escribir el código de cosas complejas como conexiones a bases de datos o hacer request http.
- El ecosistema de librerias de Python es otra gran ventaja para usar el lenguaje ya que se encontraron librerias para todas las necesidades de los componentes, haciendo fácil la realizacion de queries en MariaDB, la indexación de documentos en Elasticsearch y la publicación y escucha de mensajes en RabbitMQ, entre otras operaciones.
- Flask es una buena herramienta para crear APIs facil, esto tanto por el lenguaje Python como por la manera en la que se crean endpoints y la manera en la que se retornan las respuestas (solo con un return ya se da la respuesta del servidor, lo que lo hace muy intuitivo).
- Thunkable facilita mucho la creacion de aplicaciones móviles con su aceramiento "drag and drop" y sus integraciones con Firebase, Mapas, etc.
- Firebase es una buena opción para bases de datos que no necesitan mucha complejidad ni consistencia.
- Ngrok facilita mucho la exposición de una API a la web, ya que con solo un comando en el que se especifica el puerto que se está usando por el API, ya se expone y cualquier persona o frontend en el mundo lo puede consumir.
