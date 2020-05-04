import app.models.analisis as anal
import copy
from app.models.tablas_analisis.tabla_analisis import Tabla_analisis
from app.models.table import Table

class Tabla_verosimilitud(Tabla_analisis):
    def __init__(self, tabla, clase, atri):
        super().__init__(tabla, clase, atri)
        self.tabla_vero, self.tabla_vero_show = self.obt_tbl_vero()
        self.tabla_vero_inv = self.inv_tbl_vero() # Se invierte la tabla de verosimilitud (atributo pasa a las columnas y clase a los renglones) para
        # facilitar el despliegue al usuario y dar flexibilidad
        self.num_columnas = self.obtiene_num_col() # También lo podemos considerar como número de posibles valores para la clase
        self.num_filas = self.obtiene_num_fil() # También lo podemos considerar como número de posibles valores para el atributo


    def obt_tbl_vero(self):
        tabla_vero = None # En caso de no poder obtener la tabla de verosimilitud devolvemos None
        tabla_vero_show = None
        if (self.analisis_clase.tipo in self.tipos_categoricos
        and self.analisis_atri.tipo in self.tipos_categoricos):
            tabla_vero = {}
            for reg in self.analisis_clase.tabla_dep: # Cambiar y utlizar tabla_dep_tot. PendientesSaul!!!
                val_clase = reg[self.analisis_clase.indice] # El valor de clase para la instancia actual, en el diccionario
                # actuará como llave
                val_clase = str(val_clase) # Convertimos a clase para procesar unos y ceros como categóricos y no como numéricos
                val_atr = reg[self.analisis_atri.indice] # El valor del atributo para la instancia actual, en el segundo nivel de
                # diccionarios actuará como llave
                val_atr = str(val_atr) # Convertimos a clase para procesar unos y ceros como categóricos y no como numéricos
                if not val_clase in tabla_vero:
                    tabla_vero[val_clase] = {}
                if not val_atr in tabla_vero[val_clase]:
                    tabla_vero[val_clase][val_atr] = 0
                tabla_vero[val_clase][val_atr] += 1
            tabla_vero_show = copy.deepcopy(tabla_vero)
            for col_ll in tabla_vero:
                total_ins = 0 # El total de instancias para esta columna (valor de clase)
                for reg_v in tabla_vero[col_ll].values():
                    total_ins += reg_v
                # En este punto ya tenemos el total de instancias
                for reg_ll in tabla_vero[col_ll]:
                    val_num = tabla_vero[col_ll][reg_ll] # El numero de instancias en entero
                    tabla_vero_show[col_ll][reg_ll] = f'{val_num}/{total_ins}' # Almancenamos en string el número de instancias para
                    # el atributo entre el número de instancias totales para la clase. Ejemplo "5/12"
                    tabla_vero[col_ll][reg_ll] = val_num/total_ins # Almacenamos en valor numerico el mismo dato
        return tabla_vero, tabla_vero_show


    def inv_tbl_vero(self):
        return 'no implementado'


    def obtiene_num_col(self):
        tamaño = 0
        if self.tabla_vero:
            tamaño = len(self.tabla_vero)
        return tamaño


    def obtiene_num_fil(self):
        tamaño = 0
        if self.tabla_vero_inv:
            tamaño = len(self.tabla_vero_inv)
        return tamaño


    @staticmethod
    def tablas_verosimilitud(analisis: anal.Analisis, clase):
        if type(analisis.tabla) is Table:
            # Si el objeto analisis ya ha cargado la tabla de manera exitosa seguimos con el procedimiento
            tbls_vero = {}
            atributos = list(analisis.tabla.properties.propsAttr)
            atributos.remove(analisis.clase) # Eliminamos la clase de la lista de atributos para evitar que itere sobre si misma
            # Crearemos una tabla de frecuencia por cada atributo categórico en la tabla
            for atri in atributos:
                analisis_atri = anal.AnalisisUni(analisis.tabla, atri, clase)
                tbl = Tabla_verosimilitud(analisis_atri.tabla, clase, atri)
                if tbl.tabla_vero:
                    # Si podemos obtener una tabla de frecuencia entre el atributo y la clase la agregamos a la lista de tablas
                    tbls_vero[analisis_atri.nombre] = tbl
            return tbls_vero
        else:
            # Si la tabla aún no está cargada o no es del tipo correcto devolvemos None
            return None
