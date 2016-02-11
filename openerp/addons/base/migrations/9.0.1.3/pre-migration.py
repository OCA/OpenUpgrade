# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenUpgrade module for Odoo
#    @copyright 2015-Today: Odoo Community Association
#    @author: Stephane LE CORNEC
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

from openupgradelib import openupgrade


column_copies = {
    'ir_act_url': [
        ('help', None, None),
    ],
    # 'ir_act_window': [
    #     ('help', None, None),
    # ],
    'ir_actions': [
        ('help', None, None),
    ],
    # 'ir_act_client': [
    #     ('help', None, None),
    # ],
    'ir_act_report_xml': [
        ('help', None, None),
    ],
    'ir_act_server': [
        ('help', None, None),
    ],
    'ir_ui_view': [
        ('arch', 'arch_db', None),
    ],
}

column_renames = {
    'res_partner_bank': [
        ('bank', 'bank_id'),
    ],
}


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.copy_columns(cr, column_copies)
    openupgrade.rename_columns(cr, column_renames)
