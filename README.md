# DouFinder

Script que pesquisa no Diário Oficial da União termos de interesse e notifica por e-mail.

## Dependências

- pdfminer.six (pdfminer com suporte para python 3.x)
- smtplib
- urllib3
- mailer

`pip install pdfminer.six urllib3 mailer`

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

