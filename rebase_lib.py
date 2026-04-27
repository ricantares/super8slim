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
# TODO: riconciliare italiano e inglese nel codice e nei commenti, mantenendo coerenza e chiarezza

import numpy as np  # Numerical computing
from itertools import combinations  # Combination generator
from scipy.special import comb  # Binomial coefficient calculator
from scipy import stats  # Statistical functions

class RebaseLib:
    """
    Main class for rebase statistical analysis.
    
    Provides methods to calculate and analyze the presence (frequency) of
    number combinations across different classes (k=1 to 6) in lottery draws.
    """
    
    def __init__(self):
        """Initialize the RebaseLib object."""
        pass
    
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
    
    def count_values_with_coverage(self, arr, min_val, max_val):
        """
        Optimized version of count_values_with_coverage using vectorized NumPy operations.
        
        Counts occurrences and calculates coverage ratio within value ranges for each column.
        
        Args:
            arr (numpy.ndarray): 2D array of integers with 4 columns and multiple rows
                                - column 0 = Totale presenze 
                                - column 1 = Combinazioni con almeno una presenza
                                - column 2 = Combinazioni senza presenze
                                - column 3 = Massima frequenza di presenza
            min_val (array-like): Array of 4 floats - lower bounds for each column
            max_val (array-like): Array of 4 floats - upper bounds for each column
        
        Returns:
            numpy.ndarray: Array of 4 floats representing coverage ratios (0.0 to 1.0)
                          Returns all zeros on any error
        """
        # Initialize output with zeros (default for error cases)
        result = np.zeros(4, dtype=np.float64)
        
        try:
            # Convert inputs to numpy arrays
            arr = np.asarray(arr, dtype=np.int64)
            min_val = np.asarray(min_val, dtype=np.float64)
            max_val = np.asarray(max_val, dtype=np.float64)
            
            # Validate dimensions
            if arr.ndim != 2 or arr.shape[1] != 4:
                return result
            if min_val.shape != (4,) or max_val.shape != (4,):
                return result
            
            # Handle empty array
            if arr.size == 0 or arr.shape[0] == 0:
                return result
            
            # Validate range (min must be <= max)
            if np.any(min_val > max_val):
                return result
            
            # Process each column with vectorized operations
            for col_idx in range(4):
                column_data = arr[:, col_idx]
                
                # Get unique values and their counts using numpy
                unique, counts = np.unique(column_data, return_counts=True)
                
                # Create a mapping array (indexed by value)
                max_value = int(unique.max()) if unique.size > 0 else 0
                count_array = np.zeros(max_value + 1, dtype=np.int64)
                
                # Vectorized assignment using advanced indexing
                count_array[unique] = counts
                
                # Calculate indices with clipping
                min_idx = np.clip(np.round(min_val[col_idx]).astype(np.int64), 0, len(count_array) - 1)
                max_idx = np.clip(np.round(max_val[col_idx]).astype(np.int64), 0, len(count_array) - 1)
                
                # Handle invalid range after clipping
                if min_idx > max_idx:
                    result[col_idx] = 0.0
                    continue
                
                # Calculate sums
                sum_range = np.sum(count_array[min_idx:max_idx + 1]) # Sum of counts in the specified range
                total_sum = np.sum(count_array) # Total sum of counts for the entire column
                
                # Calculate coverage ratio (avoid division by zero)
                result[col_idx] = sum_range / total_sum if total_sum > 0 else 0.0
            
            return result
            
        except (TypeError, ValueError, IndexError, OverflowError):
            # Return zeros on any exception
            return result
    
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
    
    def print_dati_statistici(self, dati_colonna, somma_colonna, min, max):
        """
        Print statistical data for a column within specified range.
        
        Args:
            dati_colonna: Column data array
            somma_colonna: Column sum
            min: Minimum bound array
            max: Maximum bound array
        """
        copertura = np.round((self.count_values_with_coverage(dati_colonna, min, max)) * 100, 2)
        
        print(f"    Totale presenze                      [range U(k)]: {np.round(min[0], 0)} .. {np.round(max[0], 0)}, copertura: {copertura[0]}%")
        print(f"    Combinazioni con almeno una presenza [range V(k)]: {np.round(min[1], 0)} .. {np.round(max[1], 0)}, copertura: {copertura[1]}%")
        print(f"    Combinazioni senza presenze          [range W(k)]: {np.round(min[2], 0)} .. {np.round(max[2], 0)}, copertura: {copertura[2]}%")
        print(f"    Massima frequenza di presenza        [range Y(k)]: {np.round(min[3], 0)} .. {np.round(max[3], 0)}, copertura: {copertura[3]}%")
    
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