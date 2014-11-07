import snap
import json
import simplejson

REPUBLICAN = ''
DEMOCRAT = ''
INDEPENDENT = ''
THIRD = ''

def loadData():
    data = {}
    with open('contributions_small.json') as contributions:
        data = json.load(contributions)
    return data

def generateGraph():
    contributions = loadData()
    graph = snap.PNGraph.New()
    sources = {}
    nodes = []
    for contribution in contributions:
        pid = contribution["recipient_id"]
        nodes.append({"id": pid})
        for contributor in contribution["contributors"]:
            cid = contributor["contributor_ext_id"]
            if cid in sources.keys():
                if not pid in sources[cid]:
                    sources[cid].append(pid)
            else:
                sources[cid] = [pid]
    links = []
    for contributor, recipients in sources.iteritems():
        for i in xrange(len(recipients)):
            for j in xrange(i + 1, len(recipients)):
                links.append( {"source": recipients[i], "target": recipients[j]} )
    with open('recipients_graph.json', 'w') as rf:
        rf.write(simplejson.dumps({"nodes": nodes, "links": links}, indent=4))
        
if __name__ == "__main__":
    generateGraph()