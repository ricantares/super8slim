
from common_lib import CommonLib
from stats_lib import OccurencesStats
from stats_lib import SequenceStats

class Collector:
    def __init__(self, data_file_name, history_size=None, sample_size=15):
        self.data_file_name = data_file_name
        self.history_size = history_size
        self.sample_size = sample_size
    
    def collect_data(self):
        """Collect raw draw data from the CSV file."""
        clib = CommonLib(self.data_file_name)
        history_data = clib.load_data(self.history_size)
        
        return history_data
    
    def collect_occurrences(self, history_data, sample_size):
        """Collect occurrence statistics from draw data."""
        ostats = OccurencesStats()

        # Load historical draw data from CSV file
        # #history_data = clib.load_data(self.history_size)
        
        # Compute occurrence frequency for each base in the historical data
        print("\nComputing occurrences for each base:")
        occurrences = ostats.find_occurrences(history_data, sample_size)
        print("Bases analyzed:  ", len(history_data) - sample_size)

        # Summary of results for each combination class
        print(f"Occurrences on s={len(history_data)} draws for samples of size alpha={sample_size}:")
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

# Run as script
if __name__ == "__main__":
    import sys
    import os
    import json
    
    # Default output file (optional)
    DEFAULT_OUTPUT_FILE = "collector_results.json"
    
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
        
        # Initialize collector
        collector = Collector(args.input_file, args.history_size, sample_size)
        print(f"Collector initialized with: data_file={args.input_file}, history_size={args.history_size}, sample_size={sample_size}")
        
        # Run collection
        print(f"\nRunning collection...")
                
        # Get historical data
        history_data = collector.collect_data()
        
        results = {}
        results["occurrences"] = {}
        if sample_size is None:  # If 'all' was selected, we will compute for all standard sample sizes
            all_sample_sizes = [15, 30, 60, 90]
            for s in all_sample_sizes:
                results["occurrences"][s] = collector.collect_occurrences(history_data, s)
        else:
            results["occurrences"][sample_size] = collector.collect_occurrences(history_data, sample_size)
        print(f"\nOccurrences collected...")
        results["sequences"] = collector.collect_sequences(history_data)
        print(f"\nSequences collected...")
        
        # Save results
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"Results saved to: {args.output}")
        
        # Print elapsed time
        elapsed = time.time() - start_time
        print(f"\nElapsed time: {elapsed:.2f} seconds")
        
        return results
    
    # Run main if executed directly
    if __name__ == "__main__":
        main()