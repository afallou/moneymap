import snap
import json
import simplejson

REPUBLICAN = ''
DEMOCRAT = ''
INDEPENDENT = ''
THIRD = ''

def load_data():
    data = {}
    with open('contributions.json') as contributions:
        data = json.load(contributions)
    return data

def create_recipients_list(contributions):
    sources = {}
    nodes = []
    for contribution in contributions:
        pid = contribution["recipient_id"]
        nodes.append({"id": pid})
        for contributor in contribution["contributors"]:
            cid = contributor["contributor_ext_id"]
            if cid in sources:
                if not pid in sources[cid]:
                    sources[cid].append(pid)
            else:
                sources[cid] = [pid]
    return sources, nodes

def create_edges(sources):
    edges = []
    edge_checks = {}
    for contributor, recipients in sources.iteritems():
        for i in xrange(len(recipients)):
            for j in xrange(i + 1, len(recipients)):
                edge ={"source": recipients[i], "target": recipients[j]}
                edge_tuple = frozenset([recipients[i], recipients[j]])
                if not edge_tuple in edge_checks:
                    edges.append(edge)
                    edge_checks[edge_tuple] = 1
    return edges                

def generate_graph():
    contributions = load_data()
    sources, nodes = create_recipients_list(contributions)
    edges = create_edges(sources)
    with open('recipients_graph.json', 'w') as rf:
        rf.write(simplejson.dumps({"nodes": nodes, "links": edges}, indent=4))
        
if __name__ == "__main__":
    generate_graph()