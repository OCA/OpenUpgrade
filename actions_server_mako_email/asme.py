# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id: portal_security.py 654 2009-06-24 11:40:46Z chs $
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

from osv import osv
from mako.template import Template as MakoTemplate
import time

def actions_server(osv.osv):
    _inherit = 'ir.actions.server'

    def merge_message(self, cr, uid, keystr, action, context):
        obj_pool = self.pool.get(action.model_id.model)
        id = context.get('active_id')
        obj = obj_pool.browse(cr, uid, id)
        
        message = MakoTemplate(keystr).render_unicode(object=obj, context=context, time=time)
        if message == keystr:
            message = super(action_server, self).merge_message(cr, uid, keystr, action, context)
        return message

actions_server()
        
