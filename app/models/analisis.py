class Analisis:
    def __init__(self, tabla):
        self.tabla = tabla
        pass


class AnalisisUni(Analisis):
    def __init__(self, tabla):
        super().__init__(tabla)


    # Método que recivirá un string con el nombre de un atributo, 
    # obtendrá las instancias con valores faltantes para dicho atributo en 
    # el conjunto de datos y devolverá un diccionario con dichas instancias
    @staticmethod
    def val_faltantes(tabla, atributo):
        # Obtenemos el indice del atributo recibido como parametro, en caso de existir
        temp = list(tabla.properties.props['attributes'])
        indice = 0
        for item in temp:
            if item['name'] == atributo['name']:
                break
            indice = indice + 1
        
        # Obtenemos los valores faltantes en el indice encontrado
        faltantes = []
        for reg in tabla.data:
            # Iteramos en cada uno de los registros del conjunto de datos
            if not reg[indice]:
                # Si el dato está vacío agregamos todo el registro al arreglo de valores faltantes
                faltantes.append(reg)
        return faltantes


    def val_fuera_dominio(self):
        pass



class AnalisisBi(Analisis):
    def __init__(self, tabla):
        super().__init__(tabla)


    def val_faltantes(self, parameter_list):
        pass


    def val_fuera_dominio(self):
        pass