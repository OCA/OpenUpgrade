# Copyright 2018 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    try:
        with env.cr.savepoint():
            env.ref('event_sale.event_type').unlink()
    except Exception:
        pass
