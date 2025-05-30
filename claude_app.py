import numpy as np
import pandas as pd
from typing import List, Tuple, Dict
import csv
from collections import defaultdict

class LotteryAnalyzer:
    """
    Analizzatore per calcolare i ritardi delle estrazioni della lotteria.
    """
    
    def __init__(self):
        self.extractions = []  # Lista delle estrazioni (dalla più recente alla più antica)
        self.delays = []  # Lista di tutti i ritardi r(k,j)
    
    def load_data_from_file(self, filename: str) -> None:
        """
        Carica i dati da un file CSV.
        Il file deve contenere una estrazione per riga con 6 numeri separati da virgola.
        """
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    # Converte i numeri da stringa a int e li ordina
                    numbers = sorted([int(num.strip()) for num in row if num.strip()])
                    if len(numbers) == 6:
                        self.extractions.append(numbers)
            print(f"Caricati {len(self.extractions)} estrazioni dal file {filename}")
        except FileNotFoundError:
            print(f"File {filename} non trovato")
        except Exception as e:
            print(f"Errore nel caricamento del file: {e}")
    
    def load_data_from_list(self, data: List[List[int]]) -> None:
        """
        Carica i dati da una lista di liste.
        Ogni sottolista deve contenere 6 numeri.
        """
        self.extractions = []
        for extraction in data:
            if len(extraction) == 6:
                # Ordina i numeri e li aggiunge
                self.extractions.append(sorted(extraction))
        print(f"Caricati {len(self.extractions)} estrazioni dalla lista")
    
    def calculate_delays(self) -> None:
        """
        Calcola tutti i ritardi r(k,j) per ogni numero di ogni estrazione.
        """
        self.delays = []
        n_extractions = len(self.extractions)
        
        # Per ogni estrazione j (dalla più recente alla più antica)
        for j in range(n_extractions):
            current_extraction = self.extractions[j]
            
            # Per ogni numero k nell'estrazione j
            for k in current_extraction:
                # Cerca la precedente occorrenza del numero k
                delay = self._find_delay(k, j)
                if delay is not None:
                    self.delays.append(delay)
        
        print(f"Calcolati {len(self.delays)} ritardi")
    
    def _find_delay(self, number: int, current_index: int) -> int:
        """
        Trova il ritardo di un numero rispetto alla sua precedente occorrenza.
        
        Args:
            number: Il numero di cui calcolare il ritardo
            current_index: L'indice dell'estrazione corrente
        
        Returns:
            Il ritardo in giorni, o None se non trova occorrenze precedenti
        """
        # Cerca nelle estrazioni successive (più vecchie) a partire da current_index + 1
        for m in range(current_index + 1, len(self.extractions)):
            if number in self.extractions[m]:
                # Il ritardo è la differenza di giorni tra le estrazioni
                delay = m - current_index
                return delay
        
        # Se non trova il numero nelle estrazioni precedenti
        return None
    
    def calculate_statistics(self) -> Dict[str, float]:
        """
        Calcola le statistiche sui ritardi: media, mediana e scarto quadratico medio.
        
        Returns:
            Dizionario con le statistiche calcolate
        """
        if not self.delays:
            print("Nessun ritardo calcolato. Eseguire prima calculate_delays()")
            return {}
        
        delays_array = np.array(self.delays)
        
        statistics = {
            'media': np.mean(delays_array),
            'mediana': np.median(delays_array),
            'scarto_quadratico_medio': np.std(delays_array),
            'varianza': np.var(delays_array),
            'min': np.min(delays_array),
            'max': np.max(delays_array),
            'totale_ritardi': len(delays_array)
        }
        
        return statistics
    
    def print_statistics(self) -> None:
        """
        Stampa le statistiche in formato leggibile.
        """
        stats = self.calculate_statistics()
        if not stats:
            return
        
        print("\n" + "="*50)
        print("STATISTICHE DEI RITARDI")
        print("="*50)
        print(f"Totale ritardi calcolati: {stats['totale_ritardi']}")
        print(f"Media dei ritardi: {stats['media']:.2f} giorni")
        print(f"Mediana dei ritardi: {stats['mediana']:.2f} giorni")
        print(f"Scarto quadratico medio: {stats['scarto_quadratico_medio']:.2f} giorni")
        print(f"Varianza: {stats['varianza']:.2f}")
        print(f"Ritardo minimo: {stats['min']} giorni")
        print(f"Ritardo massimo: {stats['max']} giorni")
        print("="*50)
    
    def get_delay_distribution(self) -> Dict[int, int]:
        """
        Restituisce la distribuzione dei ritardi.
        
        Returns:
            Dizionario con ritardo -> frequenza
        """
        if not self.delays:
            return {}
        
        distribution = defaultdict(int)
        for delay in self.delays:
            distribution[delay] += 1
        
        return dict(distribution)
    
    def print_delay_distribution(self, max_show: int = 20) -> None:
        """
        Stampa la distribuzione dei ritardi.
        
        Args:
            max_show: Numero massimo di ritardi da mostrare
        """
        distribution = self.get_delay_distribution()
        if not distribution:
            return
        
        print(f"\nDISTRIBUZIONE DEI RITARDI (primi {max_show}):")
        print("-" * 30)
        
        # Ordina per ritardo
        sorted_delays = sorted(distribution.items())
        
        for i, (delay, frequency) in enumerate(sorted_delays[:max_show]):
            percentage = (frequency / len(self.delays)) * 100
            print(f"Ritardo {delay:2d} giorni: {frequency:4d} occorrenze ({percentage:5.1f}%)")
        
        if len(sorted_delays) > max_show:
            print(f"... e altri {len(sorted_delays) - max_show} valori")


