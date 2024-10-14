# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

from odoo import tools

from odoo.addons.openupgrade_scripts.apriori import merged_modules, renamed_modules

_logger = logging.getLogger(__name__)

_xmlids_renames = [
    (
        "mail.model_res_users_settings",
        "base.model_res_users_settings",
    ),
    (
        "mail.access_res_users_settings_all",
        "base.access_res_users_settings_all",
    ),
    (
        "mail.access_res_users_settings_user",
        "base.access_res_users_settings_user",
    ),
    (
        "mail.res_users_settings_rule_admin",
        "base.res_users_settings_rule_admin",
    ),
    (
        "mail.res_users_settings_rule_user",
        "base.res_users_settings_rule_user",
    ),
    (
        "mail.constraint_res_users_settings_unique_user_id",
        "base.constraint_res_users_settings_unique_user_id",
    ),
]
_column_renames = {
    "res_partner": [("display_name", "complete_name")],
}


def _fill_ir_server_object_lines_into_action_server(cr):
    openupgrade.logged_query(
        cr,
        """
        ALTER TABLE ir_act_server
            ADD COLUMN IF NOT EXISTS old_ias_id VARCHAR,
            ADD COLUMN IF NOT EXISTS evaluation_type VARCHAR,
            ADD COLUMN IF NOT EXISTS resource_ref VARCHAR,
            ADD COLUMN IF NOT EXISTS selection_value INTEGER,
            ADD COLUMN IF NOT EXISTS update_boolean_value VARCHAR,
            ADD COLUMN IF NOT EXISTS update_field_id INTEGER,
            ADD COLUMN IF NOT EXISTS update_m2m_operation VARCHAR,
            ADD COLUMN IF NOT EXISTS update_path VARCHAR,
            ADD COLUMN IF NOT EXISTS update_related_model_id INTEGER,
            ADD COLUMN IF NOT EXISTS value TEXT;
        """,
    )
    # Update operations
    openupgrade.logged_query(
        cr,
        """
        INSERT INTO ir_act_server
        (
            old_ias_id,
            evaluation_type,
            update_field_id,
            update_path,
            update_related_model_id,
            value,
            resource_ref,
            selection_value,
            update_boolean_value,
            update_m2m_operation,
            binding_type,
            state,
            type,
            usage,
            model_id,
            name
        )
        SELECT
            ias.id,
            CASE
                WHEN isol.evaluation_type = 'equation' then 'equation'
                ELSE 'value'
            END,
            imf.id,
            imf.name,
            im.id,
            CASE WHEN isol.evaluation_type = 'equation'
                THEN isol.value
                ELSE NULL
            END,
            CASE WHEN imf.ttype in ('many2one', 'many2many')
                THEN imf.relation || ',' || isol.value
                ELSE NULL
            END,
            imfs.id,
            CASE WHEN imf.ttype = 'boolean'
                THEN isol.value::bool
                ELSE NULL
            END,
            'add',
            'action',
            'object_write',
            'ir.actions.server',
            'ir_actions_server',
            ias.model_id,
            ias.name
        FROM ir_act_server ias
        JOIN ir_server_object_lines isol ON isol.server_id = ias.id
        JOIN ir_model_fields imf ON imf.id = isol.col1
        LEFT JOIN ir_model im ON im.model = imf.relation
        LEFT JOIN ir_model_fields_selection imfs
            ON imf.id = imfs.field_id AND imfs.value = isol.value
        WHERE ias.state = 'object_write'
        RETURNING id, old_ias_id
        """,
    )
    for row in cr.fetchall():
        cr.execute(
            """
            INSERT INTO rel_server_actions
            (action_id, server_id)
            VALUES (%s, %s)
            """,
            (row[0], row[1]),
        )
    openupgrade.logged_query(
        cr,
        """UPDATE ir_act_server ias
        SET state = 'multi'
        FROM ir_server_object_lines isol
        WHERE ias.state = 'object_write'
        AND isol.server_id = ias.id
        """,
    )
    # Create operations
    openupgrade.logged_query(
        cr,
        """UPDATE ir_act_server ias
        SET value = isol.value
        FROM ir_server_object_lines isol
        JOIN ir_model_fields imf ON imf.id = isol.col1
        WHERE ias.state = 'object_create'
        AND isol.server_id = ias.id
        AND isol.evaluation_type = 'value'
        AND imf.name = 'name'
        """,
    )


def _fill_empty_country_codes(cr):
    openupgrade.logged_query(
        cr,
        """
        UPDATE res_country
        SET code = 'OU' || id::VARCHAR
        WHERE code IS NULL
        """,
    )


def _handle_partner_private_type(cr):
    # Copy private records into a new table
    openupgrade.logged_query(
        cr,
        """
        CREATE TABLE ou_res_partner_private AS
        SELECT * FROM res_partner
        WHERE type = 'private'
        """,
    )
    # Copy column for preserving the old type values
    _column_copies = {"res_partner": [("type", None, None)]}
    openupgrade.copy_columns(cr, _column_copies)
    # Change contact type and erase sensitive information
    query = "type = 'contact'"
    for field in [
        "street",
        "street2",
        "city",
        "zip",
        "vat",
        "function",
        "phone",
        "mobile",
        "email",
        "website",
        "comment",
    ]:
        query += f", {field} = CASE WHEN {field} IS NULL THEN NULL ELSE '*****' END"
    openupgrade.logged_query(
        cr,
        f"""
        UPDATE res_partner
        SET {query},
        country_id = NULL,
        state_id = NULL
        WHERE type = 'private'
        """,
    )


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    """
    Don't request an env for the base pre-migration as flushing the env in
    odoo/modules/registry.py will break on the 'base' module not yet having
    been instantiated.
    """
    if "openupgrade_framework" not in tools.config["server_wide_modules"]:
        _logger.error(
            "openupgrade_framework is not preloaded. You are highly "
            "recommended to run the Odoo with --load=openupgrade_framework "
            "when migrating your database."
        )
    openupgrade.update_module_names(cr, renamed_modules.items())
    openupgrade.update_module_names(cr, merged_modules.items(), merge_modules=True)
    openupgrade.rename_xmlids(cr, _xmlids_renames)
    openupgrade.rename_columns(cr, _column_renames)
    _fill_ir_server_object_lines_into_action_server(cr)
    _fill_empty_country_codes(cr)
    _handle_partner_private_type(cr)
