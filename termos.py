from classes import Servidor, Termo

#definindo lista de servidores e os termos definidos em termos.py
servidores_pesquisa = []

#COLOCAR OS TERMOS DA PESQUISA NESTE TRECHO DE CÓDIGO
#####################################################
#Ex.:

termos = [Termo('FULANO DE TAL'),
          Termo('MINISTERIO XYZ'),
          Termo('AQUISIÇÃO DE')]

servidores_pesquisa.append(Servidor('FULANO DE TAL',["email1@gmail.com", "email2@email.com"],termos))

termos = [Termo('CICLANO DE TAL'),
          Termo('TERMO ABC'),
          Termo('LICITAÇÃO'),
          Termo('TCU')]
servidores_pesquisa.append(Servidor('CICLANO DE TAL',["emaildociclano@dominio.com.br"],termos))

#####################################################
