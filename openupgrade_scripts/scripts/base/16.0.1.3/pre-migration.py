# Copyright 2020 Odoo Community Association (OCA)
# Copyright 2020 Opener B.V. <stefan@opener.am>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade
from psycopg2.extensions import AsIs

from odoo import tools

from odoo.addons.openupgrade_scripts.apriori import merged_modules, renamed_modules

_logger = logging.getLogger(__name__)


def update_translatable_fields(cr):
    # map of nonstandard table names
    model2table = {
        "ir.actions.actions": "ir_actions",
        "ir.actions.act_window": "ir_act_window",
        "ir.actions.act_window.view": "ir_act_window_view",
        "ir.actions.act_window_close": "ir_actions",
        "ir.actions.act_url": "ir_act_url",
        "ir.actions.server": "ir_act_server",
        "ir.actions.client": "ir_act_client",
        "ir.actions.report": "ir_act_report_xml",
    }
    # exclude fields from translation update
    exclusions = {
        # ir.actions.* inherits the name column from ir.actions.actions
        "ir.actions.act_window": ["name", "help"],
        "ir.actions.act_url": ["name"],
        "ir.actions.server": ["name"],
        "ir.actions.client": ["name"],
        "ir.actions.report": ["name"],
    }
    cr.execute(
        "SELECT f.name, m.model FROM ir_model_fields f "
        "JOIN ir_model m ON f.model_id=m.id WHERE f.translate"
    )
    for field, model in cr.fetchall():
        if field in exclusions.get(model, []):
            continue
        table = model2table.get(model, model.replace(".", "_"))
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
            """
            WITH t AS (
                SELECT it.res_id as res_id, jsonb_object_agg(it.lang, it.value) AS value,
                    bool_or(imd.noupdate) AS noupdate
                FROM ir_translation it
                LEFT JOIN ir_model_data imd ON imd.model = %(model)s AND imd.res_id = it.res_id
                WHERE it.type = 'model' AND it.name = %(name)s AND it.state = 'translated'
                GROUP BY it.res_id
            )
            UPDATE "%(table)s" m
            SET "%(field_name)s" = CASE WHEN t.noupdate THEN m.%(field_name)s || t.value
                                    ELSE t.value || m.%(field_name)s END
            FROM t
            WHERE t.res_id = m.id
            """,
            {
                "table": AsIs(table),
                "model": model,
                "name": translation_name,
                "field_name": AsIs(field),
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
