import numpy as np
from scipy.ndimage import find_objects


def count_sequences(arr):
    """
    Count max consecutive sequences in an ordered array of 6 numbers.
    Returns counts for sequences of length 2,3,4,5,6 and their sum.
    """
    arr = np.array(arr, dtype=int)
    
    # Find consecutive differences (1 = consecutive, !=1 = break)
    diff = np.diff(arr)
    
    # Create binary mask where 1 indicates break in sequence
    breaks = np.concatenate([[1], diff != 1])
    
    # Find positions where sequences start (break or first element)
    seq_start = np.where(breaks)[0]
    seq_end = np.append(seq_start[1:] - 1, len(arr) - 1)
    
    # Calculate lengths of all sequences
    lengths = seq_end - seq_start + 1
    
    # Filter only sequences of length >= 2
    valid_lengths = lengths[lengths >= 2]
    
    # Count only max sequences (not contained in longer ones)
    max_sequences = []
    for i, len_i in enumerate(valid_lengths):
        is_max = True
        for j, len_j in enumerate(valid_lengths):
            if i != j and len_j > len_i:
                start_j, end_j = seq_start[j], seq_end[j]
                start_i, end_i = seq_start[i], seq_end[i]
                if start_i >= start_j and end_i <= end_j:
                    is_max = False
                    break
        if is_max:
            max_sequences.append(len_i)
    
    # Count by length (2,3,4,5,6)
    counts = [np.sum(np.array(max_sequences) == i) for i in range(2, 7)]
    
    return counts + [sum(counts)]


# Test
if __name__ == "__main__":
    tests = [
        ([1, 2, 3, 5, 6, 8], [1, 1, 0, 0, 0, 2]),
        ([1, 2, 3, 4, 5, 6], [0, 0, 0, 0, 1, 1]),
        ([1, 3, 5, 7, 9, 11], [0, 0, 0, 0, 0, 0]),
        ([1, 2, 4, 5, 6, 9], [1, 1, 0, 0, 0, 2]),
    ]
    
    for arr, expected in tests:
        result = count_sequences(arr)
        print(f"{arr} -> {result} (expected: {expected})")
