import snap
import json

def make_graph(f):
	data_json = open(f)
	data = json.load(data_json)

	nodes = data['nodes']
	edges = {}
	G = snap.TUNGraph.New()
	
	for k in range(len(data['nodes'])):
		G.AddNode(k)

	for k in range(len(data['links'])):
		i = data['links'][k]['source']
		j = data['links'][k]['target']
		G.AddEdge(i,j)
		edges[(i,j)] = data['links'][k]['weight']

	return G, nodes, edges

def triad_exists(edges, a, b, c):
	# check if triad a, b, and c exists in graph G with edges
	t = sorted([a, b, c])
	# all edges in dictionary in format that smaller node first
	# so only care about looking for edges in that format

	exists = ((t[0],t[1]) in edges.keys() and (t[0],t[2]) in edges.keys() and (t[1],t[2]) in edges.keys())
	return exists

def triad_balanced(edges, a, b, c):
	# check if a triad a, b, c is balanced with given edges
	# this is only for traditional sign balance theory
	t = sorted([a, b, c])
	if edges[(t[0],t[1])] < 0:
		s1 = -1
	else:
		s1 = 1
	if edges[(t[0],t[2])] < 0:
		s2 = -1
	else:
		s2 = 1
	if edges[(t[1],t[2])] < 0:
		s3 = -1
	else:
		s3 = 1
	s = s1*s2*s3
	if s > 0:
		return 1 # is balanced
	else:
		return 0 # not balanced

def triad_extended_balanced(edges, a, b, c, thresh):
	# check if a triad a, b, c is balanced with given edges
	# this is only for traditional sign balance theory
	# thresh is value for weak/strong relationships
	t = sorted([a, b, c])
	e1 = edges[(t[0],t[1])]
	spos = 0
	wpos = 0
	sneg = 0
	wneg = 0
	if e1 < -1.*thresh:
		sneg += 1
	elif e1 < 0:
		wneg += 1
	# still need to deal with neutral case
	elif e1 < thresh:
		wpos += 1
	else:
		spos += 1

	e2 = edges[(t[0],t[2])]
	if e2 < -1.*thresh:
		sneg += 1
	elif e2 < 0:
		wneg += 1
	# still need to deal with neutral case
	elif e2 < thresh:
		wpos += 1
	else:
		spos += 1

	e3 = edges[(t[1],t[2])]
	if e3 < -1.*thresh:
		sneg += 1
	elif e3 < 0:
		wneg += 1
	# still need to deal with neutral case
	elif e3 < thresh:
		wpos += 1
	else:
		spos += 1
	
	if (spos == 2 and sneg == 1) or (spos == 2 and wneg == 1) or (spos == 1 and wpos == 1 and wneg == 1) or (spos == 1 and wpos == 1 and sneg == 1) or (wpos == 2 and sneg == 1):
		return 0 # unbalanced
	else:
		return 1 # balanced

def calc_classic_balance(nodes, edges):
	# calculate percent of balanced triads in graph given
	total = 0
	balance = 0
	unbalanced = []
	for a in range(len(nodes)):
		#print a
		for b in range(a+1,len(nodes)):
			#print b
			for c in range(b+1,len(nodes)):
				if triad_exists(edges, a, b, c) == True:
					total += 1
					if triad_balanced(edges, a, b, c) == 1:
						balance += 1
					else:
						unbalanced.append((a,b,c))

	b_coeff = float(balance)/total

	return b_coeff, unbalanced

def calc_extended_balance(nodes, edges, thresh):
	# calculate percent of balanced triads in graph given
	total = 0
	balance = 0
	unbalanced = []
	for a in range(len(nodes)):
		#print a
		for b in range(a+1,len(nodes)):
			#print b
			for c in range(b+1,len(nodes)):
				if triad_exists(edges, a, b, c) == True:
					total += 1
					if triad_extended_balanced(edges, a, b, c, thresh) == 1:
						balance += 1
					else:
						unbalanced.append((a,b,c))

	b_coeff = float(balance)/total

	return b_coeff, unbalanced

graph_file = ["vote_graphs/senate_graph_1989_1990.json", "vote_graphs/senate_graph_1991_1992.json", "vote_graphs/senate_graph_1993_1994.json", "vote_graphs/senate_graph_1995_1996.json", "vote_graphs/senate_graph_1997_1998.json", "vote_graphs/senate_graph_1999_2000.json", "vote_graphs/senate_graph_2001_2002.json", "vote_graphs/senate_graph_2003_2004.json", "vote_graphs/senate_graph_2005_2006.json", "vote_graphs/senate_graph_2007_2008.json", "vote_graphs/senate_graph_2009_2010.json", "vote_graphs/senate_graph_2011_2012.json", "vote_graphs/senate_graph_2013_2014.json"]

balance_coeff = [0]*len(graph_file)
num_unbalanced = [0]*len(graph_file)

thresh = 0.5

for k in range(len(graph_file)):

	G, nodes, edges = make_graph(graph_file[k])

	#snap.PrintInfo(G, "test")

	b, unbalanced = calc_extended_balance(nodes, edges, thresh)
	#print b
	#print unbalanced
	balance_coeff[k] = b
	num_unbalanced[k] = len(unbalanced)
	print "k: %d, balance: %f, num_unbalanced: %d" % (k, balance_coeff[k], num_unbalanced[k])
