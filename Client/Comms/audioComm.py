from Client.Devices.Microphone import Microphone
from Client.Devices.AudioOutputDevice import AudioOutput
import socket
import threading
import queue
import sys
import time
from Client.Protocol import clientProtocol
from Common.Cipher import DiffiHelman, AESCipher
import os
import select

# client
class AudioClient:
    def __init__(self, server_ip, AES):
        self.my_socket = socket.socket()
        self.server_ip = server_ip
        self.port = 3000 # todo from settings
        self.audio_queue = queue.Queue()
        # todo check if we need to exchange keys or not
        # self.cipher = None
        self.cipher = AES
        self.open = False
        self.file_counter = 0
        threading.Thread(target=self._mainLoop,).start()

    def _mainLoop(self):
        """
        conect to client and exhcange keys and recv messages
        :return: None
        """
        try:
            self.my_socket.connect((self.server_ip, self.port))
        except Exception as e:
            print("error in connect:", e)
            sys.exit("server is down - try later")
        #todo check if we need to exchange keys or not
        # self._exchange_key()
        if not self.cipher:
            sys.exit("couldn't exchange keys")
        self.open = True
        while True:
            if self.open:
                decrypt_audio_chunk = ""
                try:
                    length = self.my_socket.recv(8).decode()
                    if length:
                        msg = self.my_socket.recv(int(length))
                        decrypt_audio_chunk = self.cipher.decrypt_file(msg)
                except Exception as e:
                    print(f"error in receiving message here - {e}")
                    self._close_client()
                    continue
                if decrypt_audio_chunk:
                    audio, header = clientProtocol.unpack_file(decrypt_audio_chunk)
                    if len(header) == 3:
                        opcode = header[0]
                        timestamp = float(header[1])
                        sender_ip = header[2]
                        self.audio_queue.put((audio, timestamp, sender_ip))
                    else:
                        print("incorrect audio msg")
                    
    def _close_client(self):
        """
        close the connection
        :return: None
        """
        try:
            self.my_socket.close()
            print("Client connection closed.")
        except Exception as e:
            print(f"Error closing client: {e}")
        self.open = False

    def close_client(self):
        """
        close the connection
        :return: None
        """
        self._close_client()

    def client_exchange(self, diffie, socket):
        """
        exchange keys with server according to clientProtocol
        :param diffie: diffie helman object
        :param socket: socket
        :return: shared key as string
        """
        server_public_key = None
        ret = None
        try:
            server_public_key = int(socket.recv(5).decode())
            socket.send(str(diffie.public_key).zfill(5).encode())
        except Exception as e:
            print(f"Error in receiving/sending public key: {e}")
        if server_public_key:
            shared_key = pow(server_public_key, diffie.private_key, diffie.p)
            ret = str(shared_key)
        return ret

    def _exchange_key(self):
        """
        Exchange key with server
        :return: if exchanged
        """
        diffie = DiffiHelman()
        diffie.create_keys()
        shared_key = self.client_exchange(diffie, self.my_socket)
        flag = False
        if shared_key:
            self.cipher = AESCipher(shared_key)
            print(f"Shared key established with server - {shared_key}")
            flag = True
        return flag

    def send_audio(self, audio_chunk):
        """
        send message to server
        :param audio_chunk:
        :return:
        """
        flag = False
        if self.cipher and self.open:
            audio_chunk_encrypted = self.cipher.encrypt_file(audio_chunk)
            if len(audio_chunk_encrypted) > 0:
                try:
                    self.my_socket.send(str(len(audio_chunk_encrypted)).zfill(8).encode())
                    self.my_socket.send(audio_chunk_encrypted)
                    flag = True
                except Exception as e:
                    print(f"error in sending message - {e}")
                    self._close_client()
                    self.open = False
        return flag


import socket
import threading
import queue
import select
import time

from Client.Protocol import clientProtocol


