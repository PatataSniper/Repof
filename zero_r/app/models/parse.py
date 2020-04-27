import csv
import json

def read_csv(path):
        with open(path, newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            return list(reader)

def read_json(path):
    with open(path) as file:
        return json.load(file)