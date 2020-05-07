import app.models.analisis as anal
import copy
import app.utils as utils


class Naive_bayes(anal.Analisis):
    def __init__(self, tabla, clase, tbls_vero, estado = "Numérico"):
        super().__init__(tabla, clase)
        self.estado = estado # El estado de este algoritmo (numérico, categórico)
        # Clasificaremos los registros dependiendo de la clase
        self.por_clase = self.reg_por_clase() # Obtendremos los registros de la tabla separados por clase
        self.resu_est_por_clase = self.obt_resu_por_clase() # Obtenemos el resumen estadístico para cada atribuo dividido por valor de clase
        self.tablas_vero = tbls_vero #Las tablas de verosimilitud para el conjunto de datos (atributos categóricos)
        # self.conj_analisis = self.analiza_atrib() # Creamos un analisis univariable para cada atributo en la tabla
        self.imprime_info() # Imprimimos en consola para hacer pruebas

    
    def ejecuta(self, instancia):
        if instancia and len(instancia) > 0:
            prob_clases = {} # (clase, probabilidad) Ejemplo {'yes': 0.034, 'no': 0.012}
            conj_multiplos = {} # (clase, multiplos) Ejemplo {'yes': (1/2, 3/4)} # El conjunto de multiplos para desplegarlos al usuario
            posibles_valores = self.por_clase.keys() # Uno de estos valores será el resultado de nuestro algoritmo
            for valor_clase in posibles_valores:
                probabilidad = 1
                conj_multiplos[valor_clase] = []
                for atr in instancia:
                    val_atr = instancia[atr] # El valor del atributo en la instancia introducida por el usuario
                    tabla_v = self.tablas_vero[atr].tabla_vero # Accedemos a la tabla de verosimilitud para este atributo
                    tabla_vs = self.tablas_vero[atr].tabla_vero_show # Accedemos a la tabla de verosimilitud con los strigs de las fracciones
                    conj_multiplos[valor_clase].append(tabla_vs[valor_clase][val_atr])
                    probabilidad = probabilidad * tabla_v[valor_clase][val_atr] # Obtenemos la probabilidad total para esta clase multiplicando
                    # las probabilidades de cada atributo
                prob_clases[valor_clase] = probabilidad
            mas_probable = max(prob_clases.keys(), key = (lambda k: prob_clases[k]))
            # Normalizamos las probabilidades para el rápido entendimiento del usuario
            aux = copy.deepcopy(prob_clases)
            for p in prob_clases:
                divisor = 0
                for p2 in prob_clases:
                    divisor += prob_clases[p2]
                aux[p] = round(aux[p] / divisor, 3)
            return aux, conj_multiplos, mas_probable
        else: return None
            


    def reg_por_clase(self):
        separados = {}
        for i in range(len(self.tabla.data)):
            vector = self.tabla.data[i]
            valor_clase = vector[self.index_clase]
            if valor_clase not in separados:
                separados[valor_clase] = []
            separados[valor_clase].append(vector)
        return separados


    def imprime_info(self):
        # Función de prueba que imprimirá la tabla separada por clase en la consola
        print('Registros por clase')
        for llave_clase in self.por_clase:
            print(llave_clase)
            for renglon in self.por_clase[llave_clase]:
                print(renglon)
        print('Medias y desviaciones estandar para atributos numéricos')
        for datos in self.resu_est_por_clase:
            print(datos) # (media, desviación estandar)


    def recopila_dataset(self, dataset):
        # Devolveremos un diccionario de tuplas con la sig. info. (media, desviación estandar) Para un conjunto de datos dado
        # Será necesario que el dataset solamente contenga atributos numéricos
        estadisiticas = [(utils.media(columna), utils.desviacion_est(columna), len(columna)) for columna in zip(*dataset)]
        del(estadisiticas[-1]) # Eliminamos el último elemento el cual se considera la clase. Hacer dinámico PendientesSaul!!!
        return estadisiticas


    def obt_resu_por_clase(self):
        resumen_estadistico = {}
        data = self.por_clase # La tabla de registros separados por clase
        for valor_clase, registros in data.items():
            resumen_estadistico[valor_clase] = self.recopila_dataset(registros)
        return resumen_estadistico