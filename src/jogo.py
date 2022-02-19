import socket
from time import sleep


ESTADO_INICIAL = b'1 1         '
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


E_BOAS_VINDAS = '~(˘▾˘~)'
E_DESPEDIDA = '(•‿•)/'
E_INPUT = '(•‿•)/'
E_JOGADA = '(ง •̀_•́)ง'
E_DESISTENCIA = '(Ｔ▽Ｔ)'
E_FELIZ_VITORIA = '\\(^o^)/'
E_TRISTE_DERROTA = '(T_T)'
E_EMPATE = '\'(ಠ_ಠ)'
E_ERRO = '(✖﹏✖)'
E_INVALIDO = '(o_O) ?'


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


def renderiza_jogo(estado, turno_real=True):

    estado = estado.decode('utf-8')
    tabuleiro = estado[3:]

    if turno_real:
        print('-'*80)
        print(" TURNO ", estado[2], ", tabuleiro:", sep='')

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


def seleciona_jogada(jogador_atual):

    jogada_valida = False
    while not jogada_valida:

        try:
            print(f" Sua marca é {jogador_atual}.")
            print(" Escolha onde marcar no tabuleiro pela numeração das casas.")
            print(" D, d, [Ctrl]+[C] ou [Ctrl]+[D] abandonam a partida.")
            print("\n Numeração das casas:")
            print("\n   1 | 2 | 3\n   ---------\n   4 | 5 | 6\n   ---------\n   7 | 8 | 9")
            jogada = input(f"\n {E_JOGADA}\n Marcar em: ").strip().lower()
            if jogada == 'd':
                jogada_valida = True
            else:
                jogada = int(jogada)
                if jogada in range(1, 10):
                    jogada_valida = True
                else:
                    print(f"\n {E_INVALIDO}")
                    print(" Posições válidas são de 1 a 9.")
                    print(" E a posição escolhida deve estar desocupada.\n")

        except (ValueError, KeyboardInterrupt, EOFError) as ex:
            if type(ex) is ValueError:
                print(f"\n {E_INVALIDO}")
                print(" Essa escolha não é um valor válido.")
                print(" Escolha uma casa de 1 a 9 para marcar, ou então")
                print(" use D, d, [Ctrl]+[C] ou [Ctrl]+[D] para abandonar partida.")
            elif type(ex) in (KeyboardInterrupt, EOFError):
                jogada = 'd'
                jogada_valida = True

    jogada = f"   {jogada}        "
    print()
    return jogada.encode('utf-8')


def padrao_de_jogo(estado, jogador):

    try:
        estado = estado.decode('utf-8')
    except Exception:
        pass

    tabuleiro = estado[3:].upper()
    tabuleiro = tabuleiro.replace(jogador.upper(), '1')
    tabuleiro = tabuleiro.replace(SERVIDOR.upper(), '0')
    tabuleiro = tabuleiro.replace(CLIENTE.upper(), '0')
    tabuleiro = tabuleiro.replace(' ', '0')

    return tabuleiro


def padrao_vitorioso(padrao):
    for pv in PADROES_VITORIA:
        acerto = 0
        for i in range(0, len(pv)):
            if padrao[i] == pv[i]:
                acerto += 1
        if acerto == 3:
            return True
    return False


def vitoria(estado, jogador):
    padrao = padrao_de_jogo(estado, jogador)
    return padrao_vitorioso(padrao)


def desistencia(jogada):
    if 'd' in jogada.decode('utf-8').lower():
        return True
    return False


def empate(estado):
    tabuleiro = estado.decode('utf-8')[3:]
    for i in range(0, len(tabuleiro)):
        if tabuleiro[i] == ' ':
            return False
    return True


def fim_de_jogo(estado, jogador, cliente_sock=None):

    motivo = None
    fim = False

    if jogador.upper() == SERVIDOR.upper():
        oponente = CLIENTE
    else:
        oponente = SERVIDOR

    if vitoria(estado, jogador):
        fim = True
        motivo = 'vitoria'

    elif vitoria(estado, oponente):
        fim = True
        motivo = 'derrota'

    elif empate(estado):
        fim = True
        motivo = 'empate'

    if fim:
        if cliente_sock:
            cliente_sock.send(estado)
        encerra_partida(motivo)

    return fim


