import json
import simplejson
import snap
import os, os.path
import sys
from pprint import pprint

def get_vote_dirs(path):
	# returns list of directories to all votes
	# also useful for counting total number of votes
	dirs_house = []
	dirs_senate = []
	dirs_session = os.listdir(path)
	for k in range(len(dirs_session)):
		k_path = path+'/'+dirs_session[k]+'/votes'
		dirs_years = os.listdir(k_path)
		for j in range(len(dirs_years)):
			j_path = k_path+'/'+dirs_years[j]
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
	#categories = []
	#vote_categories = []
	'''
	results of categories:
	'amendment': 5404
	'passage-suspension': 3381
	'quorum': 111
	'recommit': 747
	'unknown': 699
	'veto-overide': 29
	'impeachment': 8
	'passage': 3552
	'leadership': 8
	'procedural': 2115
	'''
	# for now, just testing with amendment data
	for k in range(len(dirs_house)):
		json_data = open(dirs_house[k]+'/data.json')
		data = json.load(json_data)
		bill_info = {}
		# not all json files have all these categories
		if 'bill' in data:
			bill_info['bill'] = data['bill']
		if 'category' in data:
			bill_info['category'] = data['category']
			#if data['category'] == 'amendment':
			for key in data['votes'].keys():
				#vote_categories.append(key)
				if 'Yea' in data['votes']:
					for j in range(len(data['votes']['Yea'])):	
						person_id = data['votes']['Yea'][j]['id']
						if person_id in house_dict:
							# this person is already in dictionary
							# so just need to add that he/she voted 
							# yes in this vote
							house_dict[person_id][0][k] = 1
						else:
							# need to add person and info to house dictionary
							name = data['votes']['Yea'][j]['display_name']
							state = data['votes']['Yea'][j]['state']
							party = data['votes']['Yea'][j]['party']
							votes = [0]*len(dirs_house)
							votes[k] = 1 # voted yes in this vote
							house_dict[person_id] = [votes,name,state,party]
				if 'Aye' in data['votes']:
					for j in range(len(data['votes']['Aye'])):
						person_id = data['votes']['Aye'][j]['id']
						if person_id in house_dict:
							# this person is already in dictionary
							# so just need to add that he/she voted 
							# yes in this vote
							house_dict[person_id][0][k] = 1
						else:
							# need to add person and info to house dictionary
							name = data['votes']['Aye'][j]['display_name']
							state = data['votes']['Aye'][j]['state']
							party = data['votes']['Aye'][j]['party']
							votes = [0]*len(dirs_house)
							votes[k] = 1 # voted yes in this vote
							house_dict[person_id] = [votes,name,state,party]
				if 'No' in data['votes']:
					for j in range(len(data['votes']['No'])):
						person_id = data['votes']['No'][j]['id']
						if person_id in house_dict:
							# this person is already in dictionary
							# so just need to add that he/she voted 
							# no in this vote
							house_dict[person_id][0][k] = -1
						else:
							# need to add person and info to house dictionary
							name = data['votes']['No'][j]['display_name']
							state = data['votes']['No'][j]['state']
							party = data['votes']['No'][j]['party']
							votes = [0]*len(dirs_house)
							votes[k] = -1 # voted no in this vote
							house_dict[person_id] = [votes,name,state,party]
				if 'Nay' in data['votes']:			
					for j in range(len(data['votes']['Nay'])):
						person_id = data['votes']['Nay'][j]['id']
						if person_id in house_dict:
							# this person is already in dictionary
							# so just need to add that he/she voted 
							# no in this vote
							house_dict[person_id][0][k] = -1
						else:
							# need to add person and info to house dictionary
							name = data['votes']['Nay'][j]['display_name']
							state = data['votes']['Nay'][j]['state']
							party = data['votes']['Nay'][j]['party']
							votes = [0]*len(dirs_house)
							votes[k] = -1 # voted no in this vote
							house_dict[person_id] = [votes,name,state,party]
		if 'question' in data:
			bill_info['question'] = data['question']
		if 'result' in data:
			bill_info['data'] = data['result']
		if 'vote_id' in data:
			bill_info['id'] = data['vote_id']


		#categories.append(data['category'])
		house_votes.append(bill_info)
		
		json_data.close()
	

	#print house_votes
	return house_votes, house_dict

def make_house_graph(house_dict):
	# make graph for house voting data
	node_id = {} # keep track of house member id to node id map
	G = snap.TUNGraph.New()
	k = 0
	for key in house_dict.keys():
		G.AddNode(k)
		node_id[k] = key
		k += 1

	edge_weights = {} # keep track of all edge weights
	# calculate all edge weights
	for i in range(len(house_dict.keys())):
		for j in range(i+1,len(house_dict.keys())):
			votes1 = house_dict[node_id[i]][0]
			votes2 = house_dict[node_id[j]][0]
			weight = calc_edge_weight(votes1, votes2)
			# only adding non-zero edge weights, can change
			# to add all
			if weight != 0:
				G.AddEdge(i,j)
				edge_weights[(i,j)] = weight

	return G, node_id, edge_weights

def calc_edge_weight(votes1, votes2):
	# calculate edge weight for two voters
	agree = 0
	disagree = 0
	for k in range(len(votes1)):
		if votes1[k] == votes2[k] and votes1[k] != 0:
			agree += 1
		if votes1[k] != 0 and votes2[k] != 0 and votes1[k] != votes2[k]:
			disagree += 1

	if (agree+disagree) > 0:
		weight = float(agree-disagree)/(agree+disagree)
	else:
		weight = 0.0
	return weight

def save_graph(G, outfile):
	# save file name in D3 format (same as Adrien)
	nodes = []
	for NI in G.Nodes():
		nodes.append({"id": NI.GetId()})
	print nodes
	edges = []
	for EI in G.Edges():
		edges.append({"source": EI.GetSrcNId(), "target": EI.GetDstNId()})
	print edges
	with open(outfile, 'w') as rf:
		rf.write(simplejson.dumps({"nodes": nodes, "links": edges}, indent=4))

def save_house_data(edge_weights, nodes, votes, dict_data):
	# save the rest of the data in json files
	with open('house_edge_weights.json', 'w') as rf:
		rf.write(simplejson.dumps(edge_weights, indent=4))
	with open('house_node_id.json', 'w') as rf:
		rf.write(simplejson.dumps(nodes, indent=4))
	with open('house_dict.json', 'w') as rf:
		rf.write(simplejson.dumps(dict_data, indent=4))
	with open('house_vote_data', 'w') as rf:
		rf.write(simplejson({'votes': votes}, indent=4))

path = 'congress/data'

dirs_house, dirs_senate = get_vote_dirs(path)

#print len(dirs_house)
#print len(dirs_senate)

house_votes, house_dict = create_house_dict(dirs_house)
house_G, house_nodes, house_edges = make_house_graph(house_dict)

save_graph(house_G, 'house_graph.json')
#save_house_data(house_edges, house_nodes, house_votes, house_dict)