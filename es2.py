#! /usr/bin/python
#-*- coding: utf-8 -*-

# Scrivere un'applicazione command line che, data in input una directory di
# log, processi i file per estrarre da essi gli errori e li mostri a video
# ordinati a partire dal più recente.

# È opportuno indicare i file dal quale gli errori provengono?
# Nota: Il programma prima legge tutte le linee di tutti i file nella directory
# specificata, poi filtra solo le linee di errore. In caso di molti file di log
# questo è inefficiente, sarebbe meglio leggere ogni file riga per riga e, se
# la linea di testo è un errore solo allora aggiungerlo al testo salvato in
# memoria

import datetime
import os
import sys

def printUsage():
    """
    Stampa a schermo i parametri del programma
    """
    print "Usage: %s path" % sys.argv[0]

if __name__ == "__main__":
    if (len(sys.argv) < 2):
        printUsage()
        exit()
    path = sys.argv[1]
    txt  = ''
    # Ciclo per concatenare il contenuto dei file di log
    # Qui si va a supporre che nel path siano presenti *solo* i file che ci
    # interessano. listdir non lista le directory speciali "." e ".." quindi
    # non dovrebbero esserci problemi per un eventuale walk indesiderato
    # attraverso il filesystem
    for f in os.listdir(path):
        inf  = open(path + f, "r")
        txt += inf.read()
        inf.close()
    # Questa list comprehension crea una lista di tuple.
    # Ogni tupla ha due elementi: la data del messaggio di log in prima
    # posizione e il mesasggio stesso in seconda posizione.
    # Le singole linee di testo sono ottenute splittando il contenuto dei due
    # file ai caratteri di newline; siccome i file stessi terminano con un
    # carattere di newline l'ultimo elemento anziché essere una linea di testo
    # sarà una stringa vuota, quindi evito di considerarla con lo splice [:-1]
    # La list comprehension conterrà in output solo le stringe di testo che
    # contengono la sottostringa "Error", in modo tale da isolare gli errori
    logs =  [
            tuple(line.split(",", 1))
            for line in txt.split('\n')[:-1]
            if "Error" in line
            ]
    # Siccome le tuple sono immutabili si genera una nuova lista di tuple,
    # questa volta aventi come primo elemento un oggetto datetime che viene
    # creato parsando la data e l'ora secondo il formato dei file di log;
    # il secondo elemento delle tuple viene lasciato invariato
    logs =  [
            (datetime.datetime.strptime(l[0], "%Y-%m-%d %H:%M:%S"), l[1])
            for l in logs
            ]
    # La funzione sort viene automaticamente applicata al primo elemento di una
    # lista di tuple, quindi si ordina per data. Si vogliono i risultati a
    # partire dal più recente, quindi si inverte l'ordine di ordinamento
    logs.sort(reverse=True)
    # Infine si stampa il risultato
    for l in logs:
        print l[0], l[1]
