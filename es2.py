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

# TODO: leggere solo i file di log (os.path.splitext)
# TODO: leggere i file ricorsivamente nella directory (os.walk)

import argparse
import datetime
import os

def concat(path):
    """
    Concatena il contenuto di tutti i file presenti nel path

    Ritorna il testo concatenato
    """
    txt  = ''
    # Ciclo per concatenare il contenuto dei file di log
    # Qui si va a supporre che nel path siano presenti *solo* i file che ci
    # interessano. listdir non lista le directory speciali "." e ".." quindi
    # non dovrebbero esserci problemi per un eventuale walk indesiderato
    # attraverso il filesystem
    for f in os.listdir(path):
        with open(path + f, "r") as inf:
            txt += inf.read()
    return txt

def makeTupList(txt, formatStr):
    """
    Crea una lista di tuple di tipo (datetime, lvl, str) a partire da una lista
    di stringhe di testo formattate secondo "dataora,livello messaggio" e una
    stringa di formato per parsare data e ora

    Ritorna la lista di tuple
    """
    logs = []
    # Ogni tupla ha tre elementi: la data del messaggio di log in prima
    # posizione, il livello di importanza del mesasggio in seconda posizione e
    # il messaggio stesso in terza posizione.
    # La list comprehension conterrà in output solo le stringe di testo che
    # cominciano la sottostringa "Error", in modo tale da isolare gli errori
    for line in txt:
        tmp             = line.split(",", 1)
        date_str        = tmp[0]
        msg_lvl, msg    = tmp[1].split(" ", 1)
        if msg.startswith("Error"):
            logs.append(tuple([date_str, msg_lvl, msg]))
    # Siccome le tuple sono immutabili si genera una nuova lista di tuple,
    # questa volta aventi come primo elemento un oggetto datetime che viene
    # creato parsando la data e l'ora secondo il formato dei file di log;
    # il secondo elemento delle tuple viene lasciato invariato
    logs =  [
            (datetime.datetime.strptime(log[0], formatStr), log[1], log[2])
            for log in logs
            ]
    return logs

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="path to log directory")
    args = parser.parse_args()
    path = args.path
    txt = concat(path)
    # Le singole linee di testo sono ottenute splittando il contenuto dei due
    # file ai caratteri di newline; siccome i file stessi terminano con un
    # carattere di newline l'ultimo elemento anziché essere una linea di testo
    # sarà una stringa vuota, quindi evito di considerarla con lo splice [:-1]
    logs = makeTupList(txt.split('\n')[:-1], "%Y-%m-%d %H:%M:%S")
    # La funzione sort viene automaticamente applicata al primo elemento di una
    # lista di tuple, quindi si ordina per data. Si vogliono i risultati a
    # partire dal più recente, quindi si inverte l'ordine di ordinamento
    logs.sort(reverse=True)
    # Infine si stampa il risultato
    for l in logs:
        print l[0], l[1], l[2]
