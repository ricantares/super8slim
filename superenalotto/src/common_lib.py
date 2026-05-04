"""
Common utilities for SuperEnalotto analysis.
"""

import logging
import random as rnd
import numpy as np


class CommonLib:
    """
    Shared utilities for loading and generating lottery data.
    """
  
    __hystorical_data_file_name = ""  
    __hystorical_data = []
    
    def __init__(self, file_name=None):
        """
        Create a CommonLib instance.
        
        Args:
            file_name: Path to historical data CSV file (optional)
        """
        if (file_name != None):
            self.set_globals(file_name) 

    def set_globals(self, file_name):
        """
        Initialize the class with file path and load data.
        
        Args:
            file_name: Path to historical data CSV file
        """
        self.__hystorical_data_file_name = file_name
        self.__hystorical_data = self.load_data()
        self.__hystorical_data_qty = len(self.__hystorical_data)

    def get_random_extraction(self):
        """
        Generate a random 6-number extraction.
        
        Returns:
            numpy.ndarray: Sorted array of 6 unique numbers in range 1-90
        """
        logging.debug("generazione estrazione")
        extraction = np.random.choice(range(1, 91), size=6, replace=False)
        extraction.sort()
        return np.array(extraction)
    
    def load_data(self, load_rows=None):
        """
        Load historical extraction data from CSV file.
        
        Args:
            load_rows: Number of rows to load (None = all)
        
        Returns:
            numpy.ndarray: 2D array of shape (k, 6) containing extractions
        """
        logging.debug("caricamento dati")
        __hystorical_data = np.loadtxt(
            self.__hystorical_data_file_name, 
            dtype=int, 
            delimiter=';', 
            skiprows=1, 
            usecols=(1, 2, 3, 4, 5, 6), 
            max_rows=load_rows
        )        
        return __hystorical_data
    
    def get_hystorical_data_qty(self):
        """
        Get the count of loaded historical extractions.
        
        Returns:
            int: Number of extractions in memory
        """
        return self.__hystorical_data_qty
    
    def get_last_extraction_date(self):
        """
        Extract the date of the most recent draw from the file.
        
        Returns:
            int: Date as integer (YYYYMMDD format)
        """
        last_extraction_date = 0
        with open(self.__hystorical_data_file_name, 'r') as csv:
            for line_number, line in enumerate(csv.readlines()):
                if line_number == 1:
                    last_extraction_date = int(line.split(";")[0])
                    break
        return last_extraction_date
    
    def count_values_with_coverage(self, data_summary, lower_bounds, upper_bounds):
        """
        Calculate coverage ratio within value ranges for each column.
        
        Uses vectorized NumPy operations for performance.
        
        Args:
            data_summary: 2D array with n columns and m rows
            lower_bounds: Array of n lower bounds
            upper_bounds: Array of n upper bounds
        
        Returns:
            Array of n coverage ratios (0.0 to 1.0)
        """
        cols = len(data_summary[0])
        result = np.zeros(cols, dtype=np.float64)
        
        try:
            data_summary = np.asarray(data_summary, dtype=np.int64)
            lower_bounds = np.asarray(lower_bounds, dtype=np.float64)
            upper_bounds = np.asarray(upper_bounds, dtype=np.float64)
            
            if data_summary.ndim != 2 or data_summary.shape[1] != cols:
                return result
            if lower_bounds.shape != (cols,) or upper_bounds.shape != (cols,):
                return result
            
            if data_summary.size == 0 or data_summary.shape[0] == 0:
                return result
            
            if np.any(lower_bounds > upper_bounds):
                return result
            
            for col_idx in range(cols):
                column_data = data_summary[:, col_idx]
                
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
