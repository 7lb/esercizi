#! /usr/bin/python
#-*- coding:utf-8 -*-

import argparse
import os
import re
import requests
import shutil
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
        head = requests.head(url)
    except requests.exceptions.ConnectionError:
        exit("Connection Error")
    try:
        head.raise_for_status()
    except requests.exceptions.HTTPError:
        exit("Bad response")
    # L'url è valido e il server risponde, iniziamo a salvare il sito
    url = requests.head(url, allow_redirects=True).url
    root = urlparse.urlparse(url).netloc
    if os.path.exists(root):
        shutil.rmtree(root)
    os.mkdir(root)
    os.chdir(root)
    download(url)


def download(url):
    html = requests.get(url).text
    html = relativize(html)


def validate(url):
    """
    Valida un url. Per essere valido deve non solo superare la validazione
    standard, ma deve anche avere uno schema tra quelli consentiti

    Torna True se l'url è valido, False altrimenti
    """
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
    """
    Filtra un link

    Ritorna True per un link accettabile, False altrimenti
    """
    if link is None:
        return False
    if link.startswith("#"):
        return False
    scheme = urlparse.urlparse(link).scheme
    if scheme not in FILTERING_SCHEMES:
        return False
    return True


def is_relative(link):
    """
    Controlla se un link è relativo

    Torna True se lo è, False altrimenti
    """
    parsed = urlparse.urlparse(link)
    if parsed.scheme:
        return False
    if parsed.netloc:
        return False
    return True


def make_relative(link):
    """
    Produce un link relativo a partire da un url assoluto
    """
    link_comps = urlparse.urlparse(link)
    start = "{0.scheme}://{0.netloc}".format(link_comps)
    return link[len(start):]


def can_be_relative(link, url):
    """
    Controlla se è possibile ottenere un link relativo a partire da uno
    assoluto, per un determinato url
    """
    url = urlparse.urlparse(url)
    link = urlparse.urlparse(link)
    if url.netloc == link.netloc:
        return True
    return False


def relativize(html):
    """
    Rende tutti i link all'interno di un documento html relativi al dominio
    stesso, per tutti i link per i quali tale operazione è possibile, lasciando
    invariati i restanti

    Ritorna una copia modificata del documento html
    """
    found_tags = find_all_tags(html)
    referenced_links = isolate_links(found_tags)
    # Si possono avere almeno tre casi indesiderati a questo punto:
    # 1. scheme indesiderato (esempio android-app:// su wikipedia)
    # 2. link relativi alla pagina stessa (#qualcosa)
    # 3. None, che si verifica quando un tag selezionato non ha attributi tra
    #    quelli specificati
    # Si risolve filtrando la lista dei link
    referenced_links = filter(link_filter, referenced_links)
    # Costruisco una lista di tuple dei link da sostituire con ciò con cui
    # devono essere sostituiti. In generale si esegue una sostituzione quando
    # si trova un link assoluto che ha lo stesso sottodominio, dominio e
    # suffisso di quello preso in input, nel qual caso si può trasformare in un
    # indirizzo relativo.
    #
    # Ad esempio https://en.wikipedia.org/wiki/Main_Page ha sottodominio "en",
    # dominio "wikipedia" e suffisso "org"; se si trova ad esempio il link
    # "https://en.wikipedia.org/w/api.php?action=rsd", che ha gli stessi valori
    # per il sottodominio, dominio e suffisso, si può trasformare
    # nell'indirizzo relativo "/w/api.php?action=rsd"
    subs = [
        (link, make_relative(link)) for link in referenced_links
        if not is_relative(link) and can_be_relative(link, url)
    ]
    for abs_, rel in subs:
        html = html.replace(abs_, rel)

    return html


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="The url of the webpage to download")
    args = parser.parse_args()
    main(args.url)
