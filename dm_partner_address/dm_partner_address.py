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

import netsvc
from osv import fields
from osv import osv

class res_partner_address(osv.osv):
    _inherit = 'res.partner.address'
    _columns = {
        'id': fields.integer('ID', readonly=True),
        'firstname' : fields.char('First Name',size=64),
        'name_complement' : fields.char('Name Complement',size=64),
        'street3' : fields.char('Street3',size=32),
        'street4' : fields.char('Street4',size=32),
        'moved' : fields.boolean('Moved'),
        'quotation' : fields.float('Quotation',digits=(16,2)),
        'origin_partner':fields.char('Origin Partner',size=64),
        'origin_support':fields.char('Origin Support',size=64),
        'origin_keyword':fields.char('Origin Keyword',size=64), 
        'origin_campaign_id':fields.many2one('dm.campaign','Origin Campaign'),
        'origin_country_id':fields.many2one('res.country','Origin Country')  
    }
res_partner_address()

#vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
