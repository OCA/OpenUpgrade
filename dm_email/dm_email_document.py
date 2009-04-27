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
    }
dm_mail_service()