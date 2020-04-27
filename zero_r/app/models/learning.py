def zero_r(classes, data):
    return [sum(d == x for d in data) for x in classes]

def zero_r_accuracy(freqs):
    return max(freqs) / sum(freqs)