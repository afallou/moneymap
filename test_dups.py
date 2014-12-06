import simplejson as json

with open('contributors.json', 'r') as f:
    data = json.load(f)
ids = []
dup_count = 0
for contributor in data:
    if contributor['contributor_ext_id'] in ids:
        dup_count += 1
    else:
        ids.append(contributor['contributor_ext_id'])

print "Dups:", dup_count