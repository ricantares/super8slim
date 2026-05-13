"""
SuperEnalotto Statistical Analysis Library
==========================================
Functions for analyzing lottery extraction patterns by calculating
frequencies of patterns across historical draws.

Key terminology:
- Base: A single extraction (6 numbers)
- Sample: Window of historical extractions to analyze
"""

import logging

import numpy as np
from itertools import combinations
from scipy.special import comb
from scipy import stats
from common_lib import CommonLib

clib = CommonLib()

class OccurencesStats:
    """
    Statistical analysis for SuperEnalotto number combinations.
    
    Analyzes occurrences (frequency) of number combinations across
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
            
            # # Generate all k-combinations from the base (k=1..6)
            # # i.e. patterns to search for in the sample window
            base_combinations = [list(combinations(base, k)) for k in range(1,7)]

            # # Calculate occurences for each combination class
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
    
    def __count_values_with_coverage(self, occurrences_summary, lower_bounds, upper_bounds):
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
                t = np.sum(s, axis=0).astype(int)
                u = np.round(np.mean(s, axis=0), 2)
                x = np.round(np.std(s, axis=0), 2)
                sk = np.round(stats.skew(s, axis=0), 2)
                
                q1 = np.round(np.quantile(s, 0.25, axis=0), 0)
                q3 = np.round(np.quantile(s, 0.75, axis=0), 0)
    
                min_bounds_simm = np.round(u - x, 0)
                max_bounds_simm = np.round(u + x, 0)
                #coverages_simm = np.round((self.__count_values_with_coverage(s, min_bounds_simm, max_bounds_simm)) * 100, 2)
                coverages_simm = np.round((clib.count_values_with_coverage(s, min_bounds_simm, max_bounds_simm)) * 100, 2)

                min_bounds_asimm = q1
                max_bounds_asimm = q3
                #coverages_asimm = np.round((self.__count_values_with_coverage(s, min_bounds_asimm, max_bounds_asimm)) * 100, 2)
                coverages_asimm = np.round((clib.count_values_with_coverage(s, min_bounds_asimm, max_bounds_asimm)) * 100, 2)
                                
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
                    measure["q1"] = q1[j]
                    measure["q3"] = q3[j]
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

    def print_statistics_from_dict(self, stats_dict):
        """
        Print statistics from the dictionary returned by get_statistics_dictionary.
        
        Args:
            stats_dict: Dictionary from get_statistics_dictionary
        """
        print("Statistiche sommari (from dictionary):")
        
        for key, class_data in stats_dict.items():
            k = class_data.get("k", int(key))
            desc = class_data.get("description", "")
            measures = class_data.get("measures", {})
            values = measures.get("values", [])
            
            print(f"\nClasse k={k}: {desc}")
            
            for measure in values:
                m_type = measure.get("type", "")
                m_mean = measure.get("mean", [])
                m_std = measure.get("std", [])
                m_skew = measure.get("skewness", [])
                m_q1 = measure.get("q1", [])
                m_q3 = measure.get("q3", [])
                
                print(f"  {m_type}:")
                print(f"    mean    : {m_mean}")
                print(f"    std     : {m_std}")
                print(f"    skewness: {m_skew}")
                print(f"    q1      : {m_q1}")
                print(f"    q3      : {m_q3}")

                simm = measure.get("simmetrica", {})
                asimm = measure.get("asimmetrica", {})
                
                print(f"    simmetrica   : min={simm.get('min')}, max={simm.get('max')}, coverage={simm.get('coverage')}%")
                print(f"    asimmetrica  : min={asimm.get('min')}, max={asimm.get('max')}, coverage={asimm.get('coverage')}%")
                
class SequenceStats:
    """
    Statistical analysis for sequences of consecutive numbers in SuperEnalotto draws.
    
    Analyzes the frequency and distribution of sequences of consecutive numbers
    across historical draws, providing insights into common patterns.
    """
    
    def __init__(self):
        """Create a new SequenceStats analyzer."""
        pass
    
    def get_sequence_dict(self, history_data):
        """
        Get a dictionary of sequence counts for an ordered array of 6 numbers.
        
        Args:
            arr: A list or array of 6 ordered numbers
        """
        ts = []
        for i in range(0,len(history_data)):
            base = history_data[i]
            seq = self.count_sequences(base)
            ts.append(seq)

            
        mind = np.round(np.min(ts, axis=0), 0)
        maxd = np.round(np.max(ts, axis=0), 0)
        #print(f"Sequenze totali \n- minimo: {mind} \n- massimo: {maxd}")

        u = np.round(np.mean(ts, axis=0), 2)
        x = np.round(np.std(ts, axis=0), 2)
        sk = np.round(stats.skew(ts, axis=0), 2)

        q1 = np.round(np.quantile(ts, 0.25, axis=0), 0)
        q3 = np.round(np.quantile(ts, 0.75, axis=0), 0)

        #print(f"Sequenze totali \n- media: {u} \n- deviazione standard: {x} \n- skewness: {sk} \n- q1: {q1} \n- q3: {q3}")

        min_bounds_simm = np.round(u - x, 0)
        max_bounds_simm = np.round(u + x, 0)
        coverages_simm = np.round((clib.count_values_with_coverage(ts, min_bounds_simm, max_bounds_simm)) * 100, 2)
        #print(f"Sequenze totali - copertura intervallo media ± deviazione standard: {coverages_simm}%")

        min_bounds_asimm = q1
        max_bounds_asimm = q3
        coverages_asimm = np.round((clib.count_values_with_coverage(ts, min_bounds_asimm, max_bounds_asimm)) * 100, 2)
        #print(f"Sequenze totali - copertura intervallo IQR: {coverages_asimm}%")

        results = {}
        measures = {}
        measures['values'] = [{}] * 6
        for j in range(0, 6):
            type = ""
            match j:
                case 0: type = "Sequenze di 2 numeri consecutivi"
                case 1: type = "Sequenze di 3 numeri consecutivi"
                case 2: type = "Sequenze di 4 numeri consecutivi"
                case 3: type = "Sequenze di 5 numeri consecutivi"
                case 4: type = "Sequenze di 6 numeri consecutivi"
                case 5: type = "Totale sequenze di numeri consecutivi"
            measures['values'][j] = {
                'id': j,
                'type': type,
                'min': mind[j],
                'max': maxd[j],
                'mean': u[j],
                'std_dev': x[j],
                'skewness': sk[j],
                'q1': q1[j],
                'q3': q3[j],
                'simmetrica': {
                    'min': min_bounds_simm[j],
                    'max': max_bounds_simm[j],
                    'coverage': coverages_simm[j]
                },
                'asimmetrica': {
                    'min': min_bounds_asimm[j],
                    'max': max_bounds_asimm[j],
                    'coverage': coverages_asimm[j]
                }
            }
        results['measures'] = measures

        # sd = {}
        # tot = np.sum(sequences, axis=0)
        # for i in range(0, len(tot)):
        #     sd[i+1] = np.round(tot[i]/len(history_data)*100, 2)
            
        # return sd      
        return results

    def count_sequences(self, arr):
        """
        Given an ordered array of 6 numbers, find all maximal consecutive sequences
        and return an array where:
        - index 0: count of sequences of length 2
        - index 1: count of sequences of length 3
        - index 2: count of sequences of length 4
        - index 3: count of sequences of length 5
        - index 4: count of sequences of length 6
        - index 5: sum of all previous counts (total number of sequences found)

        Args:
            arr: a list or array of 6 ordered numbers

        Returns:
            list of 6 integers
        """
        arr = np.array(arr, dtype=int)

        # Find positions where a new run starts (diff != 1)
        breaks = np.concatenate([[True], np.diff(arr) != 1])

        seq_start = np.where(breaks)[0]
        seq_end   = np.append(seq_start[1:] - 1, len(arr) - 1)
        lengths   = seq_end - seq_start + 1   # length of every run

        # Keep only runs of at least 2 (single numbers are not sequences)
        seq_lengths = lengths[lengths >= 2].tolist()

        # Build counts [len2, len3, len4, len5, len6]
        counts = [seq_lengths.count(i) for i in range(2, 7)]
        counts.append(sum(counts))   # total

        return counts

class DelaysStats:
    """
    Statistical analysis for delays of number combinations in SuperEnalotto draws.
    
    Analyzes the delay (number of draws since last occurrence) of specific
    number combinations across historical draws, providing insights into
    patterns of appearance and absence.
    """
    
    def __init__(self):
        """Create a new DelaysStats analyzer."""
        pass
    
    def count_delays(self, base, sample):
 
        sample_size = len(sample)
        delays = np.zeros(6, dtype=int)
        done = np.zeros(6, dtype=int)
        for i in range(sample_size):
            if 0 in done:
                for j in range(6):
                    if done[j] == 0 and base[j] not in sample[i]: delays[j] += 1
                    else: done[j] = 1
            else: break
        
        return delays
    
    def get_delays_dict(self, history_data):
        td = []
        hyp_max_delay = clib.get_hypothetic_max_delay()
        if len(history_data) < hyp_max_delay:
            #print(f"Warning: historical data has only {len(history_data)} entries, which is less than the hypothetical max delay of {hyp_max_delay}. Adjusting max delay to {len(history_data) - 1}.")
            logging.warning(f"Historical data has only {len(history_data)} entries, which is less than the hypothetical max delay of {hyp_max_delay}. Adjusting max delay to {len(history_data) - 1}.")
            hyp_max_delay = len(history_data) - 1
        for i in range(len(history_data) - hyp_max_delay):  
            #print(f"Estrazione {i+1}: {history_data[i]}")
            base = history_data[i]  # Prendi l'ultima estrazione come base per il calcolo dei ritardi
            sample_data = history_data[i+1:i+hyp_max_delay]  # Prendi le prime hyp_max_delay estrazioni per il campione   
            delays = self.count_delays(base, sample_data)

            #print(f"Ritardi: {np.sort(delays)}")
            min_delay = np.min(delays)
            max_delay = np.max(delays)
            mean_delay = np.round(np.mean(delays), 2)
            tot_delay = np.sum(delays)
            d = np.array([min_delay, max_delay, mean_delay, tot_delay])
            #print(f"Ritardo minimo: {min_delay} - massimo: {max_delay} - medio: {mean_delay}")
            td.append(d)
            
        mind = np.round(np.min(td, axis=0), 0)
        maxd = np.round(np.max(td, axis=0), 0)
        #print(f"Ritardo totale \n- minimo: {mind} \n- massimo: {maxd}")

        u = np.round(np.mean(td, axis=0), 0)
        x = np.round(np.std(td, axis=0), 0)
        sk = np.round(stats.skew(td, axis=0), 2)

        q1 = np.round(np.quantile(td, 0.25, axis=0), 0)
        q3 = np.round(np.quantile(td, 0.75, axis=0), 0)

        #print(f"Ritardo totale \n- media: {u} \n- deviazione standard: {x} \n- skewness: {sk} \n- q1: {q1} \n- q3: {q3}")

        min_bounds_simm = np.round(u - x, 0)
        max_bounds_simm = np.round(u + x, 0)
        coverages_simm = np.round((clib.count_values_with_coverage(td, min_bounds_simm, max_bounds_simm)) * 100, 2)
        #print(f"Ritardo totale - copertura intervallo media ± deviazione standard: {coverages_simm}%")

        min_bounds_asimm = q1
        max_bounds_asimm = q3
        coverages_asimm = np.round((clib.count_values_with_coverage(td, min_bounds_asimm, max_bounds_asimm)) * 100, 2)
        #print(f"Ritardo totale - copertura intervallo IQR: {coverages_asimm}%")

        results = {}
        #results['description'] = "delays"
        measures = {}
        measures['values'] = [{}] * 4
        for j in range(0, 4):
            type = ""
            match j:
                case 0: type = "Ritardo minimo"
                case 1: type = "Ritardo massimo"
                case 2: type = "Ritardo medio"
                case 3: type = "Ritardo totale"
            measures['values'][j] = {
                'id': j,
                'type': type,
                'min': mind[j],
                'max': maxd[j],
                'mean': u[j],
                'std_dev': x[j],
                'skewness': sk[j],
                'q1': q1[j],
                'q3': q3[j],
                'simmetrica': {
                    'min': min_bounds_simm[j],
                    'max': max_bounds_simm[j],
                    'coverage': coverages_simm[j]
                },
                'asimmetrica': {
                    'min': min_bounds_asimm[j],
                    'max': max_bounds_asimm[j],
                    'coverage': coverages_asimm[j]
                }
            }
        results['measures'] = measures
        #print(results)
        return results
    
class BoundsStats:
    """
    Statistical analysis for bounds (i.e. min/max values) of each column in SuperEnalotto draws.
    
    Analyzes the min/max values of each column across historical draws, providing insights into
    patterns of appearance and absence.
    """
    
    def __init__(self):
        """Create a new BoundsStats analyzer."""
        pass        
    
    def get_bounds_dict(self, history_data):
        minb = np.round(np.min(history_data, axis=0), 0)
        maxb = np.round(np.max(history_data, axis=0), 0)
        #print(f"Bounds \n- minimo: {minb} \n- massimo: {maxb}")

        u = np.round(np.mean(history_data, axis=0), 0)
        x = np.round(np.std(history_data, axis=0), 0)
        sk = np.round(stats.skew(history_data, axis=0), 2)

        q1 = np.round(np.quantile(history_data, 0.25, axis=0), 0)
        q3 = np.round(np.quantile(history_data, 0.75, axis=0), 0)

        #print(f"Bounds \n- media: {u} \n- deviazione standard: {x} \n- skewness: {sk} \n- q1: {q1} \n- q3: {q3}")

        min_bounds_simm = np.round(u - x, 0)
        max_bounds_simm = np.round(u + x, 0)
        coverages_simm = np.round((clib.count_values_with_coverage(history_data, min_bounds_simm, max_bounds_simm)) * 100, 2)
        #print(f"Bounds - copertura intervallo media ± deviazione standard: {coverages_simm}%")

        min_bounds_asimm = q1
        max_bounds_asimm = q3
        coverages_asimm = np.round((clib.count_values_with_coverage(history_data, min_bounds_asimm, max_bounds_asimm)) * 100, 2)
        #print(f"Bounds - copertura intervallo IQR: {coverages_asimm}%")

        results = {}
        results['description'] = "Bounds"
        measures = {}
        measures['values'] = [{}] * 4
        for j in range(0, 4):
            type = ""
            match j:
                case 0: type = "Bounds primo estratto"
                case 1: type = "Bounds secondo estratto"
                case 2: type = "Bounds terzo estratto"
                case 3: type = "Bounds quarto estratto"
                case 4: type = "Bounds quinto estratto"
                case 5: type = "Bounds sesto estratto"
            measures['values'][j] = {
                'id': j,
                'type': type,
                'min': minb[j],
                'max': maxb[j],
                'mean': u[j],
                'std_dev': x[j],
                'skewness': sk[j],
                'q1': q1[j],
                'q3': q3[j],
                'simmetrica': {
                    'min': min_bounds_simm[j],
                    'max': max_bounds_simm[j],
                    'coverage': coverages_simm[j]
                },
                'asimmetrica': {
                    'min': min_bounds_asimm[j],
                    'max': max_bounds_asimm[j],
                    'coverage': coverages_asimm[j]
                }
            }
        results['measures'] = measures
    
        return results