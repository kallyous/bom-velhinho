tabuleiro = []

def leTabuleiro(tabuleiro):
    '''varrer o tabuleiro e printar o estado atual'''



def menu():
    print('--1 Conectar--\n'
          '--2 Hospedar--\n'
          '--3 Sair--')

    option = input('Selecione...')
    if option == '1' or option == '2' or option == '3':
        option = int(option)

        if option == 1:
            print('solicita ip e conecta')
        elif option == 2:
            print('informa ip e aguarda conexão')
        else:
            print('finalizando, até mais')

    else:
        print('opção inválida, retornando ao menu')
        menu()

def jogo():
    for i in range(3):
        tabuleiro.append([0] * 3)

    print('--Jogo da velha--')
    menu()
    print('_|_|_\n'
          '_|_|_\n'
          '_|_|_\n'
          'Hospedeiro[O], Visitante[X]\n'
          'O hospedeiro começa jogando')
    for n in range(9):
        '''como receber as duas variaveis de uma vez e ja colocar na matriz do tabuleiro?'''
        jogada = input('jogada '+n+'\nDigite Linha e Coluna')


jogo()

