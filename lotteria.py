"""
Classe che implementa attributi e metodi generali 

    - ver 1.0 17/10/2023 - versione base
    - ver 1.1 18/10/2023 - aggiunte funzioni di calcolo combinazioni, 
    - ver 1.2 23/10/2023 - aggiunte funzioni calcolaFrequenze e conta_sequenze
    - ver 1.3 24/10/2023 - rinominate le funzioni 'calcola_*' in 'freq_*',
                           tolte le funzioni di trasformazione

    Nota: manca di gestione degli errori
"""
from scipy.special import comb
import numpy as np
import random as rnd
from itertools import combinations
import csv
import logging

class Lotteria:  
    __nro_estrazioni_std = 90  # Numero standard di estrazioni considerate nell'analisi storica
    __nro_estrazioni_90 = 15  # Numero di estrazioni contenenti 90 singoli estratti
    # __combinazioni = [6, 15, 20, 15, 6, 1]  # Numero di combinazioni semplici di n=6 oggetti in classe k=(1, 2, 3, 4, 5, 6)
                                            # combinazioni = n!/(k!(n-1)!)

    __file_estrazioni = ""  
    __matrice_estrazioni = []
    __tot_estrazioni = 0
    __data_ultima_estrazione = ""
    
    def __init__(self, file_name=None):
        if (file_name != None):
            self.inizializza(file_name) 

    def inizializza(self, file_name):  
        """ Chiamata diretta solo se la classe e' instanziata senza 'file_name'
            Da utilizzare solo per i test
        """
        self.__file_estrazioni = file_name  # file .csv contenente i dati storici delle estrazioni per data decrescente 
        self.__matrice_estrazioni = self.carica_storico() # matrice dati storici completi
        self.__tot_estrazioni = len(self.__matrice_estrazioni) # profondita' storico
        self.__data_ultima_estrazione = self.__trova_ultima_estrazione() # data ultima estrazione caricata nello storico


    def genera_estrazione(self):
        """ Genera un'estrazione casuale di 6 interi:
            - nell'intervallo [1, 90]
            - senza ripetizioni
            - ordinata in ordine crescente
        """
        logging.debug("generazione estrazione")
        estrazione = rnd.sample(range(1, 91), 6)
        estrazione.sort()
        return np.array(estrazione)
    
    def carica_storico(self, load_rows=None):
        """ Carica dal file storico "k" estrazioni (default tutto lo storico)
            in una matrice [kx6]

            Nota: il file contiene una intestazione nella prima riga e la data dell'estrazione nella prima colonna;
                  entrambi i valori non sono da considerare ai fini del caricamento della matrice
        """
        logging.debug("caricamento dati")
        matrice_estrazioni = np.loadtxt(self.__file_estrazioni, dtype=int, delimiter=';', skiprows=1, usecols=(1, 2, 3, 4, 5, 6), max_rows=load_rows)        
        return matrice_estrazioni
    
    def __trova_ultima_estrazione(self):
        """
            Ritorna la data dell'ultima estrazione
            ricavata dalla riga di intestazione del file storico
        """
        ultima_estrazione = 0
        with open(self.__file_estrazioni, 'r') as csv:
            for line_number, line in enumerate(csv.readlines()):
                if line_number == 1:
                    ultima_estrazione = int(line.split(";")[0])
                    break
        return ultima_estrazione
    
    def freq_combinazioni(self, base, init, size):
        """ calcola le frequenze di estrazione delle combinazioni
            possibili di una estrazione base
            in un subset ampio 'size' estrazioni dello storico a partire 
            da una determinata estrazione iniziale (init)

            a partire dalle combinazioni semplici della base
            - con combinazioni = n!/(k!(n-1)!) (i.e. coefficienti binomiali di 6 su k con k=1..6)
            - viene calcolato il numero di volte che una determinata
              combinazione compare nel subset storico 

            restituisce un dizionario contenente, per ogni classe k,
            la media delle frequenze osservate per la classe stessa
        """
        # array contenente le combinazioni semplici della base
        #
        # l'array e' composto da 6 array ognuno contenente 
        # le combinazioni in classe k della base:
        # k ! combinazioni
        # --+-------------
        # 1 !  6
        # 2 ! 15
        # 3 ! 20
        # 4 ! 15
        # 5 !  6
        # 6 !  1
        vettore_combinazioni = [comb(6, k, exact=True) for k in range(1,7)] # vettore coefficienti binomiali di 6 su k
        
        ac = [list(combinations(base, k)) for k in range(1,7)] # combinazioni della base
        s = self.__matrice_estrazioni[init:size+init] # subset storico
        freq = {}
        for i in range(0,6): # per ognuna delle 6 combinazioni su tutte le classi k
            f = np.empty([0, vettore_combinazioni[i]], dtype=int)
            for j in range(0, len(ac[i])): # per ogni singola combinazione in classe k
                c = np.array(ac[i][j]) # combinazione da esaminare
                l = 0 # contatore presenze
                for m in range(0, len(s)): # conta le presenze di una singola combinazione nel subset storico
                    if (len(np.setdiff1d(c, s[m])) == 0): # la combinazione e' contenuta nell'estrazione s[m]
                        l += 1 
                f = np.append(f, l)
            freq[i+1] = np.mean(f)

        return freq

    def freq_sequenze(self, base):
        """ Analisi elementi in sequenza 
            (i.e. serie di elementi la cui differenza e' pari a 1)

            Ritorna un dizionario con con il numero di sequenze trovate per ogni tipo di sequenza
            - estrazione base = [33, 34, 35, 58, 89, 90] 
              => sequenze(b) = [0, 1, 1, 1,] (ove l'indice indica la lunghezza della sequenza, il valore indica la quantita')
            - quindi ci sono una sequenza di 2 numeri (b[2] = 1) e una di 3 numeri (b[3] = 1) 
              in questo caso ritorna il dizionario
                seq = {2 : 1, 3 : 1}
            Nota:
                ritorna un dizionario vuoto (seq = {}) in caso di nessuna sequenza trovata
        """
        y = (base[1:] - base[:-1]) > 1
        i = np.append(np.where(y), len(base) - 1)
        z = np.diff(np.append(-1, i))
        b = np.bincount(z)
        seq = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0}
        for j in range(2, len(b)):
            key = j 
            seq[key] = b[j]

        return seq
    
    def freq_intervalli(self, span):
        """ 
            Conta gli elementi contenuti in intervalli di 'span' numeri
            all'interno dello storico
            Gli intervalli sono un campionamento di numeri presi nel range 1..90

            Calcola e restituisce la media e la deviazione standard del conteggio effettuato

            Nota: la suddivisione in intervalli utilizzata come probabilita' deve essere calcolata
                  come condizionata? (valutare)

        """

        intervalli = np.arange(1, 91).reshape(90//span, span) # sequenze di 'span' numeri 
        f = {}
        for j in range(0, len(intervalli)):
            count = np.empty([0, self.__tot_estrazioni], dtype=int) # elementi di ogni estrazione contenuti nell'intervallo
            for i in range(0, self.__tot_estrazioni):
                d = np.setdiff1d(self.__matrice_estrazioni[i], intervalli[j])
                l = len(self.__matrice_estrazioni[i]) - len(d) # quanti elementi sono nel range
                count = np.append(count, l)
            f[j+1] = {'media' : np.mean(count) , 'std' : np.std(count)}

        return f
    
    def freq_intervalli_base(self, base, intervalli):
        """ 
            Conta gli elementi contenuti in ogni intervallo 
            Gli intervalli sono un campionamento di numeri presi nel range 1..90

        """

        count = np.empty([0, len(intervalli)], dtype=int)
        for j in range(0, len(intervalli)):
            d = np.setdiff1d(base, intervalli[j])
            l = len(base) - len(d) # quanti elementi sono nel range
            count = np.append(count, l)

        return count
    
    def freq_singolo_estratto(self, base, ini):
        """
            Calcola e restituiscela media delle uscite di un singolo estratto in 
            15 estrazioni (15x6 = 90 estratti) dallo storico a partire dalla ini
        """

        fin = self.__nro_estrazioni_90+ini
        s = self.__matrice_estrazioni[ini:fin]
        c = np.empty((0, 6), dtype=int)
        for j in range(6):
            count = len(s[np.any(s == base[j], axis=1)])
            c = np.append(c, count,)
           
        return np.mean(c)
        
    def ritardi(self, base, ini):
        """
            Calcola i ritardi di ogni singolo estratto nell'estrazione base rispetto
            allo storico a partire dalla ini
        """

        size = self.__tot_estrazioni
        s = self.__matrice_estrazioni[ini:size-ini]
        ritardi = np.zeros(6, dtype=int)
        done = np.zeros(6, dtype=int)
        for i in range(size):
            if 0 in done:
                for j in range(6):
                    if done[j] == 0 and base[j] not in s[i]: ritardi[j] += 1
                    else: done[j] = 1
            else: break
           
        return ritardi
    
    ################ getter and setter ############################
    
    def get_nro_estrazioni_std(self):
        return self.__nro_estrazioni_std
    
    def get_nro_estrazioni_90(self):
        return self.__nro_estrazioni_90
    
    def get_file_estrazioni(self):
        return self.__file_estrazioni

    def get_estrazioni(self):  
        return self.__matrice_estrazioni
    
    def get_tot_estrazioni(self):
        return self.__tot_estrazioni
    
    def get_ultima_estrazione(self):
        return self.__data_ultima_estrazione