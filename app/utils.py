from math import sqrt

def levenshtein(s1, s2):
    rows = len(s1)+1
    cols = len(s2)+1
    dist = [[0 for x in range(cols)] for x in range(rows)]

    for i in range(1, rows):
        dist[i][0] = i

    for i in range(1, cols):
        dist[0][i] = i

    for col in range(1, cols):
        for row in range(1, rows):
            if s1[row-1] == s2[col-1]:
                cost = 0
            else:
                cost = 1
            dist[row][col] = min(dist[row-1][col] + 1,
                                 dist[row][col-1] + 1,
                                 dist[row-1][col-1] + cost)
    for r in range(len(dist)):
        print(dist[r])

    return dist[row][col]


#Calcula la media de los número recibidos
def media(numeros):
    return sum(numeros)/float(len(numeros))


def desviacion_est(numeros):
    med = media(numeros)
    varianza = sum([(x-med)**2 for x in numeros]) / float(len(numeros)-1) # Menos uno porque trabajamos con muestras no con universos
    return sqrt(varianza)
