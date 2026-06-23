# Copyright 2025 Hunki Enterprises BV
# Copyright 2026 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

from odoo.addons.base.models.ir_model import MODULE_UNINSTALL_FLAG


def _fix_apikeys_table(env, table):
    """
    This table is created manually, so we have to add the new column manually too
    """
    openupgrade.logged_query(
        env.cr,
        f"""
        ALTER TABLE {table}
        ADD COLUMN IF NOT EXISTS expiration_date timestamp without time zone
        """,
    )


def _fix_res_users_apikeys(env):
    """
    Fix the tables of models inheriting from res.users.apikeys
    """
    Apikeys = env["res.users.apikeys"]

    _fix_apikeys_table(env, Apikeys._table)

    for model_name in Apikeys._inherit_children:
        Model = env[model_name]
        if Model._table != Apikeys._table:
            _fix_apikeys_table(env, Model._table)


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.disable_invalid_filters(env)
    _fix_res_users_apikeys(env)
    env.ref("base.model_ir_property").with_context(
        **{MODULE_UNINSTALL_FLAG: True}
    ).unlink()
    env.ref("base.model_res_config_installer").with_context(
        **{MODULE_UNINSTALL_FLAG: True}
    ).unlink()
