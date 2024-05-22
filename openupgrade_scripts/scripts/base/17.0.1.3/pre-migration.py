# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# Copyright 2020 Odoo Community Association (OCA)
# Copyright 2020 Opener B.V. <stefan@opener.am>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

from odoo import tools

from odoo.addons.openupgrade_scripts.apriori import merged_modules, renamed_modules

_logger = logging.getLogger(__name__)

_xmlids_renames = [
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


def _fill_ir_server_object_lines_into_action_server(cr):
    openupgrade.logged_query(
        cr,
        """
        ALTER TABLE ir_act_server
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
    openupgrade.logged_query(
        cr,
        """
        WITH tmp AS (
            SELECT t1.id, t1.state, t2.col1, t2.value, t2.evaluation_type,
            t3.name AS update_field_name, t3.ttype,
            t3.relation, t4.id AS selection_field_id
            FROM ir_act_server t1
            JOIN ir_server_object_lines t2 on t1.id = t2.server_id
            JOIN ir_model_fields t3 on t2.col1 = t3.id
            LEFT JOIN ir_model_fields_selection t4 on t3.id = t4.field_id
        )
        UPDATE ir_act_server ias
            SET
                update_field_id = CASE
                    WHEN tmp.state = 'object_create' THEN NULL
                    WHEN tmp.state = 'object_write' THEN tmp.col1
                    ELSE NULL
                END,
                update_path = CASE
                    WHEN tmp.state = 'object_create' THEN NULL
                    WHEN tmp.state = 'object_write' THEN tmp.update_field_name
                    ELSE NULL
                END,
                update_related_model_id = CASE
                    WHEN tmp.state = 'object_write' AND tmp.evaluation_type = 'value'
                    AND tmp.relation IS NOT NULL THEN
                    (SELECT id FROM ir_model WHERE model=tmp.relation LIMIT 1)
                    ELSE NULL
                END,
                update_m2m_operation = 'add',
                evaluation_type = CASE
                    WHEN tmp.evaluation_type = 'value' then 'value'
                    WHEN tmp.evaluation_type = 'reference' then 'value'
                    WHEN tmp.evaluation_type = 'equation' then 'equation'
                    ELSE 'VALUE'
                END,
                value = tmp.value,
                resource_ref = CASE
                    WHEN tmp.ttype in ('many2one', 'many2many')
                    THEN tmp.relation || ',' || tmp.value
                    ELSE NULL
                END,
                selection_value = CASE
                    WHEN tmp.ttype = 'selection' THEN tmp.selection_field_id
                    ELSE NULL
                END,
                update_boolean_value = CASE
                    WHEN tmp.ttype = 'boolean' then 'true'
                    ELSE NULL
                END
        FROM tmp
        WHERE ias.id = tmp.id
        """,
    )


def _partner_create_column_complete_name(cr):
    openupgrade.logged_query(
        cr,
        """
        ALTER TABLE res_partner
            ADD COLUMN IF NOT EXISTS complete_name VARCHAR;
        """,
    )


def _update_partner_private_type(cr):
    openupgrade.logged_query(
        cr,
        """
        UPDATE res_partner
        SET type = 'contact'
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
    _fill_ir_server_object_lines_into_action_server(cr)
    _update_partner_private_type(cr)
    _partner_create_column_complete_name(cr)
