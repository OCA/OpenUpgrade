# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade, openupgrade_200


@openupgrade.migrate()
def migrate(env, version):
    openupgrade_200.migrate_qweb_fields(env, "mail.template", "body_html")
