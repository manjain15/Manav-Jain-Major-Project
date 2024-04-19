import cProfile
import pstats
import json
import working_model

with open('api_key.json') as f:
        api_key_file = json.load(f)

api_key = api_key_file['API_KEY']

def main():
    working_model.get_gtfs_data(api_key, 'https://api.transport.nsw.gov.au/v1/gtfs/schedule/buses', specific_file="stops.txt")

if __name__ == "__main__":
    cProfile.runctx('main()', globals(), locals(), filename='output.prof')
    stats = pstats.Stats('output.prof')
    stats.strip_dirs()
    stats.sort_stats(pstats.SortKey.TIME)
    stats.print_stats()