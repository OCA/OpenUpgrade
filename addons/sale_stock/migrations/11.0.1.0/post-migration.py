# -*- coding: utf-8 -*-
# © 2017 bloopark systems (<http://bloopark.de>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def update_procurement_field_from_sale(cr):
    """
    Connecting new sale_id field of procurement_group
    with respective sale orders
    (considering procurement_group_id of sale order)
    """
    query = ("UPDATE procurement_group AS pg "
             "SET sale_id = so.id "
             "FROM sale_order as so "
             "WHERE so.procurement_group_id = pg.id")
    openupgrade.logged_query(
        cr, query, ()
    )


def update_stock_move_field_from_procurement_order(cr):
    """
    Filling the values of new sale_order_id field of stock_move
    with respective values of old procurement_order
    """
    query = ("UPDATE stock_move AS sm "
             "SET sale_line_id = po.sale_line_id "
             "FROM procurement_order AS po "
             "WHERE sm.procurement_id = po.id")
    openupgrade.logged_query(
        cr, query, ()
    )


@openupgrade.migrate()
def migrate(env, version):
    update_procurement_field_from_sale(env.cr)
    update_stock_move_field_from_procurement_order(env.cr)
