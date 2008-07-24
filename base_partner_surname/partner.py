# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#                    Fabien Pinckaers <fp@tiny.Be>
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
from mx import DateTime
import tools
import ir
import pooler
import time

class res_partner_address(osv.osv):
    _name = 'res.partner.address'
    _inherit ='res.partner.address'
    _columns = {
        'first_name' : fields.char('First Name', size=128),
        'last_name' : fields.char('Last Name', size=128),
        'name' : fields.char('Name', size=128,readonly=True),
    }
    def write(self, cr, uid, ids, vals, context={}):
        first_name=''
        last_name=''
        if 'first_name' in vals and vals['first_name']:
            first_name=vals['first_name']
        if 'last_name' in vals and vals['last_name']:
            last_name=vals['last_name']

        vals['name']= first_name + ' ' + last_name
        return super(res_partner_address, self).write(cr, uid, ids, vals, context)

    def create(self, cr, uid, vals, context={}):
        first_name=''
        last_name=''
        if 'first_name' in vals and vals['first_name']:
            first_name=vals['first_name']
        if 'last_name' in vals and vals['last_name']:
            last_name=vals['last_name']

        vals['name']= first_name + ' ' + last_name
        return super(res_partner_address, self).create(cr, uid, vals, context)

    def onchange_name(self, cr, uid, id, first_name,last_name,context={}):
        if not first_name:
            first_name=''
        if not last_name:
            last_name=''
        return {'value': {'name': first_name + ' ' + last_name}}

res_partner_address()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

