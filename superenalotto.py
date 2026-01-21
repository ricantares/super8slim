""" Analisi dei dati storici (storico estrazioni)
    I dati ricavati dall'analisi dello storico delle estrazioni sono caricate in un json come successive
    regole di validazione dei pronostici
    - ver 1.0 16/10/2023
"""
import numpy as np
import json
import datetime
import logging
from lotteria import Lotteria

def esamina_combinazioni(ll):
    """
        Fissa una estrazione dallo storico e ne determina le combinazioni
        in classe k=1..6 dei 6 numeri estratti
        Confronta ogni combinazione della estrazione fissata con le estrazioni precedenti
        determinando la frequenza media di ogni combinazione
        (i.e. quante volte in media la combinazione di k numeri della estrazione fissata compaiono 
        nelle precedenti; es.
              data l'estrazione base
                1,13,17,34,57,84 
              e una delle possibili combinazioni in classe 2 dei singoli estratti
                13, 17
              si calcola la frequenza media della coppia di numeri 13, 17 nelle
              estrazioni precedenti a quella base)
        Ripete il calcolo per ogni estrazione/blocco calcolando
        infine la media delle medie e la relativa deviazione standard

        Ritorna la regola relativa alla frequenza di ogni combinazione
        mediata sugli n blocchi dello storico 
    """
    size = ll.get_nro_estrazioni_std()
    ff = np.empty([0, 6], dtype=int)
    for k in range(0, len(ll.get_estrazioni())-size):
        print("esamina_combinazioni: ", k, end="\r")
        f = ll.freq_combinazioni(ll.get_estrazioni()[k], k+1, size) # frequenza combinazioni k-esima estrazione su un blocco di 'size' estrazioni
        a = list(f.values())
        ff = np.append(ff, [a], axis=0)
    print("\n")

    rule = {}
    rule["content"] = "Frequenza estrazione combinazioni"
    rule["values"] = [{}] * 6
    for ii in range(0, 6):
        rule["values"][ii] = {"type": ii+1, "media": np.round(np.mean(ff[:,ii]), 2), "std": np.round(np.std(ff[:,ii]), 2)}

    return rule

def esamina_sequenze(ll):
    """
        Per ogni estrazione nello storico conta le eventuali sequenze
        di 2 o piu' numeri 

        Calcola quindi le frequenze delle sequenza individuate

        Ritorna la regola relativa alla presenza di sequenze in tutto lo storico
    """
    ff = np.empty([0, 6], dtype=int)
    for k in range(0, ll.get_tot_estrazioni()):
        print("esamina_sequenze: ", k, end="\r")
        f = ll.freq_sequenze(ll.get_estrazioni()[k])
        a = list(f.values())
        ff = np.append(ff, [a], axis=0)
    print("\n")

    rule = {}
    rule["content"] = "Frequenza sequenze"
    rule["values"] = [{}] * 6
    for ii in range(0, 6):
        rule["values"][ii] = {"type": ii+1, "media": np.round(np.mean(ff[:,ii]), 2), "std": np.round(np.std(ff[:,ii]), 2)}

    return rule

def esamina_intervalli(ll, span):
    """
        Calcola la frequenza di estratti contenuti in intervalli di 'span' numeri 
        (es. con span=30 intervalli=1..30, 31..60, 61..90)

        Ritorna la regola relativa alla frequenza dei numeri contenuti in uno specifico intervallo
    """
 
    nro_intervalli = 90//span
    ff = np.empty([0, nro_intervalli], dtype=int)
    print("esamina_intervalli [", span,"]")
    f = ll.freq_intervalli(span)

    rule = {}
    rule["content"] = "Frequenza intervalli da " + str(span) + " numeri"
    rule["values"] = [{}] * nro_intervalli
    for ii in range(0, nro_intervalli):
        rule["values"][ii] = {"type": ii+1, "media": np.round(f[ii+1]['media'], 2), "std": np.round(f[ii+1]['std'], 2)}

    return rule

def esamina_singolo_estratto(ll):
    """
        Calcola la frequenza di un singolo estratto in 15 estrazioni (i.e. 90 singoli estratti) 
        su tutto lo storico (esaminato a passi di 15 estrazioni)
    """

    freq = np.array([], dtype=float)
    for k in range(ll.get_tot_estrazioni() - ll.get_nro_estrazioni_90()):
        print( "esamina_singolo_estratto: ",k, end="\r")
        base = ll.get_estrazioni()[k]
        a = ll.freq_singolo_estratto(base, k+1)
        freq = np.append(freq, [a])
    print("\n")
    
    rule = {}
    rule["content"] = "Frequenza singolo estratto in " + str(ll.get_nro_estrazioni_90()) + " estrazioni"
    rule["values"] = [{}] 
    rule["values"][0] = {"type": 1, "media": np.round(np.mean(freq), 2), "std": np.round(np.std(freq), 2)}

    return rule

