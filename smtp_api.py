import socket
import ssl
import sys
import base64
import re


class SmtpApi:
    EHLO_request = 'EHLO smtp-image-loader'

    def __init__(self, server, port, verbose):
        self.server = server
        self.port = port
        self.verbose = verbose

        self.pipelining = False
        self.size = float('+inf')

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send(self, command, verbose):
        self.sock.sendall((command + '\r\n').encode())
        if verbose:
            print(f'c: {command}')
        response = self.sock.recv(1024)
        if verbose:
            print('s: ' + response.decode() + '\r\n')
        return response.decode()

    def start_connection(self, ssl_prot):
        self.sock.connect((self.server, self.port))
        if ssl_prot:
            self.sock = ssl.wrap_socket(self.sock)
        server_hello = self.sock.recv(1024)
        if self.verbose:
            print('s:', server_hello.decode())

        response = self.send(self.EHLO_request, self.verbose)
        if response.find("PIPELINING") != -1:
            self.pipelining = True

        size = re.findall('-SIZE (\d*)', response)
        if size:
            self.size = int(size[0])

    def close_connection(self):
        self.sock.close()

    def auth(self, login, password):
        response = self.send('AUTH LOGIN', self.verbose)
        if response.split()[0] != '334':
            print('Fail to autorizate')
            self.close_connection()
            sys.exit(1)
        response = self.send(base64.b64encode(login.encode()).decode(), self.verbose)
        if response.split()[0] != '334':
            print('Fail to autorizate on sending login')
            self.close_connection()
            sys.exit(2)
        response = self.send(base64.b64encode(password.encode()).decode(), self.verbose)
        if response.split()[0] != '235':
            print('Fail to autorizate on sending password')
            self.close_connection()
            sys.exit(3)

    def send_mail(self, _from, _to, mail):
        if len(mail) > self.size:
            print("Letter size too big")
            self.close_connection()
            exit(7)
        response = self.send(f'MAIL FROM: {_from}', self.verbose)
        if response.split()[0] != '250':
            print(f'Fail to set FROM address {_from}')
            self.close_connection()
            sys.exit(4)
        response = self.send(f'RCPT TO: {_to}', self.verbose)
        if response.split()[0] != '250':
            print(f'Fail to set TO address {_to}')
            self.close_connection()
            sys.exit(5)
        response = self.send('DATA', self.verbose)
        if response.split()[0] != '354':
            print(f'Fail to send DATA')
            self.close_connection()
            sys.exit(6)
        mail_data = mail + b'\r\n.\r\n'
        self.sock.sendall(mail_data)
        response = self.sock.recv(1024)
        print(response.decode())

    def send_mail_pipeline(self, _from, _to, mail):
        if len(mail) > self.size:
            print("Letter size too big")
            self.close_connection()
            exit(7)
        mail_data = mail + b'\r\n.\r\n'
        command = f'MAIL FROM: {_from}\r\nRCPT TO: {_to}\r\nDATA\r\n'
        response = self.send(command, verbose=False)
        if self.verbose:
            print(f'MAIL FROM: {_from}\r\nRCPT TO: {_to}\r\nDATA\r\n')
            print(response)
            print(self.sock.recv(1024).decode())
            print(self.sock.recv(1024).decode())
            self.sock.sendall(mail_data)
            print(self.sock.recv(1024).decode())

