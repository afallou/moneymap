import sys

# hack for Neeloy
sys.path.append('C:\\python27\\lib\\site-packages')

import json
import simplejson
import snap
import os, os.path
import sys
from pprint import pprint
import copy


REPUBLICAN = ''
DEMOCRAT = ''
INDEPENDENT = ''
THIRD = ''

def load_data():
	data = {}
	with open('contributions.json') as contributions:
		data = json.load(contributions)
	data_other = {}
	with open('contributors.json') as contributors:
		data_other = json.load(contributors)
	contributor_ids = {}
	for i in range(len(data_other)):
		contributor_ids[data_other[i]['contributor_ext_id']] = data_other[i]['contributor_name']
	return data, contributor_ids

def get_candidate_info():
	data = {}
	with open('congress_full.json') as congress:
		data = json.load(congress)
	people_data = {}
	for candidate in data['objects']:
		cand_info = candidate['person']
		people_data[cand_info['id']] = [cand_info['firstname'],  cand_info['lastname'], candidate['party']]
	return people_data

def create_recipients_list(contributions, contributors, candidate_info):
	sources_named = {}
	sources_ids = {}
	nodes = []
	for contribution in contributions:
		pid = contribution["recipient_id"]
		nodes.append({"id": str(pid), "name": (candidate_info[pid][0] + ' ' + candidate_info[pid][1]).encode('ascii', 'ignore'), "group": candidate_info[pid][2].encode('ascii','ignore')})
		for contributor in contribution["contributors"]:
			amount = int(float((contributor["amount"]).encode('ascii', 'ignore')))
			cid = contributor["contributor_ext_id"]
			# NEED TO COMPLETE CONTRIBUTORS.JSON
			# Key is a string not an id. Not ideal
			# Need to make sure all contributors are in the file to grab their name
			if(cid.encode('ascii', 'ignore') in contributors):
				c_name = contributors[cid.encode('ascii', 'ignore')]
				if (c_name in sources_named):
					if(pid in sources_named[c_name]):
						sources_named[c_name][pid] += amount
					else:
						sources_named[c_name][pid] = amount
				else:
					sources_named[c_name] = {pid:amount}
			if cid in sources_ids:
				if not pid in sources_ids[cid]:
					sources_ids[cid].append(pid)
			else:
				sources_ids[cid] = [pid]
	return sources_ids, sources_named, nodes


contributions, contributors = load_data()
candidate_info = get_candidate_info()
# Sources named gives all the people each contributor contributed to
sources_ids, sources_named, nodes = create_recipients_list(contributions, contributors, candidate_info)

surname_hashed_cand_info = {}
for k,v in candidate_info.iteritems():
	surname_hashed_cand_info[v[1].split(' ')[0].encode('ascii', 'ignore')] = [k, v[0], v[2]]



################################################

# Get just most recent congress data
# for each congress person we'll make a number of 
# how often each person voted the same way as the
# eventual vote of the bill and 

def get_dirs():
	path = 'congress/data/113/votes'
	yrs = os.listdir(path)

	dirs_house = []
	dirs_senate = []

	for yr in yrs:
		j_path = path+'/'+ yr
		votes = os.listdir(j_path)
		for i in range(len(votes)):
					if votes[i].startswith('s'):
						dirs_senate.append(j_path+'/'+votes[i])
					elif votes[i].startswith('h'):
						dirs_house.append(j_path+'/'+votes[i])
	return dirs_house, dirs_senate

def create_house_dict(dirs_house):
	# create dictionary for all house members/votes
	house_dict = {}
	house_ids_names = {}
	house_votes = []
	cnt = 0	
	#categories = []
	#vote_categories = []
	# for now, just testing with amendment data
	print (len(dirs_house))
	for k in range(len(dirs_house)):
		if(k%100 ==0):
			print k
		json_data = open(dirs_house[k]+'/data.json')
		data = json.load(json_data)
		bill_info = {}
		# not all json files have all these categories

		if 'bill' in data:
			bill_info['bill'] = data['bill']
		if 'result' in data:
			bill_info['result'] = data['result']
		if 'question' in data:
			bill_info['question'] = data['question']
		if 'vote_id' in data:
			bill_info['id'] = data['vote_id']

		if('Aye' in data['votes'] and 'No' in data['votes']):
			# House has Aye and No, Senate has Aye and Nay
			if(bill_info['result'] == "Passed"):
				passed = 1
				failed = 0
			elif(bill_info['result'] == "Failed"):
				passed = 0
				failed = 1
			else:
				passed = 1
				failed = 1
			ayes = data['votes']['Aye']
			noes = data['votes']['No']
			for j in range(len(ayes)):
				person_id = ayes[j]['id']
				if(person_id not in house_dict):
					house_dict[person_id] = [passed,1]
				else:
					house_dict[person_id][0] += passed
					house_dict[person_id][1] += 1
				if(person_id not in house_ids_names):
					house_ids_names[person_id] = ayes[j]['display_name']
			for j in range(len(noes)):
				person_id = noes[j]['id']
				if(person_id not in house_dict):
					house_dict[person_id] = [failed, 1]
				else:
					house_dict[person_id][0] += failed
					house_dict[person_id][1] += 1
				if(person_id not in house_ids_names):
					house_ids_names[person_id] = noes[j]['display_name']
		house_votes.append(bill_info)
		
		json_data.close()
	

	#print house_votes
	return house_votes, house_dict, house_ids_names


dirs_house, dirs_senate = get_dirs()
print "got dirs"
house_votes, house_dict, house_ids_names = create_house_dict(dirs_house)

house_impact = {}
for k,v in house_dict.iteritems():
	if(v[1] > 30):
		house_impact[k] = float(v[0])/v[1]

# TODO
# Losing about 40 people in this due to overlapping surnames.
id_to_id_dict = {}
for k,v in house_ids_names.iteritems():
	surname = v.split(' ')[0].split(',')[0].encode('ascii', 'ignore')
	if(surname in surname_hashed_cand_info):
		id_to_id_dict[surname_hashed_cand_info[surname][0]] = k
		id_to_id_dict[k] = surname_hashed_cand_info[surname][0]
# Gets 434 members but not:
#Andrews
#Watt 
#Cantor
#Radel 
#Emerson 
#Bonner
#Gutierrez
#A000210
#W000207
#C001046
#R000596
#E000172
#B001244
#G000535

# Convert ids from one to the other
sources_named_other_id = copy.deepcopy(sources_named)

for contributor, contributions in sources_named.iteritems():
	for contribution in contributions:
		if(contribution in id_to_id_dict):
			sources_named_other_id[contributor][id_to_id_dict[contribution]] = sources_named[contributor][contribution]
		del sources_named_other_id[contributor][contribution]

for contributor, contributions in sources_named_other_id.iteritems():
	for contribution_id in contributions:
		if(contribution_id in house_impact):
			contributions[contribution_id] = [contributions[contribution_id], house_impact[contribution_id]]

for contributor, contributions in sources_named_other_id.iteritems():
	for contribution_id in contributions.keys():
		if(contribution_id not in house_impact):
			del contributions[contribution_id]

# Calculate the weighted sum of impact based on amount
# given to each politician and how correlated the 
# politician was with the voting direction.
coefficients = {}
THRESHOLD = 10000
for contributor, contributions in sources_named_other_id.iteritems():
	total_spent = 0
	for contribution in contributions:
		total_spent += contributions[contribution][0]
	if(total_spent > THRESHOLD):
		tmp_vector = [v for k,v in sources_named_other_id[contributor].iteritems()]
		coefficients[contributor] = sum(x[0]*x[1]/total_spent for x in tmp_vector)