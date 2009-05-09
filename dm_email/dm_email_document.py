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

from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage

from dm.report_design import merge_message
import re
_regex = re.compile('\[\[setHtmlImage\((.+?)\)\]\]')

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
                'service_type' : fields.char('Type Code',size=64),
    }

    def on_change_service_type(self, cr, uid, ids, type_id):
        res = {'value':{}}
        if type_id:
            service_type = self.pool.get('dm.mail_service.type').read(cr, uid, [type_id])[0]
            res['value'] = {'service_type':service_type['code']}
        print res
        return res


dm_mail_service()

def set_image_email(node,msg):
    if not node.getchildren():
        if  node.tag=='img' and node.get('src') and node.get('src').find('data:image/gif;base64,')>=0:
            id = _regex.split(node.get('name'))[1]
            msgImage = MIMEImage(base64.decodestring(node.get('src').replace('data:image/gif;base64,','')))
            image_name = "image%s"%id
            msgImage.add_header('Content-ID','<%s>'%image_name)
            msg.attach(msgImage)
            node.set('src',"cid:%s"%image_name)
    else :
        for n in node.getchildren():
            set_image_email(n,msg)

def create_email_queue(cr,uid,obj,context):
    pool = pooler.get_pool(cr.dbname)
    ir_att_obj = pool.get('ir.attachment')
    email_queue_obj = pool.get('email.smtpclient.queue')
    ir_att_ids = ir_att_obj.search(cr,uid,[('res_model','=','dm.campaign.document'),('res_id','=',obj.id),('file_type','=','html')])
    for attach in ir_att_obj.browse(cr,uid,ir_att_ids):
        message = base64.decodestring(attach.datas)
        root = etree.HTML(message)
        body = root.find('body')

        msgRoot = MIMEMultipart('related')

        subject =  merge_message(cr, uid, str(obj.document_id.subject), context)
        msgRoot['Subject'] = subject

        msgRoot['From'] = str(obj.mail_service_id.smtp_server_id.email)
        msgRoot['To'] = str(obj.address_id.email)
        msgRoot.preamble = 'This is a multi-part message in MIME format.'

        msg = MIMEMultipart('alternative')
        msgRoot.attach(msg)

        set_image_email(body,msgRoot)

        msgText = MIMEText(etree.tostring(body), 'html')
        msg.attach(msgText)

        if message :
            vals = {
                'to':str(obj.address_id.email),
                'server_id':obj.mail_service_id.smtp_server_id.id,
                'cc':False,
                'bcc':False,
                'name':subject,
                'body' : msgRoot.as_string(),
                'serialized_message': msgRoot.as_string(),
                'date_create':time.strftime('%Y-%m-%d %H:%M:%S')
                }
            email_queue_obj.create(cr,uid,vals)
    return True
