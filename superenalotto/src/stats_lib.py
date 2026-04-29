"""
SuperEnalotto Statistical Analysis Library
==========================================
Functions for analyzing lottery extraction patterns by calculating
presence frequencies of number combinations across historical draws.

Key terminology:
- Base: A single extraction (6 numbers)
- Campione: Window of historical extractions to analyze
- Combinazioni: All possible k-combinations from the base (k=1..6)
- Presenze: Count of how many times a combination appears in the sample
"""

import numpy as np
from itertools import combinations
from scipy.special import comb
from scipy import stats


class OccurencesStats:
    """
    Statistical analysis for SuperEnalotto number combinations.
    
    Analyzes presence (frequency) of number combinations across
    different combination classes (k=1 to 6) in lottery draws.
    """
    
    def __init__(self):
        """Create a new OccurencesStats analyzer."""
        pass
    
    def find_occurrences(self, historical_data, sample_size):
        """
        Find all occurrences of combinations within sliding windows.
        
        Slides a window across historical extractions and calculates
        presence statistics for each window position.
        
        Args:
            historical_data: 2D array where each row is an extraction
            sample_size: Number of extractions in each sliding window
        
        Returns:
            List of 6 lists, one per combination class (k=1..6)
        """
        occurrences = [[] for i in range(0,6)]
            
        total_extractions = len(historical_data)
        max_bases = total_extractions - sample_size

        for e in range(max_bases):
            print("Basi analizzate:", e+1, end='\r')
            
            # Current extraction as the base
            base = historical_data[e, :].copy()
            
            # Subsequent extractions forming the sample window
            sample = historical_data[e+1:e+1+sample_size]
            
            # Generate all k-combinations from the base (k=1..6)
            # i.e. patterns to search for in the sample window
            base_combinations = [list(combinations(base, k)) for k in range(1,7)]

            # Calculate occurences for each combination class
            for i in range(0, 6):
                pe = self.single_combination_occurrences(base_combinations[i], sample)
                if sum(pe) > 0 or occurrences[i] != []:
                    occurrences[i].append(pe)
                    
        return occurrences
    
    def occurrences_summary(self, occurrences):
        """
        Compute summary statistics for each presence vector.
        
        For each presence vector, computes:
        - Total sum of presences [U(k)]
        - Count of combinations with at least one presence [V(k)]
        - Count of combinations with zero presences [W(k)]
        - Maximum presence value [Y(k)]
        
        Args:
            occurrences: Output from find_occurrences
        
        Returns:
            List of 6 lists, each containing [U(k), V(k), W(k), Y(k)] per position
        """
        class_summaries = [[] for i in range(0,6)]
        combinations_vector = self.get_combinations()
        
        for i in range(0, 6):
            for j, occurrence in enumerate(occurrences[i]):
                s = []
                s.append(int(sum(occurrence)))
                s.append(int(np.count_nonzero(occurrence)))
                s.append(combinations_vector[i] - int(np.count_nonzero(occurrence)))
                s.append(int(max(occurrence)))
                class_summaries[i].append(s)
        
        return class_summaries
    
    def count_values_with_coverage(self, occurrences_summary, lower_bounds, upper_bounds):
        """
        Calculate coverage ratio within value ranges for each column.
        
        Uses vectorized NumPy operations for performance.
        
        Args:
            occurrences_summary: 2D array with 4 columns
                               Col 0: Total occurrences [U(k)]
                               Col 1: Combinations with at least one presence [V(k)]
                               Col 2: Combinations without presence [W(k)]
                               Col 3: Maximum presence frequency [Y(k)]
            lower_bounds: Array of 4 lower bounds
            upper_bounds: Array of 4 upper bounds
        
        Returns:
            Array of 4 coverage ratios (0.0 to 1.0)
        """
        result = np.zeros(4, dtype=np.float64)
        
        try:
            occurrences_summary = np.asarray(occurrences_summary, dtype=np.int64)
            lower_bounds = np.asarray(lower_bounds, dtype=np.float64)
            upper_bounds = np.asarray(upper_bounds, dtype=np.float64)
            
            if occurrences_summary.ndim != 2 or occurrences_summary.shape[1] != 4:
                return result
            if lower_bounds.shape != (4,) or upper_bounds.shape != (4,):
                return result
            
            if occurrences_summary.size == 0 or occurrences_summary.shape[0] == 0:
                return result
            
            if np.any(lower_bounds > upper_bounds):
                return result
            
            for col_idx in range(4):
                column_data = occurrences_summary[:, col_idx]
                
                unique, counts = np.unique(column_data, return_counts=True)
                
                max_value = int(unique.max()) if unique.size > 0 else 0
                count_array = np.zeros(max_value + 1, dtype=np.int64)
                
                count_array[unique] = counts
                
                min_idx = np.clip(np.round(lower_bounds[col_idx]).astype(np.int64), 0, len(count_array) - 1)
                max_idx = np.clip(np.round(upper_bounds[col_idx]).astype(np.int64), 0, len(count_array) - 1)
                
                if min_idx > max_idx:
                    result[col_idx] = 0.0
                    continue
                
                # Calculate the sum of counts within the specified range
                sum_range = np.sum(count_array[min_idx:max_idx + 1])
                # Calculate the total sum of counts for normalization
                total_sum = np.sum(count_array)
                
                # Calculate coverage ratio, handling division by zero
                result[col_idx] = sum_range / total_sum if total_sum > 0 else 0.0
            
            return result
            
        except (TypeError, ValueError, IndexError, OverflowError):
            return result
    
    def get_combinations(self):
        """
        Get the number of possible combinations for each class.
        
        Returns:
            List: [C(6,1), C(6,2), C(6,3), C(6,4), C(6,5), C(6,6)]
                  [6, 15, 20, 15, 6, 1]
        """
        return [comb(6, k, exact=True) for k in range(1,7)]
      
    def single_combination_occurrences(self, base_combinations, sample):
        """
        Count how many times each combination appears in the sample.
        
        Args:
            base_combinations: List of combinations for a specific class k
            sample: 2D array of historical extractions
        
        Returns:
            1D array of presence counts, one per combination
        """
        total_combinations = len(base_combinations)
        occurrences = np.empty([0, total_combinations], dtype=int)
        
        for j in range(0, total_combinations):
            cb = np.array(base_combinations[j])
            ip = 0
            
            for m in range(0, len(sample)):
                if (len(np.setdiff1d(cb, sample[m])) == 0):
                    ip += 1 
            
            occurrences = np.append(occurrences, ip)
        
        return occurrences
    
    def __print_statistic_boundaries(self, min_bounds, max_bounds, coverages):
        """
        Print coverage statistics for each column in the summary.
        
        Args:
            min_bounds: Lower bounds for each column
            max_bounds: Upper bounds for each column
        """
        
        print(f"    Totale presenze                      [range U(k)]: {np.round(min_bounds[0], 0)} .. {np.round(max_bounds[0], 0)}, copertura: {coverages[0]}%")
        print(f"    Combinazioni con almeno una presenza [range V(k)]: {np.round(min_bounds[1], 0)} .. {np.round(max_bounds[1], 0)}, copertura: {coverages[1]}%")
        print(f"    Combinazioni senza presenze          [range W(k)]: {np.round(min_bounds[2], 0)} .. {np.round(max_bounds[2], 0)}, copertura: {coverages[2]}%")
        print(f"    Massima frequenza di presenza        [range Y(k)]: {np.round(min_bounds[3], 0)} .. {np.round(max_bounds[3], 0)}, copertura: {coverages[3]}%")
    
    # Solo per la fase di analisi visiva dei dati, non per la regola di generazione
    def print_statistics(self, summarys):
        """
        Compute and display comprehensive statistics for each class.
        
        Args:
            summarys: Summary data from occurrences_summary
        """
        print("Statistiche sommari:")
        for i in range(0,6):     
            s = summarys[i]
            
            if len(s) > 0: 
                t = np.sum(s, axis=0)
                u = np.round(np.mean(s, axis=0), 2)
                x = np.round(np.std(s, axis=0), 2)
                sk = np.round(stats.skew(s, axis=0), 2)
                
                q1 = np.round(np.quantile(s, 0.25, axis=0), 2)
                q2 = np.round(np.quantile(s, 0.75, axis=0), 2)
                
                match i:
                    case 0: print(f"\nValori per estratto singolo")
                    case 1: print(f"\nValori per coppie di estratti")
                    case 2: print(f"\nValori per terne di estratti")
                    case 3: print(f"\nValori per quaterne di estratti")
                    case 4: print(f"\nValori per cinquine di estratti")
                    case 5: print(f"\nValori per sestine di estratti")
                
                print(f"- mean    : {u}")
                print(f"- std     : {x}")
                print(f"- skewness: {sk}")
                print(f"- q1      : {q1}")
                print(f"- q3      : {q2}")
            
                if np.all(abs(sk) <= 0.5):
                    print("  Distribuzione simmetrica: ")
                else:
                    print("  Distribuzione asimmetrica: ")
                
                print("  (media e deviazione standard):")
                min_bounds = u - x
                max_bounds = u + x
                coverages = np.round((self.count_values_with_coverage(s, min_bounds, max_bounds)) * 100, 2)
                self.__print_statistic_boundaries(min_bounds, max_bounds, coverages)
                
                print("  (quartili):")
                min_bounds = q1
                max_bounds = q2
                coverages = np.round((self.count_values_with_coverage(s, min_bounds, max_bounds)) * 100, 2)
                self.__print_statistic_boundaries(min_bounds, max_bounds, coverages)


    def get_statistics_dictionary(self, summaries):
        """
        Compute and return comprehensive statistics for each class as a dictionary.
        
        Args:
            summaries: Summary data from occurrences_summary
        """
        results = {}
        class_results = {}
        class_results["risultati"] = [{}] * 6
        for i in range(0,6):     
            s = summaries[i]
            if len(s) > 0: 
                class_result = {}
                class_result["k"] = i + 1
                match i:
                    case 0: class_result["description"] = "Valori per estratto singolo"
                    case 1: class_result["description"] = "Valori per coppie di estratti"
                    case 2: class_result["description"] = "Valori per terne di estratti"
                    case 3: class_result["description"] = "Valori per quaterne di estratti"
                    case 4: class_result["description"] = "Valori per cinquine di estratti"
                    case 5: class_result["description"] = "Valori per sestine di estratti"
                t = np.sum(s, axis=0)
                u = np.round(np.mean(s, axis=0), 2)
                x = np.round(np.std(s, axis=0), 2)
                sk = np.round(stats.skew(s, axis=0), 2)
                
                q1 = np.round(np.quantile(s, 0.25, axis=0), 2)
                q2 = np.round(np.quantile(s, 0.75, axis=0), 2)
    
                min_bounds_simm = np.round(u - x, 2)
                max_bounds_simm = np.round(u + x, 2)
                coverages_simm = np.round((self.count_values_with_coverage(s, min_bounds_simm, max_bounds_simm)) * 100, 2)

                min_bounds_asimm = q1
                max_bounds_asimm = q2
                coverages_asimm = np.round((self.count_values_with_coverage(s, min_bounds_asimm, max_bounds_asimm)) * 100, 2)
                                
                measures = {}
                measures["values"] = [{}] * 4
                for j in range(0, 4): 
                    measure = {}
                    measure["id"] = j
                    match j:
                        case 0: measure["type"] = "Totale presenze"
                        case 1: measure["type"] = "Combinazioni con almeno una presenza"
                        case 2: measure["type"] = "Combinazioni senza presenze"
                        case 3: measure["type"] = "Massima frequenza di presenza"
                    measure["total"] = t[j]
                    measure["mean"] = u[j]
                    measure["std"] = x[j]
                    measure["skewness"] = sk[j]
                    measure["simmetrica"] = {
                        "min": min_bounds_simm[j],
                        "max": max_bounds_simm[j],
                        "coverage": coverages_simm[j]
                    }
                    measure["asimmetrica"] = {
                        "min": min_bounds_asimm[j],
                        "max": max_bounds_asimm[j],
                        "coverage": coverages_asimm[j]
                    }
                    measures["values"][j] = measure
                class_result["measures"] = measures
                class_results["risultati"][i] = class_result
            #results = class_results
            for i in range(0, 6):
                if class_results["risultati"][i] != {}:
                    results[f"{i+1}"] = class_results["risultati"][i]

        return results


