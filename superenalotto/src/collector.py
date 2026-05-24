
import datetime
import logging

from common_lib import CommonLib
from stats_lib import OccurencesStats
from stats_lib import SequenceStats
from stats_lib import DelaysStats
from stats_lib import BoundsStats
from stats_lib import RowSumStats

class Collector:
    """Collector for SuperEnalotto draw data.

    This class loads historical lottery draw data from a CSV file and
    provides methods to compute occurrence and sequence statistics for
    the requested sample sizes.
    """

    def __init__(self, data_file_name, history_size=None, sample_size=15):
        self.data_file_name = data_file_name
        self.history_size = history_size
        self.sample_size = sample_size
        self.last_extraction_date = None
    
    def collect_data(self):
        """Collect raw draw data from the CSV file."""
        clib = CommonLib(self.data_file_name)
        history_data = clib.load_data(self.history_size)
        self.last_extraction_date = clib.get_last_extraction_date()
        
        return history_data
    
    def collect_occurrences(self, history_data, sample_size):
        """Collect occurrence statistics from draw data."""
        ostats = OccurencesStats()
        
        # Compute occurrence frequency for each base in the historical data
        print("\nComputing occurrences for each base:")
        logging.info(f"Computing occurrences for each base with sample size: {sample_size}")
        print(f"Occurrences on s={len(history_data)} draws for samples of size alpha={sample_size}:")
        logging.info(f"Occurrences on s={len(history_data)} draws for samples of size alpha={sample_size}:")
        occurrences = ostats.find_occurrences(history_data, sample_size)
        print("Bases analyzed:  ", len(history_data) - sample_size)
        logging.info(f"Bases analyzed:  {len(history_data) - sample_size}")

        # Summary of results for each combination class
        summaries = ostats.occurrences_summary(occurrences)

        # Output statistics as dictionary
        results = ostats.get_statistics_dictionary(summaries)
        # Print statistics from dictionary
        # ostats.print_statistics_from_dict(results)
        
        return results
    
    def collect_sequences(self, history_data):
        """Collect sequence statistics from draw data."""
        sstats = SequenceStats()
        sequences = sstats.get_sequence_dict(history_data)
        return sequences
    
    def collect_delays(self, history_data):
        """Collect delay statistics from draw data."""
        dstats = DelaysStats()
        delays = dstats.get_delays_dict(history_data)
        return delays
    
    def collect_bounds(self, history_data):
        """Collect bound statistics from draw data."""
        bstats = BoundsStats()
        bounds = bstats.get_bounds_dict(history_data)
        return bounds

    def collect_row_sums(self, history_data):
        """Collect row sum statistics from draw data."""
        rstats = RowSumStats()
        row_sums = rstats.get_rowsums_dict(history_data)
        return row_sums


# Worker wrappers for parallel execution. Defined at module scope so they are picklable.
def run_sequences_worker(history_data):
    sstats = SequenceStats()
    return sstats.get_sequence_dict(history_data)


def run_delays_worker(history_data):
    dstats = DelaysStats()
    return dstats.get_delays_dict(history_data)


def run_bounds_worker(history_data):
    bstats = BoundsStats()
    return bstats.get_bounds_dict(history_data)


def run_row_sums_worker(history_data):
    rstats = RowSumStats()
    return rstats.get_rowsums_dict(history_data)

