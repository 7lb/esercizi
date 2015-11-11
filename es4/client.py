#! /usr/bin/python
#-*- coding:utf-8 -*-

# Definizione del protocollo:
# I primi 2 byte sono la lunghezza del messaggio
# I byte dal terzo in poi sono il messaggio stesso

import socket

import common as CC


def main():
    while True:
        cmd = raw_input("$ ")
        bytes_to_send = CC.pack_data(cmd)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("", 7687))
        try:
            CC.send_all(s, bytes_to_send)
        except RuntimeError:
            print "Error sending data"
            continue
        # Segnala che smettiamo di inviare, ma leggiamo
        s.shutdown(socket.SHUT_WR)
        try:
            response_header = CC.recv_all(s, CC.HEADER_SIZE)
        except RuntimeError:
            print "Error receiving response header"
            continue
        response_size = CC.size(response_header)
        try:
            response_body = CC.recv_all(s, response_size)
        except RuntimeError:
            print "Error receiving response body"
            continue
        s.close()
        print response_body


if __name__ == "__main__":
    main()
