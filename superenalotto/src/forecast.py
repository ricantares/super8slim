
from datetime import datetime
import numpy as np
import logging
import json
from itertools import combinations

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
    
    def get_occurrences_stats(self, evidenze):
        occurrences = evidenze.get('occurrences', {})
        
        limits = [] * len(occurrences)
        for key, class_data in occurrences.items(): 
            k = class_data.get("k", int(key))
            l_class = {}
            l_class["sample"] = k
            l_class["class"] = [{}] * len(class_data)
            for c_key, c_value in class_data.items():
                #print(f"  {c_key}")
                desc = c_value.get("description", "")
                measures = c_value.get("measures", {})
                values = measures.get("values", [])
                
                #print(f"\nClasse k={k}: {c_value} {desc}")
                s_limit = {}
                s_limit["k"] = c_key
                s_limit["bounds"] = [{}] * 4 
                for measure in values:
                    m_id = measure.get("id", "")
                    m_type = measure.get("type", "")
                    m_mean = measure.get("mean", [])
                    m_std = measure.get("std", [])
                    m_skew = measure.get("skewness", [])
                    m_q1 = measure.get("q1", [])
                    m_q3 = measure.get("q3", [])
                    
                    # print(f"  {m_type}:")
                    # print(f"    mean    : {m_mean}")
                    # print(f"    std     : {m_std}")
                    # print(f"    skewness: {m_skew}")
                    # print(f"    q1      : {m_q1}")
                    # print(f"    q3      : {m_q3}")

                    simm = measure.get("simmetrica", {})
                    asimm = measure.get("asimmetrica", {})
                    
                    bounds = {}
                    t = abs(m_skew)
                    match t:
                        case t if t < 0.5:
                            #print(f"simmetrica   {t}: min={simm.get('min')}, max={simm.get('max')}, coverage={simm.get('coverage')}%")
                            bounds = {"id": m_id, "min": simm.get('min'), "max": simm.get('max')}
                        case t if t > 1.0:
                            #print(f"asimmetrica  {t}: min={asimm.get('min')}, max={asimm.get('max')}, coverage={asimm.get('coverage')}%")
                            bounds = {"id": m_id, "min": asimm.get('min'), "max": asimm.get('max')}
                        case _:
                            if simm.get('coverage') >= asimm.get('coverage'):
                                bounds = {"id": m_id, "min": simm.get('min'), "max": simm.get('max')}
                                #print(f"simmetrica   {t}: min={simm.get('min')}, max={simm.get('max')}, coverage={simm.get('coverage')}%")
                            else:
                                #print(f"asimmetrica  {t}: min={asimm.get('min')}, max={asimm.get('max')}, coverage={asimm.get('coverage')}%")
                                bounds = {"id": m_id, "min": asimm.get('min'), "max": asimm.get('max')}
                    
                    #print(f"    bounds   : min={bounds.get('min')}, max={bounds.get('max')}")
                    s_limit["bounds"][int(m_id)] = bounds
                    
                #print(f"s_limit: {s_limit}")
            
                l_class['class'][int(c_key)-1] = s_limit
                #print(f"l_class: {l_class}")
                
            limits = limits + [l_class]
            

        return limits

    def get_base_occurrences(self, base_combinations, sample, single_combination_occurrences):
        occurrences = [[] * 4] * 6
        for k in range(1,7):
            o = single_combination_occurrences(base_combinations[k-1], sample)
            #print(f"Occurrences for {base}: {o} , k = {k}")
            tot = np.sum(o)
            nz = np.count_nonzero(o)
            z = len(base_combinations[k-1]) - nz
            m = np.max(o)
            #print(f"Total occurrences: {tot} - Non-zero occurrences: {nz} - Zero occurrences: {z} - Max occurrences: {m}")
            occurrences[k-1] = [tot, nz, z, m]
            
        return occurrences

    def check_occurrences(self, base_combinations, history_data, limits, single_combination_occurrences):

        for o in limits:
            sample_size = int(o.get('sample'))
            sample = history_data[:sample_size] 
            occurrences = self.get_base_occurrences(base_combinations, sample, single_combination_occurrences)
            # print(f"Occurrences: {occurrences}")
            # print(f"Sample: {sample_size}")
            classes = o.get('class', [])
            for c in classes:
                #print(f"- Class: {c.get('k')}")
                bounds = c.get('bounds', [])
                occ = occurrences[int(c.get('k'))-1]
                #print(f"  - Occurrences for class {c.get('k')}: {occ}")
                for b in bounds:
                    #print(f"  - bound: {b}")
                    id = int(b.get('id'))
                    t = occ[id]
                    #print(f"  - Bounds for measure={id}: min={b.get('min')}, max={b.get('max')}, current forecast={t}")
                    if t < b.get('min') or t > b.get('max'):
                        ##print(f"    - Measure {id} is outside the bounds!")
                        return True, {"Sample": sample_size, "Class": c.get('k'), "Measure": id, "Bounds": {"min": b.get('min'), "max": b.get('max'), "current": t}} # Log the first measure that is outside the bounds
                        
        return False, {} # All measures are within the bounds (i.e. no waste)

    def get_attempts(self, total_attempts, get_forecast):
        attempts = [[]] * total_attempts
        for i in range(total_attempts):
            attempts[i] = get_forecast()
        return attempts

    def collect_attempts_within_occurrences(self, attempts, history_data, limits, single_combination_occurrences):
        good_attempts = [[]] * len(attempts)
        j = 0 # Index for good attempts
        for i in range(len(attempts)):
            print(f"Checking attempt {i+1}/{len(attempts)}", end="\r")
            base = attempts[i]
            base_combinations = [list(combinations(base, k)) for k in range(1,7)]
            waste, log_waste = self.check_occurrences(base_combinations, history_data, limits, single_combination_occurrences)
            if not waste:
                good_attempts[j] = base
                j += 1
                
        return [row for row in good_attempts if len(row) > 0]

    def get_sequences_stats(self, evidenze):
        values = evidenze.get('sequences', {}).get('measures', {}).get('values')
        #print("tot values: ", len(values))
        
        s_limit = {}
        s_limit["bounds"] = [{}] * len(values) 
        for value in values: 
            m_id = value.get("id", "")
            m_type = value.get("type", "")
            m_mean = value.get("mean", [])
            m_std = value.get("std", [])
            m_skew = value.get("skewness", [])
            m_q1 = value.get("q1", [])
            m_q3 = value.get("q3", [])

            simm = value.get("simmetrica", {})
            asimm = value.get("asimmetrica", {})
                    
            bounds = {}
            t = abs(m_skew)
            match t:
                case t if t < 0.5:
                    #print(f"simmetrica   {t}: min={simm.get('min')}, max={simm.get('max')}, coverage={simm.get('coverage')}%")
                    bounds = {"id": m_id, "min": simm.get('min'), "max": simm.get('max')}
                case t if t > 1.0:
                    #print(f"asimmetrica  {t}: min={asimm.get('min')}, max={asimm.get('max')}, coverage={asimm.get('coverage')}%")
                    bounds = {"id": m_id, "min": asimm.get('min'), "max": asimm.get('max')}
                case _:
                    if simm.get('coverage') >= asimm.get('coverage'):
                        bounds = {"id": m_id, "min": simm.get('min'), "max": simm.get('max')}
                        #print(f"simmetrica   {t}: min={simm.get('min')}, max={simm.get('max')}, coverage={simm.get('coverage')}%")
                    else:
                        #print(f"asimmetrica  {t}: min={asimm.get('min')}, max={asimm.get('max')}, coverage={asimm.get('coverage')}%")
                        bounds = {"id": m_id, "min": asimm.get('min'), "max": asimm.get('max')}
            
            #print(f"    bounds {m_id}  : min={bounds.get('min')}, max={bounds.get('max')}")
            s_limit["bounds"][int(m_id)] = bounds
            #print("s_limit: ", m_id, " ", s_limit)
                
        #limits = limits + [s_limit]

        return s_limit
            
    def check_sequences(self, base, limits, sequences):

        bounds = limits.get('bounds', [])
        for b in bounds:
            #print(f"  - bound: {b}")
            id = int(b.get('id'))
            t = sequences[id]
            #print(f"  - Bounds for measure={id}: min={b.get('min')}, max={b.get('max')}, current forecast={t}")
            if t < b.get('min') or t > b.get('max'):
                ##print(f"    - Measure {id} is outside the bounds!")
                return True, {"Measure": id, "Bounds": {"min": b.get('min'), "max": b.get('max'), "current": t}} # Log the first measure that is outside the bounds
                    
        return False, {} # All measures are within the bounds (i.e. no waste)

    def collect_attempts_within_sequences(self, attempts, limits, count_sequences):
        good_attempts = [[]] * len(attempts)
        j = 0 # Index for good attempts
        for i in range(len(attempts)):
            print(f"Checking attempt {i+1}/{len(attempts)}", end="\r")
            base = attempts[i]
            waste, log_waste = self.check_sequences(base, limits, count_sequences(base))
            if not waste:
                good_attempts[j] = base
                j += 1
                
        return [row for row in good_attempts if len(row) > 0]


    def get_delays_stats(self, evidenze):
        values = evidenze.get('delays', {}).get('measures', {}).get('values')
        #print("tot values: ", len(values))
        
        d_limit = {}
        d_limit["bounds"] = [{}] * len(values) 
        for value in values: 
            m_id = value.get("id", "")
            m_type = value.get("type", "")
            m_mean = value.get("mean", [])
            m_std = value.get("std", [])
            m_skew = value.get("skewness", [])
            m_q1 = value.get("q1", [])
            m_q3 = value.get("q3", [])

            simm = value.get("simmetrica", {})
            asimm = value.get("asimmetrica", {})
                    
            bounds = {}
            t = abs(m_skew)
            match t:
                case t if t < 0.5:
                    #print(f"simmetrica   {t}: min={simm.get('min')}, max={simm.get('max')}, coverage={simm.get('coverage')}%")
                    bounds = {"id": m_id, "min": simm.get('min'), "max": simm.get('max')}
                case t if t > 1.0:
                    #print(f"asimmetrica  {t}: min={asimm.get('min')}, max={asimm.get('max')}, coverage={asimm.get('coverage')}%")
                    bounds = {"id": m_id, "min": asimm.get('min'), "max": asimm.get('max')}
                case _:
                    if simm.get('coverage') >= asimm.get('coverage'):
                        bounds = {"id": m_id, "min": simm.get('min'), "max": simm.get('max')}
                        #print(f"simmetrica   {t}: min={simm.get('min')}, max={simm.get('max')}, coverage={simm.get('coverage')}%")
                    else:
                        #print(f"asimmetrica  {t}: min={asimm.get('min')}, max={asimm.get('max')}, coverage={asimm.get('coverage')}%")
                        bounds = {"id": m_id, "min": asimm.get('min'), "max": asimm.get('max')}
            
            #print(f"    bounds {m_id}  : min={bounds.get('min')}, max={bounds.get('max')}")
            d_limit["bounds"][int(m_id)] = bounds
            #print("d_limit: ", m_id, " ", d_limit)
                
        #limits = limits + [s_limit]

        return d_limit

    def check_delays(self, base, sample, limits, delays):
        
        #print("Base: ", base, " - ritardi: ", delays)
        bounds = limits.get('bounds', [])
        for b in bounds:
            #print(f"  - bound: {b}")
            id = int(b.get('id'))
            t = delays[id]
            #print(f"  - Bounds for measure={id}: min={b.get('min')}, max={b.get('max')}, current forecast={t}")
            if t < b.get('min') or t > b.get('max'):
                #print(f"    - Measure {id} is outside the bounds!")
                print(f"Outside bounds for measure={id}: min={b.get('min')}, max={b.get('max')}, current forecast={t}")
                return True, {"Measure": id, "Bounds": {"min": b.get('min'), "max": b.get('max'), "current": t}} # Log the first measure that is outside the bounds
                    
        return False, {} # All measures are within the bounds (i.e. no waste)

    def collect_attempts_within_delays(self, attempts, sample, limits, count_delays):
        good_attempts = [[]] * len(attempts)
        j = 0 # Index for good attempts
        for i in range(len(attempts)):
            print(f"Checking attempt {i+1}/{len(attempts)}", end="\r")
            base = attempts[i]
            waste, log_waste = self.check_delays(base, sample, limits, count_delays(base, sample))
            if not waste:
                good_attempts[j] = base
                j += 1
                
        return [row for row in good_attempts if len(row) > 0]

    
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
        
        clib = CommonLib(args.input_file)
        ostats = OccurencesStats()
        sstats = SequenceStats()
        dstats = DelaysStats()        
        
        # Get historical data
        history_data = clib.load_data()
        forecast.last_extraction_date = clib.get_last_extraction_date()
        
        # Caricamento regole di validazine
        evidenze = {}
        with open(args.stats) as file_evidenze:
                evidenze = json.load(file_evidenze)
                
        o_limits = forecast.get_occurrences_stats(evidenze)
        s_limits = forecast.get_sequences_stats(evidenze)
        d_limits = forecast.get_delays_stats(evidenze)
     
        total_attempts = args.forecast_number
        attempts = forecast.get_attempts(total_attempts, clib.get_forecast)

        print("Checking attempts within occurrences")
        good_attempts = forecast.collect_attempts_within_occurrences(attempts, history_data, o_limits, ostats.single_combination_occurrences)

        if len(good_attempts) > 0:
            print("\nAttempts passed: ", len(good_attempts))
            
            print("\nChecking attempts within sequences")
            attempts = good_attempts
            good_attempts = forecast.collect_attempts_within_sequences(attempts, s_limits, sstats.count_sequences)
            
            if len(good_attempts) > 0:
                print("\nAttempts passed: ", len(good_attempts))
                    
                print("\nChecking attempts within delays")
                attempts = good_attempts
                hyp_max_delay = clib.get_hypothetic_max_delay()
                sample = history_data[0:hyp_max_delay]
                good_attempts = forecast.collect_attempts_within_delays(attempts, sample, d_limits, dstats.count_delays)
                
                if len(good_attempts) > 0:
                    print("\nAttempts passed: ", len(good_attempts))
                else:
                    print("\nNo good attempts found")
            else:
                print("\nNo good attempts found")
        else:
            print("\nNo good attempts found")
        
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