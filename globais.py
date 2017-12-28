import urllib3
import os, io
import re
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import gzip
import smtplib
from mailer import Mailer
from mailer import Message

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

def enviar_email(mensagem, emails_destino, remetente, servidor, porta, usuario, senha, extra):
    
    message = Message(From=remetente, To=emails_destino, charset="utf-8")

    if extra:
        message.Subject = "DouFinder - EDIÇÃO EXTRA"
    else:
        message.Subject = "DouFinder"

    message.Body = mensagem

    try:
        sender = Mailer(servidor, port=porta)
        if usuario and senha:
            sender.login(usuario, senha)
        sender.send(message)
    except smtplib.SMTPRecipientsRefused as e:
        print("ERRO AO ENVIAR LOG: %s" % str(e.recipients))
    except smtplib.SMTPException as e:
        print("ERRO AO ENVIAR LOG: %s" % e)
    except smtplib.SMTPAuthenticationError as e:
        print("ERRO AO ENVIAR LOG: %s" % e)

def print_help():
    print("\nDoufinder: Pesquisa termos no Diário Oficial da União e envia ocorrências por e-mail.\n")
    print("Sinopse:")
    print("/usr/bin/python3 main.py [OPÇÕES]...\n")
    print("Descrição:")
    print("\t-e Processa pesquisa da edição EXTRA.")
    print("\t-o Processa a pesquisa no modo OFFLINE. Opção é ignorada caso o diretório de download não esteja definido no arquivo de configuração.")
    print("\t   *Esta opção é aplicada quando a pesquisa no modo ONLINE já foi feita no mesmo dia e os arquivos de texto respectivo aos jornais já foram salvos no diretório de downloads.\n")
    print("\t   *A pesquisa offline não considera as configurações PAGINA_MIN e PAGINA_MAX..\n")
    print("ATENÇÃO:")
    print("\tA pesquisa da edição EXTRA do Diário Oficial ainda não foi implementada!\n")

