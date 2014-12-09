import json
from collections import Counter
# Sanity checks on graph outputs

# "C90011289" Americans for Tex Reform
#    "C70000716" National Rifle Assn
DONOR_ID = "C70000716"

# 300072 Mitch McConnell
PERSON_ID = None

CONTRIBUTION_TYPES = ['Independent Expenditure Against',
                    'Independent Expenditure For']

CHECK_PERSON = True

def load_data(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data

def check_contributions():
    recipients = []
    donors = []
    for recipient in data:
        if PERSON_ID is not None and recipient["recipient_id"] == PERSON_ID:
            for ct in recipient["contributors"]:
                if ct["transaction_type_description"] in CONTRIBUTION_TYPES:
                    donors.append(ct)
        for ct in recipient["contributors"]:
            if DONOR_ID is not None and ct["contributor_ext_id"] == DONOR_ID:
                recipients.append((recipient["recipient_id"], ct["amount"]))

def check_dups_in_graph(data):
    nodes_dict = Counter()
    for node in data['nodes']:
        nodes_dict[node["id"]] += 1
    return nodes_dict


if __name__ == "__main__":
    data = load_data("donor_graph_20k_thresh_independent_expenditure_against.json")
    nodes_dict = check_dups_in_graph(data)