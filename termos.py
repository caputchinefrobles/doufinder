from classes import Servidor, Termo

#definindo lista de servidores e os termos definidos em termos.py
servidores_pesquisa = []

#COLOCAR OS TERMOS DA PESQUISA NESTE TRECHO DE CÓDIGO
#####################################################
#Ex.:

termos = [Termo('SENAR'),
          Termo('AGRICULTURA'),
          Termo('CNA'),
          Termo('Serviço Nacional de Agricultura'),
          Termo('Confederação Nacional da Agricultura')]

servidores_pesquisa.append(Servidor('Bruno Justino',["bjpraciano@gmail.com"],termos))

# termos = [Termo('CICLANO DE TAL'),
#           Termo('TERMO ABC'),
#           Termo('LICITAÇÃO'),
#           Termo('TCU')]
# servidores_pesquisa.append(Servidor('CICLANO DE TAL',["emaildociclano@dominio.com.br"],termos))

#####################################################
