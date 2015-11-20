#! /usr/bin/env python
#-*- coding:utf-8 -*-

"""
Modulo per il download in locale di un sito remoto
"""

import argparse
import os
import re
import requests
import shutil
import urlparse
import validators


# Usati per la validazione dell'input utente
VALIDATING_SCHEMES = ("http", "https")

# Usati per il filtro dei link trovati all'interno delle pagine
FILTERING_SCHEMES = ("http", "https", "")

# Stringhe raw perché finiscono in una regex
INTERESTING_ATTRS = (r"href", r"src", r"url\(")

# File per i quali non ci si aspetta di torvare link all'interno
# Q: Perché invece non fare una whitelist composta da htm[l], css e forse js?
# R: Perché siti come wikipedia servono pagine senza estensione
# TODO: Valutare l'idea di aggiungere l'estensione html a tutte le pagine
#       servite senza, e sostituire la blacklist con una whitelist
NOPARSE_EXTS = (
    ".jpg", ".jpeg", ".png", ".gif", ".ico", ".zip", ".rar", ".7z", ".tar",
    ".gz", ".xz", ".exe", ".a", ".so", ".lib", ".dll", ".epub", ".pdf", ".ttl",
    ".xml", ".rdf"
)


def begin(url):
    """
    Controlla la validità dell'url e fa partire il download
    """
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
    """
    Funzione ricorsiva per la creazione delle directory nel filesystem,
    download dei file html e non, e aggiustamento degli url all'interno
    dell'html in path relativi
    """

    url_comps = urlparse.urlparse(url)
    path = url_comps.path.lstrip(os.sep)
    # Se con lstrip rimaniamo con una stringa vuota allora siamo nella root
    if not path:
        path = "."
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

    # Creiamo le cartelle necessarie se non esistono
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))

    # Scarichiamo la pagina html, cambiamo i link al suo interno per renderli
    # path relativi e infine scriviamo il contenuto sul file
    html = requests.get(url).content

    subs = downloads = []
    if not file_name.lower().endswith(NOPARSE_EXTS):
        subs, downloads = check_links(html, url)
        html = substitute(html, subs)

    with open(path, "w") as file_desc:
        file_desc.write(html)

    # Si scaricano ricorsivamente tutti i file interessanti, bisogna però
    # riconvertire ogni path relativo in un url assoluto
    for down in downloads:
        print "da", url, "scarico", down
        download(down)


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


def find_urls(txt, attr_list):
    """
    Isola i valori degli attributi passati come parametro
    """
    # Dallo standard HTML[0]
    # Gli attributi hanno un nome, seguito da zero o più space characters[1]
    # seguito da un carattere =, seguito da zero o più space characters.  Gli
    # attributi quotati possono iniziare con apici singoli o doppi e possono
    # contenere gli stessi caratteri (vedere [2] per una lista esatta) con la
    # differenza che gli attributi quotati da apice singolo non possono
    # contenerlo al loro interno, viceversa per gli apici doppi.
    # Gli attributi non quotati non possono contenere space characters, apici
    # singoli, apici doppi, caratteri minore di e maggiore di (<, >), tra gli
    # altri.
    #
    # Degno di nota il fatto che tra l'ultimo attributo del tag e il carattere
    # di chiusura (> o />) deve essere presente uno space character. Questo ci
    # permette di trovare gli attributi non quotati cercando spazi, in quanto
    # <a href=link.html> non è html valido.
    #
    # Riferimenti:
    #[0]: https://html.spec.whatwg.org/multipage/syntax.html#attributes
    #[1]: https://html.spec.whatwg.org/multipage/infrastructure.html#space-character
    #[2]: https://html.spec.whatwg.org/multipage/syntax.html#syntax-attribute-value
    pattern = re.compile(
        r"""
        (?:{0})         # gli attributi che ci interessano, presi dalla format
        (?:\s*)         # zero o più spazi
        (?:=\s*)?       # zero o più spazi dopo l'uguale (se c'è)
        (?:             # discrimino tra attributi quotati o meno
            (?:\"|')    # controllo quelli quotati
            (.*?)       # catturo tutto (lazy)
            (?:\"|')    # fino all'apice di chiusura
            |           # altrimenti l'attributo non è quotato
            (.*?)       # allora catturo tutto (lazy)
            (?:\s|$|\)) # finché non trovo uno spazio o EOL o ")" (in css)
        )
        """.format("|".join(attr_list)),
        re.VERBOSE
    )

    links = []
    vals = pattern.findall(txt)
    for val in vals:
        if not val[0] and not val[1]:
            continue
        elif val[0]:
            links.append(val[0])
        else:
            links.append(val[1])

    return links


def link_filter(link):
    """
    Filtra un link

    Ritorna True per un link accettabile, False altrimenti
    """
    if link is None:
        return False
    if link.startswith("#") or os.path.basename(link).startswith("#"):
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
    tmp_link = link[len(start):]
    if not tmp_link:
        # può succede con link che non terminano con /
        tmp_link = "/"
    return tmp_link


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
    return url.netloc.lower() == link.netloc.lower()


def check_links(html, url):
    """
    Trova tutti i link da sostituire o da scaraicare all'interno del file html

    Ritorna una lista di tuple (link, rel) dove link è il link da sostituire e
    rel è il path relativo con il quale va sostituito, e una lista con i file
    da scaricare
    """
    subs = []
    downloads = []
    referenced_links = find_urls(html, [r"href", r"src", r"url\("])
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
        if not is_relative_link(link) and not can_be_relative(link, url):
            continue

        if can_be_relative(link, url):
            rel = relative_link(link)

        if is_relative_link(link):
            rel = link

        if could_be_dir(rel):
            rel = os.path.join(rel, "index.html")

        abs_url_ = abs_url(rel, url)
        url_comps = urlparse.urlparse(url)
        # Questo ciclo rimuove "../" da un link relativo fintanto che questo
        # punta a una directory superiore rispetto alla root del sito.
        while url_comps.netloc != urlparse.urlparse(abs_url_).netloc and rel:
            rel = rel[3:]
            abs_url_ = abs_url(rel, url)

        downloads.append(abs_url(rel, url))

        url_path = url_comps.path
        if rel != link:
            if rel.lower() == url_path.lower():
                subs.append((link, "."))
            else:
                pseudo_cwd = os.path.dirname(os.path.abspath(url_path))
                if not pseudo_cwd.startswith(os.sep):
                    rel = os.path.relpath(rel, pseudo_cwd)
                subs.append((link, rel))
    return subs, downloads


def substitute(html, subs):
    """
    Sostituisce tutti i link presenti nel file html con path relativi, se
    possibile

    Ritorna il file html modificato
    """
    for link, rel in subs:
        print "sostituisco", link, "con", rel
        pattern = re.compile(r"({0}\/?)(?=[\"'\s])".format(re.escape(link.rstrip("/"))))
        html = pattern.sub(rel, html)
    return html


def abs_url(path, base_url):
    """
    Costruisce un url assoluto a partire da un url di base e un path relativo
    """
    comps = urlparse.urlparse(base_url)
    if os.path.isabs(path):
        temp_path = os.sep.join([comps.netloc, path])
    else:
        temp_path = os.sep.join([comps.netloc, os.path.dirname(comps.path), path])
    temp_path = os.path.normpath(temp_path)
    return "://".join([comps.scheme, temp_path])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="The url of the webpage to download")
    args = parser.parse_args()
    begin(args.url)