# Run as script
if __name__ == "__main__":
    import sys
    import os
    import json
    
    # Default output file (optional)
    DEFAULT_OUTPUT_FILE = "superenalotto/collector_results.json"
    
    def run_collector(args):
        """Run the collection pipeline using parsed args. Separated for profiling."""
        import time

        start_time = time.time()

        # Validate sample_size
        sample_size_values = ["15", "30", "60", "90", "all"]
        if args.sample_size not in sample_size_values:
            print(f"Error: sample-size must be one of: {', '.join(sample_size_values)}")
            sys.exit(1)

        # Convert 'all' to None for full data usage
        sample_size = None if args.sample_size == "all" else int(args.sample_size)

        print(f"Collector - SuperEnalotto Data Collector")
        print(f"=========================================")
        print(f"Input file: {args.input_file}")
        print(f"Output file: {args.output}")
        print(f"History size: {args.history_size}")
        print(f"Sample size: {args.sample_size}")
        print()

        # Validate input file exists
        if not os.path.exists(args.input_file):
            print(f"Error: Input file not found: {args.input_file}")
            sys.exit(1)

        # log file
        logging.basicConfig(filename='superenalotto/analisi_statistiche.log', filemode='w', level=logging.INFO)
        logging.info(f"Inizio analisi statistiche {datetime.datetime.now()}")

        # Initialize collector
        collector = Collector(args.input_file, args.history_size, sample_size)
        print(f"Collector initialized with: data_file={args.input_file}, history_size={args.history_size}, sample_size={sample_size}")
        logging.info(f"Collector initialized with: data_file={args.input_file}, history_size={args.history_size}, sample_size={sample_size}")

        # Get historical data
        history_data = collector.collect_data()

        # Initialize output file
        results = {}
        results["origine_dati"] = args.input_file
        results["ultima_estrazione"] = collector.last_extraction_date
        results["elementi_storico"] = len(history_data)

        # Run occurrences collection
        print(f"\nRunning occurrences collection...")
        logging.info(f"Running occurrences collection...")
        results["occurrences"] = {}
        if sample_size is None:  # If 'all' was selected, we will compute for all standard sample sizes
            all_sample_sizes = [15, 30, 60, 90]
            for s in all_sample_sizes:
                results["occurrences"][s] = collector.collect_occurrences(history_data, s)
        else:
            results["occurrences"][sample_size] = collector.collect_occurrences(history_data, sample_size)
        print(f"\nOccurrences collected...")
        logging.info(f"Occurrences collected for sample size: {args.sample_size}")

        # Run sequences, delays, bounds, and row_sums collections in parallel
        print(f"\nRunning parallel collections (sequences, delays, bounds, row_sums)...")
        logging.info(f"Running parallel collections (sequences, delays, bounds, row_sums)")

        from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
        worker_funcs = {
            "sequences": run_sequences_worker,
            "delays": run_delays_worker,
            "bounds": run_bounds_worker,
            "row_sums": run_row_sums_worker,
        }

        # Submit tasks
        results.update({k: None for k in worker_funcs})
        # Determine worker count (CLI override available)
        max_workers = args.workers if getattr(args, 'workers', None) else (os.cpu_count() or 2)

        # Choose executor type: ThreadPoolExecutor or ProcessPoolExecutor
        Executor = ThreadPoolExecutor if getattr(args, 'threaded', False) else ProcessPoolExecutor

        with Executor(max_workers=max_workers) as ex:
            future_map = {ex.submit(func, history_data): name for name, func in worker_funcs.items()}
            for fut in as_completed(future_map):
                name = future_map[fut]
                try:
                    results[name] = fut.result()
                    logging.info(f"{name} collected")
                    print(f"{name.capitalize()} collected...")
                except Exception:
                    logging.exception(f"Error collecting {name}")
                    results[name] = None

        # Save results
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"Results saved to: {args.output}")
        logging.info(f"Results saved to: {args.output}")

        # Print elapsed time
        elapsed = time.time() - start_time
        print(f"\nElapsed time: {elapsed:.2f} seconds")
        logging.info(f"Elapsed time: {elapsed:.2f} seconds")

        return results
    
    def main():
        import argparse
        import cProfile
        import pstats
        import io

        parser = argparse.ArgumentParser(description="SuperEnalotto Data Collector")
        parser.add_argument("input_file", help="Path to CSV data file")
        parser.add_argument("-o", "--output", default=DEFAULT_OUTPUT_FILE, help="Path to output JSON file")
        parser.add_argument("--history-size", type=int, default=None, help="History size (integer, default: None)")
        parser.add_argument("--sample-size", default="15", help="Sample size: 15, 30, 60, 90, or 'all' (default: 15)")
        parser.add_argument("--profile", action="store_true", help="Run under cProfile and dump stats")
        parser.add_argument("--profile-output", default="collector.prof", help="Filename to dump cProfile stats")
        parser.add_argument("--profile-top", type=int, default=20, help="Number of top functions to print from profile")
        parser.add_argument("--workers", type=int, default=None, help="Number of workers for parallel collections (default: CPU count)")
        parser.add_argument("--threaded", action="store_true", help="Use ThreadPoolExecutor instead of ProcessPoolExecutor for parallel collections")

        args = parser.parse_args()

        if args.profile:
            pr = cProfile.Profile()
            pr.runcall(run_collector, args)
            pr.dump_stats(args.profile_output)

            s = io.StringIO()
            ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
            ps.print_stats(args.profile_top)
            print(f"Profiling results (top {args.profile_top} functions):")
            print(s.getvalue())
        else:
            run_collector(args)

    # Run main if executed directly
    if __name__ == "__main__":
        main()