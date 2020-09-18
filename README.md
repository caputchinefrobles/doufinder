# DouFinder

Script que pesquisa no Diário Oficial da União termos de interesse e notifica por e-mail.

## Dependências

- pdfminer.six (pdfminer com suporte para python 3.x)
- smtplib
- urllib3
- mailer
- chardet (pdfminer)
- certifi

`pip install pdfminer.six urllib3 mailer chardet certifi`

## Utilização

Executar o comando - `/usr/bin/python3 main.py` - ou agendar no crontab para definir
a periodicidade da pesquisa.

![alt print de ajuda](help.png?raw=true "Doufinder opções")

O script acessa cada página do Diário Oficial procurando os termos cadastrados de acordo com a seguinte estrutura: 

Servidor:
- Nome do interessado 
- Lista de e-mails para o envio do alerta de ocorrência
- Termos:
  * Termo 1
  * Termo 2
  * Termo 3
  * ...  

Um exemplo de como seriam cadastrados os termos:

```python 
servidores_pesquisa = []
termos = [Termo('FULANO DE TAL'),
          Termo('MINISTERIO XYZ'),
          Termo('AQUISIÇÃO DE')]

servidores_pesquisa.append(Servidor('FULANO DE TAL',["email1@gmail.com", "email2@email.com"],termos))

termos = [Termo('CICLANO DE TAL'),
          Termo('TERMO ABC'),
          Termo('LICITAÇÃO'),
          Termo('TCU')]
servidores_pesquisa.append(Servidor('CICLANO DE TAL',["emaildociclano@dominio.com.br"],termos))
```

## Configuração

Antes de executar o script é necessário realizar definir alguns parâmetros no arquivo de configuração doufinder.cfg.  

Os únicos parâmetros obrigatórios são:
- `SMTP_SERVIDOR`
- `SMTP_PORTA`

Sem estes parâmetros não é possível o envio das ocorrências aos interessados na pesquisa. Caso o serviço de SMTP não necessite de autenticação, usuário e senha não serão necessários.


O parâmetro `DOWNLOAD_DIR` é necessário para que a função de pesquisa offline funcione.

## ERRO DE CERTIFICADO

Recentemente, o acesso às páginas do jornal do diário oficial foi convertido
para HTTPS. A cadeia de certificados usada para o host `pesquisa.in.gov.br`
não está incluida nos certificados do sistema operacional (pode ser que esteja
incluída nos certificados do browser). Desta forma, o python não consegue
validar o certificado fornecido pelo resultado do "request".

Para contornar o problema, é necessário incluir a cadeia de certificados de
https://pesquisa.in.gov.br no arquivo ca-cert.pem utilizado pelo python:
    1. Acesse pelo browser a url [https://pesquisa.in.gov.br](https://pesquisa.in.gov.br)
    2. Extraia a cadeia de certificados
    3. Abra um shell python e execute os seguintes comantes:
        a. ```python import certifi```
        b. ```python certifi```
        c. ```python print(certifi.where())```
    4. O resultado deve ser o caminho do arquivo cacert.pem que o python usa.
       Ex.: .local/lib/python3.8/site-packages/certifi/cacert.pem
    5. Adicionar o conteúdo do certificado extraído no passo 2 ao final do
       arquivo cacert.pem apontado pelo passo 3.

Executando estes passos de maneira correta, o erro de validação de certificado
deve ser resolvido. 
