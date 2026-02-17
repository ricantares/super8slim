"""
Code snippet to calculate sum of sommari[i] along axis=0 
only if values are between minSummary and maxSummary
"""

import numpy as np


def sum_sommari_filtered(sommari, minSummary, maxSummary):
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


# Alternative: if sommari is a list of 1D arrays
def sum_sommari_list_filtered(sommari_list, minSummary, maxSummary):
    """
    Calculate sum along axis=0 for a list of arrays, 
    only including values between minSummary and maxSummary.
    
    Parameters:
    -----------
    sommari_list : list of numpy.ndarray
        List where each element is a 1D array (sommari[i])
    minSummary : float
        Minimum value to include in the sum (inclusive)
    maxSummary : float
        Maximum value to include in the sum (inclusive)
    
    Returns:
    --------
    numpy.ndarray
        Sum along axis=0 with filtering applied
    """
    # Stack list into 2D array if needed
    sommari = np.array(sommari_list)
    
    # Create boolean mask
    mask = (sommari >= minSummary) & (sommari <= maxSummary)
    
    # Apply mask and sum along axis=0
    filtered = np.where(mask, sommari, 0)
    result = np.sum(filtered, axis=0)
    
    return result


# Example usage
if __name__ == "__main__":
    # Example 1: 2D numpy array
    sommari = np.array([
        [1, 5, 10, 15],   # sommari[0]
        [3, 7, 12, 20],   # sommari[1]
        [2, 6, 11, 18],   # sommari[2]
        [4, 8, 14, 25],   # sommari[3]
    ])
    
    minSummary = 5
    maxSummary = 12
    
    result = sum_sommari_filtered(sommari, minSummary, maxSummary)
    print("2D array result:", result)
    # Values in range [5,12]: sommari[0]=5,10 sommari[1]=7,12 sommari[2]=6,11 sommari[3]=8
    # Sum axis=0: [5+3+2+4, 10+7+6+8, 10+7+6+8, 15+20+18+25] = [14, 31, 31, 78]
    # After filtering (only values 5-12): [0+0+0+0, 10+7+6+8, 10+7+6+8, 0+0+0+0] = [0, 31, 31, 0]
    
    # Example 2: List of 1D arrays
    sommari_list = [
        np.array([1, 5, 10]),
        np.array([3, 7, 12]),
        np.array([2, 6, 11]),
    ]
    
    result_list = sum_sommari_list_filtered(sommari_list, minSummary, maxSummary)
    print("List result:", result_list)
