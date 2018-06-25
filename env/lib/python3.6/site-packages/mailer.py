#coding: UTF8
"""
mailer module

Simple front end to the smtplib and email modules,
to simplify sending email.

A lot of this code was taken from the online examples in the
email module documentation:
http://docs.python.org/library/email-examples.html

Released under MIT license.

Version 0.5 is based on a patch by Douglas Mayle

Sample code:

    import mailer

    message = mailer.Message()
    message.From = "me@example.com"
    message.To = "you@example.com"
    message.RTo = "you@example.com"
    message.Subject = "My Vacation"
    message.Body = open("letter.txt", "rb").read()
    message.attach("picture.jpg")

    sender = mailer.Mailer('mail.example.com')
    sender.send(message)

"""

import smtplib
import socket
import threading
import queue
import uuid

# this is to support name changes
# from version 2.4 to version 2.5
try:
    from email import encoders
    from email.header import make_header
    from email.mime.audio import MIMEAudio
    from email.mime.base import MIMEBase
    from email.mime.image import MIMEImage
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
except ImportError:
    from email import Encoders as encoders
    from email.Header import make_header
    from email.MIMEAudio import MIMEAudio
    from email.MIMEBase import MIMEBase
    from email.MIMEImage import MIMEImage
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEText import MIMEText

# For guessing MIME type based on file name extension
import mimetypes
import time

from os import path

__version__ = "0.8.1"
__author__ = "Ryan Ginstrom"
__license__ = "MIT"
__description__ = "A module to send email simply in Python"


