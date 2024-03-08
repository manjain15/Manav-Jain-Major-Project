import cProfile
import pstats
import modifying_code_structure

def main():
    modifying_code_structure.get_gtfs_data()

if __name__ == "__main__":
    cProfile.runctx('main()', globals(), locals(), filename='output.prof')
    stats = pstats.Stats('output.prof')
    stats.strip_dirs()
    stats.sort_stats(pstats.SortKey.TIME)
    stats.print_stats()