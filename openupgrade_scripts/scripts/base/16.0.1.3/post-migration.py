# Copyright 2023 Hunki Enterprises BV (https://hunki-enterprises.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade, openupgrade_160

from odoo.tools import column_exists


def update_ir_actions_translations(env):
    """Merge the translations of the name and help of ir.actions.* models.

    Those columns are inherited from ir.actions.actions: once translated
    (jsonb), the ORM converts them keeping only the en_US value. The
    pre-migration excludes them, so merge the ir_translation records here,
    while that table is still available (end-migration scripts run after the
    migration tests).
    """
    fields_spec = [
        (model_name, field_name)
        for model_name in (
            "ir.actions.act_window",
            "ir.actions.act_url",
            "ir.actions.server",
            "ir.actions.client",
            "ir.actions.report",
        )
        for field_name in ("name", "help")
        if model_name in env
        and field_name in env[model_name]._fields
        and env[model_name]._fields[field_name].translate
        and column_exists(env.cr, env[model_name]._table, field_name)
    ]
    openupgrade_160.migrate_translations_to_jsonb(env, fields_spec)


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "base", "16.0.1.3/noupdate_changes.xml")
    env.cr.execute(
        "UPDATE res_partner p SET company_registry=c.company_registry "
        "FROM res_company c WHERE c.partner_id=p.id"
    )
    update_ir_actions_translations(env)
