from classes import Servidor, Termo

#definindo lista de servidores e os termos definidos em termos.py
servidores_pesquisa = []

#COLOCAR OS TERMOS DA PESQUISA NESTE TRECHO DE CÓDIGO
#####################################################
#Ex.:

#termos = [Termo('MINISTÉRIO DA TRANSPARÊNCIA'),
#          Termo('PRESIDÊNCIA'),
#          Termo('PORTARIA')]
#
#servidores_pesquisa.append(Servidor('FULANO DE TAL',["email1@gmail.com", "email2@email.com"],termos))

#termos = [Termo('CICLANO DE TAL'),
#          Termo('TERMO ABC'),
#          Termo('LICITAÇÃO'),
#          Termo('TCU')]
#servidores_pesquisa.append(Servidor('CICLANO DE TAL',["emaildociclano@dominio.com.br"],termos))

termos = [
          Termo('MINISTÉRIO DA TRANSPARÊNCIA'),
          Termo('CGU'),
          Termo('CONTROLADORIA GERAL DA UNIÃO'),
          Termo('CONTROLADORIA-GERAL DA UNIÃO'),
          Termo('FISCALIZAÇÃO E CONTROLE'),
          Termo('CENSIPAM'),
          Termo('CENTRO GESTOR E OPERACIONAL')]
servidores_pesquisa.append(Servidor('BRUNO ALPHONSUS',["caputchinefrobles@localhost"],termos))

#####################################################
