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

    return dist[row][col]
