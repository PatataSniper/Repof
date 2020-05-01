from math import sqrt
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon
from io import BytesIO
import xml.etree.ElementTree as ET
import copy

class Analisis:
    def __init__(self, tabla):
        self.tabla = copy.deepcopy(tabla)
        self.tipos_numericos = ("integer", "number", "float")
        self.tipos_categoricos = ("enum", "boolean", "categorical")
        self.tipos_clase = ("enum", "categorical")
        self.tipos_numericos_itr = (type(int()), type(float()))
        self.tipos_categoricos_itr = (type(""),)
        self.atr_clase = self.obtiene_atr_clase()
        self.tabla_dep = self.obtiene_tabla_dep() # Tabla depurada (sin registros con valores faltantes o fuera del dominio)
        self.tabla_remp = self.obtiene_tabla_remp() # Tabla reemplazada (con los valores faltantes reemplazados)


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
        for item in temp:
            if item['name'] == atributo['name']:
                break
            indice = indice + 1
        return indice


    def obtiene_dominio(self, atributo):
        if(not atributo['type'] in self.tipos_categoricos):
            return None
        if(atributo['type'] == 'boolean'):
            # Los atributos boolean, aunque sabemos que son categoricos, no tendrán clases como tal
            return ('False', 'True')
        # Indice del atributo especificado
        indice = self.obtiene_index(atributo)
        return tuple(self.tabla.properties.propsAttr[indice]['classes'])


    # Obtenemos un atributo por nombre
    def obtiene_atributo(self, nombre):
        for atr in self.tabla.properties.propsAttr:
            if atr['name'] == nombre:
                return atr # Encontramos el atributo, lo devolvemos
        return None # No encontramos el atributo, devolvemos none


    def obtiene_tabla_dep():
        pass
        


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
        # Tabla con valores depurados (sin faltantes ni fuera de domino)
        self.tabla_dep = self.depura_tabla()
        # Estadísticas básicas
        self.media = self.obtiene_media()
        self.mediana = self.obtiene_mediana()
        self.moda = self.obtiene_moda()
        self.desviacion_estandar = self.obtiene_desviacion()


    def depura_tabla(self):
        # Eliminamos de la lista de registros los registros con valores vacíos
        aux = list(self.tabla.data)
        for vacio in self.faltantes:
            aux.remove(vacio)
        # Eliminamos de la lista los registros con valores fuera de dominio
        for fuera in self.fuera_dominio:
            if fuera in aux:
                aux.remove(fuera)
        return aux


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
        for reg in self.tabla_dep:
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
    def obtiene_datos_isto(self):
        datos = [] # Número de datos para cada clase encontrada en el atributo
        pos_val = 0 # El número de posibles valores
        for reg in self.tabla_dep:
            clase = reg[self.indice]
            if clase in self.dominio:
                if not clase in datos:
                    pos_val += 1
                datos.append(clase)
        return datos, pos_val

    
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
        # Código obtenido del siguiente enlace
        # https://matplotlib.org/3.2.1/gallery/statistics/hist.html?highlight=isto
        datos, pos_val = self.obtiene_datos_isto()
        fig, axs = plt.subplots(1, 1, sharey=True, tight_layout=True)

        # Podemos configurar el número de contenedores por medio del atributo 'bins'
        axs.hist(datos, pos_val)
        plt.show()


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
        # Obtenemos el valor mínimo y máximo para el atributo dado
        minimo = min(self.tabla_dep, key=lambda x: x[self.indice])
        minimo = minimo[self.indice]
        maximo = max(self.tabla_dep, key=lambda x: x[self.indice])
        maximo = maximo[self.indice]
        return round((maximo + minimo) / 2, 2)


    def obtiene_moda(self):
        # La moda solo la obtendremos para valores numéricos
        if(not self.atributo['type'] in str(self.tipos_numericos)):
            return None
        frecuencias = {}
        for registro in self.tabla_dep:
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
        for reg in self.tabla_dep:
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
    def __init__(self, tabla, an1, an2):
        super().__init__(tabla)
        self.analisis_1 = an1 # El objeto de analisis univariable uno
        self.analisis_2 = an2 # El objeto de analisis univariable dos


# class Zero_R():
#     def __init__(self, tabla, clase, Analisis):
#         self.tablas_frecuencia = Tabla_frecuencias.tablas_frecuencia(Analisis, clase)
#         self


