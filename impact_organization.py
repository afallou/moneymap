import snap
import json
import numpy as np
import matplotlib.pyplot as plt
import lda
import re

def find_bin(bins, num):
	# find index of first entry such that num > that entry
	k = 0
	while (bins[k] < num):
		k += 1
	return k

def calc_vote_agenda_rate(org_vote, person_vote):
	count = 0
	same = 0
	for k in range(len(org_vote)):
		if org_vote[k] == 1:
			count += 1
			if person_vote[k] == 1:
				same += 1
		if org_vote[k] == -1:
			count += 1
			if person_vote[k] == -1:
				same += 1

	if count == 0:
		return -1
	else:
		return float(same)/float(count)

def get_donation_agenda_success(contributions_file, contributors_file, house_bill_file, senate_bill_file, house_data_file, id_to_id_file):
	# open full contributions file
	data_json = open(contributions_file)
	contrib_data = json.load(data_json)
	data_json.close()

	# get dictionary of contributors {id: total contributed}
	contrib_dict = {}
	print len(contrib_data)
	for k in range(len(contrib_data)):
		if k%100 == 0:
			print k
		for donor in range(len(contrib_data[k]['contributors'])):
			donor_id = contrib_data[k]['contributors'][donor]['contributor_ext_id']
			if donor_id in contrib_dict:
				contrib_dict[donor_id] += float(contrib_data[k]['contributors'][donor]['amount'])
			else:
				contrib_dict[donor_id] = float(contrib_data[k]['contributors'][donor]['amount'])

	# open full contributors file
	data_json = open(contributors_file)
	data1 = json.load(data_json)
	data_json.close()

	# get dictionary of contributors {id: clean name}
	contrib_name = {}

	for k in range(len(data1)):
		org_str = data1[k]['contributor_name']
		org_str = re.sub('[^a-zA-Z\ ]', '', org_str)
		org_str = org_str.lower()
		org_str = re.sub('assn', '', org_str)
		org_str = re.sub('association', '', org_str)
		contrib_name[data1[k]['contributor_ext_id']] = org_str

	#contrib_set = set(contributors)

	'''
	bills = data['bills']
	data_json.close()

	organizations = []

	for k in range(len(bills)):
		for org in range(len(bills[k]['supporting'])):
			org_str = bills[k]['supporting'][org]
			org_str = re.sub('[^a-zA-Z\ ]', '', org_str)
			org_str = org_str.lower()
			org_str = re.sub('assn', '', org_str)
			org_str = re.sub('association', '', org_str)
			organizations.append(org_str)
		for org in range(len(bills[k]['opposing'])):
			org_str = bills[k]['opposing'][org]
			org_str = re.sub('[^a-zA-Z\ ]', '', org_str)
			org_str = org_str.lower()
			org_str = re.sub('assn', '', org_str)
			org_str = re.sub('association', '', org_str)
			organizations.append(org_str)

	orgs_set = set(organizations)
	'''

	# open bills files
	data_json = open(house_bill_file)
	data_house = json.load(data_json)
	bills_house = data_house['bills']
	data_json.close()

	data_json = open(senate_bill_file)
	data_senate = json.load(data_json)
	bills_senate = data_senate['bills']
	data_json.close()

	organizations = {}
	# add to dictionary
	for k in range(len(bills_house)):
		for org in range(len(bills_house[k]['supporting'])):
			# [total opinions, desired results, [opinions on each bill]]
			j = bills_house[k]['supporting'][org]
			if j in organizations:
				organizations[j][2][k] = 1
			else:
				opinions_house = [0]*len(bills_house)
				opinions_house[k] = 1
				opinions_senate = [0]*len(bills_senate)
				organizations[j] = [0,0, opinions_house, opinions_senate]
		for org in range(len(bills_house[k]['opposing'])):
			j = bills_house[k]['opposing'][org]
			if j in organizations:
				organizations[j][2][k] = -1
			else:
				opinions_house = [0]*len(bills_house)
				opinions_house[k] = -1
				opinions_senate = [0]*len(bills_senate)
				organizations[j] = [0,0, opinions_house, opinions_senate]

	for k in range(len(bills_senate)):
		for org in range(len(bills_senate[k]['supporting'])):
			# [total opinions, desired results, [opinions on each bill]]
			j = bills_senate[k]['supporting'][org]
			if j in organizations:
				organizations[j][3][k] = 1
			else:
				opinions_house = [0]*len(bills_house)
				opinions_senate = [0]*len(bills_senate)
				opinions_senate[k] = 1
				organizations[j] = [0,0, opinions_house, opinions_senate]
		for org in range(len(bills_senate[k]['opposing'])):
			j = bills_senate[k]['opposing'][org]
			if j in organizations:
				organizations[j][3][k] = -1
			else:
				opinions_house = [0]*len(bills_house)
				opinions_senate = [0]*len(bills_senate)
				opinions_senate[k] = -1
				organizations[j] = [0,0, opinions_house, opinions_senate]

	for k in range(len(bills_house)):
		if bills_house[k]['data'] == "Passed":
			for org in range(len(bills_house[k]['supporting'])):
				# total opinion and desired outcome both increase
				organizations[bills_house[k]['supporting'][org]][0] += 1
				organizations[bills_house[k]['supporting'][org]][1] += 1
			for org in range(len(bills_house[k]['opposing'])):
				# only total opinion increases
				organizations[bills_house[k]['opposing'][org]][0] += 1
		if bills_house[k]['data'] == "Failed":
			for org in range(len(bills_house[k]['opposing'])):
				# total opinion and desired outcome both increase
				organizations[bills_house[k]['opposing'][org]][0] += 1
				organizations[bills_house[k]['opposing'][org]][1] += 1
			for org in range(len(bills_house[k]['supporting'])):
				# only total opinion increases
				organizations[bills_house[k]['supporting'][org]][0] += 1

	for k in range(len(bills_senate)):
		outcome = bills_senate[k]['data'].split()
		if 'Agreed' in outcome or 'Passed' in outcome:
			for org in range(len(bills_senate[k]['supporting'])):
				# total opinion and desired outcome both increase
				organizations[bills_senate[k]['supporting'][org]][0] += 1
				organizations[bills_senate[k]['supporting'][org]][1] += 1
			for org in range(len(bills_senate[k]['opposing'])):
				# only total opinion increases
				organizations[bills_senate[k]['opposing'][org]][0] += 1
		if 'Rejected' in outcome or 'Failed' in outcome:
			for org in range(len(bills_senate[k]['opposing'])):
				# total opinion and desired outcome both increase
				organizations[bills_senate[k]['opposing'][org]][0] += 1
				organizations[bills_senate[k]['opposing'][org]][1] += 1
			for org in range(len(bills_senate[k]['supporting'])):
				# only total opinion increases
				organizations[bills_senate[k]['supporting'][org]][0] += 1

	orgs_success = {}
	for key in organizations:
		#print key
		success = float(organizations[key][1])/(organizations[key][0])
		#print "success: %f" % success
		org_str = key
		org_str = re.sub('[^a-zA-Z\ ]', '', org_str)
		org_str = org_str.lower()
		org_str = re.sub('assn', '', org_str)
		org_str = re.sub('association', '', org_str)
		orgs_success[org_str] = [success, organizations[key][2], organizations[key][3]]

	# get overlap of organizations
	overlap = (set(orgs_success.keys()) & set(contrib_name.values()))

	# open actual congressional voting data
	data_json = open(house_data_file)
	data_house_votes = json.load(data_json)
	data_json.close()

	# open id_to_id dictionary for house
	data_json = open(id_to_id_file)
	id_to_id = json.load(data_json)
	data_json.close()

	inverse_contrib_name = {v: k for k, v in contrib_name.items()}

	vote_success = []
	vote_donation = []

	impact = {}

	contrib_data_condensed = {}

	#print len(contrib_data)

	for k in range(len(contrib_data)):
		politician_id = contrib_data[k]['recipient_id']
		contributors = {}
		for donor in range(len(contrib_data[k]['contributors'])):
			donor_id = contrib_data[k]['contributors'][donor]['contributor_ext_id']
			if donor_id in contributors:
				contributors[donor_id] += float(contrib_data[k]['contributors'][donor]['amount'])
			else:
				contributors[donor_id] = float(contrib_data[k]['contributors'][donor]['amount'])
		contrib_data_condensed.update({politician_id: contributors})

	#print contrib_data_condensed
	#print len(contrib_data_condensed.keys())

	for k, v in contrib_data_condensed.iteritems():
		politician_id = str(k)
		#print k
		if politician_id in id_to_id:
			# politician in the house and we have id to id
			# data for him/her
			for donor_id, donation in v.iteritems():
				if contrib_name[donor_id] in overlap:
					# contributor in overlap
					# calculate percent of votes person voted correctly with 
					# organization's agenda
					success = calc_vote_agenda_rate(orgs_success[contrib_name[donor_id]][1], data_house_votes[id_to_id[politician_id]][0])
					if success != -1:
						vote_success.append(success)
						# amount that organization donated to candidate
						vote_donation.append(donation)
						if donor_id in impact:
							impact[donor_id][0] += success*donation
							impact[donor_id][1] += donation
							impact[donor_id][2].append(politician_id)
						else:
							impact[donor_id] = [success*donation, donation, [politician_id]]
	
	'''	
	# plot results
	plt.semilogx(vote_donation, vote_success, 'r*')
	plt.ylim(-0.1,1.1)
	plt.xlabel('donation amount')
	plt.ylabel('percent of votes towards agenda')
	plt.title('Success of organization agenda vs donation amount, House 2013-2014')
	plt.show()
	'''

	# go through and get success/total donations of each org
	overlap_donations = []
	overlap_success = []

	for donor in overlap:
		if inverse_contrib_name[donor] in contrib_dict:
			success = orgs_success[donor][0]
			overlap_success.append(success)
			donations = contrib_dict[inverse_contrib_name[donor]]
			overlap_donations.append(donations)

	'''
	plt.semilogx(overlap_donations, overlap_success, 'r*')
	plt.xlabel('total donations')
	plt.ylabel('success rate')
	plt.title('Success of organization agenda vs donation total, 2013-2014')
	plt.show()
	'''

	return vote_success, vote_donation, overlap_success, overlap_donations, impact


