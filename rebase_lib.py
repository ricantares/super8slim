
from lotteria import Lotteria
import numpy as np
from itertools import combinations
from scipy.special import comb
from scipy import stats
import matplotlib.pyplot as plt

class RebaseLib:
    def __init__(self):
        pass

    def get_combinazioni(self):
        return [comb(6, k, exact=True) for k in range(1,7)] # vettore coefficienti binomiali di 6 elementi in classe k = (1..6)

    def presenze_singola_combinazione(self, combinazioni_base, campione):
        totale_combinazioni = len(combinazioni_base)
        pe = np.empty([0, totale_combinazioni], dtype=int) # vettore di presenze per ogni combinazione di classe k, inizializzato a zero
        for j in range(0, totale_combinazioni): # per ogni singola combinazione in classe k
            cb = np.array(combinazioni_base[j]) # j-esima combinazione della base da esaminare
            ip = 0 # contatore presenze
            for m in range(0, len(campione)): # conta le presenze di una singola combinazione nel campione storico
                if (len(np.setdiff1d(cb, campione[m])) == 0): # se la combinazione e' contenuta nel campione[m]
                    ip += 1 
            pe = np.append(pe, ip)
        return pe
    
    def presenze_k_combinazioni(self, combinazioni_base, campione):
        presenze = [[] for i in range(0,6)]
        for i in range(0,6): # per ognuna delle 6 combinazioni su tutte le classi k
            pe = self.presenze_singola_combinazione(combinazioni_base[i], campione)
            if sum(pe) > 0 or presenze[i] != [] : # se ci sono presenze, aggiungi il vettore di presenze alla lista delle presenze per la classe k
                presenze[i].append(pe)
        return presenze
    
    def calcolo_presenze(self, storico_estrazioni, size_intervallo):
        presenze = [[] for i in range(0,6)]
            
        len_estrazioni = len(storico_estrazioni)
        max_basi = len_estrazioni - size_intervallo

        #print("Calcolo presenze per ogni base:")
        for e in range(max_basi):
            print("Basi analizzate:", e+1, end='\r')
            
            base = storico_estrazioni[e, :].copy()
            campione = storico_estrazioni[e+1:e+1+size_intervallo]  # Prende le righe successive alla prima come matrice di intervallo
            combinazioni_base = [list(combinations(base, k)) for k in range(1,7)] # combinazioni della base

            for i in range(0,6): # per ognuna delle 6 combinazioni su tutte le classi k

                pe = self.presenze_singola_combinazione(combinazioni_base[i], campione)
                if sum(pe) > 0 or presenze[i] != [] : # se ci sono presenze, aggiungi il vettore di presenze alla lista delle presenze per la classe k
                    presenze[i].append(pe)
                    
        return presenze
    
    def calcolo_sommari(self,presenze):
        sommari = [[] for i in range(0,6)]
        vettore_combinazioni = self.get_combinazioni()
        for i in range(0,6):
            for j, presenza in enumerate(presenze[i]):
                s = []
                s.append(int(sum(presenza)))
                s.append(int(np.count_nonzero(presenza)))
                s.append(vettore_combinazioni[i] - int(np.count_nonzero(presenza)))
                s.append(int(max(presenza)))
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
       for i in range(0,6):     
        s = sommari[i]
        #print_dati_grafico(s, i)
        if len(s) > 0: 
            t = np.sum(s, axis=0)
            u = np.round(np.mean(s, axis=0), 2)
            x = np.round(np.std(s, axis=0), 2) 
            v = np.median(s, axis=0)
            wm, wc = stats.mode(s)[0], stats.mode(s)[1]
            #y = np.min(s, axis=0)
            #z = np.max(s, axis=0)
            sk = np.round(stats.skew(s, axis=0), 2)
            # ku = np.round(stats.kurtosis(s, axis=0), 2)  
            # q1 = np.round(np.percentile(s, 25, axis=0), 2)
            # q2 = np.round(np.percentile(s, 75, axis=0), 2)
            q1 = np.round(np.quantile(s, 0.25, axis=0), 2)
            q2 = np.round(np.quantile(s, 0.75, axis=0), 2)
            match i:
                case 0: print(f"\nValori per estratto singolo")
                case 1: print(f"\nValori per coppie di estratti")
                case 2: print(f"\nValori per terne di estratti")
                case 3: print(f"\nValori per quaterne di estratti")
                case 4: print(f"\nValori per cinquine di estratti")
                case 5: print(f"\nValori per sestine di estratti")
            #print(f"- sum: {t}, \n- mean: {u}, \n- std: {x}, \n- median: {v}, \n- mode: {wm}, {wc}, \n- min: {y}, \n- max: {z}")
            print(f"- mean    : {u}")
            print(f"- median  : {v}")
            print(f"- mode    : {wm}, {wc}")
            print(f"- std     : {x}")
            print(f"- skewness: {sk}")
            #print(f"- kurtosis: {ku}")
            print(f"- q1      : {q1}")
            print(f"- q3      : {q2}")
            
            if np.all(abs(sk) <= 0.5):
                print("  Distribuzione simmetrica: ")
            else:
                print("  Distribuzione asimmetrica: ")
                
            print("  (media e deviazione standard):")
            self.print_dati_statistici(s, t, u - x, u + x)
                        
            print("  (quartili):")
            self.print_dati_statistici(s, t, q1, q2)
            
    def print_dati_statistici(self, dati_colonna, somma_colonna, min, max):

        dati_nei_limiti = self.sum_sommari_filtered(dati_colonna, min, max)
        copertura = np.round((dati_nei_limiti / somma_colonna) * 100, 2)
        
        print(f"    Totale presenze                      [range U(k)]: {np.round(min[0], 0)} .. {np.round(max[0], 0)}, copertura: {copertura[0]}%")
        print(f"    Combinazioni con almeno una presenza [range V(k)]: {np.round(min[1], 0)} .. {np.round(max[1], 0)}, copertura: {copertura[1]}%")
        print(f"    Combinazioni senza presenze          [range W(k)]: {np.round(min[2], 0)} .. {np.round(max[2], 0)}, copertura: {copertura[2]}%")
        print(f"    Massima frequenza di presenza        [range Y(k)]: {np.round(min[3], 0)} .. {np.round(max[3], 0)}, copertura: {copertura[3]}%")