# Run as script
if __name__ == "__main__":
    import sys
    import os
    import json
    
    # Default data file
    default_data_file = "../data/estrazioni_2026_2006.csv"
    
    # Parse command line arguments
    data_file = sys.argv[1] if len(sys.argv) > 1 else default_data_file
    sample_size = int(sys.argv[2]) if len(sys.argv) > 2 else 15
    load_rows = int(sys.argv[3]) if len(sys.argv) > 3 else None
    
    print(f"SuperEnalotto Statistical Analysis")
    print(f"====================================")
    print(f"Data file: {data_file}")
    print(f"Sample size: {sample_size}")
    print(f"Load rows: {load_rows if load_rows else 'all'}")
    print()
    
    # Initialize
    from common_lib import CommonLib
    clib = CommonLib(data_file)
    ostats = OccurencesStats()
    
    # Load data
    history_data = clib.load_data(load_rows)
    print(f"Loaded {len(history_data)} extractions")
    
    # Find occurrences
    print(f"\nCalculating occurrences (sample_size={sample_size})...")
    occurrences = ostats.find_occurrences(history_data, sample_size)
    print(f"Analyzed {len(history_data) - sample_size} base positions")
    
    # Compute summaries
    print(f"\nComputing summaries...")
    summaries = ostats.occurrences_summary(occurrences)
    
    # Get statistics
    results = ostats.get_statistics(summaries)
    
    # Output JSON
    print(f"\nResults (JSON):")
    print(json.dumps(results, indent=2, default=str))
    
    # Save to file
    output_file = "statistics_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to: {output_file}")