#! /usr/bin/python2
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
    url = requests.head(url, allow_redirects=True).url.lower()
    root = urlparse.urlparse(url).netloc
    if os.path.exists(root):
        shutil.rmtree(root)
    os.mkdir(root)
    os.chdir(root)
    download(url, os.getcwd())


def download(url, root_dir):
    path = relative_path(urlparse.urlparse(url).path, root_dir)

    # A os.makedirs non piace "..", inoltre il path assoluto ci fa comodo più
    # avanti, quando bisogna ricostruire un url assoluto dai path relativi
    path = abspath_dir(path)

    # file_name è "" quando path è una directory; path è una directory quando
    # il server risponde con un url che specifica una cartella e non un file.
    # Questo accade quando si richiede la pagina principale del sito (e il
    # server risponde con il file di index.
    file_name = os.path.basename(path)
    if file_name == "":
        file_name = "index.html"
        path = os.path.join(path, file_name)


    # Se esiste significa che l'abbiamo già scaricato
    if os.path.exists(path):
        print "skippo", url
        return
    print "scarico", url

    # Creiamo le cartelle necessarie se non esistono
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))

    if os.path.dirname(path) != os.path.abspath(root_dir):
        os.chdir(os.path.dirname(path))

    # Scarichiamo la pagina html, cambiamo i link al suo interno per renderli
    # path relativi e infine scriviamo il contenuto sul file
    html = requests.get(url).content
    html = relativize(html, url, root_dir)
    with open(path, "w") as fd:
        fd.write(html)

    # Dobbiamo ritrovare tutti i link presenti all'interno della pagina
    found_tags = find_all_tags(html)
    referenced_links = isolate_links(found_tags)
    referenced_links = filter(link_filter, referenced_links)
    # Si filtrano, mantenendo solo i path relativi
    referenced_links = [
        link
        for link in referenced_links
        if is_relative_link(link)
    ]

    # Si scaricano ricorsivamente tutti i file interessanti, bisogna però
    # riconvertire ogni path relativo in un url assoluto
    for path in referenced_links:
        absurl = abs_url(path, url, root_dir)
        download(absurl, root_dir)
        if os.getcwd() != os.path.abspath(root_dir):
            os.chdir("..")


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


def find_all_tags(txt, tag_list=("a", "img", "link", "script")):
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


def is_relative_link(link):
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


def relative_link(link):
    """
    Produce un link relativo a partire da un url assoluto
    """
    link_comps = urlparse.urlparse(link)
    start = "{0.scheme}://{0.netloc}".format(link_comps)
    return link[len(start):]


def relative_path(link, root_dir):
    """
    Produce un path relativo alla directory specificata, a partire da un link
    relativo

    NB: un link relativo può avere forme "/dir/file", "./dir/file",
    "../dir/file" e "dir/file"; "./dir/file" e "dir/file" sono equivalenti e
    sono path relativi, oltre a essere link relativi. Lo stesso vale per
    "../dir/file". Invece "/dir/file" è un link relativo (inteso come relativo
    al dominio cui appartiene) ma è un path assoluto
    """
    if not os.path.isabs(link):
        return link

    # Non possiamo usare os.path.abspath direttamente perché prende in
    # considerazione la directory corrente, mentre noi vogliamo un path
    # assoluto a partire da una directory principale
    abspath = os.path.join(root_dir, link[1:])
    relpath = os.path.relpath(abspath)

    if could_be_dir(link) and relpath != ".":
        return "{0}{1}".format(relpath, os.sep)
    else:
        return relpath

def abspath_dir(path):
    """
    Ritorna il path assoluto a partire da un path relativo, manentendo il
    separatore finale se il path è una directory
    """
    directory = could_be_dir(path)
    if directory:
        return os.path.join(os.path.abspath(path), "")
    else:
        return os.path.abspath(path)

def could_be_dir(path):
    """
    Ritorna True se la directory esiste o se il path specificato potrebbe
    essere una directory
    """
    return os.path.isdir(path) or path.endswith(os.sep)

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


def relativize(html, url, root_dir):
    """
    Trasforma tutti i link relativi e assoluti all'interno del documento html
    in path relativi alla directory dove si sta salvando il sito

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
    #
    # I link relativi non vengono sostituiti direttamente, ma vengono prima
    # trasformati in path relativi. Così ad esempio se stiamo analizzando un
    # documento html e ci troviamo nella nella directory
    # "en.wikipedia.org/wiki" e si trova un link assoluto come
    # "https://en.wikipedia.org/w/api.php" lo si va a sotituire non con il link
    # relativo "/w/api.php" ma con il path relativo "../w/api.php"
    for link in referenced_links:
        if not is_relative_link(link) and not can_be_relative(link.lower(), url):
            continue
        if not is_relative_link(link) and can_be_relative(link.lower(), url):
            rel = relative_path(relative_link(link), root_dir)
        if is_relative_link(link):
            rel = relative_path(link, root_dir)

        # Trova tutte le sottostringhe *esatte*, così nel caso speciale in cui
        # rel sia "." (perché si trova un link che punta alla homepage) non si
        # andrà a sostituire un link del tipo "http://www.sito.com/subdir" con
        # il link relativo ".subdir" come invece accadrebbe sostituendo in modo
        # banale tutte le occorrenze di "http://www.sito.com/" con "."
        if could_be_dir(rel) and rel.startswith(".") and not rel.startswith(".."):#re.match(r"^\.[^\.]", rel):
            rel = os.sep.join([rel, "index.html"])
        elif could_be_dir(rel):
            rel = "{0}{1}".format(rel, "index.html")
        else:
            continue

        print "sostituisco", link, "con", rel
        pattern = r"({0}\/?)(?=[\"'\s])".format(link.rstrip("/"))
        html = re.sub(pattern, rel, html)
    return html

def abs_url(path, base_url, root_dir):
    """
    Costruisce un url assoluto a partire da un url di base e un path relativo
    """
    comps = urlparse.urlparse(base_url)
    absurl_beginning = "{0}://{1}".format(comps.scheme, comps.netloc)
    path = abspath_dir(path)
    absurl_ending = path[len(root_dir):]
    return "{0}/{1}".format(absurl_beginning.rstrip("/"),
        absurl_ending.lstrip(os.sep))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="The url of the webpage to download")
    args = parser.parse_args()
    main(args.url)
