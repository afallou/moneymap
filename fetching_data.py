import json
import simplejson
from transparencydata import TransparencyData
from influenceexplorer import InfluenceExplorer


td = TransparencyData('4df4c44769f4411a982d024313deb894')
api = InfluenceExplorer('4df4c44769f4411a982d024313deb894')

def process_person():
    

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
with open('contributors.json', 'w') as contf:
    with open('contributions.json', 'w') as matchf:
        matches = []
        for person in congress_data['objects']:
            if count < MAX_COUNT:
                count += 1
                name = person['person']['firstname'] + ' ' + person['person']['lastname']
                print "Processing", name
                # fetch data from api
                contributions = td.contributions(cycle='2012', recipient_ft = name)
                contributors_id = []
                for contribution in contributions:
                    contributors_id.append(contribution['contributor_ext_id'])
                    # We've haven't seen this funding source before
                    if not contribution['contributor_ext_id'] in funding_sources_id:
                        funding_sources_id.append(contribution['contributor_ext_id'])
                        source = {}
                        # add source to our dict
                        for key in cont_interesting_keys:
                            source[key] = contribution[key]
                        funding_sources.append(source)
                matches.append({'recipient_id': person['person']['id'], 'contributors': contributors_id })
        ### end for person ###
        matchf.write(simplejson.dumps(matches, indent=4, sort_keys=False))
        contf.write(simplejson.dumps(funding_sources, indent=4, sort_keys=True))