def create_sample_data() -> List[List[int]]:
    """
    Crea dati di esempio per testare l'algoritmo.
    """
    np.random.seed(42)  # Per risultati riproducibili
    
    sample_data = []
    # Genera 100 estrazioni di esempio
    for _ in range(100):
        # Genera 6 numeri casuali tra 1 e 90 senza ripetizioni
        numbers = sorted(np.random.choice(range(1, 91), size=6, replace=False).tolist())
        sample_data.append(numbers)
    
    return sample_data


def main():
    """
    Funzione principale di esempio.
    """
    print("ANALIZZATORE RITARDI LOTTERIA")
    print("="*50)
    
    # Crea l'analizzatore
    analyzer = LotteryAnalyzer()
    
    # Opzione 1: Carica dati da file CSV
    # analyzer.load_data_from_file('estrazioni.csv')
    
    # Opzione 2: Usa dati di esempio
    print("Generazione dati di esempio...")
    sample_data = create_sample_data()
    analyzer.load_data_from_list(sample_data)
    
    # Mostra alcune estrazioni di esempio
    print("\nPrime 5 estrazioni (dalla più recente):")
    for i, extraction in enumerate(analyzer.extractions[:5]):
        print(f"Estrazione {i+1}: {extraction}")
    
    # Calcola i ritardi
    print("\nCalcolo dei ritardi in corso...")
    analyzer.calculate_delays()
    
    # Mostra le statistiche
    analyzer.print_statistics()
    
    # Mostra la distribuzione dei ritardi
    analyzer.print_delay_distribution()
    
    # Esempio di come accedere ai dati
    stats = analyzer.calculate_statistics()
    print(f"\nLa media dei ritardi è: {stats['media']:.2f} giorni")


if __name__ == "__main__":
    main()


# ESEMPIO DI UTILIZZO CON DATI PERSONALIZZATI:
"""
# Per utilizzare con i tuoi dati:

# 1. Da file CSV:
analyzer = LotteryAnalyzer()
analyzer.load_data_from_file('il_tuo_file.csv')
analyzer.calculate_delays()
analyzer.print_statistics()

# 2. Da lista Python:
dati_estrazioni = [
    [12, 25, 33, 45, 67, 89],  # Estrazione più recente
    [5, 18, 33, 42, 55, 78],   # Estrazione precedente
    [12, 30, 44, 55, 67, 81],  # ...
    # ... altre estrazioni in ordine cronologico inverso
]

analyzer = LotteryAnalyzer()
analyzer.load_data_from_list(dati_estrazioni)
analyzer.calculate_delays()
stats = analyzer.calculate_statistics()
print(f"Media: {stats['media']:.2f}")
print(f"Mediana: {stats['mediana']:.2f}")
print(f"Scarto quadratico medio: {stats['scarto_quadratico_medio']:.2f}")
"""