#!/usr/bin/env python
#coding: utf-8
#
# HTML mail module for OpenERP
#
# (c) 2007-2008 Sednacom <http://www.sednacom.fr>
#
# authors :
#  - Brice V. < brice@sednacom.fr >

import smtplib
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.Header import Header
from email.Utils import formatdate, COMMASPACE
from email import Encoders
import mimetypes
import os
from tools import config
import urllib
import urllib2
import base64

_ZARAFA_MAIL_URL = 'http://%(zarafa_server)s/webaccess/sednamail.php'

def zarafa_email_html_send_attach(obj, cr, uid, email_from, email_to, subject, body,
                        email_cc=None, email_bcc=None, on_error=False,
                        reply_to=False, attach=None, tinycrm=False):

    o_ru = obj.pool.get('res.users')
    zud = o_ru.read(cr, uid, [uid,], ['zarafa_server', 'zarafa_user', 'zarafa_password'])[0]

    zto = '|'.join(email_to)
    data = {
        'user': zud['zarafa_user'] ,
        'password': zud['zarafa_password'] ,
        'subject' : subject ,
        'body' : body ,
        'recipients' : zto ,
        'from_email' : email_from,
    }
    if attach :
        zattach = '|'.join([ '%s|%s' % (n, base64.b64encode(c)) for n,c in attach ])
        data['attachments'] = zattach

    postvars = urllib.urlencode(data)
    zurl = _ZARAFA_MAIL_URL % zud

    ures = urllib2.urlopen(zurl, postvars)

    return True

def email_html_send_attach(email_from, email_to, subject, body, email_cc=None, email_bcc=None, on_error=False, reply_to=False, attach=None, tinycrm=False):
    if not email_cc:
        email_cc=[]
    if not email_bcc:
        email_bcc=[]
    if not attach:
        attach=[]

    msg = MIMEMultipart('related')

    msg['Subject'] = Header(subject.decode('utf8'), 'utf-8')
    msg['From'] = email_from
    del msg['Reply-To']
    if reply_to:
        msg['Reply-To'] = reply_to
    msg['To'] = COMMASPACE.join(email_to)
    if email_cc:
        msg['Cc'] = COMMASPACE.join(email_cc)
    if email_bcc:
        msg['Bcc'] = COMMASPACE.join(email_bcc)
    if tinycrm:
        msg['Message-Id'] = '<'+str(time.time())+'-tinycrm-'+str(tinycrm)+'@'+socket.gethostname()+'>'
    msg['Date'] = formatdate(localtime=True)

    msg_alt = MIMEMultipart('alternative')

    msg_alt.attach(MIMEText("Vous devez activez l'affichage en mode HTML pour lire ce message."))

    body_part = MIMEText(body , _subtype='html')
    body_part.set_charset('UTF-8')

    msg_alt.attach(body_part)

    msg.attach(msg_alt)

    for (fname,fcontent) in attach:
        part = MIMEBase('application', "octet-stream")
        part.set_payload( fcontent )
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % (fname,))
        msg.attach(part)
    try:
        s = smtplib.SMTP()
        s.connect(config['smtp_server'])
        if config['smtp_user'] or config['smtp_password']:
            s.login(config['smtp_user'], config['smtp_password'])
        s.sendmail(email_from, email_to + email_cc + email_bcc, msg.as_string())
        s.quit()
    except Exception, e:
        import logging
        logging.getLogger().info(str(e))
    return True
