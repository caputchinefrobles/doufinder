# DouFinder

Script que pesquisa no Diário Oficial da União termos de interesse e notifica por e-mail.

## Dependências

- pdfminer.six (pdfminer com suporte para python 3.x)
- smtplib
- urllib3
- mailer

## Utilização

Executar o comando - `/usr/bin/python3 main.py` - ou agendar no crontab para definir
a periodicidade da pesquisa.

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

Para que os alertas sejam enviados, é necessário informar o endereço de SMTP e a porta utilizada além do respectivo usuário e senha para o serviço. Para isto, basta substituir os valores de email_remetente@dominio.xyz, host_smtp, usuario_smtp e senha_smtp dentro da função enviar_log:

```python
    **message = Message(From="__email_remetente@dominio.xyz__", To=emails_destino, charset="utf-8")**

    if extra:
        message.Subject = "DouFinder - EDIÇÃO EXTRA"
    else:
        message.Subject = "DouFinder"

    message.Body = mensagem

    try:
        **sender = Mailer('__host_smtp__', port=25)**
        **sender.login('__usuario_smtp__', '__senha_smtp__')**
        sender.send(message)
    except smtplib.SMTPRecipientsRefused as e:
```
