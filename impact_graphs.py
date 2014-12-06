import sys

# hack for Neeloy
sys.path.append('C:\\python27\\lib\\site-packages')

import json
import simplejson
import snap
import os, os.path
import sys
from pprint import pprint


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






################################################

# Get just most recent congress data
# for each congress person we'll make a number of 
# how often each person voted the same way as the
# eventual vote of the bill and 

def get_dirs():
	path = 'congress/data/112/votes'
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
				print "bill recorded as neither passing nor failing"
				print bill_info['result']
				passed = 1
				failed = 1
			print data['votes'].keys()
			ayes = data['votes']['Aye']
			noes = data['votes']['No']
			for j in range(len(ayes)):
				person_id = ayes[j]['id']
				if(person_id not in house_dict):
					house_dict[person_id] = [passed,1]
				else:
					house_dict[person_id][0] += passed
					house_dict[person_id][1] += 1
			for j in range(len(noes)):
				person_id = noes[j]['id']
				if(person_id not in house_dict):
					house_dict[person_id] = [failed, 1]
				else:
					house_dict[person_id][0] += failed
					house_dict[person_id][1] += 1

		house_votes.append(bill_info)
		
		json_data.close()
	

	#print house_votes
	return house_votes, house_dict


dirs_house, dirs_senate = get_dirs()
print "got dirs"
house_votes, house_dict = create_house_dict(dirs_house)

max_val = 0
max_index = 0
for k,v in house_dict.iteritems():
	if (((float(v[0]) / v[1]) > max_val) and (v[1] > 30)):
		max_val = float(v[0])/v[1]
		max_index = k