contributions_file = 'contributions.json'
contributors_file = 'contributors_full.json'
house_bill_file = 'organization_vote_data/house_bill_data_with_orgs_2011_2012.json'
senate_bill_file = 'organization_vote_data/senate_bill_data_with_orgs_2011_2012.json'
house_data_file = 'organization_vote_data/house_data_with_orgs_2011_2012.json'
id_to_id_file = 'id_to_id_2010.json'

vote_success, vote_donation, overlap_success, overlap_donation, impact = get_donation_agenda_success(contributions_file, contributors_file, house_bill_file, senate_bill_file, house_data_file, id_to_id_file)

# average over levels of success
success_rate = np.zeros(101)
for k in range(101):
	success_rate[k] = k*0.01

donation_avg = np.zeros(101)
success_bin = np.zeros(101)
for k in range(len(vote_success)):
	bin = round(vote_success[k]*100)
	success_bin[bin] += 1
	donation_avg[bin] += vote_donation[k]

for k in range(101):
	donation_avg[k] = float(donation_avg[k])/success_bin[k]

house_plt = plt.semilogy(vote_success, vote_donation, 'b+')
house_avg = plt.semilogy(success_rate, donation_avg, 'r', linewidth=3)
plt.xlabel('rate of congressman voting with organization agenda', fontsize=12)
plt.ylabel('amount of money candidate gets from organization in next cycle', fontsize=12)
#plt.title('Past voting data vs future donations', fontsize=20)
plt.xlim(-0.1,1.1)
plt.show()

