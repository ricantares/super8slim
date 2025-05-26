""" Libreria funzioni helper per il software di gestione 
    del superenalotto
    - ver 1.0 16/10/2023
"""

import numpy as np
import random as rnd
import csv
import logging

# Funzioni

# da verificare
def get_std():
    """ Numero standard di estrazioni considerate nell'analisi storica
    """
    return 90;

# OK
def genera():
    """ Genera un'estrazione casuale di 6 interi:
        - nell'intervallo [1, 90]
        - senza ripetizioni
        - ordinata in ordine crescente
    """
    logging.debug("generazione estrazione")
    estrazione = rnd.sample(range(1, 91), 6)
    estrazione.sort()
    return np.array(estrazione)

# da verificare
def trasforma(estrazione):
    """ Trasforma un array di sei numeri interi compresi fra 1 e 90 (i.e. "numeri estratti")
        in un vettore di 90 elementi in cui l'(i-1)-esimo elemento e' pari a 
        - 1 se l'array originale contiene il valore i 
            (e.g. se nell'estrazione e' presente il numero "32", nell'array trasformato "t" t[31]=1)
        - 0 altrimenti 
            (e.g. se nell'estrazione non e' presente il numero "32", nell'array trasformato "t" t[31]=0)

        Un esempio su un numero ridotto di estratti (es. 3) con un ridotto range di valori possibili (es. 1-5).
        Si ipotizzi l'estrazione [2, 3, 5]
        Questa produrrebbe la trasformazione [0, 1, 1, 0, 1]:
          -  i numeri 2, 3 e 5 sono presenti ("1"), 
          -  i numeri 1 e 4 non sono presenti ("0")
    """
    trasformata = np.zeros(90, dtype=int)
    logging.debug(f"Estrazione: {estrazione}")
    for i in estrazione:
        # In python gli array sono 0-based (come in java)
        trasformata[i-1] = 1
    return trasformata

# da verificare
def goBack(trasformata):
    """ Riporta un vettore trasformato nella sua forma originale
        di elenco di 6 numeri
        (funzione inversa della "trasforma()")
    """
    go_back = []
    for idx, i in enumerate(trasformata):
        if i == 1:
            go_back.append(idx+1)
    return go_back

# OK
def loadCsv(file_name, load_rows=None):
    """ Carica il file csv contenente n estrazioni 
        in una matrice [nx6]

        Nota: il file contiene una intestazione nella prima riga e la data dell'estrazione nella prima colonna;
              entrambi i valori non sono da considerare ai fini del caricamento della matrice
    """
    matrice_estrazioni = np.loadtxt(
        file_name, dtype=int, delimiter=';', skiprows=1, usecols=(1, 2, 3, 4, 5, 6), max_rows=load_rows)
    return matrice_estrazioni


def load_and_transform(file_name, load_rows=None):
    """ Carica da un file csv le estrazioni di un determinato periodo
        e restituisce la matrice le cui righe sono i vettori trasformati
        di ogni singola estrazione
    """
    matrice_estrazioni = loadCsv(file_name, load_rows)
    trasformate = np.empty([0, 90], dtype=int)
    if np.ndim(matrice_estrazioni) > 1:
        for e in matrice_estrazioni:
            trasformate = np.append(trasformate, [trasforma(e)], axis=0)
    else:
        logging.debug(f"Trasforma: {matrice_estrazioni}")
        # Anche un array 1D deve essere trattato come 2D
        trasformate = np.append(trasformate, [trasforma(matrice_estrazioni)], axis=0)
    
    return trasformate

def count_results_std(base, mat_standard):
    """ Calcola il numero di ripetizioni dei risultati di una estrazione "base"
        rispetto alla matrice "standard" composta dalle "len_std" estrazioni temporalmente antecedenti
        l'estrazione "base""
    """

    # Matching
    # Il prodotto righe/colonne fra la matrice delle estrazioni ("mat_standard") e
    # l'estrazione base ("base") restituisce, per ogni estrazione, il numero
    # di risultati presenti sia nell'estrazione base, sia in ognuno degli
    # elementi della matrice delle estrazioni
    
    return np.dot(mat_standard, base)

