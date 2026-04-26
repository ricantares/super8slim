"""
RebaseLib - Library for SuperEnalotto statistical analysis
==========================================================
This module provides functions to analyze lottery extraction patterns
by calculating presence frequencies of number combinations across historical draws.

Key concepts:
- Base: A set of 6 numbers (single extraction)
- Campione: A window of historical extractions to analyze
- Combinazioni: All possible k-combinations from the base (k=1..6)
- Presenze: How many times a specific combination appears in the sample
"""

from lotteria import Lotteria  # Base lottery class
import numpy as np  # Numerical computing
from itertools import combinations  # Combination generator
from scipy.special import comb  # Binomial coefficient calculator
from scipy import stats  # Statistical functions
import matplotlib.pyplot as plt  # Plotting library

class RebaseLib:
    """
    Main class for rebase statistical analysis.
    
    Provides methods to calculate and analyze the presence (frequency) of
    number combinations across different classes (k=1 to 6) in lottery draws.
    """
    
    def __init__(self):
        """Initialize the RebaseLib object."""
        pass
    
    def count_values_with_coverage(self, arr, min_val, max_val):
        
        # Handle empty array
        if len(arr) == 0:
            return 0.0
        
        if np.any(min_val > max_val):
            return 0.0
        
        sum_range = np.array([])
        total_sum = np.array([])
        
        dati = arr
        #print("dati: ", dati)
        for k in range(len(dati[0])):
            #print("k: ", k)
            column_data = np.array(dati)[:, k]
            #print("column_data: ", column_data)
            if len(column_data) > 0:  # Check if list is not empty
                uniq = np.unique_counts(column_data)
                #print(uniq)
                #print(uniq.values)
                #print(uniq.counts)
                count_array = np.zeros(max(uniq.values) + 1, dtype=int)
                for val, count in zip(uniq.values, uniq.counts):
                    count_array[val] = count
                #print(count_array)
                min_idx = np.maximum(0, np.round(min_val[k], 0)).astype(int)
                max_idx = np.minimum(len(count_array) - 1, np.round(max_val[k], 0)).astype(int)  
                sum_range = np.append(sum_range, np.sum(count_array[min_idx:max_idx + 1]))
                total_sum = np.append(total_sum, np.sum(count_array))
            else:
                sum_range = np.append(sum_range, 0)
                total_sum = np.append(total_sum, 0)
            #print("sum_range: ", sum_range)
            #print("total_sum: ", total_sum)
        
        # Calculate coverage ratio (avoid division by zero)
        return sum_range / total_sum if np.any(total_sum > 0) else 0.0

    def count_values_with_coverage_old(self, arr, min_val, max_val):
        """
        Count occurrences and calculate coverage within a value range.
        
        Combines count_values and calc_copertura into a single operation:
        1. Counts occurrences of each unique value in the input array
        2. Calculates coverage ratio for values in range [min_val, max_val]
        
        Args:
            arr (array-like): Input array of integers
            min_val (int): Lower bound index (inclusive)
            max_val (int): Upper bound index (inclusive)
        
        Returns:
            float: Coverage ratio (0.0 to 1.0), representing the percentage
                   of total counts that fall within the specified range
        """
        # Handle empty array
        if len(arr) == 0:
            return 0.0
        
        # Step 1: Count occurrences of each unique value
        unique, counts = np.unique(arr, return_counts=True)
        
        # Create count array indexed by value
        max_val_in_arr = int(max(unique))
        count_array = np.zeros(max_val_in_arr + 1, dtype=int)
        
        for val, count in zip(unique, counts):
            count_array[val] = count
        
        # Step 2: Calculate coverage within specified range
        # Clamp bounds to valid array indices
        print("pippo: ", min_val, max_val)
        print("pippo round: ", np.round(min_val, 0), np.round(max_val, 0))
        print("count_array: ", count_array, len(count_array))
        #min_idx = max(0, np.round(min_val, 0)).astype(int)
        #max_idx = min(len(count_array) - 1, np.round(max_val, 0)).astype(int)
        min_idx = np.maximum(0, np.round(min_val, 0)).astype(int)
        max_idx = np.minimum(len(count_array) - 1, np.round(max_val, 0)).astype(int)    
        print("pippo1: ", min_idx, max_idx)
        
        # Invalid range check
        if np.any(min_idx > max_idx):
            return 0
        
        # Sum of counts within the specified range
        sum_range = np.sum(count_array[min_idx:max_idx + 1])
        
        # Total sum of all counts
        total_sum = np.sum(count_array)
        
        # Calculate coverage ratio (avoid division by zero)
        return sum_range / total_sum if total_sum > 0 else 0.0


    def get_combinazioni(self):
        """
        Calculate binomial coefficients for 6-element combinations.
        
        Returns:
            list: Vector of binomial coefficients C(6,k) for k=1..6
                  [6, 15, 20, 15, 6, 1]
                  Represents number of possible combinations of k elements from 6.
        """
        return [comb(6, k, exact=True) for k in range(1,7)] # vettore coefficienti binomiali di 6 elementi in classe k = (1..6)

    def presenze_singola_combinazione(self, combinazioni_base, campione):
        """
        Calculate presence count for a single combination class.
        
        For a given combination class (e.g., all pairs k=2), counts how many
        times each combination appears in the historical sample.
        
        Args:
            combinazioni_base (list): List of combinations for a specific class k
            campione (numpy.ndarray): Matrix of historical extractions to search
        
        Returns:
            numpy.ndarray: Vector of presence counts for each combination
        """
        totale_combinazioni = len(combinazioni_base)
        # Initialize empty vector for presence counts per combination class k
        pe = np.empty([0, totale_combinazioni], dtype=int) # vettore di presenze per ogni combinazione di classe k, inizializzato a zero
        for j in range(0, totale_combinazioni):
            cb = np.array(combinazioni_base[j])  # j-th combination from class k
            ip = 0  # Presence counter
            
            # Count how many times this combination appears in the historical sample
            for m in range(0, len(campione)):
                # If the combination is contained in campione[m], it's a presence
                if (len(np.setdiff1d(cb, campione[m])) == 0):
                    ip += 1 
            
            pe = np.append(pe, ip)  # Append presence count for this combination
        
        return pe
    
    def presenze_k_combinazioni(self, combinazioni_base, campione):
        """
        Calculate presences for all 6 combination classes (k=1..6).
        
        Args:
            combinazioni_base (list): List of combinations for all 6 classes [[k=1], [k=2], ...]
            campione (numpy.ndarray): Historical sample to analyze
        
        Returns:
            list: Nested list [6] where each element contains presence vectors for class k
        """
        presenze = [[] for i in range(0,6)]
        
        # Process each of the 6 combination classes
        for i in range(0, 6):
            pe = self.presenze_singola_combinazione(combinazioni_base[i], campione)
            # If there are presences, add the presence vector to the list for class k
            if sum(pe) > 0 or presenze[i] != []:
                presenze[i].append(pe)
        
        return presenze
    
    def calcolo_presenze(self, storico_estrazioni, size_intervallo):
        """
        Calculate presences for all base windows in the historical data.
        
        This is the main analysis function that slides a window across the
        historical extractions and calculates presence statistics for each position.
        
        Args:
            storico_estrazioni (numpy.ndarray): Matrix of all historical extractions
            size_intervallo (int): Size of the sample window for each base
        
        Returns:
            list: Nested list [6] containing presence vectors for each class k
        """
        presenze = [[] for i in range(0,6)]
            
        len_estrazioni = len(storico_estrazioni)
        max_basi = len_estrazioni - size_intervallo  # Number of possible base positions

        # Process each base position in the historical data
        for e in range(max_basi):
            print("Basi analizzate:", e+1, end='\r')
            
            # Base: the extraction at position e
            base = storico_estrazioni[e, :].copy()
            
            # Campione: subsequent extractions forming the sample window
            campione = storico_estrazioni[e+1:e+1+size_intervallo]
            
            # Generate all k-combinations from the base (k=1..6)
            combinazioni_base = [list(combinations(base, k)) for k in range(1,7)]

            # Calculate presences for each combination class
            for i in range(0, 6):
                pe = self.presenze_singola_combinazione(combinazioni_base[i], campione)
                if sum(pe) > 0 or presenze[i] != []:
                    presenze[i].append(pe)
                    
        return presenze
    
    def calcolo_sommari(self, presenze):
        """
        Calculate summary statistics for each presence vector.
        
        For each presence vector, computes:
        - Sum of all presences (total occurrences)
        - Count of combinations with at least one presence
        - Count of combinations with zero presences
        - Maximum presence value
        
        Args:
            presenze (list): Nested list of presence vectors from calcolo_presenze
        
        Returns:
            list: Nested list [6] of summary statistics for each class k
                  Each summary is [U(k), V(k), W(k), Y(k)]
        """
        sommari = [[] for i in range(0,6)]
        vettore_combinazioni = self.get_combinazioni()  # Total combinations per class
        
        for i in range(0, 6):
            for j, presenza in enumerate(presenze[i]):
                s = []
                s.append(int(sum(presenza)))  # U(k): Total presenze
                s.append(int(np.count_nonzero(presenza)))  # V(k): Combinations with at least 1 presence
                s.append(vettore_combinazioni[i] - int(np.count_nonzero(presenza)))  # W(k): Combinations with 0 presenze
                s.append(int(max(presenza)))  # Y(k): Maximum presence frequency
                sommari[i].append(s)
        
        return sommari
    
    def sum_sommari_filtered(self, sommari, minSummary, maxSummary):
        """
        Calculate sum of sommari along axis=0 only for values between minSummary and maxSummary.
        
        Parameters:
        -----------
        sommari : numpy.ndarray
            2D array where each row i contains sommari[i]
        minSummary : float
            Minimum value to include in the sum (inclusive)
        maxSummary : float
            Maximum value to include in the sum (inclusive)
        
        Returns:
        --------
        numpy.ndarray
            Sum along axis=0 with filtering applied (values outside range excluded)
        """
        # Create a boolean mask for values between minSummary and maxSummary (inclusive)
        mask = (sommari >= minSummary) & (sommari <= maxSummary)
        
        # Apply mask: keep values in range, set others to 0
        filtered = np.where(mask, sommari, 0)
        
        # Sum along axis=0
        result = np.sum(filtered, axis=0)
        
        return result
    
    def statistiche_sommari(self, sommari):
        """
        Calculate and display comprehensive statistics for each combination class.
        
        Computes mean, median, mode, std, skewness, and quartiles for each class.
        
        Args:
            sommari (list): Summary statistics from calcolo_sommari
        """
        print("Statistiche sommari:")
        for i in range(0,6):     
            s = sommari[i]
            
            if len(s) > 0: 
                t = np.sum(s, axis=0)  # Total sum
                u = np.round(np.mean(s, axis=0), 2)  # Mean
                x = np.round(np.std(s, axis=0), 2)  # Standard deviation
                v = np.median(s, axis=0)  # Median
                wm, wc = stats.mode(s)[0], stats.mode(s)[1]  # Mode (value and count)
                sk = np.round(stats.skew(s, axis=0), 2)  # Skewness
                
                # Quartiles (Q1 = 25th, Q3 = 75th percentile)
                q1 = np.round(np.quantile(s, 0.25, axis=0), 2)
                q2 = np.round(np.quantile(s, 0.75, axis=0), 2)
                
                # Print statistics header based on combination class
                match i:
                    case 0: print(f"\nValori per estratto singolo")
                    case 1: print(f"\nValori per coppie di estratti")
                    case 2: print(f"\nValori per terne di estratti")
                    case 3: print(f"\nValori per quaterne di estratti")
                    case 4: print(f"\nValori per cinquine di estratti")
                    case 5: print(f"\nValori per sestine di estratti")
                
                # Print statistical measures
                print(f"- mean    : {u}")
                print(f"- median  : {v}")
                print(f"- mode    : {wm}, {wc}")
                print(f"- std     : {x}")
                print(f"- skewness: {sk}")
                print(f"- q1      : {q1}")
                print(f"- q3      : {q2}")
                
                # Determine distribution symmetry
                if np.all(abs(sk) <= 0.5):
                    print("  Distribuzione simmetrica: ")
                else:
                    print("  Distribuzione asimmetrica: ")
                
                # Print coverage analysis (mean ± std range)
                print("  (media e deviazione standard):")
                self.print_dati_statistici(s, t, u - x, u + x)
                
                # Print coverage analysis (quartile range)
                print("  (quartili):")
                self.print_dati_statistici(s, t, q1, q2)
                
    def print_dati_statistici(self, dati_colonna, somma_colonna, min, max):

        # dati_nei_limiti = self.sum_sommari_filtered(dati_colonna, min, max)
        # copertura = np.round((dati_nei_limiti / somma_colonna) * 100, 2)
        #print("  Dati colonna: ", dati_colonna)
        #print("  Dati statistici per range: ", np.round(min, 0), " .. ", np.round(max, 0))
        copertura = np.round((self.count_values_with_coverage(dati_colonna, min, max)) * 100, 2)
        
        print(f"    Totale presenze                      [range U(k)]: {np.round(min[0], 0)} .. {np.round(max[0], 0)}, copertura: {copertura[0]}%")
        print(f"    Combinazioni con almeno una presenza [range V(k)]: {np.round(min[1], 0)} .. {np.round(max[1], 0)}, copertura: {copertura[1]}%")
        print(f"    Combinazioni senza presenze          [range W(k)]: {np.round(min[2], 0)} .. {np.round(max[2], 0)}, copertura: {copertura[2]}%")
        print(f"    Massima frequenza di presenza        [range Y(k)]: {np.round(min[3], 0)} .. {np.round(max[3], 0)}, copertura: {copertura[3]}%")