# coding=utf-8
import os
import sys,getopt
import datetime
import urllib3
import io
from io import BytesIO
import re
#import PyPDF2
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import gzip
import smtplib
from mailer import Mailer
from mailer import Message

#classes e funções globais
class Servidor:
    def __init__(self, nome = '', emails_notificacao = [], termos_pesquisa = []):
        self.nome = nome
        self.emails_notificacao = emails_notificacao
        self.termos_pesquisa = termos_pesquisa

class Termo:
    def __init__(self, valor = '') :
        self.valor = valor
        self.ocorrencias = []

# https://stackoverflow.com/questions/26494211/extracting-text-from-a-pdf-file-using-pdfminer-in-python
def extrair_texto(stream):
    rsrcmgr = PDFResourceManager()
    retstr = io.StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    #fp = open(stream, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos = set()

    for page in PDFPage.get_pages(stream, pagenos, maxpages=maxpages,
                                  password=password,
                                  caching=caching,
                                  check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    stream.close()
    device.close()
    retstr.close()
    return text

def enviar_log(mensagem, emails_destino, extra):
    
    message = Message(From="email_remetente@dominio.xyz", To=emails_destino, charset="utf-8")

    if extra:
        message.Subject = "DouFinder - EDIÇÃO EXTRA"
    else:
        message.Subject = "DouFinder"

    message.Body = mensagem

    try:
        sender = Mailer('smtp_host', port=25)
        sender.login('usuario_smtp', 'senha_smtp')
        sender.send(message)
    except smtplib.SMTPRecipientsRefused as e:
        print("ERRO AO ENVIAR LOG: %s" % str(e.recipients))
    except smtplib.SMTPException as e:
        print("ERRO AO ENVIAR LOG: %s" % e)
    except smtplib.SMTPAuthenticatioError as e:
        print("ERRO AO ENVIAR LOG: %s" % e)

#variáveis globais
hoje = datetime.datetime.now().date()
str_hoje = hoje.strftime("%d/%m/%Y")
# corrigido string de captcha que estava incorreta no sistema da imprensa nacional e agora foi corrigida
url = "http://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?jornal={0}&pagina={1}&data={2}&captchafield=firstAccess"
diretorio_texto = "%s%s/" % ("./Downloads/diarios_oficiais/", hoje.strftime("%d-%m-%Y"))

#COLOCAR OS TERMOS DA PESQUISA NESTE TRECHO DE CÓDIGO
#####################################################
servidores_pesquisa = []

#Ex.:
#termos = [Termo('FULANO DE TAL'),
#          Termo('MINISTERIO XYZ'),
#          Termo('AQUISIÇÃO DE')]
#
#servidores_pesquisa.append(Servidor('FULANO DE TAL',["email1@gmail.com", "email2@email.com"],termos))
#
#termos = [Termo('CICLANO DE TAL'),
#          Termo('TERMO ABC'),
#          Termo('LICITAÇÃO'),
#          Termo('TCU')]
#servidores_pesquisa.append(Servidor('CICLANO DE TAL',["emaildociclano@dominio.com.br"],termos))

#####################################################


#procurando no diário oficial edição extra
def extra():
    for j in range(1000,4000, 1000):
        for p in range (1,500):
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
            full_url = url.format(j,p,str_hoje)
            response = http.request('GET', full_url, headers=header)

            print ("Seção {0}, Página {1}".format(j, p))
            if 'text/html' not in response.headers['Content-Type'] and response.headers['Content-Encoding'] == 'gzip':
                buff = response.data
                arquivo = BytesIO(buff)
                texto = PyPDF2.PdfFileReader(arquivo).getPage(0).extractText().upper().replace('\n',' ')

                #escrevendo a pagina em disco no diretório de download
                if not os.path.exists(diretorio_texto):
                        os.makedirs(diretorio_texto)
                filename = "%s-%s.%s" % (j, p, "txt")
                with open("%s%s" % (diretorio_texto,filename), 'w') as out:
                        out.write(texto)
        
                for servidor in servidores_pesquisa:
                    for termo in servidor.termos_pesquisa:

                        if re.search(termo.valor.replace(' ','(\s|)*').replace(' DA ','(DA|)').replace(' DE ','(DE|)'),texto):
                            ocor = 'Jornal: {0}, Página: {1}, URL: {2}'.format(j, p, full_url)
                            termo.ocorrencias.append(ocor)
            else: break
        
        for servidor in servidores_pesquisa:
            msg = ''
            for termo in servidor.termos_pesquisa:
                if len(termo.ocorrencias) > 0:
                    msg += "\n\n" + termo.valor + ":\n"
                    for ocorrencia in termo.ocorrencias:
                        msg += '\t' + ocorrencia + '\n'
    
            if msg is not '' : 
                enviar_log(msg, servidor.emails_notificacao, False)

def processar_pesquisa(jornal, extra=False):
    #range dos jornais mudou de 1, 2 e 3 para 515, 529 e 530
    for pagina in range (1,500):
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
           arquivo = BytesIO(buff)
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


def main(argv):

    try:
        opts, args = getopt.getopt(argv, "e")
    except getopt.GetoptError:
        print("Erro de argumento\n")
        sys.ext(2)

    if len(opts) > 0:
        for opt, arg in opts:
            if opt =='-e':
                extra()
                processar_pesquisa(515, True)
                processar_pesquisa(529, True)
                processar_pesquisa(530, True)
            else:
                print("Erro de argumento\n")
                sys.ext(2)
    else:
        processar_pesquisa(515)
        processar_pesquisa(529)
        processar_pesquisa(530)
        
        for servidor in servidores_pesquisa:
            msg = ''
            for termo in servidor.termos_pesquisa:
                if len(termo.ocorrencias) > 0:
                    msg += "\n\n" + termo.valor + ":\n"
                    for ocorrencia in termo.ocorrencias:
                        msg += '\t' + ocorrencia + '\n'
    
            if msg is not '' : 
                enviar_log(msg, servidor.emails_notificacao, False)

if __name__ == "__main__": main(sys.argv[1:])
