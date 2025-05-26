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

############################################### MAIN #################################################################

def main():
    
    print("Inizio valutazione pronostici", datetime.datetime.now())

    # log file
    logging.basicConfig(filename='superenalotto_run.log', filemode='w', level=logging.INFO)

    # Dizionario delle evidenze (i.e. regole) ricavate dalle successive analisi dei dati storici
    logging.info(f"Inizio valutazione pronostici {datetime.datetime.now()}")

    # Caricamento regole di validazione
    evidenze = {}
    with open('evidenze.json') as file_evidenze:
          evidenze = json.load(file_evidenze)
    tot_rules = len(evidenze["rules"])

    # Caricamento dello storico estrazioni da file esterno
    file_storico = "./data/estrazioni_2023_2006.csv"
    ll_s = Lotteria(file_storico)

    # Generazione pronostici
    file_test = "./data/estrazioni_test_2023.csv"
    ll_t = Lotteria(file_test)

    pronostici = {}
    for i in range(ll_t.get_tot_estrazioni()):
        base = ll_t.get_estrazioni()[i]
        esiti = [0]*tot_rules
        pronostici[i] = {"estrazione" : base, "esitiOk" : esiti}

    # ######################  Valutazione pronostici
    
    # frequenza combinazioni
    print("Frequenza combinazioni ----------------------")
    nrule = "1"
    lrule = len(evidenze["rules"][nrule]["values"])
    amin = np.empty(lrule, dtype=float)
    amax = np.empty(lrule, dtype=float)
    for i in range(lrule):
        amin[i] = evidenze["rules"][nrule]["values"][i]['media'] - evidenze["rules"][nrule]["values"][i]['std']
        if amin[i] < 0: amin[i] = 0
        amax[i] = evidenze["rules"][nrule]["values"][i]['media'] + evidenze["rules"][nrule]["values"][i]['std']

    #print("amin ", amin)
    #print("amax ", amax)

    atot_in = np.zeros(lrule, dtype=int)
    atot_out = np.zeros(lrule, dtype=int)
    for i in range(ll_t.get_tot_estrazioni()):
        print("frequenza combinazioni: ",i, end="\r")
        base = ll_t.get_estrazioni()[i]
        freq = esamina_combinazioni(ll_s, base)
        value = np.array(list(freq.values()))
        esitiOk = 0
        for j in range(lrule):
            if amin[j] <= value[j] <= amax[j]: 
                atot_in[j] += 1
                esitiOk += 1
            else: atot_out[j] += 1
        if (esitiOk == lrule): pronostici[i]["esitiOk"][int(nrule)] = 1

    for i in range(lrule):
        print("\nevidenze storico: intervallo [", i+1, "]=[", amin[i], " ", amax[i], "]")
        print("test compresi: ", atot_in[i], " = ", np.round(atot_in[i]/(atot_in[i]+atot_out[i])*100, 2), "%")
        print("test esclusi : ", atot_out[i], " = ", np.round(atot_out[i]/(atot_in[i]+atot_out[i])*100, 2), "%")

    # frequenza sequenze
    print("\nFrequenza sequenze ----------------------")
    nrule = "2"
    lrule = len(evidenze["rules"][nrule]["values"])
    amin = np.empty(lrule, dtype=float)
    amax = np.empty(lrule, dtype=float)
    for i in range(lrule):
        amin[i] = evidenze["rules"][nrule]["values"][i]['media'] - evidenze["rules"][nrule]["values"][i]['std']
        if amin[i] < 0: amin[i] = 0
        amax[i] = evidenze["rules"][nrule]["values"][i]['media'] + evidenze["rules"][nrule]["values"][i]['std']

    #print("amin ", amin)
    #print("amax ", amax)

    atot_in = np.zeros(lrule, dtype=int)
    atot_out = np.zeros(lrule, dtype=int)
    for i in range(ll_t.get_tot_estrazioni()):
        print("frequenza sequenze: ",i, end="\r")
        base = ll_t.get_estrazioni()[i]
        freq = esamina_sequenze(ll_s, base)
        value = np.array(list(freq.values()))
        esitiOk = 0
        for j in range(lrule):
            if amin[j] <= value[j] <= amax[j]: 
                atot_in[j] += 1
                esitiOk += 1
            else: atot_out[j] += 1
        if (esitiOk == lrule): pronostici[i]["esitiOk"][int(nrule)] = 1

    for i in range(lrule):
        print("\nevidenze storico: intervallo [", i+1, "]=[", amin[i], " ", amax[i], "]")
        print("test compresi: ", atot_in[i], " = ", np.round(atot_in[i]/(atot_in[i]+atot_out[i])*100, 2), "%")
        print("test esclusi : ", atot_out[i], " = ", np.round(atot_out[i]/(atot_in[i]+atot_out[i])*100, 2), "%")

    # frequenza intervallo 30
    # vengono presi in considerazione i pronostici che ricadono nel 66% dei casi (i.e. 2/3)
    print("\nFrequenza intervallo 30 ----------------------")
    nrule = "3"
    span = 30
    intervalli = np.arange(1, 91).reshape(90//span, span)
    ni = len(intervalli)

    amin = np.empty(ni, dtype=float)
    amax = np.empty(ni, dtype=float)
    for i in range(ni):
        amin[i] = evidenze["rules"][nrule]["values"][i]['media'] - evidenze["rules"][nrule]["values"][i]['std']
        if amin[i] < 0: amin[i] = 0
        amax[i] = evidenze["rules"][nrule]["values"][i]['media'] + evidenze["rules"][nrule]["values"][i]['std']

    #print("amin ", amin)
    #print("amax ", amax)

    atot_in = np.zeros(ni, dtype=int)
    atot_out = np.zeros(ni, dtype=int)
    for i in range(ll_t.get_tot_estrazioni()):
        print("frequenza intervalli [30]: ",i, end="\r")
        base = ll_t.get_estrazioni()[i]
        value = esamina_intervalli(ll_s, base, span)
        esitiOk = 0
        for j in range(ni):
            if amin[j] <= value[j] <= amax[j]: 
                atot_in[j] += 1
                esitiOk += 1
            else: atot_out[j] += 1
        if (esitiOk >= int(ni*2/3)): pronostici[i]["esitiOk"][int(nrule)] = 1

    for i in range(ni):
        print("\nevidenze storico: intervallo [", i+1, "]=[", amin[i], " ", amax[i], "]")
        print("test compresi: ", atot_in[i], " = ", np.round(atot_in[i]/(atot_in[i]+atot_out[i])*100, 2), "%")
        print("test esclusi : ", atot_out[i], " = ", np.round(atot_out[i]/(atot_in[i]+atot_out[i])*100, 2), "%")

    # frequenza intervallo 15
    print("\nFrequenza intervallo 15 ----------------------")
    nrule = "4"
    span = 15
    intervalli = np.arange(1, 91).reshape(90//span, span)
    ni = len(intervalli)

    amin = np.empty(ni, dtype=float)
    amax = np.empty(ni, dtype=float)
    for i in range(ni):
        amin[i] = evidenze["rules"][nrule]["values"][i]['media'] - evidenze["rules"][nrule]["values"][i]['std']
        if amin[i] < 0: amin[i] = 0
        amax[i] = evidenze["rules"][nrule]["values"][i]['media'] + evidenze["rules"][nrule]["values"][i]['std']

    #print("amin ", amin)
    #print("amax ", amax)

    atot_in = np.zeros(ni, dtype=int)
    atot_out = np.zeros(ni, dtype=int)
    for i in range(ll_t.get_tot_estrazioni()):
        print("frequenza intervalli [15]: ",i, end="\r")
        base = ll_t.get_estrazioni()[i]
        value = esamina_intervalli(ll_s, base, span)
        esitiOk = 0
        for j in range(ni):
            if amin[j] <= value[j] <= amax[j]: 
                atot_in[j] += 1
                esitiOk += 1
            else: atot_out[j] += 1
        if (esitiOk >= int(ni*2/3)): pronostici[i]["esitiOk"][int(nrule)] = 1

    for i in range(ni):
        print("\nevidenze storico: intervallo [", i+1, "]=[", amin[i], " ", amax[i], "]")
        print("test compresi: ", atot_in[i], " = ", np.round(atot_in[i]/(atot_in[i]+atot_out[i])*100, 2), "%")
        print("test esclusi : ", atot_out[i], " = ", np.round(atot_out[i]/(atot_in[i]+atot_out[i])*100, 2), "%")

    # frequenza singolo estratto
    
    print("\nFrequenza singolo estratto ----------------------")
    nrule = "5"
    lrule = len(evidenze["rules"][nrule]["values"])
    amin = np.empty(6, dtype=int)
    min = evidenze["rules"][nrule]["values"][0]['media'] - evidenze["rules"][nrule]["values"][0]['std']
    max = evidenze["rules"][nrule]["values"][0]['media'] + evidenze["rules"][nrule]["values"][0]['std']
    tot_in = 0
    tot_out = 0
    for i in range(ll_t.get_tot_estrazioni()):
        base = ll_t.get_estrazioni()[i]
        freq = esamina_singolo_estratto(ll_s, base)
        #print("freq: ", freq)
        esitiOk = 0
        if min <= freq <= max: 
            tot_in += 1
            esitiOk += 1
        else: tot_out += 1
        if (esitiOk > 0): pronostici[i]["esitiOk"][int(nrule)] = 1

    print("evidenze storico: intervallo=[", min, " ", max, "]")
    print("test compresi: ", tot_in, " = ", np.round(tot_in/(tot_in+tot_out)*100, 2), "%")
    print("test esclusi : ", tot_out, " = ", np.round(tot_out/(tot_in+tot_out)*100, 2), "%")

    print("Risultati:\n")
    for i in range(ll_t.get_tot_estrazioni()):
        #r = 0
        #n = pronostici[i]["esitiOk"]
        #while n:
        #    r, n = r + n % 10, n // 10
        r = sum(pronostici[i]["esitiOk"])
        if (r > 3): 
            print("pronostico[{}]: {}".format(i, pronostici[i]))

    print("\nFine   valutazione pronostici", datetime.datetime.now())
    logging.info(f"Fine   valutazione pronostici {datetime.datetime.now()}")

if __name__ == "__main__":
    main()