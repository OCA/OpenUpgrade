# Copyright 2023 Hunki Enterprises BV (https://hunki-enterprises.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade, openupgrade_160

from odoo.tools import column_exists


def update_ir_actions_name_translations(env):
    """Merge the translations of the name of the ir.actions.* models.

    Those names inherit their column from ir.actions.actions: it cannot be
    altered on the child tables, and when it becomes translated (jsonb) the
    ORM converts it together with the inherited copies, keeping only the
    current en_US value.  The base pre-migration excludes these fields, so
    merge the ir_translation records here, once the columns are jsonb and the
    source table is still available.

    This must run in the post-migration: end-migration scripts are executed
    after the OpenUpgrade migration tests, and "ir.translation" is still
    available at this stage.
    """
    name_fields = [
        ("ir.actions.act_window", "name"),
        ("ir.actions.act_url", "name"),
        ("ir.actions.server", "name"),
        ("ir.actions.client", "name"),
        ("ir.actions.report", "name"),
    ]
    fields_spec = [
        (model_name, field_name)
        for model_name, field_name in name_fields
        if model_name in env
        and field_name in env[model_name]._fields
        and column_exists(env.cr, env[model_name]._table, field_name)
        and not callable(env[model_name]._fields[field_name].translate)
    ]
    openupgrade_160.migrate_translations_to_jsonb(env, fields_spec)


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "base", "16.0.1.3/noupdate_changes.xml")
    env.cr.execute(
        "UPDATE res_partner p SET company_registry=c.company_registry "
        "FROM res_company c WHERE c.partner_id=p.id"
    )
    update_ir_actions_name_translations(env)
