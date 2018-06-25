# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    try:
        with env.cr.savepoint():
            # Remove noupdate ir.rule
            env.ref('portal_stock.portal_stock_picking_user_rule').unlink()
    except Exception:
        pass
