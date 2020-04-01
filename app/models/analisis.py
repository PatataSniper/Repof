class Analisis:
    def __init__(self, tabla):
        self.tabla = tabla
        pass

    
    # Obtenemos el indice del atributo recibido como parametro, en caso de existir
    def obtiene_index(self, atributo):
        temp = list(self.tabla.properties.props['attributes'])
        indice = 0
        for item in temp:
            if item['name'] == atributo['name']:
                break
            indice = indice + 1
        return indice


class AnalisisUni(Analisis):
    def __init__(self, tabla, atributo):
        super().__init__(tabla)
        self.atributo = atributo
        self.nombre = atributo['name']
        self.tipo = atributo['type']
        self.faltantes = self.val_faltantes(atributo)
        self.cant_faltantes = len(self.faltantes)
        self.porc_faltantes = f'{round(self.cant_faltantes * 100 / len(tabla.data), 2)}%'
        self.media = self.obtiene_media(atributo)
        self.mediana = self.obtiene_mediana(atributo)
        self.moda = self.obtiene_moda(atributo)
        self.fuera_dominio = self.val_fuera_dominio(atributo)


    def obtiene_media(self, atributo):
        # La media solo la obtendremos para valores numéricos
        if(atributo['type'] != 'number' and atributo['type'] != 'int'):
            return None

        total = 0
        n_instancias =  len(self.tabla.data)
        indice = self.obtiene_index(atributo)

        for reg in self.tabla.data:
            if reg[indice]:
                total = total + int(reg[indice])
        
        return round(total / n_instancias, 2)



    def obtiene_mediana(self, atributo):
        # La mediana solo la obtendremos para valores numéricos
        if(atributo['type'] != 'number' and atributo['type'] != 'int'):
            return None
        indice = self.obtiene_index(atributo)
        # Necesitamos eliminar de la lista de registros los registros con valores vacíos
        aux = self.tabla.data
        for vacio in self.faltantes:
            aux.remove(vacio)
        # Obtenemos el valor mínimo y máximo para el atributo dado
        minimo = min(aux, key=lambda x: x[indice])
        minimo = minimo[indice]
        maximo = max(aux, key=lambda x: x[indice])
        maximo = maximo[indice]
        return round((maximo + minimo) / 2, 2)


    def obtiene_moda(self, atributo):
        # La moda solo la obtendremos para valores numéricos
        if(atributo['type'] != 'number' and atributo['type'] != 'int'):
            return None
        # Obtenemos el indice del atributo recibido como parametro, en caso de existir
        temp = list(self.tabla.properties.props['attributes'])
        indice = self.obtiene_index(atributo)
        frecuencias = {}
        for registro in self.tabla.data:
            if(registro[indice] not in frecuencias.keys()):
                # Si el diccionario aún no tiene esta cantidad agregada la agregamos
                frecuencias[f'{registro[indice]}'] = 0
            frecuencias[f'{registro[indice]}'] += 1
        # Devolvemos el valor con mas instancias en el conjunton de datos
        return max(frecuencias)



    # Método que recivirá un string con el nombre de un atributo, 
    # obtendrá las instancias con valores faltantes para dicho atributo en 
    # el conjunto de datos y devolverá un diccionario con dichas instancias
    def val_faltantes(self, atributo):
        # Obtenemos el indice del atributo recibido como parametro, en caso de existir
        temp = list(self.tabla.properties.props['attributes'])
        indice = 0
        for item in temp:
            if item['name'] == atributo['name']:
                break
            indice = indice + 1
        
        # Obtenemos los valores faltantes en el indice encontrado
        faltantes = []
        for reg in self.tabla.data:
            # Iteramos en cada uno de los registros del conjunto de datos
            if not reg[indice]:
                # Si el dato está vacío agregamos todo el registro al arreglo de valores faltantes
                faltantes.append(reg)
        return faltantes


    def val_fuera_dominio(self, atributo):
        pass


class AnalisisBi(Analisis):
    def __init__(self, tabla):
        super().__init__(tabla)
    