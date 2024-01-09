# Copyright 2020 Odoo Community Association (OCA)
# Copyright 2020 Opener B.V. <stefan@opener.am>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

from odoo import tools

from odoo.addons.openupgrade_scripts.apriori import merged_modules, renamed_modules

_logger = logging.getLogger(__name__)


def enable_coupon_sharing_within_entity(cr):
    """Check before merging `coupon_commercial_partner_applicability` into
    `loyalty_partner_applicability` if it was installed in v15 to set the parameter
    to True to keep the same functionality"""
    if openupgrade.is_module_installed(cr, "coupon_commercial_partner_applicability"):
        # The value of the configuration parameter is set to True.
        openupgrade.logged_query(
            cr,
            """
            INSERT INTO ir_config_parameter (key, value)
            VALUES ('loyalty_partner_applicability.allow_coupon_sharing', 'true')
            """,
        )


def login_or_registration_required_at_checkout(cr):
    """The website_sale_require_login module is merged into website_sale. Check if the
    it was installed in v15 to set the website.account_on_checkout field as mandatory
    so that the functionality remains the same, login/registration required for
    checkout."""
    # Check if the module is installed and its status is "installed".
    if openupgrade.is_module_installed(cr, "website_sale_require_login"):
        # Add the field 'account_on_checkout' to the 'website' table if it doesn't exist yet.
        openupgrade.logged_query(
            cr,
            """
            ALTER TABLE website
            ADD COLUMN IF NOT EXISTS account_on_checkout VARCHAR
            """,
        )
        # Set the value 'mandatory' in the field for all records in the table 'website'.
        openupgrade.logged_query(
            cr,
            """
            UPDATE website
            SET account_on_checkout = 'mandatory'
            """,
        )


def update_translatable_fields(cr):
    # exclude fields from translation update
    exclusions = {
        # ir.actions.* inherits the name column from ir.actions.actions
        "ir.actions.act_window": ["name", "help"],
        "ir.actions.act_url": ["name"],
        "ir.actions.server": ["name"],
        "ir.actions.client": ["name", "help"],
        "ir.actions.report": ["name"],
    }
    cr.execute(
        "SELECT f.name, m.model FROM ir_model_fields f "
        "JOIN ir_model m ON f.model_id=m.id WHERE f.translate"
    )
    for field, model in cr.fetchall():
        if field in exclusions.get(model, []):
            continue
        table = openupgrade.get_model2table(model)
        if not openupgrade.table_exists(cr, table):
            _logger.warning(
                "Couldn't find table for model %s - not updating translations", model
            )
            continue
        columns = tools.sql.table_columns(cr, table)
        if field in columns:
            if columns[field]["udt_name"] in ["varchar", "text"]:
                tools.sql.convert_column_translatable(cr, table, field, "jsonb")
        else:
            _logger.warning(
                "Couldn't find column for field %s - not updating translations", field
            )
            continue
        # borrowed from odoo/tools/translate.py#_get_translation_upgrade_queries
        translation_name = "%s,%s" % (model, field)
        openupgrade.logged_query(
            cr,
            f"""
            WITH t AS (
                SELECT it.res_id as res_id, jsonb_object_agg(it.lang, it.value) AS value,
                    bool_or(imd.noupdate) AS noupdate
                FROM ir_translation it
                LEFT JOIN ir_model_data imd ON imd.model = %(model)s AND imd.res_id = it.res_id
                WHERE it.type = 'model' AND it.name = %(name)s AND it.state = 'translated'
                GROUP BY it.res_id
            )
            UPDATE {table} m
            SET "{field}" = CASE WHEN t.noupdate IS FALSE THEN t.value || m."{field}"
                                 ELSE m."{field}" || t.value END
            FROM t
            WHERE t.res_id = m.id
            """,
            {
                "model": model,
                "name": translation_name,
            },
        )
        openupgrade.logged_query(
            cr,
            "DELETE FROM ir_translation WHERE type = 'model' AND name = %s",
            [translation_name],
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
    login_or_registration_required_at_checkout(cr)
    enable_coupon_sharing_within_entity(cr)
    openupgrade.update_module_names(cr, renamed_modules.items())
    openupgrade.update_module_names(cr, merged_modules.items(), merge_modules=True)
    # restricting inherited views to groups isn't allowed any more
    cr.execute(
        "DELETE FROM ir_ui_view_group_rel r "
        "USING ir_ui_view v "
        "WHERE r.view_id=v.id AND v.inherit_id IS NOT NULL AND v.mode != 'primary'"
    )
    # update all translatable fields
    update_translatable_fields(cr)
