# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2008-2009 Syleam Info Services (<http://www.syleam.fr>). All Rights Reserved
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


from osv import fields, osv

class project(osv.osv):
    _inherit = "project.project"

    _columns = {
        'contact_id2': fields.many2one('res.partner.contact', 'Contact'),
    }

    def onchange_partner_id(self, cr, uid, ids, part):
        if not part:
            return {'value':{'contact_id': False, 'contact_id2': False, 'pricelist_id': False}}

        pricelist = self.pool.get('res.partner').browse(cr, uid, part).property_product_pricelist.id
        return {'value':{'contact_id': False, 'contact_id2': False, 'pricelist_id': pricelist}}

project()
