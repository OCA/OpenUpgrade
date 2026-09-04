# Copyright 2026 Tecnativa - Cristina Hidalgo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.cow_templates_replicate_upstream(env.cr)
