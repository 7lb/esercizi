#! /usr/bin/python
#-*- coding: utf-8 -*-

# Necessario per l'internazionalizzazione
#import gettext
#_ = gettext.translation("es3", "./locale").ugettext

import argparse
import requests
import time
import validators
import sys


# Costanti globali
OK_STATUS_LIST = [200, 201, 202, 203, 204, 205, 206, 207, 208, 226]
ERROR_STATUS_LIST = [400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410,
                     411, 412, 413, 414, 415, 416, 417, 418, 419, 420, 421,
                     422, 423, 424, 426, 428, 429, 431, 440, 444, 449, 450,
                     451, 494, 495, 496, 497, 498, 499,
                     500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510,
                     511, 520, 522, 598, 599]
COLOR_SUCCESS = "\033[32m"
COLOR_FAILURE = "\033[31m"
COLOR_RESET = "\033[39m"
WEIGHT_NORMAL = "\033[21m"
WEIGHT_BOLD = "\033[1m"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="file containing the url list to test")
    args = parser.parse_args()

    try:
        good_urls, bad_urls = read_urls_from(args.file)
    except IOError:
        exit("%s: no such file or directory" % args.file)

    if not good_urls:
        exit("No valid urls specified")

    test_urls(good_urls)

    if bad_urls:
        log_urls(bad_urls)
        print 'There are rejected urls. See "rejected_urls.txt" for a list'


def read_urls_from(file_):
    """
    Legge il file specificato linea per linea, validando gli url uno alla
    volta.

    Restituisce due liste di tuple (numero_url, valido, url) dove numero_url
    rappresenta l'ordinale dell'url nella lista originale e valido indica se ha
    passato o meno il test di validità.

    La prima lista è quella degli url validi, la seconda di quelli invalidi
    """
    good_urls = []
    bad_urls = []
    with open(file_, "r") as urls_file:
        for i, url in enumerate(urls_file):
            if validators.url(url):
                good_urls.append((i, True, url.strip()))
            else:
                bad_urls.append((i, False, url.strip()))
    return (good_urls, bad_urls)


def test_urls(url_tuples):
    """
    Testa la lista di url uno alla volta stampando a schermo il risultato.
    """
    for url_tup in url_tuples:
        url = url_tup[2]
        sys.stdout.write("Testing {0}...\r".format(url))
        sys.stdout.flush()
        req, elapsed = test_url(url)
        print_url(url, req, elapsed)


def test_url(url):
    """
    Testa un singolo url (si suppone sia valido, il filtro è eseguito a monte)

    Ritorna l'oggetto request se ha successo, False se fallisce, e il tempo
    impiegato per eseguire la richiesta
    """
    start = time.time()
    req = requests.get(url)
    return (req, time.time() - start)


def log_urls(urls, file_="rejected_urls.txt"):
    """
    Scrive sul file specificato la lista di url non validi, cioè rifiutati
    da validators.url
    """
    # Estrae gli url dalla lista di tuple (numero_url, valido, url)
    urls = [ "%s%s" % (tup[2], "\n") for tup in urls ]
    with open(file_, "w") as fd:
        fd.writelines(urls)


def print_url(url, req, elapsed):
    """
    Stampa a video url, risultato della richiesta (con formattazione dei
    colori) e tempo necessario per eseguire la richiesta. Inoltre logga ragione
    e body della richiesta se il server risponde con un codice delle famiglie
    4xx o 5xx.
    """
    print url,
    if req.status_code in OK_STATUS_LIST:
        print_status(req, COLOR_SUCCESS)
    else:
        print_status(req, COLOR_FAILURE)
        log_body(url, req)
    print "{0} {1:.2f}s".format("time taken: ", elapsed)


def print_status(req, color):
    """
    Stampa a video lo status_code e la reason della richiesta, nel colore
    specificato
    """
    print color + "{0}: {1}".format(
            WEIGHT_BOLD + str(req.status_code) + WEIGHT_NORMAL,
            req.reason) + COLOR_RESET,


def log_body(url, req, file_="failed_responses.txt"):
    """
    Scrive sul file specificato la risposta ricevuta dall'url, solo se è in
    JSON
    """
    with open(file_, "w") as fd:
        try:
            r = req.json()
        except ValueError:
            return
        fd.write("%s: %s\n" % (url, r))

# TODO: elementtree (output xml)
# TODO: mock


if __name__ == "__main__":
    main()
