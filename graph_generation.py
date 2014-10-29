import snap
import json

def loadData():
    data = {}
    with open('json_file.json') as jsonData:
        data = json.load(jsonData)
    return data

def generateGraph:
    graph = snap.PNGraph.New()
    