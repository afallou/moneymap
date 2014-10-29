import csv
import json
from transparencydata import TransparencyData
from influenceexplorer import InfluenceExplorer

td = TransparencyData('4df4c44769f4411a982d024313deb894')

api = InfluenceExplorer('4df4c44769f4411a982d024313deb894')

# Dictionary for ids->[name, probably party]
crp_ids = {}

with open('CRP_IDs.csv', 'rb') as f:
    reader = csv.reader(f)
    for row in reader:
        if(row[0] != ''):
            crp_ids[row[0]] = [row[1],row[2]]


# Dictionary for names-> td_ids
# We can use these td_ids to access the
# influence explorer methods.
#cand_ids = {}
#for cand_id in crp_ids:
#    try:
#   	ent = api.entities.id_lookup(namespace='urn:crp:recipient', id=str(cand_id))
#        cand_ids[crp_ids[cand_id][0]] = ent[0][u'id'].encode('ascii')
#        print 'found candidate ', crp_ids[cand_id][0]
#    except:
#        print 'error in finding candidate ' + crp_ids[cand_id][0] + ' in database'
#        continue


a = []
# Get all entities
for i in range(20):
	a.append(api.entities.list(10000*i, 10000*(i+1)))
# Flatten list
a = [item for sublist in a for item in sublist]

# Count the number of politicians in the data set
#cnt = 0
#for i in a:
#	if i['type'] == 'politician':
#		cnt += 1
#print cnt

# organization = 60k
# individual = 40k
# politician = 80k
# industry 569

# Taking forever
############################
#funding = {}
#cnt = 0
#for i in a:
#	if i['type'] == 'politician':
#		try:
#			name = i['name'].encode('ascii')
#			funding[name] = td.contributions(cycle='2012', recipient_ft = name)
#			cnt += 1
#		except:
#			print "couldn't find funding for ", name
#	if(cnt % 100 == 0):
#		print cnt, ' out of 80000: ', cnt*100.0/80000, '%'
#######################################

import json
f = open('congress_full.json', 'r')
x = json.load(f)
f.close()

funding_reps = {}
funding_senate = {}
cnt = 0
for i in x['objects']:
	name = i['person']['firstname'] + ' ' + i['person']['lastname']
	if i['role_type'] == 'senator':
		# do shit
		try:
			funding_senate[name] = td.contributions(cycle='2012', recipient_ft = name)
			cnt += 1
		except:
			print "couldn't find senator ", name
	elif i['role_type'] == 'representative':
		# do shit
		try:
			funding_reps[name] = td.contributions(cycle='2012', recipient_ft = name)
			cnt += 1
		except:
			print "couldn't find rep ", name
	else:
		continue
	print cnt

with open('senate_data.json', 'wb') as fp:
	json.dump(funding_senate,fp)

with open('rep_data.json', 'wb') as fp:
	json.dump(funding_reps,fp)