def esamina_ritardi():
    """
        Riporta i dati osservati sui ritardi:
        - 81% delle estrazioni ha un ritardo minimo inferiore a 4 estrazioni consecutive (1.5 +/- 1.5)
        - 85% delle estrazioni ha un ritardo massimo compreso fra 11 e 53 estrazioni consecutive (32.0 +/- 21.0)
    """

    media_ritardi_min = 1.5
    std_ritardi_min = 1.5
    media_ritardi_max = 32.0
    std_ritardi_max = 21.0

    rule = {}
    rule["content"] = "Frequenza numeri ritardatari"
    rule["values"] = [{}] * 2
    rule["values"][0] = {"type": 1, "media": media_ritardi_min, "std": std_ritardi_min}
    rule["values"][1] = {"type": 2, "media": media_ritardi_max, "std": std_ritardi_max}

    return rule

def esamina_ritardi(ll):
    """
    Suggerita da copilot (da verificare)
    Calcola la percentuale di frequenza dei ritardi per ogni numero.
    Per ogni estrazione, determina il ritardo di ogni numero (quante estrazioni 
    sono passate dall'ultima volta che è uscito).
    Ritorna un dizionario con le statistiche dei ritardi.
    """
    # Inizializza array per tenere traccia dell'ultima estrazione di ogni numero
    ultima_estrazione = np.zeros(91, dtype=int)  # indice 0 non usato
    frequenze_ritardi = {}  # dizionario numero -> lista ritardi
    
    # Inizializza il dizionario delle frequenze
    for i in range(1, 91):
        frequenze_ritardi[i] = []
    
    estrazioni = ll.get_estrazioni()
    for idx, estrazione in enumerate(estrazioni):
        # Per ogni numero da 1 a 90
        for num in range(1, 91):
            if num in estrazione:
                # Se il numero è presente nell'estrazione corrente
                if ultima_estrazione[num] > 0:  # se non è la prima volta che esce
                    ritardo = idx - ultima_estrazione[num]
                    frequenze_ritardi[num].append(ritardo)
                ultima_estrazione[num] = idx
    
    # Calcola statistiche
    statistiche = {}
    for num in range(1, 91):
        if frequenze_ritardi[num]:
            ritardi = np.array(frequenze_ritardi[num])
            statistiche[num] = {
                'media': np.round(np.mean(ritardi), 2),
                'std': np.round(np.std(ritardi), 2),
                'max': int(np.max(ritardi)),
                'min': int(np.min(ritardi))
            }
    
    # Crea il formato rule per la compatibilità con il resto del codice
    rule = {}
    rule["content"] = "Statistiche ritardi per numero"
    rule["values"] = [{}]
    rule["values"][0] = {"type": 1, "statistiche": statistiche}
    
    return rule
############################################### MAIN #################################################################

def main():
    
    print("Inizio analisi evidenze", datetime.datetime.now())

    # log file
    logging.basicConfig(filename='superenalotto.log', filemode='w', level=logging.INFO)

    # Dizionario delle evidenze (i.e. regole) ricavate dalle precedenti analisi dei dati storici
    logging.info(f"Inizio analisi evidenze {datetime.datetime.now()}")
    evidenze = {}

    # Caricamento dello storico estrazioni da file esterno
    file_estrazione = "./data/estrazioni_2026_2006.csv"
    ll = Lotteria(file_estrazione)
    storico_completo = ll.get_estrazioni()

    # Info riassuntive dei dati in esame
    evidenze["origine_dati"] = file_estrazione
    evidenze["ultima_estrazione"] = ll.get_ultima_estrazione()
    evidenze["elementi_storico"] = ll.get_tot_estrazioni()
    evidenze["rules"] = {}

    # Costruzione storico

    # frequenza combinazioni
    rule = esamina_combinazioni(ll)
    evidenze["rules"][1] = rule

    # frequenza sequenze
    rule = esamina_sequenze(ll)
    evidenze["rules"][2] = rule

    # frequenza intervallo 30
    rule = esamina_intervalli(ll, 30)
    evidenze["rules"][3] = rule

    # frequenza intervallo 15
    rule = esamina_intervalli(ll, 15)
    evidenze["rules"][4] = rule

    # frequenza singolo estratto
    rule = esamina_singolo_estratto(ll)
    evidenze["rules"][5] = rule

    # frequenza singolo estratto
    rule = esamina_ritardi(ll)
    evidenze["rules"][6] = rule
    
    #TODO: stabilito un ritardo massimo accettabile, determinare quanti numeri ritardatari possono essere presenti in una estrazione 
    #todo: in alternativa, determinare il ritardo (oppure i ritardi su diverse ampiezze di ritardo) di una estrazione ottenuto sommando i ritardi dei singoli numeri estratti      
    
    with open('evidenze.json', 'w') as fp:
        json.dump(evidenze, fp, indent=4)

    print("Fine   analisi evidenze", datetime.datetime.now())
    logging.info(f"Fine   analisi evidenze {datetime.datetime.now()}")

if __name__ == "__main__":
    main()