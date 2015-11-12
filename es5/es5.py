#! /usr/bin/python
#-*- coding:utf-8 -*-

import argparse
import re
import requests
import urlparse
import validators


# Usati per la validazione dell'input utente
VALIDATING_SCHEMES = ["http", "https"]
# Usati per il filtro dei link trovati all'interno delle pagine
FILTERING_SCHEMES = ["http", "https", ""]


def main(url):
    if not validate(url):
        exit("Invalid URL")
    try:
        html = requests.get(url)
        html.raise_for_status()
    except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError):
        exit("Connection Error")
    html = html.text
    found_tags = find_all_tags(html)
    referenced_links = isolate_links(found_tags)
    # Si possono avere almeno tre casi indesiderati in questo caso:
    # 1. scheme indesiderato (esempio android-app:// su wikipedia)
    # 2. link relativi alla pagina stessa (#qualcosa)
    # 3. None, che si verifica quando un tag selezionato non ha attributi tra
    #    quelli specificati
    # Si risolve filtrando la lista dei link
    referenced_links = filter(link_filter, referenced_links)
    for link in referenced_links:
        print link


def validate(url):
    parse_res = urlparse.urlparse(url)
    if parse_res.scheme in VALIDATING_SCHEMES and validators.url(url):
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
        # siamo di fronte a uno scheme relative url. Li trattiamo come https; è
        # sempre valido richiedere una risorsa su https, anche se è solo
        # disponibile su http, il contrario non è vero
        if val.startswith("//"):
            val = "https:{0}".format(val)
        return val


def link_filter(link):
    if link is None:
        return False
    if link.startswith("#"):
        return False
    scheme = urlparse.urlparse(link).scheme
    if scheme not in FILTERING_SCHEMES:
        return False
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="The url of the webpage to download")
    args = parser.parse_args()
    main(args.url)
