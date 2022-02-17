import socket
from time import sleep

""" Regra/Protocolo de comunicação da aplicação:

INICIO

1. Quando o cliente se conecta, o servidor imediatamente envia o estado inicial
   do jogo. Após isso o servidor aguarda a jogada do cliente. O cliente sempre
   joga primeiro. O servidor usa o símbolo X e o cliente usa O para marcarem
   suas jogadas.

2. As mensagens trocadas entre cliente e servidor são compostas por uma string
   (byte object) de 12 caracteres, cada caracter um com um significado próprio
   a ser especificado a seguir.

3. O servidor envia o estado de jogo nesses 12 caracteres. O jogador informa
   sua jogada.


ESTADO DE JOGO

[0] O caracter na posição 1 indica se a última jogada efetuada pelo cliente foi
válida ou ilegal. Nesse contexto o caracter estará definido para 1 se a jogada
foi válida. No caso de 0 (jogada anterior foi inválida) o estado de jogo não
é atualizado pelo servidor e sua resposta apenas defini esse caracter para 0.
O servidor usa também esse caracter para indicar desistência.

[1] O segundo caracter indica se uma condição de fim de jogo foi alcançada.
Se um jogador venceu, o caracter 2 será definido para o símbolo do vencedor
(i.e. X ou O), ou para E caso tenha-se alcançado um empate. Em outros casos,
será o caracter de espaço em branco.

[2] O terceiro caracter informa o número da jogada. É incrementado com cada
jogada válida efetuada. Vai de 0 (estado inicial do jogo) a 9.

[3-11] Os últimos 9 caracteres acomodam o símbolo marcado pelo jogador nas
respectivas posições. Um caracter na posição aᵢⱼ com espaço em branco indica
que nenhum jogador marcou a casa deste índice. Caso contrário, terá o símbolo
do jogador que marcou.

A ordem das posições é contada de forma crescente da esquerda para a direita e
de cima para baxo, como descrito a seguir:

    1 = a₁₁   2 = a₂₁   3 = a₃₁
    4 = a₁₂   5 = a₂₂   6 = a₃₂
    7 = a₁₃   8 = a₂₃   9 = a₃₃


JOGADA

1. Para informar sua jogada, o cliente define a string inteira para espaços em
   branco, com exeção do quarto caracter (i.e. índice 3). Este será o caracter
   de jogada.

2. Para informar que desistiu da partida, o cliente deverá enviar a letra d
   ou D no caracter de jogada.

3. Para informar em qual casa deseja por sua marca, o cliente deve informar o
   número do índice desejado no caracter de jogada.
   Se a casa informada já estiver ocupada ou não existir, o servidor rejeitará
   a jogada reenviando o mesmo estado de jogo, porém com o caracter de
   posição 1 (i.e. índice 0) definido para 0. O mesmo será feito se o caracter
   de jogada não for nem um número nem a letra d/D .

"""

ESTADO_INICIAL = b'1 0         '
SERVIDOR = 'X'
CLIENTE = 'O'
PADROES_VITORIA = [
    '111......',
    '1..1..1..',
    '1...1...1',
    '.1..1..1.',
    '..1.1.1..',
    '..1..1..1',
    '...111...',
    '......111'
]

class GameSocket:
    MSGLEN = 12
    PORT = 6667

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
        std_sock, addr = self.sock.accept()
        return GameSocket(std_sock), addr

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


def renderiza_jogo(estado):

    estado = estado.decode('utf-8')
    tabuleiro = estado[3:]
    meta = estado[:3]

    print("\n JOGADA ", estado[1], ", estado do jogo:", sep='')

    # DEBUG
    print(estado.replace(' ', '_'),
          meta.replace(' ', '_'),
          tabuleiro.replace(' ', '_'))

    i = 0
    render = '\n'
    for y in range(0, 3):
        render += '\t'
        for x in range(0, 3):
            render += tabuleiro[i]
            if x < 2:
                render += ' | '
            else:
                render += '\n'
            i += 1
        if y < 2:
            render += '\t---------\n'
    print(render)

    if meta[1] != ' ':
        print("\nVitória de", estado[0].upper(), '\n')
    else:
        print("\n Escolha sua próxima jogada pela numeração das casas:")
        print("\n   1 | 2 | 3\n   ---------\n   4 | 5 | 6\n   ---------\n   7 | 8 | 9\n")