class Mailer(object):
    """
    Represents an SMTP connection.

    Use login() to log in with a username and password.
    """

    def __init__(self, host="localhost", port=0, use_tls=False, usr=None, pwd=None, use_ssl=False, use_plain_auth=False,
                 timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        self.host           = host
        self.port           = port
        self.use_tls        = use_tls
        self.use_ssl        = use_ssl
        self.use_plain_auth = use_plain_auth
        self._usr           = usr
        self._pwd           = pwd
        self.timeout        = timeout

    def login(self, usr, pwd):
        self._usr = usr
        self._pwd = pwd

    def send(self, msg, debug=False):
        """
        Send one message or a sequence of messages.

        Every time you call send, the mailer creates a new
        connection, so if you have several emails to send, pass
        them as a list:
        mailer.send([msg1, msg2, msg3])
        """
        if self.use_ssl:
            server = smtplib.SMTP_SSL(self.host, self.port, timeout=self.timeout)
        else:
            server = smtplib.SMTP(self.host, self.port, timeout=self.timeout)

        if debug:
            server.set_debuglevel(1)

        if self._usr and self._pwd:
            if self.use_tls is True:
                server.ehlo()
                server.starttls()
                server.ehlo()

            if self.use_plain_auth is True:
                server.esmtp_features["auth"] = "LOGIN PLAIN"

            server.login(self._usr, self._pwd)

        if isinstance(msg, Message):
            msg = [msg]

        for m in msg:
            self._send(server, m)

        server.quit()

    def _send(self, server, msg):
        """
        Sends a single message using the server
        we created in send()
        """
        me = msg.From
        if isinstance(msg.To, str):
            to = [msg.To]
        else:
            to = list(msg.To)

        cc = []
        if msg.CC:
            if isinstance(msg.CC, str):
                cc = [msg.CC]
            else:
                cc = list(msg.CC)

        bcc = []
        if msg.BCC:
            if isinstance(msg.BCC, str):
                bcc = [msg.BCC]
            else:
                bcc = list(msg.BCC)

        rto = []
        if msg.RTo:
            if isinstance(msg.RTo, str):
                rto = [msg.RTo]
            else:
                rto = list(msg.RTo)

        you = to + cc + bcc
        server.sendmail(me, you, msg.as_string())


class Message(object):
    """
    Represents an email message.

    Set the To, From, Reply-To, Subject, and Body attributes as plain-text strings.
    Optionally, set the Html attribute to send an HTML email, or use the
    attach() method to attach files.

    Use the charset property to send messages using other than us-ascii

    If you specify an attachments argument, it should be a list of
    attachment filenames: ["file1.txt", "file2.txt"]

    `To` should be a string for a single address, and a sequence
    of strings for multiple recipients (castable to list)

    Send using the Mailer class.
    """

    def __init__(self, **kwargs):
        """
        Parameters and default values (parameter names are case insensitive):
            To=None, From=None, RTo=None, CC=None, BCC=None, Subject=None, Body=None, Html=None,
            Date=None, Attachments=None, Charset=None, Headers=None
        """

        # extract  parameters and convert names to lowercase
        params = {}
        for i in kwargs:
            params[i.lower()] = kwargs[i]

        # preprocess attachments
        self.attachments = []
        attachments = params.get('attachments', None)
        if attachments:
            for attachment in attachments:
                if isinstance(attachment, str):
                    self.attachments.append((attachment, None, None, None, None))
                else:
                    try:
                        length = len(attachment)
                    except TypeError:
                        length = None
                    else:
                        if length is None or length <= 4:
                            self.attachments.append((attachment, None, None, None, None))
                        else:
                            self.attachments.append((tuple(attachment) + (None, None, None, None))[:4])


        self.To         = params.get('to', None)
        self.RTo        = params.get('rto', None)
        self.CC         = params.get('cc', None)
        self.BCC        = params.get('bcc', None)
        self.From       = params.get('from', None) # string or iterable
        self.Subject    = params.get('subject', '') # string
        self.Body       = params.get('body', None)
        self.Html       = params.get('html', None)
        self.Date       = params.get('date', time.strftime("%a, %d %b %Y %H:%M:%S %z", time.gmtime()))
        self.charset    = params.get('charset', 'us-ascii')
        self.Headers    = params.get('headers', {})

        if isinstance(self.Body, str):
            self.Body = self.Body.encode(self.charset)

        self.message_id = self.make_key()


    def make_key(self):
        return str(uuid.uuid4())

    def header(self, key, value):
        self.Headers[key] = value

    def as_string(self):
        """Get the email as a string to send in the mailer"""

        if not self.attachments:
            return self._plaintext()
        else:
            return self._multipart()

    def _plaintext(self):
        """Plain text email with no attachments"""

        if not self.Html:
            msg = MIMEText(self.Body, 'plain', self.charset)
        else:
            msg = self._with_html()

        self._set_info(msg)
        return msg.as_string()

    def _with_html(self):
        """There's an html part"""

        outer = MIMEMultipart('alternative')

        part1 = MIMEText(self.Body, 'plain', self.charset)
        part2 = MIMEText(self.Html, 'html', self.charset)

        outer.attach(part1)
        outer.attach(part2)

        return outer

    def _set_info(self, msg):
        if self.charset == 'us-ascii':
            msg['Subject'] = self.Subject
            msg['From'] = self.From

        else:
            if isinstance(self.Subject, str):
                subject = self.Subject
            else:
                subject = str(self.Subject, self.charset)
            msg['Subject'] = str(make_header([(subject, self.charset)]))

            if isinstance(self.From, str):
                from_ = self.From
            else:
                from_ = str(self.From, self.charset)
            msg['From'] = str(make_header([(from_, self.charset)]))


        if isinstance(self.To, str):
            msg['To'] = self.To
        else:
            self.To = list(self.To)
            msg['To'] = ", ".join(self.To)

        if self.RTo:
            if isinstance(self.RTo, str):
                msg.add_header('reply-to', self.RTo)
            else:
                self.RTo = list(self.RTo)
                msg.add_header('reply-to', ", ".join(self.RTo))

        if self.CC:
            if isinstance(self.CC, str):
                msg['CC'] = self.CC
            else:
                self.CC = list(self.CC)
                msg['CC'] = ", ".join(self.CC)


        if self.BCC:
            if isinstance(self.BCC, str):
                msg['BCC'] = self.BCC
            else:
                self.BCC = list(self.BCC)
                msg['BCC'] = ", ".join(self.BCC)


        if self.Headers:
            for key, value in list(self.Headers.items()):
                msg[key] = str(value).encode(self.charset)


        msg['Date'] = self.Date

    def _multipart(self):
        """The email has attachments"""

        msg = MIMEMultipart('related')

        if self.Html:
            outer = MIMEMultipart('alternative')

            part1 = MIMEText(self.Body, 'plain', self.charset)
            part1.add_header('Content-Disposition', 'inline')

            part2 = MIMEText(self.Html, 'html', self.charset)
            part2.add_header('Content-Disposition', 'inline')

            outer.attach(part1)
            outer.attach(part2)
            msg.attach(outer)
        else:
            msg.attach(MIMEText(self.Body, 'plain', self.charset))

        self._set_info(msg)
        msg.preamble = self.Subject

        for filename, cid, mimetype, content, charset in self.attachments:
            self._add_attachment(msg, filename, cid, mimetype, content, charset)

        return msg.as_string()

    def _add_attachment(self, outer, filename, cid, mimetype, content, charset):
        """
        If mimetype is None, it will try to guess the mimetype
        """
        if mimetype:
            ctype = mimetype
            encoding = None
        else:
            ctype, encoding = mimetypes.guess_type(filename)

        if ctype is None or encoding is not None:
            # No guess could be made, or the file is encoded (compressed), so
            # use a generic bag-of-bits type.
            ctype = 'application/octet-stream'

        maintype, subtype = ctype.split('/', 1)
        if not content:
            with open(filename, 'rb') as fp:
                content = fp.read()

        if maintype == 'text':
            # Note: we should handle calculating the charset
            msg = MIMEText(content, _subtype=subtype, _charset=charset)
        elif maintype == 'image':
            msg = MIMEImage(content, _subtype=subtype)
        elif maintype == 'audio':
            msg = MIMEAudio(content, _subtype=subtype)
        else:
            msg = MIMEBase(maintype, subtype)
            msg.set_payload(content)
            # Encode the payload using Base64
            encoders.encode_base64(msg)

        # Set the content-ID header
        if cid:
            msg.add_header('Content-ID', '<%s>' % cid)
            msg.add_header('Content-Disposition', 'inline')
        else:
            # Set the filename parameter
            msg.add_header('Content-Disposition', 'attachment', filename=path.basename(filename))

        outer.attach(msg)

    def attach(self, filename, cid=None, mimetype=None, content=None, charset=None):
        """
        Attach a file to the email. Specify the name of the file;
        Message will figure out the MIME type and load the file.

        Specify mimetype to set the MIME type manually. The content
        argument take the contents of the file if they are already loaded
        in memory.
        """

        self.attachments.append((filename, cid, mimetype, content, charset))


class Manager(threading.Thread):
    """
    Manages the sending of email in the background.

    You can supply it with an instance of class Mailer or pass in the same
    parameters that you would have used to create an instance of Mailer.

    If a message was succesfully sent, self.results[msg.message_id] returns a 3
    element tuple (True/False, err_code, err_message).
    """

    def __init__(self, mailer=None, callback=None, **kwargs):
        threading.Thread.__init__(self)

        self.queue = queue.Queue()
        self.mailer = mailer
        self.abort = False
        self.callback = callback
        self._results = {}
        self._result_lock = threading.RLock()

        if self.mailer is None:
            self.mailer = Mailer(
                host=kwargs.get('host', 'localhost'),
                port=kwargs.get('port', 25),
                use_tls=kwargs.get('use_tls', False),
                usr=kwargs.get('usr', None),
                pwd=kwargs.get('pwd', None),
            )

    def __getattr__(self, name):
        if name == 'results':
            with self._result_lock:
                return self._results
        else:
            return None

    def run(self):

        while self.abort is False:
            msg = self.queue.get(block=True)
            if msg is None:
                break

            if isinstance(msg, Message):
                msg = [msg]

            for m in msg:
                try:
                    self.results[m.message_id] = (False, -1, '')
                    self.mailer.send(m)
                    self.results[m.message_id] = (True, 0, '')

                except Exception as e:
                    args = e.args
                    if len(args) < 2:
                        args = (-1, e.args[0])

                    self.results[m.message_id] = (False, args[0], args[1])

                if self.callback:
                    try:
                        self.callback(m.message_id)
                    except Exception:
                        pass

            # endfor

            self.queue.task_done()

    def send(self, msg):
        self.queue.put(msg)
