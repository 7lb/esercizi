#! /usr/bin/python
#-*- coding:utf-8 -*-

import struct

# In bytes
HEADER_SIZE = 2

def pack_data(data):
    """
    Prepara la stringa da inviare sulla socket secondo il protocollo
    """
    return struct.pack(">H", len(data)) + data

def size(header):
    return struct.unpack(">H", header)[0]

def send_all(socket, data):
    """
    Invia tutti i dati sulla socket specificata

    Solleva RuntimeError se la connessione viene interrotta
    """
    sent_data = 0
    data_size = len(data)
    while sent_data < data_size:
        sent_now = socket.send(data[sent_data:])
        if sent_now == 0:
            raise RuntimeError("Error sending data")
        sent_data += sent_now


def recv_all(socket, data_size):
    """
    Legge dalla socket il numero di bytes specificato

    Solleva runtime error se la connessione viene interrotta

    Ritorna i byte letti
    """
    received_data = 0
    data_chunks = []
    while received_data < data_size:
        chunk = socket.recv(min(data_size - received_data, 4096))
        if chunk == "":
            raise RuntimeError("Error receiving data")
        data_chunks.append(chunk)
        received_data += len(chunk)
    return "".join(data_chunks)


