from graph_generation import load_data, create_edges
import simplejson
import pdb

# minimum donation amount, in dollars, for a
# donor to appear on the graph
DONOR_THRESHOLD = 20000

def get_donors_dict():
    donors = load_data('contributors.json')
    donors_dict = {}
    for donor in donors:
        donors_dict[donor["contributor_ext_id"]] = donor["contributor_name"]
    return donors_dict

def get_donor_lists(contributions, donors_names):
    sources = {}
    nodes = []
    for contribution in contributions:
        pid = contribution["recipient_id"]
        if len(contribution["contributors"]) > 0:
            cids = []
            for ct in contribution["contributors"]:
                if float(ct["amount"]) >= DONOR_THRESHOLD:
                    cid = ct["contributor_ext_id"]
                    nodes.append({"id": cid,
                                  "name": donors_names[cid],
                                  "group": "Democrat"
                                })
                    cids.append(cid)
            sources[pid] = cids
    return sources, nodes


def generate_graph(out_filename):
    contributions = load_data('contributions.json')
    donors_names = get_donors_dict()
    sources, nodes = get_donor_lists(contributions, donors_names)
    edges = create_edges(sources, nodes)
    with open(out_filename, 'w') as cf:
        cf.write(simplejson.dumps({"nodes": nodes, "links": edges}, indent=4))


if __name__ == "__main__":
    generate_graph('donor_graph_20k_thresh.json')
