# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(env.cr, "ALTER TABLE calendar_event ADD google_id VARCHAR")
    openupgrade.logged_query(
        env.cr, "ALTER TABLE calendar_recurrence ADD google_id VARCHAR"
    )
