import json
import simplejson
from transparencydata import TransparencyData
from influenceexplorer import InfluenceExplorer
import multiprocessing
import signal
import sys
import pdb


td = TransparencyData('4df4c44769f4411a982d024313deb894')
api = InfluenceExplorer('4df4c44769f4411a982d024313deb894')

# keys we get for a contributor
contributor_keys = [
                    "contributor_ext_id",
                    "contributor_name",
                    "contributor_type"
                    ]

contribution_keys = ["contributor_ext_id",
                    "amount",
                    "transaction_type_description"]

multiprocessing_treatment = False

# terminate subprocesses as well
def signal_handler(signal, frame):
    print "Exiting"
    api_pool.terminate()
    if multiprocessing_treatment:
        processing_pool.terminate()
    sys.exit(0)

# make the api call (async call)
def process_person(names, person_id):
    name = names['firstname'] + ' ' + names['lastname']
    print "Fetching data for", name
    # fetch data from api
    contributions = td.contributions(cycle='2012', recipient_ft = name)
    if len(contributions) == 0:
        if len(names['nickname']) > 0:
            name = names['nickname'] + ' ' + names['lastname']
            contributions = td.contributions(cycle='2012', recipient_ft = name)
        else:
            nodata_queue.put(name)
    return person_id, contributions

# Back to main process, treat the data (in other processes)
def api_callback(api_out):
    person_id, contributions = api_out
    if multiprocessing_treatment:
        processing_pool.apply(process_api_data, args=(person_id, contributions, out_data_queue, funding_sources_id, lock, contributor_keys, contribution_keys,))
    else:
        process_api_data(person_id, contributions, out_data_queue, funding_sources_id, lock, contributor_keys, contribution_keys)

def process_api_data(person_id, contributions, out_data_queue, funding_sources_id, lock, contributor_keys, contribution_keys):
    contributors_id = []
    sources = []
    for contribution in contributions:
        source = {}
        contribution_fields = {}
        for key in contribution_keys:
            contribution_fields[key] = contribution[key]
        contributors_id.append(contribution_fields)
        # We've haven't seen this funding source before
        with lock:
            if not contribution['contributor_ext_id'] in funding_sources_id:
                funding_sources_id.add(contribution['contributor_ext_id'])
                # add source to our dict
                for key in contributor_keys:
                    source[key] = contribution[key]
                sources.append(source)
    match = {'recipient_id': person_id, 'contributors': contributors_id }
    out_data_queue.put({'match': match, 'sources': sources})

if __name__ == "__main__":
    f = open('congress_full.json', 'r')
    congress_data = json.load(f)
    f.close()

    funding_reps = {}
    funding_senate = {}
    funding_sources = [] # matchup {person_id: [support_id, support_id...]}
    supports = [] # funding source full gamut (for json)
    funding_sources_id = set() # funding source ids (for tracking in this script)


    count = 0
    MAX_COUNT = 10000
    num_api_processes = 12
    num_treatment_processes = 4

    signal.signal(signal.SIGTERM, signal_handler)

    # multiprocessing stuff
    manager = multiprocessing.Manager()
    api_pool = multiprocessing.Pool(processes=num_api_processes)
    if multiprocessing_treatment:
        processing_pool = multiprocessing.Pool(processes=num_treatment_processes)
    nodata_queue = manager.Queue()
    out_data_queue = manager.Queue()
    lock = manager.Lock()

   
    matches = []
    for person in congress_data['objects']:
        if count < MAX_COUNT:
            count += 1
            names = {'firstname': person['person']['firstname'], 'lastname': person['person']['lastname'], 'nickname': person['person']['nickname']} 
            api_pool.apply_async(process_person, args=(names, person['person']['id'],), callback=api_callback)
    # Close pool and wait for processes to finish
    api_pool.close()
    api_pool.join()
    if multiprocessing_treatment:
        processing_pool.close()
        processing_pool.join()

    print "Trying to get extra data"
    with open('nodata_names.txt', 'w') as nodt:
        while not nodata_queue.empty():
            print "no data for", name
            name = nodata_queue.get()
            nodt.write(name)

    print "Extend ouputs"
    while not out_data_queue.empty():
        "not empty"
        out_data = out_data_queue.get()
        matches.append(out_data['match'])
        if not len(out_data['sources']) == 0:
            funding_sources.extend(out_data['sources'])
 
    with open('contributors.json', 'w') as contf:
        with open('contributions.json', 'w') as matchf:
            matchf.write(simplejson.dumps(matches, indent=4, sort_keys=False))
            contf.write(simplejson.dumps(funding_sources, indent=4, sort_keys=True))
