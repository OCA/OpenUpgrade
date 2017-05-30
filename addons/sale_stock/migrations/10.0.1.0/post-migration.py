# -*- coding: utf-8 -*-
# © 2017 bloopark systems (<http://bloopark.de>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def update_to_refund_so(cr):
    openupgrade.logged_query(
        cr, """UPDATE stock_move SET to_refund_so=True
               WHERE origin_returned_move_id IS NOT NULL"""
    )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    update_to_refund_so(cr)
