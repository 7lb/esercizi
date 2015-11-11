#! /usr/bin/python
#-*- coding:utf-8 -*-

import select
import socket
import struct
import subprocess

import common as CC

# In secondi
TIMEOUT = 60

# Variabili globali
in_socks = []
out_socks = []
err_socks = []
sock_map = {}

class SocketState():
    def __init__(self):
        self.received_chunks = []
        self.req_size = 0
        self.req_header = ""
        self.req_body = ""
        self.response_computed = False
        self.response = ""
        self.bytes_sent = 0

    def header_len(self):
        return len(self.req_header)

    def req_len(self):
        return sum(map(len, self.received_chunks))

    def resp_len(self):
        return len(self.response)


def dbg_dump_state(sock, where):
    sock_state = sock_map[sock]
    print where
    print "\tSocket ", sock
    print "\tReq_size: ", sock_state.req_size
    print "\tReq_header: ", sock_state.req_header
    print "\tReq_body: ", sock_state.req_body
    for i, chunk in enumerate(sock_state.received_chunks):
        print "\tChunk[{0}]: {1}".format(i, chunk)
    print "\tResponse_computed: ", sock_state.response_computed
    print "\tResponse: ", sock_state.response
    print "\tBytes_sent: ", sock_state.bytes_sent


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("", 7687))
    server_socket.setblocking(0)
    server_socket.listen(5)

    in_socks.append(server_socket)
    while True:
        readable, writable, in_error = select.select(
                in_socks, out_socks, err_socks, TIMEOUT)

        for sock in readable:
            if sock == server_socket:
                (client_socket, client_addr) = server_socket.accept()
                in_socks.append(client_socket)
                sock_map[client_socket] = SocketState()
            else:
                dbg_dump_state(sock, "before handle_input")
                handle_input_socket(sock)
                dbg_dump_state(sock, "after handle_input")

        for sock in writable:
            if sock_map[sock].response_computed:
                dbg_dump_state(sock, "before handle_output")
                handle_output_socket(sock)
                #dbg_dump_state(sock, "after_handle_output")
            else:
                dbg_dump_state(sock, "before compute_response")
                compute_response(sock)
                dbg_dump_state(sock, "after compute_response")


def handle_input_socket(sock):
    sock_state = sock_map[sock]
    header_len = sock_state.header_len()
    # Se non ho ancora letto l'header, o non l'ho letto tutto
    if header_len < CC.HEADER_SIZE:
        # Provo a leggere il numero di byte mancanti per completare l'header
        header_data = sock.recv(CC.HEADER_SIZE - header_len)
        if header_data:
            sock_state.req_header += header_data
            # Anche se ho letto qualcosa potrei non aver letto tutti i byte che
            # mi servivano a completare l'header, quindi controllo
            if sock_state.header_len() == CC.HEADER_SIZE:
                # Se ho finito di leggere l'header dalla socket allora posso
                # calcolare la lunghezza del messaggio e salvarla nello stato
                sock_state.req_size = CC.size(
                        sock_state.req_header)
                # Segnalo che ho smesso di leggere, ma invio
                sock.shutdown(socket.SHUT_RD)
        else:
            # Se non ho letto niente ma non avevo nemmeno finito di leggere
            # l'header allora c'è sicuramente stato un errore di connessione
            shut_socket(sock)
            in_socks.remove(sock)
    else:
        # In questo caso l'header della richiesta è completo, allora comincio a
        # leggere il messaggio stesso. Leggo al massimo 4kB, a meno che non ne
        # manchino meno alla fine del messaggio
        chunk = sock.recv(
                min(sock_state.req_size - sock_state.req_len(),
                    4096))
        if chunk:
            sock_state.received_chunks.append(chunk)
            if sock_state.req_len() == sock_state.req_size:
                # Avendo ricevuto un chunk controllo se ho terminato di leggere
                # il messaggio. In questo caso il client ha terminato l'invio e
                # devo rispondere, quindi tolgo la socket dalla lista di quelle
                # che vorrei leggere e la aggiungo alla lista di quelle sulle
                # quali mi piacerebbe scrivere
                in_socks.remove(sock)
                out_socks.append(sock)
        else:
            # Se non ho ricevuto un chunk c'è stato un errore di connessione
            # dal momento che select mi aveva promesso che questo socket
            # sarebbe stato leggibile
            shut_socket(sock)
            in_socks.remove(sock)


def handle_output_socket(sock):
    sock_state = sock_map[sock]
    sent_data = sock.send(sock_state.response[sock_state.bytes_sent:])
    # Se invio qualcosa aggiorno lo stato per continuare da dove ero rimasto
    if sent_data:
        sock_state.bytes_sent += sent_data
        # Se ho finito di inviare la risposta allora il lavoro di questa socket
        # è concluso
        if sock_state.bytes_sent == sock_state.resp_len():
            shut_socket(sock)
            out_socks.remove(sock)
    else:
        # Non ho inviato niente, quindi c'è stato un errore di connessione
        shut_socket(sock)
        out_socks.remove(sock)


def compute_response(sock):
    sock_state = sock_map[sock]
    sock_state.req_body = "".join(sock_state.received_chunks)
    try:
        cmd_output = subprocess.check_output(sock_state.req_body.split())
    except subprocess.CalledProcessError as e:
        cmd_output = e.output
    sock_state.response = CC.pack_data(cmd_output)
    sock_state.response_computed = True


def shut_socket(sock):
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()
    del sock_map[sock]


if __name__ == "__main__":
    main()
