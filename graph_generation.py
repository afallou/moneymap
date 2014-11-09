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
        nodes.append({"name": str(pid)})
        for contributor in contribution["contributors"]:
            cid = contributor["contributor_ext_id"]
            if cid in sources:
                if not pid in sources[cid]:
                    sources[cid].append(pid)
            else:
                sources[cid] = [pid]
    return sources, nodes

def create_edges(sources, nodes):
    edges = []
    edge_checks = set()
    cnt = 0
    for contributor, recipients in sources.iteritems():
        cnt += 1
        print cnt
        for i in xrange(len(recipients)):
            for j in xrange(i + 1, len(recipients)):
                for k in range(len(nodes)):
                    if str(recipients[i]) == nodes[k]['name']:
                        src = k
                    if str(recipients[j]) == nodes[k]['name']:
                        dst = k
                edge ={"source": src, "target": dst, "value": 1}
                edge_tuple = frozenset((src, dst))
                if not edge_tuple in edge_checks:
                    edges.append(edge)
                    edge_checks.add(edge_tuple)
    return edges                

def generate_graph():
    contributions = load_data()
    sources, nodes = create_recipients_list(contributions)
    print "done nodes"
    edges = create_edges(sources, nodes)
    with open('recipients_graph_test_large.json', 'w') as rf:
        rf.write(simplejson.dumps({"nodes": nodes, "links": edges}, indent=4))
    return nodes
        
if __name__ == "__main__":
    n = generate_graph()