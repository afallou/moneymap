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

def get_candidate_info():
    data = {}
    with open('congress_full.json') as congress:
        data = json.load(congress)
    people_data = {}
    for candidate in data['objects']:
        cand_info = candidate['person']
        people_data[cand_info['id']] = [cand_info['firstname'],  cand_info['lastname'], candidate['party']]
    return people_data

def create_recipients_list(contributions, candidate_info):
    sources = {}
    nodes = []
    for contribution in contributions:
        pid = contribution["recipient_id"]
        nodes.append({"id": str(pid), "name": (candidate_info[pid][0] + ' ' + candidate_info[pid][1]).encode('ascii', 'ignore'), "group": candidate_info[pid][2].encode('ascii','ignore')})
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
    int_nodes = [int(k['id']) for k in nodes]
    int_nodes_dict = {}
    for i in range(len(int_nodes)):
        int_nodes_dict[int_nodes[i]] = i
    l = len(sources)
    print l
    cnt = 0
    for contributor, recipients in sources.iteritems():
        print str(cnt)+ '/' + str(l)
        cnt += 1
        for i in xrange(len(recipients)):
            for j in xrange(i + 1, len(recipients)):
                src = int_nodes_dict[recipients[i]]
                dst = int_nodes_dict[recipients[j]]
                edge ={"source": src, "target": dst, "value": 1}
                edge_tuple = frozenset((src, dst))
                if not edge_tuple in edge_checks:
                    edges.append(edge)
                    edge_checks.add(edge_tuple)
    return edges                

def generate_graph():
    contributions = load_data()
    candidate_info = get_candidate_info()
    sources, nodes = create_recipients_list(contributions, candidate_info)
    print "done nodes"
    edges = create_edges(sources, nodes)
    print 'done edges'
    with open('recipients_graph_test_large_sparse.json', 'w') as rf:
        rf.write(simplejson.dumps({"nodes": nodes, "links": edges}, indent=4))
    return nodes
        
if __name__ == "__main__":
    n = generate_graph()