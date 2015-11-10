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
    parser.add_argument("file", type=argparse.FileType("r"),
            help="file containing the url list to test")
    parser.add_argument("-x", "--xml",
                        help="xml output location")
    args = parser.parse_args()

    xml_data = []
    bad_urls = []
    good_urls = []

    #url_data è una tupla (url, timeout)
    for url_data, is_valid in read_urls_from(args.file):
        if is_valid:
            good_urls.append(url_data)
        else:
            bad_urls.append(url_data)

    if not good_urls:
        exit("No valid urls specified")

    for url_data in good_urls:
        if not args.xml:
            sys.stdout.write("Testing {0}...\r".format(url_data[0]))
            sys.stdout.flush()
        resp, elapsed = test_url(url_data[0])
        if args.xml:
            xml_data.append(make_xml_tuple(url_data, resp, elapsed))
        if not args.xml:
            print_url(url_data, resp, elapsed)

    if bad_urls:
        log_urls(bad_urls)
        if not args.xml:
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
    for url_descriptor in file_:
        url, timeout = map(str.strip, url_descriptor.split(","))
        try:
            is_valid = validators.url(url)
        except validators.ValidationFailure:
            is_valid = False
        yield (url, float(timeout)), is_valid


def test_url(url):
    """
    Testa un singolo url (si suppone sia valido, il filtro è eseguito a monte)

    Ritorna l'oggetto request e il tempo impiegato per eseguire la richiesta
    """
    start = time.time()
    resp = requests.get(url)
    return (resp, time.time() - start)


def log_urls(urls, file_=os.path.join(PROGRAM_DIR, "rejected_urls.txt")):
    """
    Scrive sul file specificato la lista di url non validi, cioè rifiutati
    da validators.url
    """
    # Estrae gli url dalla lista di tuple (numero_url, url)
    urls = [ "{0}\n".format(url_data[0]) for url_data in urls ]
    with open(file_, "w") as fd:
        fd.writelines(urls)


def print_url(url_data, resp, elapsed):
    """
    Stampa a video url, risultato della richiesta (con formattazione dei
    colori) e tempo necessario per eseguire la richiesta. Inoltre logga ragione
    e body della richiesta se il server risponde con un codice delle famiglie
    4xx o 5xx.
    """

    formatted_string = "{0} {1:.2f}s {2} {3:.2f}s".format(
            "time taken: ", elapsed, "timeout: ", url_data[1])
    response_timed_out = elapsed > url_data[1]
    print url_data[0],
    try:
        resp.raise_for_status()
        if response_timed_out:
            print_status(resp, COLOR_FAILURE)
        else:
            print_status(resp, COLOR_SUCCESS)
    except requests.exceptions.HTTPError:
        print_status(resp, COLOR_FAILURE)
    print formatted_string


def print_status(resp, color):
    """
    Stampa a video lo status_code e la reason della richiesta, nel colore
    specificato
    """
    print color + "{0}: {1}".format(
            WEIGHT_BOLD + str(resp.status_code) + WEIGHT_NORMAL,
            resp.reason) \
    + COLOR_RESET,


def write_xml(file_, xml_data):
    """
    Scrive sul file xml specificato il risultato del test. Ogni url ha la
    seguente struttura xml:

    <url value="URL">
        <status>status_code</status>
        <timeout>timeout</timeout>
        <time>elapsed</time>
        <response>response</response>
    </url>

    dove n è l'ordinale dell'URL testato all'interno del file originale, URL è
    l'url testato, status_code è il codice di stato ritornato dal test, time è
    il tempo che è stato necessario alla richiesta e response è il contenuto in
    JSON dela risposta, se presente
    """
    root = ET.Element("urls")
    for elem in xml_data:
        url = ET.SubElement(root, "url")
        url.set("value", elem[0])
        status = ET.SubElement(url, "status")
        status.text = str(elem[1])
        timeout = ET.SubElement(url, "timeout")
        timeout.text = str(elem[2])
        time = ET.SubElement(url, "time")
        time.text = str(elem[3])
        response = ET.SubElement(url, "response")
        response.text = elem[4]
    tree = ET.ElementTree(root)
    tree.write(file_)


# TODO: mock


def make_xml_tuple(url_data, resp, elapsed):
    """
    Costruisce una tupla con tutti i dati necessari per l'output xml
    """
    return (url_data[0], resp.status_code, url_data[1], elapsed, resp.text)

if __name__ == "__main__":
    main()
