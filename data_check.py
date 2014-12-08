import json
# Sanity checks on graph outputs

# "C90011289" Americans for Tex Reform
DONOR_ID = "C90011289"

with open('contributions.json', 'r') as f:
    data = json.load(f)

recipients = []
for recipient in data:
    for ct in recipient["contributors"]:
        if ct["contributor_ext_id"] == DONOR_ID:
            recipients.append((recipient["recipient_id"], ct["amount"]))