def seleciona_jogada():

    jogada_valida = False
    while not jogada_valida:

        try:
            jogada = input(" Onde marcar? ").strip().lower()
            if jogada != 'd':
                jogada = int(jogada)
                if jogada in range(1, 10):
                    jogada_valida = True
            else:
                jogada_valida = True

        except ValueError:
            print("", jogada, "não é um valor válido.")
            print(" Escolha uma casa de 1 a 9 para marcar ou")
            print(" use D para abandonar partida.")

    jogada = f"   {jogada}        "
    return jogada.encode('utf-8')


def desistencia(jogada):
    if 'd' in jogada.decode('utf-8').lower():
        return True
    return False


def padrao_de_jogo(estado, jogador):
    tabuleiro = estado[3:].upper()
    tabuleiro = tabuleiro.replace(jogador.upper(), '1')
    tabuleiro = tabuleiro.replace(SERVIDOR.upper(), '0')
    tabuleiro = tabuleiro.replace(CLIENTE.upper(), '0')
    tabuleiro = tabuleiro.replace(' ', '0')
    return tabuleiro


def padrao_vitorioso(padrao):
    print(" DEBUG padrao_vitorioso()\n", "123456789\n", padrao)
    return False


def vitoria(estado, jogador):
    padrao = padrao_de_jogo(estado, jogador)
    return padrao_vitorioso(padrao)


def encerra_partida(motivo):
    if motivo == 'desistencia-propria':
        print("\n DERROTA...\n Você desistiu da partida.\n")
    elif motivo == 'desistencia-oponente':
        print("\n VITÓRIA!\n O adversário desistiu da partida.\n")
    elif motivo == 'empate':
        print("\n EMPATE.\n Ninguém venceu essa.")
    elif motivo == 'vitoria':
        print("\n VITÓRIA!\n Você derrotou seu oponente.\n")
    else:
        print("\n DERROTA...\n O Jogo. Sim. Você perdeu.\n")

    input(" Pressione [Enter] pra continuar.")


def jogada_valida(estado, jogada):
    return True


def atualiza_estado_jogo(estado, jogada, jogador):
    """ Apenas o servidor atualiza efetivamente o estado.
        O cliente usa esta função apenas pra poder rederizar sua própria
        jogada declarada, antes do servidor validá-la."""

    jogador = jogador.strip().upper()
    estado = estado.decode('utf-8')
    jogada = jogada.decode('utf-8')

    # Põe 'd' na primeira posição indicando desistência do servidor.
    if 'd' in jogada:
        estado = 'd' + estado[1:]

    # Marca X ou O no índice declarado da jogada.
    else:
        # Extrai a posição no tabuleiro informada na jogada e adiciona
        # o deslocamento/offset pra string do estado de jogo.
        i = int(jogada.strip()) + 2
        estado = estado[:i] + jogador + estado[i+1:]

        # Detecta se jogada atual resultou em vitória do jogador.
        if vitoria(estado, jogador):
            estado = estado[:1] + jogador + estado[2:]


    return estado.encode('utf-8')


