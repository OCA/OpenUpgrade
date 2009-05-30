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


def send_email(cr,uid,obj,context):

    """ Get Emailmvision connection infos """
    ev_host = obj.mail_service_id.ev_host
    ev_service = obj.mail_service_id.ev_service
    ev_encrypt = obj.mail_service_id.ev_encrypt
    ev_random = obj.mail_service_id.ev_random

    email_dest = obj.address_id.email

    pool = pooler.get_pool(cr.dbname)
    ir_att_obj = pool.get('ir.attachment')
    ir_att_ids = ir_att_obj.search(cr,uid,[('res_model','=','dm.campaign.document'),('res_id','=',obj.id),('file_type','=','html')])
    for attach in ir_att_obj.browse(cr,uid,ir_att_ids):
        message = base64.decodestring(attach.datas)
        print "message :", message

        html_content = etree.HTML(message)
        text_content = "This is a test"

        "Composing XML"
        msg = etree.Element("MultiSendRequest")
        sendrequest = etree.SubElement(msg, "sendrequest")

        content = etree.SubElement(sendrequest, "content")
        entry1 = etree.SubElement(content, "entry")
        key1 = etree.SubElement(entry1, "key")
        key1.text = "1"
        value1 = etree.SubElement(entry1, "value")
        value1.text = etree.CDATA(etree.tostring(html_content))
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
        senddate.text = "2008-05-06T00:00:00.000+01:00"
        synchrotype = etree.SubElement(sendrequest, "synchrotype")
        synchrotype.text = "OTHING"

        print("<?xml version=\"1.0\" encoding=\"UTF-8\"?>" + "\n" + etree.tostring(msg, method="xml", encoding='utf-8', pretty_print=True))

        xml_msg = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" + etree.tostring(msg, encoding="utf-8")


        "Sending to Emailvision NMSXML API"
        ev_api = httplib.HTTP(ev_host +":80")
        ev_api.putrequest("POST", "/" + ev_service)
        ev_api.putheader("Content-type", "text/xml; charset=\"UTF-8\"")
        ev_api.putheader("Content-length", str(len(xml_msg)))
        ev_api.endheaders()
        ev_api.send(xml_msg)

        "Get Emailvision Reply"
        statuscode, statusmessage, header = ev_api.getreply()
        res = ev_api.getfile().read()

        if statuscode != 200:
            error_msg = "This document cannot be sent to Emailvision NMS API\nStatus Code : " + str(statuscode) + "\nStatus Message : " + statusmessage + "\nHeader : " + str(header) + "\nResult : " + res
            pool.get('dm.campaign.document').write(cr, uid, [obj.id], {'state':'error','error_msg':error_msg})
            return False

    return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
