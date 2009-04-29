# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution····
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
import time 
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class dm_offer_document(osv.osv):
    _inherit = "dm.offer.document"
    _columns = {
                'subject' : fields.char('Subject',size=64,),
                'editor' : fields.selection([('internal','Internal'),('oord','DM Open Office Report Design')],'Editor'),
                'content' : fields.text('Content'),
                'media_id':fields.related('step_id','media_id','name',type='char', relation='dm.media', string='Media'),
            }

dm_offer_document()

class dm_mail_service(osv.osv):
    _inherit = "dm.mail_service"
    _columns = {
                'smtp_server_id' : fields.many2one('email.smtpclient', 'SMTP Server', ondelete="cascade"),
                'service_type' : fields.related('type_id','code',type='char',relation='dm.mail_service.type',string="Service Type"),
    }


dm_mail_service()

def create_email_queue(cr,uid,obj,context):
    pool = pooler.get_pool(cr.dbname)
    ir_att_obj = pool.get('ir.attachment')
    email_queue_obj = pool.get('email.smtpclient.queue')
    ir_att_ids = ir_att_obj.search(cr,uid,[('res_model','=','dm.campaign.document'),('res_id','=',obj.id),('file_type','=','html')])
    for attach in ir_att_obj.browse(cr,uid,ir_att_ids):
        message = base64.decodestring(attach.datas)
        root = etree.HTML(message)
        body = root.findall('body')[0]
        msg = MIMEMultipart('alternative')
        msg['Subject'] = str(obj.document_id.subject)
        msg['From'] = str(obj.mail_service_id.smtp_server_id.email)
        msg['To'] = str(obj.address_id.email)
        part2 = MIMEText(message, 'html')
        msg.attach(part2)
        if body is not None:
            vals = {
                'to':str(obj.address_id.email),
                'server_id':obj.mail_service_id.smtp_server_id.id,
                'cc':False,
                'bcc':False,
                'name':str(obj.document_id.subject),
                'body' : msg.as_string(),
                'serialized_message': msg.as_string(),
                'date_create':time.strftime('%Y-%m-%d %H:%M:%S')
                }
            email_queue_obj.create(cr,uid,vals)
    return True
