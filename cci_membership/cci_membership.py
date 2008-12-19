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

from osv import fields, osv

class res_partner(osv.osv):
    _inherit = 'res.partner'
    _description = 'Partner'

    def _membership_vcs(self, cr, uid, ids, field_name=None, arg=None, context={}):
        '''To obtain the ID of the partner in the form of a belgian VCS for a membership offer'''
        res = {}
        for id in ids:
            value_digits = 1000000000 + id
            check_digits = value_digits % 97
            if check_digits == 0:
                check_digits = 97
            pure_string = str(value_digits) + ( str(check_digits).zfill(2) )
            res[id] = '***' + pure_string[0:3] + '/' + pure_string[3:7] + '/' + pure_string[7:] + '***'
        return res

    _columns = {
        'membership_vcs': fields.function( _membership_vcs, method=True,string='VCS number for membership offer', type='char', size=20),
        'refuse_membership': fields.boolean('Refuse to Become a Member'),
    }

    _default = {
        'refuse_membership': lambda *a: 0,
    }

res_partner()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

