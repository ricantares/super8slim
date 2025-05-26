""" 
    Test evidenze su un set di estrazioni non ricomprese nello storico
    utilizzato per la redazione delle evidenze stesse

    - ver 1.0 27/10/2023

    Promemoria:
    in una distribuzione normale, nell'intervallo
    [-sigma .. sigma] rientrano il 68,27% dei valori
    [-2*sigma .. 2*sigma] rientrano il 95,45% dei valori
    [-3*sigma .. 3*sigma] rientrano il 99,73% dei valori
"""
import numpy as np
import json
import datetime
import logging
from lotteria import Lotteria

def esamina_combinazioni(storico, test):
    """
        Confronta le combinazioni dell'estrazione di test con un blocco delle successive
        determinando la frequenza media di ogni combinazione

        Ritorna la frequenza rilevata per l'estrazione di test
    """
    freq = storico.freq_combinazioni(test, 0, storico.get_nro_estrazioni_std()) 

    return freq

def esamina_sequenze(storico, test):
    """
        Conta le eventuali sequenze
        di 2 o piu' numeri nell'estrazione di test

        Calcola quindi le frequenze delle sequenza individuate

        Ritorna le sequene trovate
    """

    freq = storico.freq_sequenze(test) 

    return freq


def esamina_intervalli(storico, base, span):
    """
        Calcola la frequenza di estratti contenuti in intervalli di 'span' numeri 
        (es. con span=30 intervalli=1..30, 31..60, 61..90)

        Ritorna a regola relativa alla frequenza dei numeri contenuti in uno specifico intervallo
    """
    
    intervalli = np.arange(1, 91).reshape(90//span, span)
    nro_intervalli = len(intervalli)
    f = storico.freq_intervalli_base(base, intervalli)

    return f

def esamina_singolo_estratto(storico, test):
    """
        Calcola la frequenza di un singolo estratto, presente in una estrazione di test,
        in 15 estrazioni (i.e. 90 singoli estratti) ricavate dalle estrazioni nello storico
        inclusa l'estrazione di test
    """

    freq = storico.freq_singolo_estratto(test, 0)
    
    return np.round(freq, 2)

def esamina_ritardi(storico, test):
    """
        Calcola i ritardi di ogni singolo estratto nell'estrazione di test
    """

    rit = storico.ritardi(test, 0)
    
    return rit

############################################### MAIN #################################################################

def main():
    
    print("Inizio test evidenze", datetime.datetime.now())

    # log file
    logging.basicConfig(filename='superenalotto_test.log', filemode='w', level=logging.INFO)

    # Dizionario delle evidenze (i.e. regole) ricavate dalle successive analisi dei dati storici
    logging.info(f"Inizio test evidenze {datetime.datetime.now()}")

    # Caricamento regole di validazione
    evidenze = {}
    with open('evidenze.json') as file_evidenze:
          evidenze = json.load(file_evidenze)

    # Caricamento dello storico estrazioni da file esterno
    file_storico = "./data/estrazioni_2023_2006.csv"
    ll_s = Lotteria(file_storico)

    # Caricamento delle estrazioni test da file esterno
    file_test = "./data/estrazioni_test_2023.csv"
    ll_t = Lotteria(file_test)

    # Info riassuntive dei dati in esame

    # Costruzione storico
    
    # frequenza combinazioni
    print("Frequenza combinazioni ----------------------")
    amin = np.empty(6, dtype=float)
    amax = np.empty(6, dtype=float)
    for i in range(6):
        amin[i] = evidenze["rules"]["1"]["values"][i]['media'] - evidenze["rules"]["1"]["values"][i]['std']
        if amin[i] < 0: amin[i] = 0
        amax[i] = evidenze["rules"]["1"]["values"][i]['media'] + evidenze["rules"]["1"]["values"][i]['std']

    #print("amin ", amin)
    #print("amax ", amax)

    atot_in = np.zeros(6, dtype=int)
    atot_out = np.zeros(6, dtype=int)
    for i in range(ll_t.get_tot_estrazioni()):
        print("frequenza combinazioni: ",i, end="\r")
        base = ll_t.get_estrazioni()[i]
        freq = esamina_combinazioni(ll_s, base)
        value = np.array(list(freq.values()))
        for j in range(6):
            if amin[j] <= value[j] <= amax[j]: atot_in[j] += 1
            else: atot_out[j] += 1

    for i in range(6):
        print("\nevidenze storico: intervallo [", i+1, "]=[", amin[i], " ", amax[i], "]")
        print("test compresi: ", atot_in[i], " = ", np.round(atot_in[i]/(atot_in[i]+atot_out[i])*100, 2), "%")
        print("test esclusi : ", atot_out[i], " = ", np.round(atot_out[i]/(atot_in[i]+atot_out[i])*100, 2), "%")

    # frequenza sequenze
    print("\nFrequenza sequenze ----------------------")
    amin = np.empty(6, dtype=float)
    amax = np.empty(6, dtype=float)
    for i in range(6):
        amin[i] = evidenze["rules"]["2"]["values"][i]['media'] - evidenze["rules"]["2"]["values"][i]['std']
        if amin[i] < 0: amin[i] = 0
        amax[i] = evidenze["rules"]["2"]["values"][i]['media'] + evidenze["rules"]["2"]["values"][i]['std']

    #print("amin ", amin)
    #print("amax ", amax)

    atot_in = np.zeros(6, dtype=int)
    atot_out = np.zeros(6, dtype=int)
    for i in range(ll_t.get_tot_estrazioni()):
        print("frequenza sequenze: ",i, end="\r")
        base = ll_t.get_estrazioni()[i]
        freq = esamina_sequenze(ll_s, base)
        value = np.array(list(freq.values()))
        for j in range(6):
            if amin[j] <= value[j] <= amax[j]: atot_in[j] += 1
            else: atot_out[j] += 1

    for i in range(6):
        print("\nevidenze storico: intervallo [", i+1, "]=[", amin[i], " ", amax[i], "]")
        print("test compresi: ", atot_in[i], " = ", np.round(atot_in[i]/(atot_in[i]+atot_out[i])*100, 2), "%")
        print("test esclusi : ", atot_out[i], " = ", np.round(atot_out[i]/(atot_in[i]+atot_out[i])*100, 2), "%")

    # frequenza intervallo 30
    print("\nFrequenza intervallo 30 ----------------------")
    span = 30
    intervalli = np.arange(1, 91).reshape(90//span, span)
    ni = len(intervalli)

    amin = np.empty(ni, dtype=float)
    amax = np.empty(ni, dtype=float)
    for i in range(ni):
        amin[i] = evidenze["rules"]["3"]["values"][i]['media'] - evidenze["rules"]["3"]["values"][i]['std']
        if amin[i] < 0: amin[i] = 0
        amax[i] = evidenze["rules"]["3"]["values"][i]['media'] + evidenze["rules"]["3"]["values"][i]['std']

    #print("amin ", amin)
    #print("amax ", amax)

    atot_in = np.zeros(ni, dtype=int)
    atot_out = np.zeros(ni, dtype=int)
    for i in range(ll_t.get_tot_estrazioni()):
        print("frequenza intervalli [30]: ",i, end="\r")
        base = ll_t.get_estrazioni()[i]
        value = esamina_intervalli(ll_s, base, span)
        for j in range(ni):
            if amin[j] <= value[j] <= amax[j]: atot_in[j] += 1
            else: atot_out[j] += 1

    for i in range(ni):
        print("\nevidenze storico: intervallo [", i+1, "]=[", amin[i], " ", amax[i], "]")
        print("test compresi: ", atot_in[i], " = ", np.round(atot_in[i]/(atot_in[i]+atot_out[i])*100, 2), "%")
        print("test esclusi : ", atot_out[i], " = ", np.round(atot_out[i]/(atot_in[i]+atot_out[i])*100, 2), "%")

    # frequenza intervallo 15
    print("\nFrequenza intervallo 15 ----------------------")
    span = 15
    intervalli = np.arange(1, 91).reshape(90//span, span)
    ni = len(intervalli)

    amin = np.empty(ni, dtype=float)
    amax = np.empty(ni, dtype=float)
    for i in range(ni):
        amin[i] = evidenze["rules"]["4"]["values"][i]['media'] - evidenze["rules"]["4"]["values"][i]['std']
        if amin[i] < 0: amin[i] = 0
        amax[i] = evidenze["rules"]["4"]["values"][i]['media'] + evidenze["rules"]["4"]["values"][i]['std']

    #print("amin ", amin)
    #print("amax ", amax)

    atot_in = np.zeros(ni, dtype=int)
    atot_out = np.zeros(ni, dtype=int)
    for i in range(ll_t.get_tot_estrazioni()):
        print("frequenza intervalli [15]: ",i, end="\r")
        base = ll_t.get_estrazioni()[i]
        value = esamina_intervalli(ll_s, base, span)
        for j in range(ni):
            if amin[j] <= value[j] <= amax[j]: atot_in[j] += 1
            else: atot_out[j] += 1

    for i in range(ni):
        print("\nevidenze storico: intervallo [", i+1, "]=[", amin[i], " ", amax[i], "]")
        print("test compresi: ", atot_in[i], " = ", np.round(atot_in[i]/(atot_in[i]+atot_out[i])*100, 2), "%")
        print("test esclusi : ", atot_out[i], " = ", np.round(atot_out[i]/(atot_in[i]+atot_out[i])*100, 2), "%")

    # frequenza singolo estratto
    
    print("\nFrequenza singolo estratto ----------------------")
    #amin = np.empty(6, dtype=int)
    min = evidenze["rules"]["5"]["values"][0]['media'] - evidenze["rules"]["5"]["values"][0]['std']
    max = evidenze["rules"]["5"]["values"][0]['media'] + evidenze["rules"]["5"]["values"][0]['std']
    tot_in = 0
    tot_out = 0
    for i in range(ll_t.get_tot_estrazioni()):
        base = ll_t.get_estrazioni()[i]
        freq = esamina_singolo_estratto(ll_s, base)
        #print("freq: ", freq)
        if min <= freq <= max: tot_in += 1
        else: tot_out += 1
    print("evidenze storico: intervallo=[", min, " ", max, "]")
    print("test compresi: ", tot_in, " = ", np.round(tot_in/(tot_in+tot_out)*100, 2), "%")
    print("test esclusi : ", tot_out, " = ", np.round(tot_out/(tot_in+tot_out)*100, 2), "%")

    # numeri ritardatari
    
    print("\nNumeri ritardatari ----------------------")
    amin = np.empty(6, dtype=int)
    min_da = evidenze["rules"]["6"]["values"][0]['media'] - evidenze["rules"]["6"]["values"][0]['std']
    min_a  = evidenze["rules"]["6"]["values"][0]['media'] + evidenze["rules"]["6"]["values"][0]['std']
    max_da = evidenze["rules"]["6"]["values"][1]['media'] - evidenze["rules"]["6"]["values"][1]['std']
    max_a  = evidenze["rules"]["6"]["values"][1]['media'] + evidenze["rules"]["6"]["values"][1]['std']
    tot_in = 0
    tot_out = 0
    for i in range(ll_t.get_tot_estrazioni()):
        base = ll_t.get_estrazioni()[i]
        freq = np.sort(esamina_ritardi(ll_s, base))
        #freq1 = np.sort(freq)[0:5]
        #print("base: ", base, " ritardi: ", freq, "", " media: ", np.round(freq.mean(), 1), " sotto: ", (freq <= freq.mean()).sum())
        if (freq[0] <= min_a) and (max_da <= freq[5] and freq[5] <= max_a): tot_in += 1
        else: tot_out += 1
    print("evidenze storico: intervalli=[", min_da, ":", min_a, " ", max_da, ":", max_a,"]")
    print("test compresi: ", tot_in, " = ", np.round(tot_in/(tot_in+tot_out)*100, 2), "%")
    print("test esclusi : ", tot_out, " = ", np.round(tot_out/(tot_in+tot_out)*100, 2), "%")

    print("Fine   test evidenze", datetime.datetime.now())
    logging.info(f"Fine   test evidenze {datetime.datetime.now()}")

if __name__ == "__main__":
    main()