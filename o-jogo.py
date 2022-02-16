import socket


class GameSocket:
    MSGLEN = 12
    PORT = 6666

    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(
                            socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def bind(self, addres_port):
        self.sock.bind(addres_port)

    def listen(self, queue_size):
        self.sock.listen(queue_size)

    def accept(self):
        return self.sock.accept()

    def connect(self, host, port):
        self.sock.connect((host, port))

    def send(self, msg):
        totalsent = 0
        while totalsent < self.MSGLEN:
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent

    def recv(self):
        chunks = []
        bytes_recvd = 0
        while bytes_recvd < self.MSGLEN:
            chunk = self.sock.recv(min(self.MSGLEN - bytes_recvd, 2048))
            if chunk == b'':
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            bytes_recvd = bytes_recvd + len(chunk)
        return b''.join(chunks)

    def shutdown(self, mode):
        self.sock.shutdown(mode)

    def close(self):
        self.sock.close()


def creditos():
    print("""
 Feito por Lucas Carvalho e Vitor Magno.
    """)


def servir_partida():
    print("\n #1 Servindo o jogo...")

    # Prepara socket do servidor para servir jogo.
    serv_sock = GameSocket()
    serv_sock.bind(('', GameSocket.PORT))
    serv_sock.listen(2)

    # Loop principal de jogo.
    while True:

        try:
            # Aceita conexão vinda de fora no nosso amado socket.
            client_sock, address = serv_sock.accept()
            print(" Conexão estabelecida com", address)

            # Rotina de servidor do jogo vem aqui.
            client_sock.send(b" Eu te vejo.")
            break

        except Exception:
            break

    print("\n Partida encerrada.")

    # Importante fechar os sockets.
    client_sock.shutdown(2)
    client_sock.close()
    serv_sock.shutdown(2)
    serv_sock.close()


def conectar_partida():
    print("\n #2 Conectando a partida...")
    serv_addr = input("\n Informar endereço do servidor: ")

    # Prepara socket do cliente e conecta com servidor no endereço especificado.
    client_sock = GameSocket()
    client_sock.connect(serv_addr, GameSocket.PORT)

    # Rotina de cliente do jogo vem aqui.
    msg = client_sock.recv()
    print("\n#1 SERVIDOR : ", msg.decode('utf-8'))

    # Importante fechar os sockets.
    client_sock.shutdown(2)
    client_sock.close()


def main():

    opcao = 0

    while opcao in [0, 1, 2, 3]:

        try: opcao = int(menu_principal())
        except ValueError: opcao = -1

        if int(opcao) == 1:
            servir_partida()
        elif int(opcao) == 2:
            conectar_partida()
        elif int(opcao) == 3:
            creditos()
        else:
            opcao = -1

    print("\n Encerrando jogo... (•‿•)/ bye\n")


def menu_principal():

    TEXTO_PRINCIPAL = """
 --- O BOM VELHINHO ---
 Jogo da velha em seu terminal! \\(>.<)/

 Opções:
   1. Servir novo jogo
   2. Conectar a jogo existente
   3. Créditos

 Entre qualter outra coisa para encerrar o jogo.
    """

    print(TEXTO_PRINCIPAL)

    return input("(•‿•)/ : ")


if __name__ == '__main__':
    main()
