# -*- coding: utf-8 -*-
# Copyright 2017 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def fill_account_invoice_mixin(cr):
    """
    Fills in account.invoice the fields campaign_id, medium_id and
    source_id from sale.order
    :param cr: cursor variable
    """
    openupgrade.logged_query(
        cr,
        """
        UPDATE account_invoice ai
        SET campaign_id = so.campaign_id,
            medium_id = so.medium_id,
            source_id = so.source_id
        FROM account_invoice_line ail,
            sale_order_line sol,
            sale_order so,
            sale_order_line_invoice_rel rel
        WHERE ai.id = ail.invoice_id
            AND ail.id = rel.invoice_line_id
            AND rel.order_line_id = sol.id
            AND sol.order_id = so.id
        """)


@openupgrade.migrate()
def migrate(env, version):
    fill_account_invoice_mixin(env.cr)
