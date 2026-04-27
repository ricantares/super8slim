"""
    Porzioni di codice obsolete, rimosse per semplificare il codice.
"""
# import numpy as np
#
# class RebaseLib_deprecated:
    # def count_values_with_coverage_mia(self, arr, min_val, max_val):
        
    #     # Handle empty array
    #     if len(arr) == 0:
    #         return 0.0
        
    #     if np.any(min_val > max_val):
    #         return 0.0
        
    #     sum_range = np.array([])
    #     total_sum = np.array([])
        
    #     dati = arr
    #     #print("dati: ", dati)
    #     for k in range(len(dati[0])):
    #         #print("k: ", k)
    #         column_data = np.array(dati)[:, k]
    #         #print("column_data: ", column_data)
    #         if len(column_data) > 0:  # Check if list is not empty
    #             uniq = np.unique_counts(column_data)
    #             #print(uniq)
    #             #print(uniq.values)
    #             #print(uniq.counts)
    #             count_array = np.zeros(max(uniq.values) + 1, dtype=int)
    #             for val, count in zip(uniq.values, uniq.counts):
    #                 count_array[val] = count
    #             #print(count_array)
    #             min_idx = np.maximum(0, np.round(min_val[k], 0)).astype(int)
    #             max_idx = np.minimum(len(count_array) - 1, np.round(max_val[k], 0)).astype(int)  
    #             sum_range = np.append(sum_range, np.sum(count_array[min_idx:max_idx + 1]))
    #             total_sum = np.append(total_sum, np.sum(count_array))
    #         else:
    #             sum_range = np.append(sum_range, 0)
    #             total_sum = np.append(total_sum, 0)
    #         #print("sum_range: ", sum_range)
    #         #print("total_sum: ", total_sum)
        
    #     # Calculate coverage ratio (avoid division by zero)
    #     return sum_range / total_sum if np.any(total_sum > 0) else 0.0
    
    # def presenze_k_combinazioni(self, combinazioni_base, campione):
    #     """
    #     Calculate presences for all 6 combination classes (k=1..6).
        
    #     Args:
    #         combinazioni_base (list): List of combinations for all 6 classes [[k=1], [k=2], ...]
    #         campione (numpy.ndarray): Historical sample to analyze
        
    #     Returns:
    #         list: Nested list [6] where each element contains presence vectors for class k
    #     """
    #     presenze = [[] for i in range(0,6)]
        
    #     # Process each of the 6 combination classes
    #     for i in range(0, 6):
    #         pe = self.presenze_singola_combinazione(combinazioni_base[i], campione)
    #         # If there are presences, add the presence vector to the list for class k
    #         if sum(pe) > 0 or presenze[i] != []:
    #             presenze[i].append(pe)
        
    #     return presenze
