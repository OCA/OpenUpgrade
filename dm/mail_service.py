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
import time

from osv import fields
from osv import osv
import pooler

class dm_mail_service(osv.osv):
    _name = "dm.mail.service"
    def _default_name(self, cr, uid, ids, name, args, context={}):
        res={}
        for rec in self.browse(cr, uid, ids):
             res[rec.id] = (rec.partner_id and rec.partner_id.name or '') + ' for ' + (rec.media_id and rec.media_id.name or '')
        return res 
    
    _columns = {
        'name' : fields.function(_default_name, method=True, string='Name',store=True ,type='char' ,size=128),
        'partner_id' : fields.many2one('res.partner','Partner',domain=[('category_id','=','Mail Service')]),
        'media_id' : fields.many2one('dm.media','Media'),
        'action_id' : fields.many2one('ir.actions.server','Action')
    }


dm_mail_service()