class AudioServer:
    def __init__(self, port=3000, AES=None, open_clients=None):
        """
        :param port:
        :param AES:
        :param open_clients:
        :return:
        """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.port = port
        self.AES = AES
        self.open_clients = open_clients if open_clients is not None else {}

        self.audio_queue = queue.Queue()

        # audio sockets only
        self.audio_clients = {}          # ip -> socket
        self.open_clients_soc_ip = {}    # socket -> ip

        self.running = True

        self.server_socket.bind(("0.0.0.0", self.port))
        self.server_socket.listen(8)

        threading.Thread(target=self._mainLoop, daemon=True).start()

    def _recv_exact(self, sock, size):
        """
        :param sock:
        :param size:
        :return:
        """
        data = b""
        while len(data) < size and self.running:
            chunk = sock.recv(size - len(data))
            if not chunk:
                return None
            data += chunk
        return data

    def _mainLoop(self):
        """
        :return:
        """
        print("audio server listen on port:", self.port)

        while self.running:
            try:
                rlist, _, _ = select.select(
                    [self.server_socket] + list(self.open_clients_soc_ip.keys()),
                    [],
                    [],
                    0.01
                )
            except Exception:
                continue

            for current_socket in rlist:
                if current_socket is self.server_socket:
                    try:
                        client_socket, addr = self.server_socket.accept()
                        client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

                        client_ip = addr[0]
                        self.audio_clients[client_ip] = client_socket
                        self.open_clients_soc_ip[client_socket] = client_ip

                        print(f"{client_ip} connected to audio server")
                    except Exception as e:
                        print("audio accept error:", e)

                else:
                    client_ip = self.open_clients_soc_ip.get(current_socket)
                    if not client_ip:
                        continue

                    try:
                        length_bytes = self._recv_exact(current_socket, 8)
                        if not length_bytes:
                            self.close_client(client_ip)
                            continue

                        msg_len = int(length_bytes.decode())
                        payload = self._recv_exact(current_socket, msg_len)
                        if not payload:
                            self.close_client(client_ip)
                            continue

                        if not self.AES:
                            continue

                        decrypt_audio_chunk = self.AES.decrypt_file(payload)
                        audio, header = clientProtocol.unpack_file(decrypt_audio_chunk)

                        if len(header) == 3:
                            opcode = header[0]
                            timestamp = float(header[1])
                            sender_ip = header[2]
                            self.audio_queue.put((audio, timestamp, sender_ip))
                        else:
                            print("incorrect audio msg")

                    except Exception as e:
                        print(f"audio receive error from {client_ip}: {e}")
                        self.close_client(client_ip)

    def close_client(self, client_ip):
        """
        :param client_ip:
        :return:
        """
        try:
            if client_ip in self.audio_clients:
                client_soc = self.audio_clients[client_ip]

                if client_soc in self.open_clients_soc_ip:
                    del self.open_clients_soc_ip[client_soc]

                del self.audio_clients[client_ip]
                client_soc.close()
                print(f"Audio client {client_ip} closed.")
        except Exception as e:
            print(f"Error closing audio client {client_ip}: {e}")

    def broadcast_audio(self, audio_chunk, sender_ip):
        """
        :param audio_chunk:
        :param sender_ip:
        :return:
        """
        for ip in list(self.audio_clients.keys()):
            if ip != sender_ip:
                self.send_audio(ip, audio_chunk)

    def send_audio(self, client_ip, audio_chunk):
        """
        :param client_ip:
        :param audio_chunk:
        :return:
        """
        if client_ip not in self.audio_clients or not self.AES:
            return

        client_soc = self.audio_clients[client_ip]
        encrypted_audio_chunk = self.AES.encrypt_file(audio_chunk)

        try:
            client_soc.sendall(str(len(encrypted_audio_chunk)).zfill(8).encode())
            client_soc.sendall(encrypted_audio_chunk)
        except Exception as e:
            print(f"audio send error to {client_ip}: {e}")
            self.close_client(client_ip)

    def close(self):
        """
        :return:
        """
        self.running = False

        for ip in list(self.audio_clients.keys()):
            self.close_client(ip)

        try:
            self.server_socket.close()
        except Exception:
            pass