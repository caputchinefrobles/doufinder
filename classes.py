from globais import *

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
    def __init__(self, lista_servidores=None):
        lista = lista_servidores

    #TODO: incluir o processamento da edição EXTRA
    def processar(jornal, extra=False):
        
        #alterando o número máximo de páginas da pesquisa (hoje 26/12, só o jornal 1 teve mais de 
        #1000 páginas).
        for pagina in range (1,1100):
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
           full_url = url.format(jornal,pagina,str_hoje)
           print(full_url)
           response = http.request('GET', full_url, headers=header)
    
           print ("Seção {0}, Página {1}".format(jornal, pagina))
           if 'text/html' not in response.headers['Content-Type'] and response.headers['Content-Encoding'] == 'gzip':
               buff = response.data
               arquivo = io.BytesIO(buff)
               #print(PyPDF2.PdfFileReader(arquivo).getPage(0).extractText())
               #texto = PyPDF2.PdfFileReader(arquivo).getPage(0).extractText().upper().replace('\n',' ')
               texto = extrair_texto(arquivo).upper()
           
               #escrevendo a pagina em disco no diretório de download
               if not os.path.exists(diretorio_texto):
                       os.makedirs(diretorio_texto)
               filename = "%s-%s.%s" % (jornal, pagina, "txt")
               with open("%s%s" % (diretorio_texto,filename), 'w') as out:
                       out.write(texto)
        
               for servidor in servidores_pesquisa:
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

    def enviar_ocorrencias():
        for servidor in servidores_pesquisa:
            #caso haja ocorrência de algum termo, montar mensagem e enviar e-mail
            msg = ''
            for termo in servidor.termos_pesquisa:
                if len(termo.ocorrencias) > 0:
                    msg += "\n\n" + termo.valor + ":\n"
                    for ocorrencia in termo.ocorrencias:
                       msg += '\t' + ocorrencia + '\n'
   
            if msg is not '' : 
                enviar_email(msg, servidor.emails_notificacao, False)
