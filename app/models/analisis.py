from math import sqrt
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon
from io import BytesIO
import xml.etree.ElementTree as ET

class Analisis:
    def __init__(self, tabla):
        self.tabla = tabla
        self.tipos_numericos = ("integer", "number", "float")
        self.tipos_categoricos = ("enum", "boolean", "categorical")
        self.tipos_clase = ("enum", "categorical")
        self.tipos_numericos_itr = (type(int()), type(float()))
        self.tipos_categoricos_itr = (type(""),)
        self.atr_clase = self.obtiene_atr_clase()


    # Obtenemos los atributos categóricos que podríamos utilizar como clases
    def obtiene_atr_clase(self):
        atributos_clase = []
        for atr in self.tabla.properties.propsAttr:
            if atr['type'] in self.tipos_clase:
                # Sabemos que el atributo actual contiene clases, lo agregamos a la lista
                atributos_clase.append(atr)
        # Si la lista contiene elementos la devolvemos, si no, devolvemos None
        return atributos_clase if atributos_clase != [] else None

    
    # Obtenemos el indice del atributo recibido como parametro, en caso de existir
    def obtiene_index(self, atributo):
        temp = list(self.tabla.properties.props['attributes'])
        indice = 0
        nombre_atr = atributo['name']
        for item in temp:
            if item['name'] == atributo['name']:
                break
            indice = indice + 1
        return indice


    def obtiene_dominio(self, atributo):
        if(not atributo['type'] in self.tipos_categoricos):
            return None
        # Indice del atributo especificado
        indice = self.obtiene_index(atributo)
        return tuple(self.tabla.properties.propsAttr[indice]['classes'])


