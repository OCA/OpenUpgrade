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

from osv import fields,osv

class res_partner(osv.osv):
    _inherit = "res.partner"
    _name = "res.partner"
    _columns = {
        'ref': fields.char('Acronym', size=64, select=True),
        'number': fields.char('Number', size=64, readonly=True),
        'partner_ref' : fields.char('Partner Ref.', size=64,  help='The reference of my company for this partner'),
        'to_export': fields.boolean('To export'),
        'to_update': fields.boolean('To update'),       }

    _defaults = {
        'to_export': lambda *a: True,
        'to_update': lambda *a: False,
        }

    def create(self, cr, uid, vals, context= None):
        if not vals.get('number'):
            vals['number']= self.pool.get('ir.sequence').get(cr, uid, 'res.partner')
        return super(res_partner, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, values, context=None):
        if not values:
            values = {}
        if "to_update" not in values:
            values['to_update'] = True
        return super(res_partner,self).write(cr, uid, ids, values, context)

res_partner()



class res_partner_address(osv.osv):
    _inherit = 'res.partner.address'
    _columns = {
        'comment': fields.text('Notes'),

    }
res_partner_address()


class res_partner_category(osv.osv):
    _inherit = 'res.partner.category'
    _columns={
        'export_enabled': fields.boolean('Export this category to financial software'),
        }
    _defaults={
        'export_enabled': lambda *a : False,
        }

res_partner_category()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