def servir_partida():
    print("\n #1 Servindo o jogo...")

    # Prepara socket do servidor para servir jogo.
    serv_sock = GameSocket()
    serv_sock.bind(('', GameSocket.PORT))
    serv_sock.listen(2)

    # Laço para aguardar conexões de clientes.
    while True:
        print("\n Aguardando outro jogador.\n Entre [Ctrl]+[C] para cancelar.")

        try:

            # Aceita conexão vinda de fora no nosso amado socket.
            client_sock, address = serv_sock.accept()
            print(" Conexão estabelecida com", address)

            # Estado inicial do jogo.
            estado_jogo = ESTADO_INICIAL

            # Rotina de servidor do jogo vem aqui.
            while True:

                # Envia estado atual do jogo.
                client_sock.send(estado_jogo)

                # Recebe jogada do cliente e checa por desistência.
                jogada = client_sock.recv()
                if desistencia(jogada):
                    encerra_partida('desistencia-oponente')
                    break

                #Verifica se jogada é válida.
                if not jogada_valida(estado_jogo, jogada):
                    # Marca estado como inválido antes de reenviar ao cliente.
                    continue

                # Atualiza e renderiza estado do jogo.
                estado_jogo = atualiza_estado_jogo(estado_jogo, jogada, CLIENTE)
                renderiza_jogo(estado_jogo)

                # Checa condição de vitória e, se for o caso, encerra jogo.
                # TODO

                # Se jogo continua, pega jogada do jogador local e valida
                # contra o estado atual do jogo.
                jogada = seleciona_jogada()
                while not jogada_valida(estado_jogo, jogada):
                    print(" Jogada inválida, escolha uma casa livre de 1 a 9.")
                    jogada = seleciona_jogada()

                # Atualiza estado do jogo com nova jogada.
                estado_jogo = atualiza_estado_jogo(estado_jogo, jogada, SERVIDOR)
                renderiza_jogo(estado_jogo)

                if desistencia(jogada):
                    client_sock.send(estado_jogo)
                    encerra_partida('desistencia-propria')
                    break

                # Verifica condição de vitória novamente.

        except KeyboardInterrupt:
            break

        # Importante fechar os sockets.
        try:
            client_sock.shutdown(2)
            client_sock.close()
        # Se o servidor fechou a conexão antes, não quebra o jogo.
        except Exception:
            pass

    # Importante fechar os sockets.
    try:
        serv_sock.shutdown(2)
        serv_sock.close()
    # Se o socket fechou prematuramente, não quebra o jogo.
    except Exception:
        pass


def conectar_partida():
    print("\n #2 Conectando a partida...")
    serv_addr = input("\n Informar endereço do servidor: ")

    # Prepara socket do cliente e conecta com servidor no endereço especificado.
    client_sock = GameSocket()
    client_sock.connect(serv_addr, GameSocket.PORT)

    print(" Conexão estabelecida, iniciando partida.")

    # Rotina de cliente do jogo vem aqui.
    while True:

        # Recebe um byte obj, decoda passa pra string em UTF-8.
        estado_jogo = client_sock.recv()

        # Interpreta estado de jogo e exibe ao jogador.
        renderiza_jogo(estado_jogo)

        # Saída antecipada.
        if desistencia(estado_jogo):
            encerra_partida('desistencia-oponente')
            break

        # Pega jogada do cliente.
        jogada = seleciona_jogada()
        while not jogada_valida(estado_jogo, jogada):
            print(" Jogada inválida, escolha uma casa livre de 1 a 9.")
            jogada = seleciona_jogada()

        # Envia jogada ao servidor
        client_sock.send(jogada)

        # Saída antecipada.
        if desistencia(jogada):
            encerra_partida('desistencia-propria')
            break

        # Exibe suposto estado atual do jogo (o servidor é o árbitro final).
        estado_jogo = atualiza_estado_jogo(estado_jogo, jogada, CLIENTE)
        renderiza_jogo(estado_jogo)

    # Importante fechar os sockets.
    try:
        client_sock.shutdown(2)
        client_sock.close()
    # Se o servidor fechou a conexão antes, não quebra o jogo.
    except Exception:
        pass


def creditos():
    print("Feito por Lucas Carvalho e Vitor Magno.")


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