def encerra_partida(motivo=None):
    if motivo == 'desistencia-propria':
        print(f"\n {E_TRISTE_DERROTA} DERROTA...\n Você desistiu da partida.\n")
    elif motivo == 'desistencia-oponente':
        print(f"\n {E_FELIZ_VITORIA} VITÓRIA!\n O adversário desistiu da partida.\n")
    elif motivo == 'empate':
        print(f"\n {E_EMPATE} EMPATE.\n Ninguém venceu essa.\n")
    elif motivo == 'vitoria':
        print(f"\n {E_FELIZ_VITORIA} VITÓRIA!\n Você derrotou seu oponente.\n")
    elif motivo == 'derrota':
        print(f"\n {E_TRISTE_DERROTA} DERROTA...\n O Jogo. Você perdeu. Sim.\n")
    else:
        print(f'\n {E_INVALIDO}\n Jogo encerrado por motivo desconhecido.\n')

    input(" Pressione [Enter] pra continuar.")


def jogada_valida(estado, jogada):
    estado = estado.decode('utf-8')
    jogada = jogada.decode('utf-8').strip()

    try:
        tabuleiro = estado[3:]
        indice_jogada = int(jogada) - 1
    except Exception:
        if 'd' in jogada.lower():
            return True
        else:
            return False

    if tabuleiro[indice_jogada] == ' ':
        return True
    else:
        return False


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

        # Atualiza contador de rodada.
        if jogador.upper() == SERVIDOR:
            try:
                rodada = int(estado[2]) + 1
            except ValueError:
                rodada = 1
            estado = estado[:2] + f'{rodada}' + estado[3:]


    return estado.encode('utf-8')


def servir_partida():
    print("\n #1 Servindo o jogo...")

    try:
        # Prepara socket do servidor para servir jogo.
        serv_sock = GameSocket()
        serv_sock.bind(('', GameSocket.PORT))
        serv_sock.listen(2)
    except OSError:
        print(f"\n {E_ERRO} ERRO:\n Falha ao vincular porta {GameSocket.PORT}, verifique se esta não está em uso por outra aplicação ou bloqueada.")
        print(" Note que portas recentemente usadas costumam levar até 2min para serem liberadas pelo S.O. para reuso.\n")
        return

    # Laço para aguardar conexões de clientes.
    run = True
    while run:
        print("\n Aguardando outro jogador.\n Entre [Ctrl]+[C] para cancelar.")

        try:
            # Aceita conexão vinda de fora no nosso amado socket.
            client_sock, address = serv_sock.accept()
            print(" Conexão estabelecida com", address, "iniciando jogo.\n")

            # Estado inicial do jogo.
            estado_jogo = ESTADO_INICIAL
            renderiza_jogo(estado_jogo)
            print(" Aguardando jogada inicial do cliente.\n")

            # Rotina de servidor do jogo vem aqui.
            while run:

                try:
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
                    if fim_de_jogo(estado_jogo, SERVIDOR, client_sock):
                        break

                    # Se jogo continua, pega jogada do jogador local e valida
                    # contra o estado atual do jogo.
                    jogada = seleciona_jogada(SERVIDOR)
                    while not jogada_valida(estado_jogo, jogada):
                        print(f"\n {E_INVALIDO}\n Jogada inválida, escolha uma casa livre de 1 a 9.")
                        jogada = seleciona_jogada()

                    # Atualiza estado do jogo com nova jogada.
                    estado_jogo = atualiza_estado_jogo(estado_jogo, jogada, SERVIDOR)
                    renderiza_jogo(estado_jogo, False)

                    # Checa se jogar local desistiu.
                    if desistencia(jogada):
                        client_sock.send(estado_jogo)
                        encerra_partida('desistencia-propria')
                        break

                    # Verifica condição de vitória novamente.
                    if fim_de_jogo(estado_jogo, SERVIDOR, client_sock):
                        break

                except (OSError, RuntimeError) as ex:
                    print(f"\n {E_ERRO} ERRO:\n Conexão com cliente perdida, voltando ao menu principal.\n")
                    run = False
                    break

                except (OSError, RuntimeError, KeyboardInterrupt) as ex:
                    if type(ex) is KeyboardInterrupt:
                        encerra_partida('desistencia-propria')
                    else:
                        print(f"\n {E_ERRO} ERRO:\n Conexão com cliente perdida. Voltando ao menu principal.\n")
                    run = False
                    break

        except (KeyboardInterrupt, EOFError, OSError, RuntimeError) as ex:
            if type(ex) in (OSError, RuntimeError):
                print(f"\n {E_ERRO} ERRO:\n Falha de comunicação com cliente.")
            print("\n Voltando ao menu principal.\n")
            run = False
            break

    # Importante fechar os sockets.
    try:
        client_sock.shutdown(2)
        client_sock.close()
        serv_sock.shutdown(2)
        serv_sock.close()
    # Se o socket fechou prematuramente, não quebra o jogo.
    except Exception:
        pass


