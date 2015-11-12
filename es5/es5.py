#! /usr/bin/python
#-*- coding:utf-8 -*-

import argparse
import re
import requests
import urlparse
import validators


def main(url):
    if not validate(url):
        exit("Invalid URL")
    try:
        html = requests.get(url).text
        html.raise_for_status()
    except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError):
        exit("Connection Error")
    found_tags = find_all_tags(html)
    referenced_links = isolate_links(found_tags)


def validate(url):
    valid_schemes = ["http", "https"]
    parse_res = urlparse.urlparse(url)
    if parse_res.scheme in valid_schemes and validators.url(url):
        return True
    return False


def find_all_tags(txt, tag_list=["a", "img", "link", "script"]):
    """
    Trova tutti i tag specificati in tag_list all'interno di txt e li ritorna
    come lista di tuple (tag, attr) dove attr è una stringa contenente tutti
    gli attributi del tag
    """
    pattern_tags = "|".join(tag_list)
    pattern = "<({0})([^>]+)".format(pattern_tags)
    return re.findall(pattern, txt)


def isolate_links(tags):
    """
    Ritorna una lista di link
    """
    links = []
    for tag in tags:
        links.append(isolate_value(tag[1], ["href", "src"]))
    return links


def isolate_value(attr_str, attr_list):
    """
    Isola i valori degli attributi passati come parametro
    """
    for attr in attr_list:
        attr_pos = attr_str.find(attr)
        if attr_pos == -1:
            continue
        # elimino fino all'ultimo carattere del nome dell'attributo
        val = attr_str[attr_pos + len(attr):]
        # elimino tutto finché non trovo il primo carattere del valore
        while val.startswith(" ") or val.startswith("="):
            val = val[1:]
        # se il valore è quotato con apici singoli o doppi elimino tutto ciò
        # che compare dagli apici di chiusura in poi, e della stringa rimanente
        # prendo tutto tranne il primo elemento (che è l'apice di apertura)
        if val.startswith('"') or val.startswith("'"):
            val = val[1:val.find(val[0], 1)]
        # se il valore non è quotato elimino tutto ciò che compare dal primo
        # spazio in poi
        else:
            value_end = val.find(" ")
            # se il valore è quello dell'ultimo attributo non c'è uno spazio
            if value_end != -1:
                val = val[:value_end]
        return val

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="The url of the webpage to download")
    args = parser.parse_args()
    main(args.url)
