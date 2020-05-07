import os
import urllib.request
from app import app
from flask import Flask, flash, request, redirect, render_template, session
from werkzeug.utils import secure_filename
from app.models.properties import Properties
from app.models.table import Table
from flask.helpers import url_for
from app.models.analisis import AnalisisUni
from app.models.analisis import AnalisisBi
from app.models.analisis import Analisis
from app.models.tablas_analisis.tabla_frecuencia import Tabla_frecuencia
from app.models.tablas_analisis.tabla_verosimilitud import Tabla_verosimilitud
from app.models.algoritmos_predictores.naive_bayes import Naive_bayes
import urllib

ALLOWED_EXTENSIONS = set(['csv', 'json'])

table = None
analisis_uni = None


if __name__ == "__main__":
    app.run()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['POST', 'GET'])
def upload_form():
    if request.method == 'POST':
        # Checamos si la petición tiene los elementos de carga de archivos
        files_names = ['csv', 'properties']
        cont = 0
        global table
        rutas = [] # Las rutas para los archivos recién subidos
        for name in files_names:
            if name not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files[name]
            # Intentamos obtener un archivo del cliente por cada tipo de archivo requerido
            if file.filename == '':
                flash('No ha seleccionado un archivo')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                # Nos aseguramos que el archivo recibido tenga un nombre válido
                filename = secure_filename(file.filename)
                rutas.append(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                flash('Éxito al subir el archivo')
                cont += 1
                if (cont == len(files_names) and len(rutas) >= 2):
                    # Una vez cargados todos los archivos redireccionamos a la vista de estadisticas
                    # Cargamos las direcciones para los archivos recien subidos
                    # Hacer las rutas dinámicas. PendientesSaul!!!
                    schema = "app/properties.schema"
                    csvdata = rutas[0]
                    props = rutas[1]
                    # Cargamos un objeto properties, el cual almacenará la funcionalidad del proceso de
                    # análisis de datos
                    props = Properties(schema, props, csvdata)
                    props.printErrors()  # Mostramos errores de cargado en caso de existir
                    # El objeto Properties se encargará de analizar el archivo csv
                    # y devolver la información obtenida en formato de tabla
                    table = props.getTable()
                    print(table.data)
                    return redirect(url_for('estadisticas'))
            else:
                flash('Allowed file types are txt, pdf, png, jpg, jpeg, gif')
                return redirect(request.url)
    else:
        # El metodo recibido es GET o cualquier otro
        return render_template('upload.html')


@app.route('/box_plot', methods=['POST'])
def box_plot():
    if analisis_uni:
        if request.method == 'POST':
            clase = request.form['clases']
            # Obtenemos el atributo perteneciente a la clase proporcionada
            atr_clase = next(
                (x for x in analisis_uni.tabla.properties.props['attributes'] if x['name'] == clase), None)
            if not atr_clase:
                return redirect(url_for('estadisticas'))
            analisis_uni.muestra_box_plot(atr_clase)
            return redirect(url_for('atributo', nombre=analisis_uni.nombre))
    else:
        return redirect(url_for('upload_form'))


@app.route('/istograma', methods=['POST'])
def istograma():
    if analisis_uni:
        if request.method == 'POST':
            analisis_uni.muestra_istograma()
            return redirect(url_for('atributo', nombre=analisis_uni.nombre))
    else:
        return redirect(url_for('upload_form'))


@app.route('/estadisticas')
def estadisticas():
    if table != None:
        numero_atributos = table.properties.props['attributes_number']
        numero_instancias = len(table.data)
        atributos = table.properties.props['attributes']
        return render_template('estadisticas.html', table=table, numero_atributos=numero_atributos,
                               numero_instancias=numero_instancias, atributos=atributos)
    return redirect(url_for('upload_form'))


@app.route('/atributo/<string:nombre>', methods=['GET', 'POST'])
def atributo(nombre):
    if table != None:
        global analisis_uni
        atr = next(
            (x for x in table.properties.props['attributes'] if x['name'] == nombre), None)
        clase = "jugar"  # No es código dinámico, calcular de manera dinámica. PendientesSaul!!!
        # Creamos un objeto de analisis univariable
        analisis_uni = AnalisisUni(table, atr, clase)
        # Obtenemos la lista de Tablas de frecuencia
        tbls_frec = Tabla_frecuencia.tablas_frecuencia(analisis_uni)
        # Pasamos los atributos como un diccionario a parte
        atributos = table.properties.props['attributes']
        return render_template('atributo.html', analisis_uni=analisis_uni, atributos=atributos, tbls_frec=tbls_frec)
    else:
        return redirect(url_for('upload_form'))


@app.route('/naive_bayes', methods=['GET', 'POST'])
def naive_bayes():
    if table != None:
        analisis = Analisis(table)
        # Creamos un objeto naive_bayes
        tbls_vero = Tabla_verosimilitud.tablas_verosimilitud(analisis)
        tbls_frec = Tabla_frecuencia.tablas_frecuencia(analisis)
        naive = Naive_bayes(table, analisis.nombre_clase, tbls_vero)
        if request.method == 'POST':
            # El usuario ya envió el registro propuesto para realizar la clasificación
            registro = {}
            prefijo = "reng_prop_" # El prefijo para los imputs del template 'registro_propuesto'
            for atr in analisis.atr_clase:
                nombre = atr['name']
                if nombre != analisis.nombre_clase:
                    valor = request.form[f'{prefijo}{nombre}']
                    if valor:
                        # La clase no la obtendremos en los datos ya que es el valor que intentamos predecir
                        registro[nombre] = valor
            # Ejecutamos el algorimo naive_bayes
            probabilidades, conj_multiplos, mas_probable = naive.ejecuta(registro)
            return render_template('algoritmos_predictores/naive_bayes.html', tbls_frec=tbls_frec, tbls_vero=tbls_vero, naive=naive,
             probabilidades = probabilidades, conj_multiplos = conj_multiplos, mas_probable = mas_probable, ejec = True, registro = registro)
        else:
            return render_template('algoritmos_predictores/naive_bayes.html', tbls_frec=tbls_frec, tbls_vero=tbls_vero, naive=naive, ejec = False)
        
    else:
        return redirect(url_for('upload_form'))
