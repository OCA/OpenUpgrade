# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Therp BV
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

import logging
from openerp.openupgrade import openupgrade

logger = logging.getLogger('OpenUpgrade.purchase')


column_renames = {
    'procurement_order': [('purchase_id', None)],
    'purchase_order_line': [('move_dest_id', None)],
    }


def create_field_reception_to_invoice(cr):
    cr.execute("""
        ALTER TABLE "stock_picking"
        ADD COLUMN "reception_to_invoice" bool DEFAULT False""")
    logger.info(
        "Fast creation of the field stock_picking.reception_to_invoice")


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_columns(cr, column_renames)
    create_field_reception_to_invoice(cr)
