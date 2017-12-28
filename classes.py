from globais import *
import datetime

class Servidor:
    def __init__(self, nome = '', emails_notificacao = [], termos_pesquisa = []):
        self.nome = nome
        self.emails_notificacao = emails_notificacao
        self.termos_pesquisa = termos_pesquisa

class Termo:
    def __init__(self, valor = '') :
        self.valor = valor
        self.ocorrencias = []

class Pesquisa:

    def __init__(self, lista_servidores=None, diretorio_offline=None):
        self.lista = lista_servidores
        self.url = "http://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?jornal={0}&pagina={1}&data={2}&captchafield=firstAccess"
        self.hoje = datetime.datetime.now().date()
        self.diretorio_offline = diretorio_offline

    #TODO: 
    #
    #       incluir o processamento da edição EXTRA
    #
    def processar(self, jornal, pagina_inicio=1, pagina_fim=1100, extra=False):
        
        #alterando o número máximo de páginas da pesquisa (hoje 26/12, só o jornal 1 teve mais de 
        #1000 páginas).
        for pagina in range (pagina_inicio,pagina_fim):
           header = {
               'Content-Type':'application/pdf',
               'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
               'Accept-Encoding':'gzip, deflate',
               'Accept-Language':'en,pt-BR;q=0.8,pt;q=0.6',
               'Cache-Controle':'no-cache',
               'Connection':'keep-alive',
               'Host':'pesquisa.in.gov.br',
               'Upgrade-Insecure-Requests':'1'}
        
           http = urllib3.PoolManager()
           full_url = self.url.format(jornal,pagina,
                   self.hoje.strftime("%d/%m/%Y"))
           
           print ("Seção {0}, Página {1}".format(jornal, pagina))
           print(full_url)
           response = http.request('GET', full_url, headers=header)
    
           if 'text/html' not in response.headers['Content-Type'] and response.headers['Content-Encoding'] == 'gzip':
               buff = response.data
               arquivo = io.BytesIO(buff)
               texto = extrair_texto(arquivo).upper()
           
               if self.diretorio_offline: 

                   #escrevendo a pagina em disco no diretório de download
                   if not os.path.exists(self.diretorio_offline):
                           os.makedirs(self.diretorio_offline)

                   filename = "%s-%s.%s" % (jornal, pagina, "txt")
                   #with open("%s%s" % (diretorio_offline,filename), 'w') as out:
                   with open(os.path.join(self.diretorio_offline,filename), 'w') as out:
                       out.write(texto)
                       print("Salvo em %s..." % os.path.realpath(out.name))
        
               for servidor in self.lista:
                   #pesquisa os termos do servidor interessado
                   for termo in servidor.termos_pesquisa:
    
                       if re.search(termo.valor.replace(' ','(\s|)*').replace(' DA ','(DA|)').replace(' DE ','(DE|)'),texto):
                           if jornal == 515:
                               ocor = 'Jornal: 1, Página: {0}, URL: {1}'.format(pagina, full_url)
                           if jornal == 529:
                               ocor = 'Jornal: 2, Página: {0}, URL: {1}'.format(pagina, full_url)
                           if jornal == 530:
                               ocor = 'Jornal: 3, Página: {0}, URL: {1}'.format(pagina, full_url)
                           termo.ocorrencias.append(ocor)

           else: break

    def enviar_ocorrencias(self, remetente, servidor_smtp, porta, usuario, senha):
        for servidor in self.lista:
            #caso haja ocorrência de algum termo, montar mensagem e enviar e-mail
            msg = ''
            for termo in servidor.termos_pesquisa:
                if len(termo.ocorrencias) > 0:
                    msg += "\n\n" + termo.valor + ":\n"
                    for ocorrencia in termo.ocorrencias:
                       msg += '\t' + ocorrencia + '\n'
   
            if msg is not '' : 
                enviar_email(msg, servidor.emails_notificacao, 
                        remetente, servidor_smtp, porta, usuario, senha, False)
