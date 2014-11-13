import json
import simplejson
from transparencydata import TransparencyData
from influenceexplorer import InfluenceExplorer
import multiprocessing
import signal
import sys


td = TransparencyData('4df4c44769f4411a982d024313deb894')
api = InfluenceExplorer('4df4c44769f4411a982d024313deb894')

# keys we get for a contributor
contributor_keys = ["contributor_address",
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

contribution_keys = ["contributor_ext_id",
                    "amount",
                    "transaction_type_description"]

# terminate subprocesses as well
def signal_handler(signal, frame):
    print "Exiting"
    api_pool.terminate()
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
    processing_pool.apply(process_api_data, args=(person_id, contributions, out_data_queue, funding_sources_id, lock, contributor_keys, contribution_keys,))

def process_api_data(person_id, contributions, out_data_queue, funding_sources_id, lock, contributor_keys, contribution_keys):
    contributors_id = []
    source = {}
    for contribution in contributions:
        contribution_fields = {}
        for key in contribution_keys:
            contribution_fields[key] = contribution[key]
        contributors_id.append(contribution_fields)
        # We've haven't seen this funding source before
        lock.acquire()
        if not contribution['contributor_ext_id'] in funding_sources_id:
            funding_sources_id.append(contribution['contributor_ext_id'])
            lock.release()
            # add source to our dict
            for key in contributor_keys:
                source[key] = contribution[key]
        else:
            lock.release()
    match = {'recipient_id': person_id, 'contributors': contributors_id }
    out_data_queue.put({'match': match, 'source': source})

if __name__ == "__main__":
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
    num_api_processes = 12
    num_treatment_processes = 4

    signal.signal(signal.SIGTERM, signal_handler)

    # multiprocessing stuff
    manager = multiprocessing.Manager()
    api_pool = multiprocessing.Pool(processes=num_api_processes)
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
    processing_pool.close()
    processing_pool.join()

    with open('nodata_names.txt', 'w') as nodt:
        while not nodata_queue.empty():
            print "no data for", name
            name = nodata_queue.get()
            nodt.write(name)

    while not out_data_queue.empty():
        out_data = out_data_queue.get()
        matches.append(out_data['match'])
        if not len(out_data['source']) == 0:
            funding_sources.append(out_data['source'])
 
    with open('contributors.json', 'w') as contf:
        with open('contributions.json', 'w') as matchf:
            matchf.write(simplejson.dumps(matches, indent=4, sort_keys=False))
            contf.write(simplejson.dumps(funding_sources, indent=4, sort_keys=True))
