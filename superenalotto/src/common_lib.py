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
