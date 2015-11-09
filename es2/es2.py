#! /usr/bin/python
#-*- coding: utf-8 -*-

# Scrivere un'applicazione command line che, data in input una directory di
# log, processi i file per estrarre da essi gli errori e li mostri a video
# ordinati a partire dal più recente.

import argparse
import datetime
import os
import re

def list_files(path, ext_list=["txt"]):
    """
    Esegue un walk nel path cercando tutti i file con una delle estensioni
    definite dal parametro ext_list

    Ritorna la lista dei file da leggere
    """
    log_files = []
    for root, dirs, files in os.walk(path):
        for name in files:
            # Lo splice [1:] qui sotto serve a escludere il dot dall'estensione
            if (os.path.splitext(name)[1][1:] in ext_list):
                log_files.append(os.path.join(root, name))
    return log_files

def filter_file(
        f,
        pattern="^(\d{4}\-\d{2}\-\d{2}\s{1}\d{2}\:\d{2}\:\d{2})\,(\d{1})\s{1}(Error\:.*)"):
    """
    Filtra il contenuto del file in modo tale da isolare gli errori

    Ritorna una lista di tuple di tipo (datetime, int, str)
    """
    logs = []
    with open(f, "r") as fd:
        for line in fd:
            try:
                r = re.search(pattern, line).groups()
            except AttributeError:
                continue
            rdate = datetime.datetime.strptime(r[0], "%Y-%m-%d %H:%M:%S")
            logs.append((rdate, int(r[1]), r[2]))

    return logs

def concat(path, ext_list=["txt"]):
    """
    Concatena il contenuto di tutti i file presenti nel path che hanno una
    delle estensioni specificate

    Ritorna una lista di tuple
    """
    logs = []
    log_files = list_files(path, ext_list)
    for f in log_files:
        ff = filter_file(f)
        if ff:
           logs.extend(ff)

    return logs

def sortl(logs):
    # La funzione sort viene automaticamente applicata al primo elemento di una
    # lista di tuple, quindi si ordina per data. Si vogliono i risultati a
    # partire dal più recente, quindi si inverte l'ordine di ordinamento
    return sorted(logs, reverse=True)

def printl(logs, human=False):
    """
    Stampa a schermo il risultato
    """
    print
    print "data".center(22), "lvl", "messaggio"
    for l in logs:
        if human:
            print l[0].strftime("%a, %x %X").ljust(22), str(l[1]).center(3), l[2]
        else:
            print l[0], l[1], l[2]
    print

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="path to log directory")
    parser.add_argument("-e", "--extensions", default="",
                        help="comma separated list of valid estensions for log files")
    parser.add_argument("-r", "--human", action="store_true",
                        help="prints in human-readable format if specified")
    args = parser.parse_args()
    path = args.path
    logs = concat(path, args.extensions.split(",")) if args.extensions else concat(path)

    logs = sortl(logs)
    printl(logs, args.human)
