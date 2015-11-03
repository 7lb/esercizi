#! /usr/bin/python
#-*- coding: utf-8 -*-

# Realizzare un'applicazione command line che dato un elenco di argomenti li
# stampi in ordine alfabetico.

import sys

if __name__ == "__main__":
    # Si ignora il primo elemento, che è il nome dell'eseguibile stesso
    l = sys.argv[1:]
    # Si ordinano gli argomenti
    l.sort()
    # Infine si stampano
    for arg in l:
        print arg