def conectar_partida():
    print("\n #2 Conectando a partida...")
    try:
        serv_addr = input("\n Informar endereço do servidor: ")
    except (KeyboardInterrupt, EOFError):
        print("\n Cancelado pelo usuário, voltando ao menu principal.\n")
        return

    try:
        # Prepara socket do cliente e conecta com servidor no endereço especificado.
        client_sock = GameSocket()
        client_sock.connect(serv_addr, GameSocket.PORT)
        print(" Conexão estabelecida, iniciando partida.\n")
    except (OSError, RuntimeError, KeyboardInterrupt) as ex:
        if type(ex) is not KeyboardInterrupt:
            print(f"\n {E_ERRO} ERRO:\n Não foi possível conectar-se ao servidor.")
            print(f" Verifique o IP e se a porta {GameSocket.PORT} está disponível e desbloqueada.")
        print("\n Voltando ao menu principal.\n")
        return

    # Rotina de cliente do jogo vem aqui.
    while True:

        try:
            # Recebe do servidor o estado do jogo.
            estado_jogo = client_sock.recv()

            # Interpreta estado de jogo e exibe ao jogador.
            renderiza_jogo(estado_jogo)

            # Servidor desistiu da partida.
            if desistencia(estado_jogo):
                encerra_partida('desistencia-oponente')
                break

            # Verifica condição de vitória e encerra o jogo se for o caso.
            if fim_de_jogo(estado_jogo, CLIENTE, client_sock):
                break

            # Pega jogada do cliente.
            jogada = seleciona_jogada(CLIENTE)
            while not jogada_valida(estado_jogo, jogada):
                print(f"\n {E_INVALIDO}\n Jogada inválida, escolha uma casa livre de 1 a 9.")
                jogada = seleciona_jogada()

            # Envia jogada ao servidor
            client_sock.send(jogada)

            # Saída antecipada.
            if desistencia(jogada):
                encerra_partida('desistencia-propria')
                break

            # Exibe suposto estado atual do jogo (o servidor é o árbitro final).
            estado_jogo = atualiza_estado_jogo(estado_jogo, jogada, CLIENTE)
            print(" Enviado ao servidor:")
            renderiza_jogo(estado_jogo, False)

        except (OSError, RuntimeError, KeyboardInterrupt) as ex:
            if type(ex) is KeyboardInterrupt:
                encerra_partida('desistencia-propria')
            else:
                print(f"\n {E_ERRO} ERRO:\n Conexão com servidor perdida. Voltando ao menu principal.\n")
            break

    # Importante fechar os sockets.
    try:
        client_sock.shutdown(2)
        client_sock.close()
    # Se o servidor fechou a conexão antes, não quebra o jogo.
    except Exception:
        pass


def creditos():
    print("\n\n\n ( •_•) ( •_•)>⌐■-■ (⌐■_■)\n Feito por Lucas Carvalho e Vitor Magno.\n\n")


def menu_principal():

    TEXTO_PRINCIPAL = f"""
 --- BOM VELHINHO ---
 Jogo da velha em seu terminal! {E_BOAS_VINDAS}

 Opções:
   1. Servir novo jogo
   2. Conectar a jogo existente
   3. Créditos

 Entre qualquer outra coisa para encerrar o jogo.
    """

    print(TEXTO_PRINCIPAL)

    return input(f"{E_INPUT} : ")


def main():

    opcao = 0

    while opcao in [0, 1, 2, 3]:

        try:
            opcao = int(menu_principal())
        except (ValueError, KeyboardInterrupt, EOFError):
            print()
            break

        if int(opcao) == 1:
            servir_partida()
        elif int(opcao) == 2:
            conectar_partida()
        elif int(opcao) == 3:
            creditos()
        else:
            opcao = -1

    print(f"\n Encerrando jogo...{E_DESPEDIDA}  bye\n")


if __name__ == '__main__':
    main()
