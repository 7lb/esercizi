#! /usr/bin/python
#-*- coding: utf-8 -*-

# Necessario per l'internazionalizzazione
#import gettext
#_ = gettext.translation("es3", "./locale").ugettext

import argparse
import os
import requests
import sys
import time
import validators
import xml.etree.ElementTree as ET


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
PROGRAM_DIR = os.path.dirname(os.path.realpath(__file__))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="file containing the url list to test")
    parser.add_argument("-x", "--xml",
                        help="xml output location")
    parser.add_argument("-s", "--silent", action="store_true",
                        help="suppress stdout output")
    args = parser.parse_args()

    xml_data = []

    try:
        good_urls, bad_urls = read_urls_from(args.file)
    except IOError:
        exit("%s: no such file or directory" % args.file)

    if not good_urls:
        exit("No valid urls specified")

    for url_tup in good_urls:
        url = url_tup[1]
        if not args.silent:
            sys.stdout.write("Testing {0}...\r".format(url))
            sys.stdout.flush()
        req, elapsed = test_url(url)
        if args.xml:
            xml_data.append(make_xml_tuple(url_tup, req, elapsed))
        if not args.silent:
            print_url(url, req, elapsed)

    if bad_urls:
        log_urls(bad_urls)
        print 'There are rejected urls. See "rejected_urls.txt" for a list'

    if args.xml:
        write_xml(args.xml, xml_data)


def read_urls_from(file_):
    """
    Legge il file specificato linea per linea, validando gli url uno alla
    volta.

    Restituisce due liste di tuple (numero_url, url) dove numero_url
    rappresenta l'ordinale dell'url nella lista originale.

    La prima lista è quella degli url validi, la seconda di quelli invalidi
    """
    good_urls = []
    bad_urls = []
    with open(file_, "r") as urls_file:
        for i, url in enumerate(urls_file):
            if validators.url(url):
                good_urls.append((i, url.strip()))
            else:
                bad_urls.append((i, url.strip()))
    return (good_urls, bad_urls)


def test_url(url):
    """
    Testa un singolo url (si suppone sia valido, il filtro è eseguito a monte)

    Ritorna l'oggetto request se ha successo, False se fallisce, e il tempo
    impiegato per eseguire la richiesta
    """
    start = time.time()
    req = requests.get(url)
    return (req, time.time() - start)


def log_urls(urls, file_=os.path.join(PROGRAM_DIR, "rejected_urls.txt")):
    """
    Scrive sul file specificato la lista di url non validi, cioè rifiutati
    da validators.url
    """
    # Estrae gli url dalla lista di tuple (numero_url, url)
    urls = [ "%s%s" % (tup[1], "\n") for tup in urls ]
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
    elif req.status_code in ERROR_STATUS_LIST:
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
            req.reason) \
    + COLOR_RESET,


def log_body(url, req, file_=os.path.join(PROGRAM_DIR, "failed_responses.txt")):
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


def write_xml(file_, xml_data):
    """
    Scrive sul file xml specificato il risultato del test. Ogni url ha la
    seguente struttura xml:

    <url num="n" value="URL">
        <status>status_code</status>
        <time>elapsed</time>
        <response>JSON response</response>
    </url>

    dove n è l'ordinale dell'URL testato all'interno del file originale, URL è
    l'url testato, status_code è il codice di stato ritornato dal test, time è
    il tempo che è stato necessario alla richiesta e response è il contenuto in
    JSON dela risposta, se presente
    """
    root = ET.Element("urls")
    for elem in xml_data:
        url = ET.SubElement(root, "url")
        url.set("num", str(elem[0]))
        url.set("value", elem[1])
        status = ET.SubElement(url, "status")
        status.text = str(elem[2])
        time = ET.SubElement(url, "time")
        time.text = str(elem[3])
        response = ET.SubElement(url, "response")
        response.text = str(elem[4])
    tree = ET.ElementTree(root)
    tree.write(file_)


# TODO: mock


def make_xml_tuple(url_tup, req, elapsed):
    """
    Costruisce una tupla con tutti i dati necessari per l'output xml
    """
    json_content = ""
    try:
        json_content = req.json()
    except ValueError:
        pass
    xml_data = list(url_tup)
    xml_data.extend([req.status_code, elapsed, json_content])
    return xml_data

if __name__ == "__main__":
    main()
