import json
import simplejson
from transparencydata import TransparencyData
from influenceexplorer import InfluenceExplorer
import multiprocessing


td = TransparencyData('4df4c44769f4411a982d024313deb894')
api = InfluenceExplorer('4df4c44769f4411a982d024313deb894')

# keys we get for a contributor
cont_interesting_keys = ["contributor_address",
                        "contributor_category",
                        "contributor_city",
                        "contributor_employer",
                        "contributor_ext_id",
                        "contributor_gender",
                        "contributor_name",
                        "contributor_occupation",
                        "contributor_state",
                        "contributor_type",
                        "contributor_zipcode"]

def process_person(name, person_id, contributor_keys):
    print "Fetching data for", name
    # fetch data from api
    contributions = td.contributions(cycle='2012', recipient_ft = name)
    return person_id, contributions

def api_callback(api_out):
    person_id, contributions = api_out
    contributors_id = []
    source = {}
    for contribution in contributions:
        contributors_id.append(contribution['contributor_ext_id'])
        # We've haven't seen this funding source before
        if not contribution['contributor_ext_id'] in funding_sources_id:
            funding_sources_id.append(contribution['contributor_ext_id'])
            # add source to our dict
            for key in contributor_keys:
                source[key] = contribution[key]
    matches.append({'recipient_id': , 'contributors': contributors_id })


f = open('congress_full.json', 'r')
congress_data = json.load(f)
f.close()

funding_reps = {}
funding_senate = {}
funding_sources = [] # matchup {person_id: [support_id, support_id...]}
supports = [] # funding source full gamut (for json)
funding_sources_id = [] # funding source ids (for tracking in this script)


count = 0
MAX_COUNT = 10000
num_processes = 4

pool = multiprocessing.Pool(processes=num_processes)
person_queue = multiprocessing.Queue()
out_data_queue = multiprocessing.Queue()
with open('contributors.json', 'w') as contf:
    with open('contributions.json', 'w') as matchf:
        matches = []
        for person in congress_data['objects']:
            if count < MAX_COUNT:
                count += 1
                name = person['person']['firstname'] + ' ' + person['person']['lastname']
                pool.apply_async(process_person, [name, person['person']['id'], cont_interesting_keys])
        ### end for person ###
        matchf.write(simplejson.dumps(matches, indent=4, sort_keys=False))
        contf.write(simplejson.dumps(funding_sources, indent=4, sort_keys=True))
