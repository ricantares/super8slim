
from datetime import datetime
import logging

from common_lib import CommonLib
from stats_lib import OccurencesStats
from stats_lib import SequenceStats
from stats_lib import DelaysStats

class Forecast:
    """Collector for SuperEnalotto draw data.

    This class loads historical lottery draw data from a CSV file and
    provides methods to compute occurrence and sequence statistics for
    the requested sample sizes.
    """

    def __init__(self, data_file_name, forecasts_number=100):
        self.data_file_name = data_file_name
        self.forecasts_number = forecasts_number
        self.last_extraction_date = None
    
    def collect_data(self):
        """Collect raw draw data from the CSV file."""
        clib = CommonLib(self.data_file_name)
        history_data = clib.load_data()
        self.last_extraction_date = clib.get_last_extraction_date()
        
        return history_data
    
# Run as script
if __name__ == "__main__":
    import sys
    import os
    import json
    
    # Default input statistics file (optional)
    DEFAULT_STATS_FILE = "superenalotto/collector_results.json"
    
    def main():
        """Main entry point for the Forecast script."""
        import argparse
        import time
        
        start_time = time.time()
        
        parser = argparse.ArgumentParser(description="SuperEnalotto Data Collector")
        parser.add_argument("input_file", help="Path to CSV data file")
        parser.add_argument("--stats", default=DEFAULT_STATS_FILE, help="Path to statistics JSON file")
        parser.add_argument("--forecast_number", default="100", help="Number of forecasts to generate (default: 100)")
        
        args = parser.parse_args()
        
        # Validate forecast number
        if isinstance(args.forecast_number, str):
            try:
                args.forecast_number = int(args.forecast_number)
            except ValueError:
                print(f"Error: forecast_number must be a positive integer")
                sys.exit(1)
        if args.forecast_number <= 0:
            print(f"Error: forecast_number must be a positive integer")
            sys.exit(1)
                
        print(f"Forecast - SuperEnalotto Forecast Generator")
        print(f"=========================================")
        print(f"Input hystorical data file: {args.input_file}")
        print(f"Input stats file: {args.stats}")
        print(f"Forecast number: {args.forecast_number}")
        print()
        
        # Validate input file exists
        if not os.path.exists(args.input_file):
            print(f"Error: Input file not found: {args.input_file}")
            sys.exit(1)
               
        # log file
        logging.basicConfig(filename='superenalotto/analisi_statistiche.log', filemode='w', level=logging.INFO)
        logging.info(f"Inizio analisi statistiche {datetime.now()}")
        
        # Initialize forecast
        forecast = Forecast(args.input_file, args.forecast_number)
        print(f"Forecast initialized with: data_file={args.input_file}, forecast_number={args.forecast_number}")
        logging.info(f"Forecast initialized with: data_file={args.input_file}, forecast_number={args.forecast_number}")
        
        # Run forecast generation
        print(f"\nRunning forecast generation...")
        logging.info(f"Running forecast generation...")
                
        # Get historical data
        history_data = forecast.collect_data()
        
        print(f"\nForecast generated...")
        logging.info(f"Forecast generated")
        
        # Save results
        # with open(args.output, 'w') as f:
        #     json.dump(results, f, indent=2, default=str)
        # print(f"Results saved to: {args.output}")
        # logging.info(f"Results saved to: {args.output}")
        
        # Print elapsed time
        elapsed = time.time() - start_time
        print(f"\nElapsed time: {elapsed:.2f} seconds")
        logging.info(f"Elapsed time: {elapsed:.2f} seconds")
        
        return 0
    
    # Run main if executed directly
    if __name__ == "__main__":
        main()