'''
contributions_file = 'contributions2010.json'
contributors_file = 'contributors2010.json'
house_bill_file = 'organization_vote_data/house_bill_data_with_orgs_2011_2012.json'
senate_bill_file = 'organization_vote_data/senate_bill_data_with_orgs_2011_2012.json'
house_data_file = 'organization_vote_data/house_data_with_orgs_2011_2012.json'
id_to_id_file = 'id_to_id_2010.json'

vote_success_2010, vote_donation_2010, overlap_success_2010, overlap_donation_2010, impact_2010 = get_donation_agenda_success(contributions_file, contributors_file, house_bill_file, senate_bill_file, house_data_file, id_to_id_file)

contributions_file = 'contributions.json'
contributors_file = 'contributors_full.json'
house_bill_file = 'organization_vote_data/house_bill_data_with_orgs_2013_2014.json'
senate_bill_file = 'organization_vote_data/senate_bill_data_with_orgs_2013_2014.json'
house_data_file = 'organization_vote_data/house_data_with_orgs_2013_2014.json'
id_to_id_file = 'id_to_id.json'

vote_success_2012, vote_donation_2012, overlap_success_2012, overlap_donation_2012, impact_2012 = get_donation_agenda_success(contributions_file, contributors_file, house_bill_file, senate_bill_file, house_data_file, id_to_id_file)
'''
'''
max_donation_2010 = max(vote_donation_2010)

n = 10000
donation_bins_2010 = np.logspace(0,7,n)
success_avg_2010 = np.zeros(n)
donation_totals_2010 = np.zeros(n)
for k in range(len(vote_donation_2010)):
	bin = find_bin(donation_bins_2010, vote_donation_2010[k])
	success_avg_2010[bin] += vote_success_2010[k]
	donation_totals_2010[bin] += 1

for k in range(len(success_avg_2010)):
	success_avg_2010[k] = float(success_avg_2010[k])/donation_totals_2010[k]

max_donation_2012 = max(vote_donation_2012)

donation_bins_2012 = np.logspace(0,7,n)
success_avg_2012 = np.zeros(n)
donation_totals_2012 = np.zeros(n)
for k in range(len(vote_donation_2012)):
	bin = find_bin(donation_bins_2012, vote_donation_2012[k])
	success_avg_2012[bin] += vote_success_2012[k]
	donation_totals_2012[bin] += 1

for k in range(len(success_avg_2012)):
	success_avg_2012[k] = float(success_avg_2012[k])/donation_totals_2012[k]
'''
'''
# plot individual donor/agenda results
#house2010_plt, = plt.semilogx(vote_donation_2010, vote_success_2010, 'rx')
house2012_plt, = plt.semilogx(vote_donation_2012, vote_success_2012, 'b+')
#avg2010_plt, = plt.semilogx(donation_bins_2010, success_avg_2010, 'r', linewidth=2)
#avg2012_plt, = plt.semilogx(donation_bins_2012, success_avg_2012, 'b', linewidth=2)
plt.ylim(-0.1,1.1)
plt.xlabel('donation amount', fontsize=15)
plt.ylabel('percent of votes towards agenda', fontsize=15)
#plt.title('Success of organization agenda vs donation amount, House', fontsize=18)
plt.legend([house2012_plt],['2013-14'])
plt.show()

# plot total donation/agenda results
all2010_plt, = plt.semilogx(overlap_donation_2010, overlap_success_2010, 'rx')
all2012_plt, = plt.semilogx(overlap_donation_2012, overlap_success_2012, 'b+')
plt.ylim(-0.1,1.1)
plt.xlabel('total donations', fontsize=15)
plt.ylabel('success rate', fontsize=15)
#plt.title('Success of organization agenda vs donation total', fontsize=20)
plt.legend([all2010_plt,all2012_plt],['2011-12','2013-14'],loc=3)
plt.show()

# calculate and plot impact scores
impact_2010_dict = {}
for k in impact_2010:
	impact_2010_dict[k] = [impact_2010[k][0]/impact_2010[k][1], len(set(impact_2010[k][2]))]

impact_2012_dict = {}
for k in impact_2012:
	impact_2012_dict[k] = [impact_2012[k][0]/impact_2012[k][1], len(set(impact_2012[k][2]))]

impact_2010_sorted = sorted(impact_2010_dict.values(), reverse=True)
impact_2012_sorted = sorted(impact_2012_dict.values(), reverse=True)

impact_2010_scores = []
impact_2012_scores = []
impact_2010_donations = []
impact_2012_donations = []

for k in range(len(impact_2010_sorted)):
	impact_2010_scores.append(impact_2010_sorted[k][0])
	impact_2010_donations.append(impact_2010_sorted[k][1])

for k in range(len(impact_2012_sorted)):
	impact_2012_scores.append(impact_2012_sorted[k][0])
	impact_2012_donations.append(impact_2012_sorted[k][1])

index2010 = np.arange(len(impact_2010_donations))
index2012 = np.arange(len(impact_2012_donations))

plt.figure(1)
plt.subplot(211)
#plt.title('Agenda impact of organization money', fontsize=30)
impact2010_plt, = plt.plot(impact_2010_scores, 'r', linewidth=3)
impact2012_plt, = plt.plot(impact_2012_scores, 'b', linewidth=3)
plt.ylabel('impact', fontsize=18)
plt.legend([impact2010_plt, impact2012_plt], ['2011-12','2013-14'],loc=3)

plt.subplot(212)
bar2010_plt = plt.bar(index2010, impact_2010_donations, color='r')
#bar2010_plt.set_color('r')
bar2012_plt = plt.bar(index2012, impact_2012_donations, color='b')
#bar2010_plt.set_color('b')
plt.ylabel('number of candidates donated to', fontsize=18)
plt.show()
'''

