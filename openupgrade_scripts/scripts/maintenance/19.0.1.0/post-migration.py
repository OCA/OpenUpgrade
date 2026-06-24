# Copyright 2026 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "maintenance", "19.0.1.0/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "maintenance",
        ["mail_act_maintenance_request"],
        ["summary"],
    )
    model_id = env["ir.model"]._get_id("maintenance.equipment.category")
    env["mail.alias"].search([("alias_parent_model_id", "=", model_id)]).unlink()
