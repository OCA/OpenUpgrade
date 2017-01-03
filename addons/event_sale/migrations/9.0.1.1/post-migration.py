# -*- coding: utf-8 -*-
# © 2016 Tecnativa - Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def update_sale_order(cr):
    cr.execute("""
        UPDATE event_registration er
        SET sale_order_id = so.id
        FROM sale_order so, sale_order_line sol
        WHERE er.partner_id = so.partner_id
        AND so.id = sol.order_id
        AND sol.event_id = er.event_id
    """)


def update_sale_order_line(cr):
    cr.execute("""
        UPDATE event_registration er
        SET sale_order_line_id = sol.id
        FROM sale_order so, sale_order_line sol
        WHERE er.partner_id = so.partner_id
        AND so.id = sol.order_id
        AND sol.event_id = er.event_id
    """)


@openupgrade.migrate()
def migrate(cr, version):
    update_sale_order(cr)
    update_sale_order_line(cr)
