# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: partner.py 1007 2005-07-25 13:18:09Z kayhman $
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
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