'''
hist, bins = numpy.histogram(success_vec, density=True)
center = (bins[:-1]+bins[1:])/2
width = 0.7*(bins[1]-bins[0])
plt.bar(center,hist,align='center',width=width)

plt.xlim(0,1)
plt.xlabel('success rate')
plt.ylabel('frequency')
plt.title('Success of organization support/opposition, House 2011-2012')
plt.show()
'''

'''
# Set of all words used
set_of_words = set()
for org in organizations.keys():
	for word in org.split():
		set_of_words.add(word)

num_words = len(set_of_words)
num_orgs = len(organizations.keys())
# Dict to provide quick lookup
word_location = {}
cnt = 0
for i in set_of_words:
	word_location[i] = cnt
	cnt+= 1

X = np.zeros([num_orgs, num_words])

org_number = 0
for org in organizations.keys():
	for word in org.split():
		X[org_number, word_location[word]] += 1
	org_number += 1
	#if(bill_number%100 == 0):
	#	print bill_number

model = lda.LDA(n_topics=30, n_iter=500, random_state=1)
model.fit(X)
topic_word = model.topic_word_  # model.components_ also works
n_top_words = 8
for i, topic_dist in enumerate(topic_word):
	topic_words = np.array([i for i in set_of_words])[np.argsort(topic_dist)][:-n_top_words:-1]
	print('Topic {}: {}'.format(i, ' '.join(topic_words)))
'''