def count_ripetizioni(blocco_estrazioni):
    """ Quanti estratti si ripetono e per quante volte su un blocoo di estrazioni
        (e.g. se 5, 19, 84, 89 si ripetono 3 volte e  7, 54 si ripetono 2 volte nelle estrazioni
        allora 4 numeri si ripetono 3 volte, 2 numeri si ripetono 2 volte)
    """
    # Vettore identita'
    ident = np.ones(len(blocco_estrazioni), dtype=int) 
    # Trasposta
    trasp = np.transpose(blocco_estrazioni)
    # Numero di volte, su una matrice standard di  estrazioni, in cui un numero risulta estratto
    estr = np.dot(trasp, ident)
    # Frequenza di estrazione (i.e. quanti numeri estratti quante volte)
    return np.bincount(estr)

def count_sequenze(mat_standard):
    """ Analisi elementi in sequenza (sw copiato, ma devo capire come funziona esattamente)
        Trova il totale di numeri in sequenza
        Es:
         - estrazione(estr) = [1, 1, 0, 0, 0, 1, 1, 1, 0] 
         => sequenza(z) = [2, 3, 3, 1]
         => valori contenuti in ogni sequenza(dd) = [1, 0, 1, 0]
        Confrontando z e dd e considerando solo i numeri estratti (i.e. dd=1)
        si possono ottenere le sequenze presenti nell'estrazione
        Es:
         - ci sono una sequenza di 2 numeri (dd[0] = 1, z[0] = 2) 
           e una di 3 numeri (dd[2] = 1, z[2] = 3) 
    """

    n = len(mat_standard)
    y = mat_standard[1:] != mat_standard[:-1]  # contiene "True" se due numeri adiacenti non sono in sequenza, "False" altrimenti
    i = np.append(np.where(y), n - 1) # contiene "True" per ogni rottura di sequenza, "False" altrimenti
    z = np.diff(np.append(-1, i)) # contiene il numero di elementi per ogni sequenza individuata
    dd = np.empty([0, len(i)], dtype=int)
    seq = np.empty([0, 3], dtype=int)
    for r in i:
        dd = np.append(dd, mat_standard[r])
        for q, s in enumerate(dd):
            # quanti estratti sono in sequenza e quanto e' lunga la sequenza?
            if s and z[q] > 1:
                # interessano solo le sequenze di numeri presenti nell'estrazione (i.e. ="1")
                seq = np.append(seq, z[q])
        
    return seq

def get_intervalli(span):
    """ Intervalli da "span" numeri
    """

    intervalli = np.empty([90//span, 90], dtype=int)
    if span == 30:
        intervalli[0] = np.hstack((np.ones(30, dtype=int), np.zeros(60, dtype=int)))
        intervalli[1] = np.hstack((np.zeros(30, dtype=int), np.ones(30, dtype=int), np.zeros(30, dtype=int)))
        intervalli[2] = np.hstack((np.zeros(60, dtype=int), np.ones(30, dtype=int)))
    if span == 15:
        intervalli[0] = np.hstack((np.ones(15, dtype=int), np.zeros(75, dtype=int)))
        intervalli[1] = np.hstack((np.zeros(15, dtype=int), np.ones(15, dtype=int), np.zeros(60, dtype=int)))
        intervalli[2] = np.hstack((np.zeros(30, dtype=int), np.ones(15, dtype=int), np.zeros(45, dtype=int)))
        intervalli[3] = np.hstack((np.zeros(45, dtype=int), np.ones(15, dtype=int), np.zeros(30, dtype=int)))
        intervalli[4] = np.hstack((np.zeros(60, dtype=int), np.ones(15, dtype=int), np.zeros(15, dtype=int)))
        intervalli[5] = np.hstack((np.zeros(75, dtype=int), np.ones(15, dtype=int)))

    return intervalli

def analisi_intervallo(intervalli, base):
    """ Distribuzione estratti negli intervalli da span numeri su una estrazione
    """

    rd = np.empty([0, len(intervalli)], dtype=int)
    for i in range(len(intervalli)):
        rd = np.append(rd, np.dot(base, intervalli[i]))
    #np.hstack((np.dot(estr, i1), np.dot(estr, i2), np.dot(estr, i3)))
    #print("new rd :\n", rd)
    #print("old rd :\n", np.hstack((np.dot(base, intervalli[0]), np.dot(base, intervalli[1]), np.dot(base, intervalli[2]))))
    return rd