import sys,getopt
from configparser import ConfigParser
from termos import servidores_pesquisa, Pesquisa
import datetime

#variáveis globais
hoje = datetime.datetime.now().date()
str_hoje = hoje.strftime("%d/%m/%Y")
# corrigido string de captcha que estava incorreta no sistema da imprensa nacional e agora foi corrigida

url = "http://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?jornal={0}&pagina={1}&data={2}&captchafield=firstAccess"

config_smtp_servidor = ''
config_smtp_porta = ''
config_smtp_usuario = ''
config_smtp_senha = ''
config_download_dir = ''

def main(argv):
    try:
        config = ConfigParser()
        config_arquivo = os.path.join(os.path.dirname(__file__), 'doufinder.cfg')

        if os.path.isfile(config_arquivo):
            config.read_file(open(config_arquivo),'UTF-8')
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

        config_smtp_usuario = str(config['EMAIL']['SMTP_USUARIO'])
        config_smtp_senha = str(config['EMAIL']['SMTP_SENHA'])

        if config['OFFLINE']['DOWNLOAD_DIR']:
            config_download_dir = os.path.join(
                str(config['OFFLINE']['DOWNLOAD_DIR']),
                hoje.strftime("%d-%m-%Y"))
        
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
        pesquisa = Pesquisa(servidores_pesquisa)
        pesquisa.processar(515)
        pesquisa.processar(529)
        pesquisa.processar(530)

        #depois de processada a pesquisa dos termos nos jornais
        #enviar as ocorrencias para os e-mails informados no cadastro dos termos
        pesquisa.enviar_ocorrencias()

if __name__ == "__main__": main(sys.argv[1:])
