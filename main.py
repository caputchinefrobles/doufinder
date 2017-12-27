import sys, os, getopt
import configparser

def main(argv):

    try:

        config = configparser.ConfigParser()
        config.read_file(open('doufinder.cfg'))
        
        opts, args = getopt.getopt(argv, "e")

    except getopt.GetoptError:
        print("Erro de argumento\n")
        sys.exit(2)
    except getopt.GetoptError:
        print("Erro de argumento\n")
        sys.exit(2)
    except FileNotFoundError:
        print('Não foi possível ler o arquivo de configuração "./doufinder.cfg"\n')
        sys.exit(3)

    if len(opts) > 0:
        for opt, arg in opts:
            if opt =='-e':
                print("Pesquisa na edição EXTRA ainda não implementada.")
                sys.ext(4)
                #extra()
                #processar_pesquisa(515, True)
                #processar_pesquisa(529, True)
                #processar_pesquisa(530, True)
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
