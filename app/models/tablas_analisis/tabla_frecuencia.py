import app.models.analisis as anal
from app.models.tablas_analisis.tabla_analisis import Tabla_analisis
from app.models.table import Table

class Tabla_frecuencia(Tabla_analisis):
    def __init__(self, tabla, clase, atri):
        super().__init__(tabla, clase, atri)
        self.tabla_frecuencia = self.obtiene_tabla_frecuencia()
        self.tabla_frecuencia_inv = self.inv_tabla_frec()
        self.num_columnas = self.obtiene_num_col() # También lo podemos considerar como número de posibles valores para la clase
        self.num_filas = self.obtiene_num_fil() # También lo podemos considerar como número de posibles valores para el atributo
        self.reglas = self.obtiene_reglas()

    def obtiene_tabla_frecuencia(self):
        tabla_frec = None # En caso de no poder obtener la tabla de frecuencia ni las reglas devolvemos None
        if (self.analisis_clase.tipo in self.tipos_categoricos 
        and self.analisis_atri.tipo in self.tipos_categoricos):
            tabla_frec = {}
            for reg in self.analisis_clase.tabla_dep: # Cambiar y utlizar tabla_dep_tot. PendientesSaul!!!
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


    # Invertiremos la tabla de frecuencia
    def inv_tabla_frec(self):
        tabla_frec = None # En caso de no poder obtener la tabla de frecuencia ni las reglas devolvemos None
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
        if self.tabla_frecuencia: # Es necesario que ya esté cargada la tabla de frecuencia
            if num_col == None and num_fila == None:
                # Obtenemos el numero total de instancias
                for col in self.tabla_frecuencia:
                    for registro in col:
                        total += registro
            if num_col == None and num_fila != None:
                if num_fila < self.num_filas:
                    # Obtenemos el total de instancias para el número de fila
                    for col in self.tabla_frecuencia:
                        total += col[num_fila]
            if num_col != None and num_fila == None:
                if num_col < self.num_columnas:
                    # Obtenemos el total de instancias para el número de columna
                    col = self.tabla_frecuencia[num_col]
                    for registro in col:
                        total += registro
        return total
            


    def obtiene_num_col(self):
        tamaño = 0
        if self.tabla_frecuencia:
            tamaño = len(self.tabla_frecuencia)
        return tamaño


    def obtiene_num_fil(self):
        tamaño = 0
        if self.tabla_frecuencia_inv:
            tamaño = len(self.tabla_frecuencia_inv)
        return tamaño


    def obtiene_reglas(self):
        if self.tabla_frecuencia_inv:
            reglas = [] # Lista de string con todas las reglas
            errores = [] # La lista de errores 
            error_total = 0
            total_instancias = 0
            for valor, fila in self.tabla_frecuencia_inv.items():
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
            return None # Si no hay tabla de frecuencia, no hay reglas

    
    @staticmethod
    def tablas_frecuencia(analisis: anal.Analisis, clase):
        if type(analisis.tabla) is Table:
            # Si el objeto analisis ya ha cargado la tabla de manera exitosa seguimos con el procedimiento
            tbls_frec = []
            reglas = {} # Las reglas aplicadas a las tablas de frecuencia, tendrá los siguientes elementos anidados
            # Atributo -> {Reglas, Errores, Error Total} Atributo: String, Reglas: String, Errores: Decimal, Error Total: Decimal
            atributos = list(analisis.tabla.properties.propsAttr)
            atributos.remove(analisis.clase) # Eliminamos la clase de la lista de atributos para evitar que itere sobre si misma
            # Crearemos una tabla de frecuencia por cada atributo categórico en la tabla
            for atri in atributos:
                analisis_atri = anal.AnalisisUni(analisis.tabla, atri, clase)
                tbl = Tabla_frecuencia(analisis_atri.tabla, clase, atri)
                if tbl.tabla_frecuencia:
                    # Si podemos obtener una tabla de frecuencia entre el atributo y la clase la agregamos a la lista de tablas
                    tbls_frec.append(tbl)
                    # Agregamos las reglas al diccionario
                    reglas[analisis_atri.nombre] = tbl.reglas
            return tbls_frec
        else:
            # Si la tabla aún no está cargada o no es del tipo correcto devolvemos None
            return None