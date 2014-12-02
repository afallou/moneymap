from pattern.web import URL, PDF
import os, os.path
import json
import simplejson
import sys
import numpy
import math

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

def create_url(typ, num, con, house):
	# create url for the pdf of the bill
	if house == 'h':
		url = 'http://www.gpo.gov/fdsys/pkg/BILLS-' + str(con) + typ + str(num) + 'ih/pdf/BILLS-' + str(con) + typ + str(num) + 'ih.pdf'
		f_in = 'BILLS-' + str(con) + typ + str(num) + 'ih.pdf'
		f_out = 'bills_txt/BILLS-' + str(con) + typ + str(num) + 'ih.txt'

	elif house == 's':
		url = 'http://www.gpo.gov/fdsys/pkg/BILLS-' + str(con) + typ + str(num) + 'is/pdf/BILLS-' + str(con) + typ + str(num) + 'is.pdf'
		f_in = 'BILLS-' + str(con) + typ + str(num) + 'is.pdf'
		f_out = 'bills_txt/BILLS-' + str(con) + typ + str(num) + 'is.txt'

	return url, f_in, f_out

def create_text(url, f_in, f_out):
	# download pdf file and convert to text
	try:
		url1 = URL(url)
		f = open(f_in, 'wb')
		f.write(url1.download(cached=False))
		f.close()
		os.system(("ps2ascii %s %s") % (f_in, f_out))
		os.remove(f_in)
	except:
		print "no pdf file exists"

def get_all_text(dirs, con):
	# get all the text files for bills from dirs (directory list)
	# of certain congress number
	bills = []
	for k in range(len(dirs)):
		json_data = open(dirs[k]+'/data.json')
		data = json.load(json_data)
		if data['congress'] == con:
			if 'bill' in data:
				bills.append(data['vote_id'])
				num = data['bill']['number']
				typ = data['bill']['type']
				house = data['chamber']
				url, f_in, f_out = create_url(typ, num, con, house)
				create_text(url, f_in, f_out)

	return bills

path = 'congress/data'

dirs_house, dirs_senate = get_vote_dirs(path)

con = 112

bills = get_all_text(dirs_house, con)