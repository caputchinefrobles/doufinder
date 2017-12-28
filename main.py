import sys,os,getopt
from configparser import ConfigParser
from classes import Pesquisa
from termos import servidores_pesquisa
import termos
from datetime import datetime


config_smtp_servidor = ''
config_smtp_porta = ''
config_smtp_usuario = ''
config_smtp_senha = ''
config_download_dir = ''

def main(argv):
    try:

        #carregando configurações
        config = ConfigParser()
        config_arquivo = os.path.join(os.path.dirname(__file__), 'doufinder.cfg')

        if os.path.isfile(config_arquivo):
            config.read_file(open(config_arquivo, 'r'),'UTF-8')
        else:
            raise FileNotFoundError

        if not config['EMAIL']['SMTP_SERVIDOR']:
            raise Exception('Servidor SMTP não definido em "doufinder.cfg"')
        else:
            config_smtp_servidor = str(config['EMAIL']['SMTP_SERVIDOR'])
        
        if not config['EMAIL']['SMTP_PORTA']:
            raise Exception('Porta SMTP não definida em "doufinder.cfg"')
        else:
            config_smtp_porta = int(config['EMAIL']['SMTP_PORTA'])
        
        if not config['EMAIL']['SMTP_REMETENTE']:
            raise Exception('Remetente SMTP não definido em "doufinder.cfg"')
        else:
            config_smtp_remetente = str(config['EMAIL']['SMTP_REMETENTE'])

        config_smtp_usuario = str(config['EMAIL']['SMTP_USUARIO'])
        config_smtp_senha = str(config['EMAIL']['SMTP_SENHA'])

        if config['OFFLINE']['DOWNLOAD_DIR']:
            config_download_dir = os.path.join(
                str(config['OFFLINE']['DOWNLOAD_DIR']),
                datetime.now().date().strftime("%d-%m-%Y"))

        if (config['JORNAIS']['ID_JORNAL1']):
            config_id_jornal1 = int(config['JORNAIS']['ID_JORNAL1'])

        if (config['JORNAIS']['ID_JORNAL2']):
            config_id_jornal2 = int(config['JORNAIS']['ID_JORNAL2'])

        if (config['JORNAIS']['ID_JORNAL3']):
            config_id_jornal3 = int(config['JORNAIS']['ID_JORNAL3'])

        if (config['JORNAIS']['PAGINA_MIN']):
            config_pagina_min = int(config['JORNAIS']['PAGINA_MIN'])

        if (config['JORNAIS']['PAGINA_MAX']):
            config_pagina_max = int(config['JORNAIS']['PAGINA_MAX'])

        #verificando opção para pesquisa na edição extra do jornal
        #ainda não implementada
        opts, args = getopt.getopt(argv, "e")

    except getopt.GetoptError as e:
        print("%s: Erro de argumento\n" % type(e).__name__)
        sys.exit(2)
    except FileNotFoundError as e:
        print('s%: Não foi possível ler o arquivo "doufinder.cfg"\n' %
                type(e).__name__)
        sys.exit(4)
    except BaseException as e:
        print("%s: %s\n" % (type(e).__name__, e))
        sys.exit(4)

    if len(opts) > 0:
        for opt, arg in opts:
            if opt =='-e':
                print("Pesquisa na edição EXTRA ainda não implementada.")
                sys.exit(3)
            else:
                print("Erro de argumento\n")
                sys.exit(2)
    else:

        try:
            pesquisa = Pesquisa(servidores_pesquisa, config_download_dir)
            if config_id_jornal1:
                pesquisa.processar(config_id_jornal1, config_pagina_min, config_pagina_max)
            if config_id_jornal2:
                pesquisa.processar(config_id_jornal2, config_pagina_min, config_pagina_max)
            if config_id_jornal3:
                pesquisa.processar(config_id_jornal3, config_pagina_min, config_pagina_max)

            #depois de processada a pesquisa dos termos nos jornais
            #enviar as ocorrencias para os e-mails informados no cadastro dos termos
            pesquisa.enviar_ocorrencias(config_smtp_remetente, config_smtp_servidor, config_smtp_porta, 
                    config_smtp_usuario, config_smtp_senha)
        except BaseException:
            raise

if __name__ == "__main__": main(sys.argv[1:])
