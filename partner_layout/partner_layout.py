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


class res_partner(osv.osv):
    _name = "res.partner"
    _inherit="res.partner"
    _columns = {
        'header' : fields.binary('Header (.odt)'),
        'logo' : fields.binary('Logo'),
        'signature' : fields.binary('Signature')
    }
    
    def _default_company(self, cr, uid, context={}):
        if 'category_id' in context and context['category_id']:
            id_cat = self.pool.get('res.partner.category').search(cr,uid,[('name','ilike',context['category_id'])])[0]
            return [id_cat]
        return []
   
    _defaults = {
        'category_id': _default_company,
    }
res_partner()
