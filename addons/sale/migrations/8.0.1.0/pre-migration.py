# -*- coding: utf-8 -*-
##############################################################################
#
# Odoo, an open source suite of business apps
# This module copyright (C) 2014 Therp BV (<http://therp.nl>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.openupgrade import openupgrade

xmlid_renames = [
    ('sale_stock.act_cancel3', 'sale.act_cancel3'),
    ('sale_stock.act_ship', 'sale.act_ship'),
    ('sale_stock.act_ship_cancel', 'sale.act_ship_cancel'),
    ('sale_stock.act_ship_end', 'sale.act_ship_end'),
    ('sale_stock.act_ship_except', 'sale.act_ship_except'),
    ('sale_stock.act_wait_ship', 'sale.act_wait_ship'),
    ('sale_stock.trans_router_wait_invoice_shipping',
     'sale.trans_router_wait_invoice_shipping'),
    ('sale_stock.trans_router_wait_ship', 'sale.trans_router_wait_ship'),
    ('sale_stock.trans_ship_end_done', 'sale.trans_ship_end_done'),
    ('sale_stock.trans_ship_except_ship', 'sale.trans_ship_except_ship'),
    ('sale_stock.trans_ship_except_ship_cancel',
     'sale.trans_ship_except_ship_cancel'),
    ('sale_stock.trans_ship_except_ship_end',
     'sale.trans_ship_except_ship_end'),
    ('sale_stock.trans_ship_ship_end', 'sale.trans_ship_ship_end'),
    ('sale_stock.trans_ship_ship_except', 'sale.trans_ship_ship_except'),
    ('sale_stock.trans_wait_invoice_invoice',
     'sale.trans_wait_invoice_invoice '),
    ('sale_stock.trans_wait_ship_cancel3', 'sale.trans_wait_ship_cancel3'),
    ('sale_stock.trans_wait_ship_ship', 'sale_stock.trans_wait_ship_ship'),
    ]


def preserve_date_order(cr):
    """ Copy date_order column for access to the original data after migration
    from date to datetime type."""
    cr.execute(
        """
        ALTER TABLE sale_order
        ADD COLUMN {date_order} date;
        UPDATE sale_order SET {date_order}=date_order;
        """.format(
            date_order=openupgrade.get_legacy_name('date_order')))


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_xmlids(cr, xmlid_renames)
    preserve_date_order(cr)
