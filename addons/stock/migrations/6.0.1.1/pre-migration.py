# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This migration script copyright (C) 2012 Therp BV (<http://therp.nl>)
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

from openupgrade import openupgrade

renamed_columns = {
    'stock_move': [
        ('date_planned', 'date_expected'),
        ],
    'stock_location': [
        ('account_id', 'openupgrade_legacy_account_id'),
        ],
    }

renamed_xmlids = [
    ('stock.seq_type_picking', 'stock.seq_type_picking_in'),
    ('stock.seq_picking', 'stock.seq_picking_in'),
    ]

@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_columns(cr, renamed_columns)
    openupgrade.rename_xmlids(cr, renamed_xmlids)

