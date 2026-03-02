import numpy as np


def count_sequences(arr):
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


# ── self-test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    tests = [
        ([1, 2, 3, 5, 6, 8],   [1, 1, 0, 0, 0, 2]),   # seq-3 + seq-2
        ([1, 2, 3, 4, 5, 6],   [0, 0, 0, 0, 1, 1]),   # one seq-6
        ([1, 3, 5, 7, 9, 11],  [0, 0, 0, 0, 0, 0]),   # no sequences
        ([1, 2, 4, 5, 6, 9],   [1, 1, 0, 0, 0, 2]),   # seq-2 + seq-3
        ([1, 2, 3, 4, 6, 7],   [1, 0, 1, 0, 0, 2]),   # seq-4 + seq-2
    ]

    all_ok = True
    for arr, expected in tests:
        result = count_sequences(arr)
        ok = result == expected
        all_ok = all_ok and ok
        status = "OK  " if ok else "FAIL"
        print(f"{status}: {arr} -> {result}  (expected {expected})")

    print("\nAll tests passed!" if all_ok else "\nSome tests FAILED.")
