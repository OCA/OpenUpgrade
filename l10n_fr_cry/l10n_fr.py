# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008 JAILLET Simon - CrysaLEAD - www.crysalead.fr
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

from osv import fields, osv

class account_tax_code(osv.osv):
    _name = 'account.tax.code'
    _inherit = 'account.tax.code'
    _columns = {
        'code': fields.char('Case Code', size=256),
    }
account_tax_code()


class l10n_fr_report(osv.osv):
    _name = 'l10n.fr.report'
    _columns = {
        'code': fields.char('Code', size=64),
        'name': fields.char('Name', size=128),
        'line_ids': fields.one2many('l10n.fr.line', 'report_id', 'Lines'),
    }
    _sql_constraints = [
                ('code_uniq', 'unique (code)','The code report must be unique !')
        ]
l10n_fr_report()

class l10n_fr_line(osv.osv):
    _name = 'l10n.fr.line'
    _columns = {
        'code': fields.char('Variable Name', size=64),
        'definition': fields.char('Definition', size=512),
        'name': fields.char('Name', size=256),
        'report_id': fields.many2one('l10n.fr.report', 'Report'),
    }
    _sql_constraints = [
        ('code_uniq', 'unique (code)','The variable name must be unique !')
    ]
l10n_fr_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

