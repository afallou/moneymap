import snap
import json
import sys
sys.path.append("C:\\python27\\lib\\site-packages")
import simplejson
import operator
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter


def load_data(filename):
    data = {}
    with open(filename) as contributions:
        data = json.load(contributions)
    return data

def neeloys_stuff():
    data = load_data("recipients_graph_good_and_bad_reps.json")

    nodes = data['nodes'] 
    edges = data['links']

    g = snap.TUNGraph.New()

    id_to_snap_labels = {}
    for i in range(len(nodes)):
    	id_to_snap_labels[i] = nodes[i]['id']
    	id_to_snap_labels[nodes[i]['id']] = i
    	g.AddNode(i)

    for i in range(len(edges)):
    	g.AddEdge(edges[i]['source'], edges[i]['target'])

    maxscc = snap.GetMxScc(g)

    Nodes = snap.TIntFltH()
    Edges = snap.TIntPrFltH()
    snap.GetBetweennessCentr(maxscc, Nodes, Edges, 1.0)
    node_centr = {}
    edge_centr = {}

    for node in Nodes:
        node_centr[node] = Nodes[node]

    for edge in Edges:
        edge_centr[(edge.GetVal1(), edge.GetVal2())] = Edges[edge]

    max_centrality_people = sorted(node_centr.iteritems(), key= operator.itemgetter(1), reverse=True)



    y = np.array([x[1] for x in max_centrality_people])
    x = np.arange(len(max_centrality_people))

    plt.semilogy(x, y, color='blue', lw=2, label='Centrality value')
    #plt.plot((1,len(max_impact_orgs)), (max_y, max_y), 'k-')
    plt.xlabel('Politicians in the max scc')
    plt.ylabel('Centrality values')
    plt.title('Looking at distribution of centrality values')
    plt.show()

    # Mix of Democrats and Republicans as top centrality people
    for i in range(5):
    	node_id = id_to_snap_labels[max_centrality_people[i][0]]
    	node_val = max_centrality_people[i][1]
    	for j in nodes:
    		if j['id'] == node_id:
    			print j['name'], int(node_val), j['group']

    ### Time to calculate my own centrality dual values

def centrality_measure(data):
    names = {}
    with open("name_dict.json") as nf:
        names = json.load(nf)
    edge_count = 0
    edges = {}
    total = 0
    degrees = Counter()
    for recipient in data:
        pid = recipient["recipient_id"]
        assert(pid not in edges)
        edges[pid] = {}
        for ct in recipient["contributors"]:
            cid = ct["contributor_ext_id"]
            amount = float(ct["amount"])
            edges[pid][cid] = amount
            degrees[cid] += 1
            edge_count += 1
            total += amount

    centrality = {}
    normalizer = 1. / (edge_count * total)
    for pid in edges:
        summ = 0
        for cid in edges[pid]:
            summ += degrees[cid] * edges[pid][cid]
        centrality[pid] = {"name": names[str(pid)], "centrality": summ * normalizer  }

    with open("centrality.json", 'w') as cf:
        cf.write(simplejson.dumps(centrality, indent=4))
    return centrality

if __name__ == "__main__":
    data = load_data("contributions.json")
    centrality = centrality_measure(data)


