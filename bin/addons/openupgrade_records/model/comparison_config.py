# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module Copyright (C) 2012 OpenUpgrade community
#    https://launchpad.net/~openupgrade-committers
#
#    Contributors:
#    Therp BV <http://therp.nl>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields
import openerplib
from tools.translate import _

class openupgrade_comparison_config(osv.osv):
    _name = 'openupgrade.comparison.config'
    _columns = {
        'name': fields.char('Name', size=64),
        'server': fields.char('Server', size=64, required=True),
        'port': fields.integer('Port', required=True),
        'protocol': fields.selection(
            [('http://', 'XML-RPC')],
            # ('https://', 'XML-RPC Secure')], not supported by libopenerp
            'Protocol', required=True),
        'database': fields.char('Database', size=64, required=True),
        'username': fields.char('Username', size=24, required=True),
        'password': fields.char('Password', size=24, required=True, password=True),
        'last_log': fields.text('Last log'),
        }
    _defaults = {
        'port': lambda *a: 8069,
        'protocol': lambda *a: 'http://',
        }

    def get_connection(self, cr, uid, ids, context=None):
        if not ids:
            raise osv.except_osv(
                _("Cannot connect"), _("Invalid id passed."))
        conf = self.read(cr, uid, ids[0], context=None)
        return openerplib.get_connection(
           hostname=conf['server'],
           database=conf['database'],
           login=conf['username'],
           password=conf['password'],
           port=conf['port'],
           )

    def test_connection(self, cr, uid, ids, context=None):
        try:
            connection = self.get_connection(cr, uid, [ids[0]], context)
            user_model = connection.get_model("res.users")
            ids = user_model.search([("login", "=", "admin")])
            user_info = user_model.read(ids[0], ["name"])
        except Exception, e:
            raise osv.except_osv(
                _("Connection failed."), unicode(e))
        raise osv.except_osv(
            _("Connection succesful."),
            _("%s is connected.") % user_info["name"]
            )
    
    def analyze(self, cr, uid, ids, context=None):
        """
        Run the analysis wizard
        """
        wizard_obj = self.pool.get('openupgrade.analysis.wizard')
        wizard_id = wizard_obj.create(
            cr, uid, {'server_config': ids[0]}, context)
        result = {
            'name': wizard_obj._description,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'openupgrade.analysis.wizard',
            'domain': [],
            'context': context,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': wizard_id,
            'nodestroy': True,
            }
        return result

openupgrade_comparison_config()
