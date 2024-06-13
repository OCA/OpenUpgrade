# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade, openupgrade_160

from odoo.tools import column_exists


def update_callable_translatable_fields(env):
    """Use Odoo's core method to get complete translations of translated fields with
    a callable method for translations (html_translate, xml_translate)"""
    exclusions = [
        # ir.actions.* inherits the name and help columns from ir.actions.actions
        ("ir.actions.act_window", "name"),
        ("ir.actions.act_window", "help"),
        ("ir.actions.act_url", "name"),
        ("ir.actions.act_url", "help"),
        ("ir.actions.server", "name"),
        ("ir.actions.server", "help"),
        ("ir.actions.client", "name"),
        ("ir.actions.client", "help"),
        ("ir.actions.report", "name"),
        ("ir.actions.report", "help"),
    ]
    fields = env["ir.model.fields"].search_read(
        [("translate", "=", True)], ["model", "name"]
    )
    fields_spec = [
        (f["model"], f["name"])
        for f in fields
        if (
            (f["model"], f["name"]) not in exclusions
            and f["model"] in env
            and column_exists(env.cr, env[f["model"]]._table, f["name"])
            and f["name"] in env[f["model"]]._fields
            and callable(env[f["model"]]._fields[f["name"]].translate)
        )
    ]
    openupgrade_160.migrate_translations_to_jsonb(env, fields_spec)


@openupgrade.migrate()
def migrate(env, version):
    update_callable_translatable_fields(env)