class Tabla_frecuencias(Analisis):
    def __init__(self, tabla, clase, atri):
        super().__init__(tabla)
        self.clase = clase # La clase con la cual se realizará la tabla de frecuencias
        self.atri = atri # El atributo a utilizar en la tabla de frecuencias
        self.analisis_clase = AnalisisUni(self.tabla, self.clase) # Creamos un objeto de analisis para la clase
        self.analisis_atri = AnalisisUni(self.tabla, self.atri) # Creamos un objeto de analisis para la clase
        self.tabla_frecuencias = self.obtiene_tabla_frecuencias()
        self.tabla_frecuencias_inv = self.inv_tabla_frec()
        self.num_columnas = self.obtiene_num_col()
        self.num_filas = self.obtiene_num_fil()
        self.reglas = self.obtiene_reglas()

    def obtiene_tabla_frecuencias(self):
        tabla_frec = None # En caso de no poder obtener la tabla de frecuencias ni las reglas devolvemos None
        if (self.analisis_clase.tipo in self.tipos_categoricos 
        and self.analisis_atri.tipo in self.tipos_categoricos):
            tabla_frec = {}
            for reg in self.analisis_clase.tabla_dep:
                val_clase = reg[self.analisis_clase.indice] # El valor de clase para la instancia actual, en el diccionario
                # actuará como llave
                val_clase = str(val_clase)
                val_atr = reg[self.analisis_atri.indice] # El valor del atributo para la instancia actual, en el segundo nivel de
                # diccionarios actuará como llave
                val_atr = str(val_atr)
                if not val_clase in tabla_frec:
                    tabla_frec[val_clase] = {}
                if not val_atr in tabla_frec[val_clase]:
                    tabla_frec[val_clase][val_atr] = 0
                tabla_frec[val_clase][val_atr] += 1

        # Devolvemos un diccionario de diccionarios de enteros, ejemplo:
        #               -------------------------------------------
        #               |                  PLAY                   |
        #               |-----------------------------------------|
        #               |     SI              |       NO          |
        # --------------|-----------------------------------------|
        # |    Sunny    |       2             |         3         |
        # --------------|-----------------------------------------|
        # |   Overcast  |       4             |         0         |
        # --------------|-----------------------------------------|
        return tabla_frec


    # Invertiremos la tabla de frecuencias
    def inv_tabla_frec(self):
        tabla_frec = None # En caso de no poder obtener la tabla de frecuencias ni las reglas devolvemos None
        if (self.analisis_clase.tipo in self.tipos_categoricos 
        and self.analisis_atri.tipo in self.tipos_categoricos):
            tabla_frec = {}
            for reg in self.analisis_clase.tabla_dep:
                val_clase = reg[self.analisis_clase.indice] # El valor de clase para la instancia actual, en el diccionario
                # actuará como llave
                val_clase = str(val_clase)
                val_atr = reg[self.analisis_atri.indice] # El valor del atributo para la instancia actual, en el segundo nivel de
                # diccionarios actuará como llave
                val_atr = str(val_atr)
                if not val_atr in tabla_frec:
                    tabla_frec[val_atr] = {}
                if not val_clase in tabla_frec[val_atr]:
                    tabla_frec[val_atr][val_clase] = 0
                tabla_frec[val_atr][val_clase] += 1

        # Devolvemos un diccionario de diccionarios de enteros, ejemplo:
        #               -------------------------------------------
        #               |                  PLAY                   |
        #               |-----------------------------------------|
        #               |     SI              |       NO          |
        # --------------|-----------------------------------------|
        # |    Sunny    |       2             |         3         |
        # --------------|-----------------------------------------|
        # |   Overcast  |       4             |         0         |
        # --------------|-----------------------------------------|
        return tabla_frec


    #Función para obtener el total de instancias, tambien se puede calcular por columna o por fila
    def obtiene_total_instancias(self, num_col = None, num_fila = None):
        total = 0
        if self.tabla_frecuencias: # Es necesario que ya esté cargada la tabla de frecuencias
            if num_col == None and num_fila == None:
                # Obtenemos el numero total de instancias
                for col in self.tabla_frecuencias:
                    for registro in col:
                        total += registro
            if num_col == None and num_fila != None:
                if num_fila < self.num_filas:
                    # Obtenemos el total de instancias para el número de fila
                    for col in self.tabla_frecuencias:
                        total += col[num_fila]
            if num_col != None and num_fila == None:
                if num_col < self.num_columnas:
                    # Obtenemos el total de instancias para el número de columna
                    col = self.tabla_frecuencias[num_col]
                    for registro in col:
                        total += registro
        return total
            


    def obtiene_num_col(self):
        tamaño = 0
        if self.tabla_frecuencias:
            tamaño = len(self.tabla_frecuencias)
        return tamaño


    def obtiene_num_fil(self):
        tamaño = 0
        if self.tabla_frecuencias_inv:
            tamaño = len(self.tabla_frecuencias_inv)
        return tamaño


    def obtiene_reglas(self):
        if self.tabla_frecuencias_inv:
            reglas = [] # Lista de string con todas las reglas
            errores = [] # La lista de errores 
            error_total = 0
            total_instancias = 0
            for valor, fila in self.tabla_frecuencias_inv.items():
                # Obtenemos el valor máximo para la fila actual
                maximo_key = max(fila.keys(), key = (lambda k: fila[k]))
                maximo = fila[maximo_key]
                reglas.append(f"{valor} -> {maximo_key}")
                total_instancias_fila = 0
                for elem in fila.values():
                    total_instancias_fila += int(elem)
                error = total_instancias_fila - maximo
                errores.append(f"{error}/{total_instancias_fila}")
                # Sumamos el error total
                error_total += error
                # Sumamos las instancias totales
                total_instancias += total_instancias_fila
            error_total = f"{error_total}/{total_instancias}"
            return reglas, errores, error_total
        else:
            return None # Si no hay tabla de frecuencias, no hay reglas

    
    @staticmethod
    def tablas_frecuencia(analisis: Analisis, clase):
        tbls_frec = []
        reglas = {} # Las reglas aplicadas a las tablas de frecuencias, tendrá los siguientes elementos anidados
        # Atributo -> {Reglas, Errores, Error Total} Atributo: String, Reglas: String, Errores: Decimal, Error Total: Decimal
        atributos = list(analisis.tabla.properties.propsAttr)
        atributos.remove(clase) # Eliminamos la clase de la lista de atributos para evitar que itere sobre si misma
        # Crearemos una tabla de frecuencia por cada atributo categórico en la tabla
        for atri in atributos:
            analisis_atri = AnalisisUni(analisis.tabla, atri)
            tbl = Tabla_frecuencias(analisis_atri.tabla, clase, atri)
            if tbl.tabla_frecuencias:
                # Si podemos obtener una tabla de frecuencias entre el atributo y la clase la agregamos a la lista de tablas
                tbls_frec.append(tbl)
                # Agregamos las reglas al diccionario
                reglas[analisis_atri.nombre] = tbl.reglas
        return tbls_frec