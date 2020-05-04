import app.models.analisis as anal

class Tabla_analisis(anal.Analisis):
    def __init__(self, tabla, clase, atri):
        super().__init__(tabla, clase)
        self.atri = atri # El atributo a utilizar en la tabla de analisis
        self.analisis_clase = anal.AnalisisUni(self.tabla, self.clase, clase) # Creamos un objeto de analisis para la clase
        self.analisis_atri = anal.AnalisisUni(self.tabla, self.atri, clase) # Creamos un objeto de analisis para el atributo
