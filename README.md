# Bom Velhinho
Jogo da velha no terminal em Python, para avaliação de Redes de Computadores - UFAL 2022

---

### Equipe:
* Lucas Carvalho Flores
* Vitor Magno

---

## Instalação & Execução

1. [Instalação do Python](https://www.python.org/downloads/) - É necessário ter o Python 3.7 ou posterior devidamente instalado e funcional nas máquinas a rodar o jogo:
2. Navegar até a pasta raiz do projeto pelo terminal.
3. Dentro da pasta raiz do projeto, executar o comando `python3 src/jogo.py` para iniciar a aplicação.  
Alguns sistemas aceitam `python` como atalho para `python3`, na dúvida verifique com `python --version` e `python3 --version`. Isso informará a versão do python chamada por estes comandos.

---

## Como Jogar

As opções são numeradas. Escolha uma opção e entre seu número quando solicitado.

Siga as instruções de jogo durante a partida.

Quando jogando como servidor, a porta usada para servir o jogo é a 6666. Certifique-se de que esta porta esteja acessível (sem bloqueios no firewall ou sendo usada por outra aplicação).

Quando rodando como cliente, será necessário apenas informar o IP do servidor, já que a porta é conhecida pelo cliente.

---

## Protocolo da Aplicação

As regras de comunicação ou protocolo da camada de aplicação estão registrados em `src/protocolo-aplicação.txt` para consulta.

---
