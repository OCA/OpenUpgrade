# -*- coding: utf-8 -*-
# © 2016 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def set_last_sale_on_partner(cr):
    openupgrade.logged_query(cr, """
            UPDATE res_partner rp
            SET last_website_so_id = so.id
            FROM sale_order so
            WHERE so.id = (
               SELECT max(id) FROM sale_order
               WHERE partner_id = rp.id
            )
            AND rp.last_website_so_id IS NULL;
            """)


@openupgrade.migrate()
def migrate(cr, version):
    set_last_sale_on_partner(cr)
