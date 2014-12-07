from pattern.web import URL, PDF
import os, os.path
import json
import sys
#for Neeloy
sys.path.append("C:\\python27\\lib\\site-packages")
import simplejson
import numpy as np
import math
import re
from pyPdf import PdfFileReader

def get_vote_dirs(path,con):
	# returns list of directories to all votes
	# also useful for counting total number of votes
	dirs_house = []
	dirs_senate = []
	#dirs_session = os.listdir(path)
	#for k in range(len(dirs_session)):
	k_path = path+'/'+str(con)+'/votes'
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
		f = PdfFileReader(file(f_in, "rb"))
		string_text = ""
		# Remove numbers from the file amd make it all lower case
		for page in range(len(f.pages)):
			text = f.getPage(page).extractText().encode("ascii", "ignore")
			tmp_text = re.sub("\.", " ", text)
			tmp_1_text = re.sub("  ", " ", tmp_text)
			new_text = re.sub("[^a-zA-Z\ ]", "", tmp_1_text).lower()
			string_text = string_text + " " + new_text
		
		return string_text
		#os.system(("ps2ascii %s %s") % (f_in, f_out))
		os.remove(f_in)
	except:
		print "no pdf file exists"
		return ""

def get_all_text(dirs, con):
	# get all the text files for bills from dirs (directory list)
	# of certain congress number
	bills = []
	text_of_bills = []
	for k in range(len(dirs)):
		print str(k) + "/" + str(len(dirs))
		json_data = open(dirs[k]+'/data.json')
		data = json.load(json_data)
		if data['congress'] == con:
			if 'bill' in data:
				bills.append(data['vote_id'])
				num = data['bill']['number']
				typ = data['bill']['type']
				house = data['chamber']
				url, f_in, f_out = create_url(typ, num, con, house)
				text = create_text(url, f_in, f_out)
				text_of_bills.append(text)

	return bills, text_of_bills

path = 'congress/data'

con = 113

dirs_house, dirs_senate = get_vote_dirs(path, con)


bills, text_of_bills = get_all_text(dirs_house, con)

# Set of all words used
set_of_words = set()
for bill in text_of_bills:
	for word in bill.split():
		set_of_words.add(word)

num_words = len(set_of_words)
num_bills = len(text_of_bills)
# Dict to provide quick lookup
word_location = {}
cnt = 0
for i in set_of_words:
	word_location[i] = cnt
	cnt+= 1

X = np.zeros([num_bills, num_words])

bill_number = 0
for bill in text_of_bills:
	for word in bill.split():
		X[bill_number, word_location[word]] += 1
	bill_number += 1
	if(bill_number%100 == 0):
		print bill_number