from flask import Flask, render_template, request, redirect, send_from_directory, url_for
from flaskext.mysql import MySQL
from datetime import datetime
import os

app = Flask(__name__)


# conexion a la base de datos
mysql = MySQL()
# indicamos que para que se conecte a la base de datos 'MYSQL_DATABASE_***' vamos a utilizar 
app.config['MYSQL_DATABASE_HOST'] = 'localhost'     # el localhost
app.config['MYSQL_DATABASE_USER'] = 'root'          # el usuario
app.config['MYSQL_DATABASE_PASSWORD'] = '123456'    # la constrasena
app.config['MYSQL_DATABASE_DB'] = 'sistema'         # el nombre de la DB

# mysql inicia la conexion
mysql.init_app(app)

# creamos una referancia a la carpeta uploads en formato join
CARPETA= os.path.join('uploads')
# utilizamo la configuracion para guardar esa ruta pero comu un valor del valor de la variable carpeta
app.config['CARPETA']=CARPETA

# creamos la url que contenga el nombre de la foto
@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'],nombreFoto)

# ruta inicial / que renderice el archivo index.html
@app.route('/')
def index():

    # variable selecionamos a la tabla
    sql = "SELECT * FROM `empleados`;"
    # se va aconectar a mysql
    conn = mysql.connect()
    # cusros es informacion que almacena lo que se ejecuta
    cursor = conn.cursor()

    # mandamoa a ejecutar la instruccion
    cursor.execute(sql)
    
    #! variable para saber que esta devolviendo bien la informacion con fetchall()
    empleados = cursor.fetchall()
    # para comfirmar que este ok se imprime en cosola los datos de la tabla
    # print(empleados)

    # cerramos la conexion con un commit
    conn.commit()

    # enviamos la informacion a el achivo html con una variable empleados
    return render_template('empleados/index.html' , empleados = empleados)


@app.route('/create')
def create():
    return render_template('empleados/create.html' )

@app.route('/store', methods=['POST'])
def storage():

    # llamamos al modulo request para signar los datos el usuario ingresa en el formulario html
    _nombre = request.form ['txtNombre']
    _correo = request.form ['txtCorreo']

    # al ser un foto se debe solicitar en formato de archivo
    _foto = request.files ['txtFoto']

    # !con el modulo time se dara formato de tiempo para el archivo de foto
    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")

    #si hay una fotografia, se adjunta con su nuevo nombre
    global nuevafoto
    if _foto.filename !='':
        nuevafoto = tiempo   + str(_foto.filename)
        _foto.save("uploads/"+nuevafoto)

    # intruccion sql 
    #  el %s reemplaza al valor que ingresa el usuario
    sql = "INSERT INTO `empleados` (`id`, `nombre`, `correo`, `foto`) VALUES (NULL, %s, %s, %s);"
    # variable para los datos que vamos a insertar
    datos=(_nombre,_correo,nuevafoto)

    # se va aconectar a mysql
    conn = mysql.connect()
    # cusros es informacion que almacena lo que se ejecuta
    cursor = conn.cursor()

    # mandamoa a ejecutar la instruccion
    cursor.execute(sql, datos)

    # cerramos la conexion con un commit
    conn.commit()

    return redirect('/')

# ? Editar registro con el parametro id
@app.route('/edit/<int:id>')
def edit(id):

    # abre conexion
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT *  FROM empleados WHERE id=%s",(id))

    #! variable para saber que esta devolviendo bien la informacion con fetchall()
    empleados = cursor.fetchall()

    #  cierre la conexion 
    conn.commit()

    #  # usamos el modulo redireccionar para ir a la ruta inicial
    return render_template('empleados/edit.html', empleados = empleados)


@app.route('/update', methods=['POST'])
def update():
    
    # llamamos al modulo request para signar los datos el usuario ingresa en el formulario html
    _nombre = request.form ['txtNombre']
    _correo = request.form ['txtCorreo']

    # al ser un foto se debe solicitar en formato de archivo
    _foto = request.files ['txtFoto']

    # *vamos aponer un id entre [] para ser encoentrado
    id =request.form['txtId']

    # instruccion SQL
    sql = "UPDATE empleados SET nombre= %s, correo = %s WHERE id=%s;"
    # variable para los datos que vamos a insertar
    datos=(_nombre,_correo,id)

    # se va aconectar a mysql
    conn = mysql.connect()
    cursor = conn.cursor()

    #?configuracion del archivo de la foto
    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")

    #si hay una fotografia, se adjunta con su nuevo nombre
    global nuevafoto
    if _foto.filename !='':
        nuevafoto = tiempo   + str(_foto.filename)
        _foto.save("uploads/"+nuevafoto)

        # intruccion para buscar la foto
        cursor.execute("SELECT foto  FROM empleados WHERE id=%s",id)
        fila=cursor.fetchall()

        # removemos la foto selecionada
        os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))
        # actualiza la misma tabla pero solo el nombre de la foto
        cursor.execute("UPDATE empleados SET foto = %s WHERE id = %s", (nuevafoto,id))
        conn.commit()

    # mandamoa a ejecutar la instruccion
    cursor.execute(sql, datos)

    # cerramos la conexion con un commit
    conn.commit()
    
    return redirect ('/')

# ?eleminar registro con el parametro id
@app.route('/destroy/<int:id>')
def destroy(id):

    # abre conexion
     conn = mysql.connect()
     cursor = conn.cursor()

    # intruccion para buscar la foto
     cursor.execute("SELECT foto FROM empleados WHERE id=%s",id)
     fila=cursor.fetchall()
      # removemos la foto selecionada
     os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))
    

     print(app.config['CARPETA'])
     # Ejecuta la instruccion SQL
     cursor.execute("DELETE FROM empleados WHERE id=%s",(id))

     #  cierre la conexion 
     conn.commit()

     # usamos el modulo redireccionar para ir a la ruta inicial
     return redirect('/')

#
if __name__ == '__main__':
    app.run(debug=True)
