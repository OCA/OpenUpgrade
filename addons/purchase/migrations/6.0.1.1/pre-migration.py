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

logger = logging.getLogger('OpenUpgrade: purchase')

column_renames = {
    # this is a mapping per table from old column name
    # to new column name
    'purchase_order': [
        ('invoice_id', 'openupgrade_legacy_invoice_id')
        ],
    }

renamed_xmlids = [
    ('mrp.act_buy', 'purchase.act_buy'),
    ('mrp.trans_buy_make_done', 'purchase.trans_buy_make_done'),
    ('mrp.trans_buy_cancel', 'purchase.trans_buy_cancel'),
]   

@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_columns(cr, column_renames)
    openupgrade.rename_xmlids(cr, renamed_xmlids)
    logger.warn(
        'TODO: check whether datetime field preserves '
        'content when migrated to date field '
        '(purchase_order.minimum_planned_date and po_line.date_planned)')