class AnalisisUni(Analisis):
    def __init__(self, tabla, atributo):
        super().__init__(tabla)
        # Información atributo a analizar del conjunto de datos
        self.atributo = atributo
        self.indice = self.obtiene_index(atributo)
        self.nombre = atributo['name']
        self.tipo = atributo['type']
        self.dominio = self.obtiene_dominio(self.atributo)
        self.datos_crud = self.obtiene_datos_crudos()
        # Estadísticas de registros con datos faltantes
        self.faltantes = self.val_faltantes()
        self.cant_faltantes = len(self.faltantes)
        self.porc_faltantes = f'{round(self.cant_faltantes * 100 / len(tabla.data), 2)}%'
        # Estadísticas de registros con datos fuera del dominio
        self.fuera_dominio = self.val_fuera_dominio()
        self.cant_fuera_dominio = len(self.fuera_dominio)
        self.porc_fuera_dominio = f'{round(self.cant_fuera_dominio * 100 / len(tabla.data), 2)}%'
        # Estadísticas básicas
        self.media = self.obtiene_media()
        self.mediana = self.obtiene_mediana()
        self.moda = self.obtiene_moda()
        self.desviacion_estandar = self.obtiene_desviacion()


    # Obtención de datos crudos, los devolveremos en una lista
    def obtiene_datos_crudos(self):
        datos = []
        for reg in self.tabla.data:
            valor = reg[self.indice]
            datos.append(valor if valor else 0)
        return datos


    # Obtención de datos discrimiados por clase, los devolveremos en un diccionario
    # o en una lista, dependiendo de lo que se necesite
    def obtiene_datos_disc(self, clase, regresa_tipo = 'lista'):
        # Obtenemos el index de la clase en el conjunto de datos
        index_clase = self.obtiene_index(clase)
        datos = {}
        etiquetas = []
        # Obtenemos el dominio de la clase especificada
        dominio_clase = self.obtiene_dominio(clase)
        for reg in self.tabla.data:
            valor = reg[self.indice]
            clase = reg[index_clase]
            # No incuiremos en el conjunto de datos los que tienen un valor de clase fuera del dominio
            if clase in dominio_clase:
                if not clase in datos:
                    datos[f'{clase}'] = [] # Inicializamos la lista en el diccionario
                    etiquetas.append(clase) # Agregamos la etiqueta nueva
                datos[f'{clase}'].append(reg[self.indice])
        if regresa_tipo == 'diccionario':
            # La llamada espera un diccionario de listas
            return datos, etiquetas
        elif regresa_tipo == 'lista':
            # La llamada espera una lista de listas
            datos_lista = []
            for entrada in datos.values():
                datos_lista.append(entrada)
            return datos_lista, etiquetas
        # Cualquier valor para regresa_tipo no válido devolverá None
        return None


    # Obtención de datos clasificados para presentación en istográma, esto es, número de
    # instancias por clase (solo válido para atributos categóricos)
    # los devolveremos en un diccionario o en una lista
    # dependiendo de lo que se necesite
    def obtiene_datos_isto(self, regresa_tipo = 'lista'):
        datos = {} # Número de datos para cada clase encontrada en el atributo
        etiquetas = []
        for reg in self.tabla.data:
            clase = reg[self.indice]
            # No incluiremos en el conjunto de datos lo que tienen un valor de clase fuera del dominio
            if clase in self.dominio:
                if not clase in datos:
                    datos[f'{clase}'] = 0 # Inicializamos la lista en el diccionario
                    etiquetas.append(clase) # Agregamos la etiqueta nueva
                datos[f'{clase}'] += 1 # Aumentamos el número de instancias para esta clase
        if regresa_tipo == 'diccionario':
            # La llamada espera un diccionario de números
            return datos, etiquetas
        elif regresa_tipo == 'lista':
            # La llamada espera una lista de números
            datos_lista = []
            for entrada in datos.values():
                datos_lista.append(entrada)
            return datos_lista, etiquetas
        # Cualquier valor para regresa_tipo no válido devolverá None
        return None
                    

    
    def muestra_box_plot(self, clase):
        # El box plot solamente podrá ser creado para atributos numéricos
        if(not self.atributo['type'] in str(self.tipos_numericos)):
            return None
        datos = [] # Los datos que utilizaremos para llenar el box plot
        fig, axs = plt.subplots() # Creamos un subplot y una figura
        if clase:
            # Diccionario con los datos discriminado por la clase especificada
            datos, etiquetas = self.obtiene_datos_disc(clase, 'lista')
            axs.boxplot(datos, labels = etiquetas) # Cargamos los datos crudos en el box plot
        else:
            datos = self.datos_crud
            axs.boxplot(datos) # Cargamos los datos crudos en el box plot
        axs.set_title(f'Box plot - {self.nombre}')
        plt.show()


    def muestra_istograma(self):
        # El istograma solamente podrá ser creado para atributos categóricos
        if (not self.atributo['type'] in self.tipos_categoricos):
            return None
        plt.figure()
        # Código obtenido del siguiente enlace
        # https://matplotlib.org/3.2.1/gallery/user_interfaces/svg_histogram_sgskip.html#sphx-glr-gallery-user-interfaces-svg-histogram-sgskip-py
        datos, etiquetas = self.obtiene_datos_isto()
        istograma = plt.hist(datos, label = etiquetas)
        containers = istograma[-1]
        leyenda = plt.legend(frameon = False)
        plt.title("Desde un navegador, has clic en la leyenda\n"
        "para activar el istograma correspondiente.")

        # Agregamos ids a los objetos svg's que vamos a modificar
        hist_patches = {}
        for ic, c in enumerate(containers):
            hist_patches['hist_%d' % ic] = []
            for il, element in enumerate(c):
                element.set_gid('hist_%d_patch_%d' % (ic, il))
                hist_patches['hist_%d' % ic].append('hist_%d_patch_%d' % (ic, il))

        # Configuramos los ids para las leyendas
        for i, t in enumerate(leyenda.get_patches()):
            t.set_gid('leg_patch_%d' % i)

        # Configuramos los ids para los textos
        for i, t in enumerate(leyenda.get_texts()):
            t.set_gid('leg_text_%d' % i)

        # Guardamos la imagen svg en un archivo
        f = BytesIO()
        plt.savefig(f, format="svg")

        # Create XML tree from the SVG file.
        tree, xmlid = ET.XMLID(f.getvalue())


        # --- Add interactivity ---

        # Add attributes to the patch objects.
        for i, t in enumerate(leyenda.get_patches()):
            el = xmlid['leg_patch_%d' % i]
            el.set('cursor', 'pointer')
            el.set('onclick', "toggle_hist(this)")

        # Add attributes to the text objects.
        for i, t in enumerate(leyenda.get_texts()):
            el = xmlid['leg_text_%d' % i]
            el.set('cursor', 'pointer')
            el.set('onclick', "toggle_hist(this)")
        


    def obtiene_media(self):
        # La media solo la obtendremos para valores numéricos
        if( not self.atributo['type'] in str(self.tipos_numericos)):
            return None

        total = 0
        n_instancias =  len(self.tabla.data)

        for reg in self.tabla.data:
            if reg[self.indice]:
                total = total + int(reg[self.indice])
        
        return round(total / n_instancias, 2)


    def obtiene_mediana(self):
        # La mediana solo la obtendremos para valores numéricos
        if( not self.atributo['type'] in str(self.tipos_numericos)):
            return None
        # Necesitamos eliminar de la lista de registros los registros con valores vacíos
        aux = self.tabla.data
        for vacio in self.faltantes:
            aux.remove(vacio)
        # Obtenemos el valor mínimo y máximo para el atributo dado
        minimo = min(aux, key=lambda x: x[self.indice])
        minimo = minimo[self.indice]
        maximo = max(aux, key=lambda x: x[self.indice])
        maximo = maximo[self.indice]
        return round((maximo + minimo) / 2, 2)


    def obtiene_moda(self):
        # La moda solo la obtendremos para valores numéricos
        if(not self.atributo['type'] in str(self.tipos_numericos)):
            return None
        frecuencias = {}
        for registro in self.tabla.data:
            if(registro[self.indice] not in frecuencias.keys()):
                # Si el diccionario aún no tiene esta cantidad agregada la agregamos
                frecuencias[f'{registro[self.indice]}'] = 0
            frecuencias[f'{registro[self.indice]}'] += 1
        # Devolvemos el valor con mas instancias en el conjunton de datos
        return max(frecuencias)


    def obtiene_desviacion(self):
        # La desviación estandar solo la obtendremos para valores numéricos
        if (not self.tipo in str(self.tipos_numericos)):
            return None
        res = 0
        for reg in self.tabla.data:
            res += pow(reg[self.indice] - self.media, 2)
        # Dividimos la suma de las desviaciones entre el numero de instancias menos uno
        # (se trata de una muestra) y obtenemos raiz cuadrada
        res = res / len(self.tabla.data) - 1
        res = sqrt(res)
        return round(res, 2)


    # Método que recivirá un string con el nombre de un atributo, 
    # obtendrá las instancias con valores faltantes para dicho atributo en 
    # el conjunto de datos y devolverá un diccionario con dichas instancias
    def val_faltantes(self):
        # Obtenemos los valores faltantes en el indice encontrado
        faltantes = []
        for reg in self.tabla.data:
            # Iteramos en cada uno de los registros del conjunto de datos
            if not reg[self.indice]:
                # Si el dato está vacío agregamos todo el registro al arreglo de valores faltantes
                faltantes.append(reg)
        return faltantes


    def val_fuera_dominio(self):
        # Obtenemos el tipo de dato, el rango en caso de tratarse de un atributo numérico
        # y el dominio en caso de tratarse de uno categórico, obtendremos esta información de 
        # tabla.properties.propsAttr
        fuera_dominio = []
        if (self.tipo in str(self.tipos_numericos)):
            # Nos encontramos con un atributo numérico
            for reg in self.tabla.data:
                # Checaremos que cada instancia del atributo sea del tipo requerido
                if(not type(reg[self.indice]) in self.tipos_numericos_itr):
                    # El dato no es del tipo correcto, lo agregamos a la lista de
                    # registros fuera del dominio
                    fuera_dominio.append(reg)
                # Checaremos que cada instancia se encuentre dentro del rango permitido
                # PendientesSaul!!!
                
        elif (self.tipo in str(self.tipos_categoricos)):
            # Nos encontramos con un atributo categórico
            # Checaremos que el valor se ecuentre dentro del dominio permitido
            for reg in self.tabla.data:
                # Checamos que cada instancia del atributo sea del tipo requerido
                if(not type(reg[self.indice]) in self.tipos_categoricos_itr):
                    # El dato no se del tipo correcto
                    fuera_dominio.append(reg)
                else:
                    if(not reg[self.indice] in str(self.dominio)):
                        # El valor no se encuentra dentro del dominio
                        fuera_dominio.append(reg)
        # Devolveremos la lista de instancias con valores fuera del dominio
        return fuera_dominio            


class AnalisisBi(Analisis):
    def __init__(self, tabla):
        super().__init__(tabla)
    