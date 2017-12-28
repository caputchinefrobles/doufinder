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

