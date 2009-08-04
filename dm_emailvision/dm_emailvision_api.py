# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields
from osv import osv
import pooler

from lxml import etree
import httplib
import base64
import time

from dm.report_design import merge_message

#from dm_email.dm_email_document import set_image_email - not of use
#from email.MIMEMultipart import MIMEMultipart
#from email.MIMEText import MIMEText
#from email.MIMEImage import MIMEImage

class dm_mail_service(osv.osv):
     _inherit = "dm.mail_service"
     _columns = {
          'ev_host' : fields.char('Emailvision Host', size=64),
          'ev_service' : fields.char('Emailvision Service', size=64),
          'ev_encrypt' : fields.char('Emailvision Encrypt Key', size=64),
          'ev_random' : fields.char('Emailvision Random Key',size=64),
     }
     _defaults = {
        'ev_host': lambda *a : 'api.notificationmessaging.com',
        'ev_service': lambda *a : 'NMSXML',
    }
dm_mail_service()

#Dont need any more (not sure)
#def set_image_email(node,msg):
#    if not node.getchildren():
#        if  node.tag=='img' and node.get('src') and node.get('src').find('data:image/gif;base64,')>=0:
#            msgImage = MIMEImage(base64.decodestring(node.get('src').replace('data:image/gif;base64,','')))
#            image_name = ''.join( Random().sample(string.letters+string.digits, 12) )
#            msgImage.add_header('Content-ID','<%s>'%image_name)
#            msg.attach(msgImage)
#            node.set('src',"cid:%s"%image_name)
#        else :
#            for n in node.getchildren():
#                set_image_email(n,msg)

#def _email_body(body):
#    msgRoot = MIMEMultipart('related')
#    msgRoot.preamble = 'This is a multi-part message in MIME format.'
#
#    msg = MIMEMultipart('alternative')
#    msgRoot.attach(msg)
#
#    set_image_email(body,msgRoot)
#    msgText = MIMEText(etree.tostring(body), 'html')
#    msg.attach(msgText)
#    return  msgRoot.as_string()

def send_email(cr,uid,obj,context):

    """ Get Emailmvision connection infos """
    ev_host = obj.mail_service_id.ev_host
    ev_service = obj.mail_service_id.ev_service
    ev_encrypt = obj.mail_service_id.ev_encrypt
    ev_random = obj.mail_service_id.ev_random

    email_dest = obj.address_id.email or ''
    email_reply = obj.segment_id.campaign_id.trademark_id.email or ''

    context['document_id'] = obj.document_id.id
    context['address_id'] = obj.address_id.id

    email_subject = merge_message(cr, uid, obj.document_id.subject or '',context)
    name_from = obj.segment_id.campaign_id.trademark_id.name or ''
    name_reply = obj.segment_id.campaign_id.trademark_id.name or ''

    pool = pooler.get_pool(cr.dbname)
    ir_att_obj = pool.get('ir.attachment')
    ir_att_ids = ir_att_obj.search(cr,uid,[('res_model','=','dm.campaign.document'),('res_id','=',obj.id),('file_type','=','html')])

    for attach in ir_att_obj.browse(cr,uid,ir_att_ids):
        message = base64.decodestring(attach.datas)
        root = etree.HTML(message)
        body = root.find('body')

        print "message :", message
        # I think html_content = message should wrk
        html_content = ''.join([ etree.tostring(x) for x in body.getchildren()])
        print "body :", html_content
#        html_content = _email_body(body)
        text_content = "This is a test"
        print "Test"

        "Composing XML"
        msg = etree.Element("MultiSendRequest")
        sendrequest = etree.SubElement(msg, "sendrequest")
        dyn = etree.SubElement(sendrequest, "dyn")

        dynentry1 = etree.SubElement(dyn, "entry")
        dynkey1 = etree.SubElement(dynentry1, "key")
        dynkey1.text = "EMAIL_DEST"
        dynvalue1 = etree.SubElement(dynentry1, "value")
        dynvalue1.text = email_dest

        dynentry2 = etree.SubElement(dyn, "entry")
        dynkey2 = etree.SubElement(dynentry2, "key")
        dynkey2.text = "SUBJECT"
        dynvalue2 = etree.SubElement(dynentry2, "value")
        dynvalue2.text = email_subject

        dynentry3 = etree.SubElement(dyn, "entry")
        dynkey3 = etree.SubElement(dynentry3, "key")
        dynkey3.text = "EMAIL_REPLY"
        dynvalue3 = etree.SubElement(dynentry3, "value")
        dynvalue3.text = email_reply

        dynentry4 = etree.SubElement(dyn, "entry")
        dynkey4 = etree.SubElement(dynentry4, "key")
        dynkey4.text = "NAME_FROM"
        dynvalue4 = etree.SubElement(dynentry4, "value")
        dynvalue4.text = name_from

        dynentry5 = etree.SubElement(dyn, "entry")
        dynkey5 = etree.SubElement(dynentry5, "key")
        dynkey5.text = "NAME_REPLY"
        dynvalue5 = etree.SubElement(dynentry5, "value")
        dynvalue5.text = name_reply


        content = etree.SubElement(sendrequest, "content")
        entry1 = etree.SubElement(content, "entry")
        key1 = etree.SubElement(entry1, "key")
        key1.text = "1"
        value1 = etree.SubElement(entry1, "value")
        value1.text = etree.CDATA(html_content)
        entry2 = etree.SubElement(content, "entry")
        key2 = etree.SubElement(entry2, "key")
        key2.text = "2"
        value2 = etree.SubElement(entry2, "value")
        value2.text = text_content

        email = etree.SubElement(sendrequest, "email")
        email.text = email_dest
        encrypt = etree.SubElement(sendrequest, "encrypt")
        encrypt.text = ev_encrypt
        random = etree.SubElement(sendrequest, "random")
        random.text = ev_random
        senddate = etree.SubElement(sendrequest, "senddate")
        senddate.text = time.strftime('%Y-%m-%dT%H:%M:%S')
        synchrotype = etree.SubElement(sendrequest, "synchrotype")
        synchrotype.text = "NOTHING"

        print("<?xml version=\"1.0\" encoding=\"UTF-8\"?>" + "\n" + etree.tostring(msg, method="xml", encoding='utf-8', pretty_print=True))

        xml_msg = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" + etree.tostring(msg, encoding="utf-8")

        "Sending to Emailvision NMSXML API"
        ev_api = httplib.HTTP( ev_host +":80")
        ev_api.putrequest("POST", "/" + ev_service)
        ev_api.putheader("Content-type", "text/xml; charset=\"UTF-8\"")
        ev_api.putheader("Content-length", str(len(xml_msg)))
        ev_api.endheaders()
        ev_api.send(xml_msg)
    
        "Get Emailvision Reply"
        statuscode, statusmessage, header = ev_api.getreply()
        res = ev_api.getfile().read()
    
        if statuscode != 200:
            print "E"*50
            error_msg = "This document cannot be sent to Emailvision NMS API\nStatus Code : " + str(statuscode) + "\nStatus Message : " + statusmessage + "\nHeader : " + str(header) + "\nResult : " + res
            pool.get('dm.campaign.document').write(cr, uid, [obj.id], {'state':'error','error_msg':error_msg})
            return False

    return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
