
import datetime
import logging

from common_lib import CommonLib
from stats_lib import OccurencesStats
from stats_lib import SequenceStats
from stats_lib import DelaysStats

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


# Run as script
if __name__ == "__main__":
    import sys
    import os
    import json
    
    # Default output file (optional)
    DEFAULT_OUTPUT_FILE = "superenalotto/collector_results.json"
    
    def main():
        """Main entry point for the Collector script."""
        import argparse
        import time
        
        start_time = time.time()
        
        parser = argparse.ArgumentParser(description="SuperEnalotto Data Collector")
        parser.add_argument("input_file", help="Path to CSV data file")
        parser.add_argument("-o", "--output", default=DEFAULT_OUTPUT_FILE, help="Path to output JSON file")
        parser.add_argument("--history-size", type=int, default=None, help="History size (integer, default: None)")
        parser.add_argument("--sample-size", default="15", help="Sample size: 15, 30, 60, 90, or 'all' (default: 15)")
        
        args = parser.parse_args()
        
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
        
        # Run occurrences collection
        print(f"\nRunning occurrences collection...")
        logging.info(f"Running occurrences collection...")
                
        # Get historical data
        history_data = collector.collect_data()
        
        results = {}
        results["origine_dati"] = args.input_file
        results["ultima_estrazione"] = collector.last_extraction_date
        results["elementi_storico"] = len(history_data)
        
        results["occurrences"] = {}
        if sample_size is None:  # If 'all' was selected, we will compute for all standard sample sizes
            all_sample_sizes = [15, 30, 60, 90]
            for s in all_sample_sizes:
                results["occurrences"][s] = collector.collect_occurrences(history_data, s)
        else:
            results["occurrences"][sample_size] = collector.collect_occurrences(history_data, sample_size)
        print(f"\nOccurrences collected...")
        logging.info(f"Occurrences collected for sample size: {args.sample_size}")
        
        
        # Run sequences collection
        print(f"\nRunning sequences collection...")
        logging.info(f"Running sequences collection...")
        results["sequences"] = collector.collect_sequences(history_data)
        print(f"\nSequences collected...")
        logging.info(f"Sequences collected")
                
        # Run delays collection
        print(f"\nRunning delays collection...")
        logging.info(f"Running delays collection...")
        results["delays"] = collector.collect_delays(history_data)
        print(f"\nDelays collected...")
        logging.info(f"Delays collected")
        
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
    
    # Run main if executed directly
    if __name__ == "__main__":
        main()