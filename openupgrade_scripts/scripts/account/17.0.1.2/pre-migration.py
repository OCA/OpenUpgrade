# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

from odoo.tools.sql import convert_column_translatable

_fields_renames = [
    (
        "res.company",
        "res_company",
        "invoice_is_print",
        "invoice_is_download",
    ),
]

_l10n_generic_coa_tax_group_xmlid = "account.tax_group_15"


def _map_account_report_filter_account_type(env):
    openupgrade.rename_columns(
        env.cr, {"account_report": [("filter_account_type", None)]}
    )
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_report
        ADD COLUMN filter_account_type character varying;
        """,
    )
    openupgrade.logged_query(
        env.cr,
        f"""
        UPDATE account_report
        SET filter_account_type = CASE
            WHEN {openupgrade.get_legacy_name('filter_account_type')} THEN 'both'
            ELSE 'disabled'
            END
        """,
    )


def _generic_coa_rename_xml_id(env):
    """
    Since the removal of account.chart.template
    we need to rename some xml_id like tax or tax.group
    in order to avoid duplication
    """
    _dummy, template_id = env["ir.model.data"]._xmlid_to_res_model_res_id(
        "account.configurable_chart_template",
    )
    if not template_id:
        return
    env.cr.execute(
        f"""
        SELECT id FROM res_company
        WHERE chart_template_id={template_id}
        """
    )
    xmlids_renames = []
    for (company_id,) in env.cr.fetchall():
        old_xml_id = _l10n_generic_coa_tax_group_xmlid
        new_xmlid = (
            f"account.{company_id}_" + _l10n_generic_coa_tax_group_xmlid.split(".")[1]
        )
        xmlids_renames.append((old_xml_id, new_xmlid))
    openupgrade.rename_xmlids(env.cr, xmlids_renames)
    openupgrade.set_xml_ids_noupdate_value(
        env, "account", [_l10n_generic_coa_tax_group_xmlid.split(".")[1]], False
    )


def _convert_account_tax_description(env):
    openupgrade.rename_columns(
        env.cr, {"account_tax": [("description", "invoice_label")]}
    )
    convert_column_translatable(env.cr, "account_tax", "invoice_label", "jsonb")


def _am_create_delivery_date_column(env):
    """
    Create column then in module need them like l10n_de and sale_stock will fill value,
    https://github.com/odoo/odoo/pull/116643
    """
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_move
        ADD COLUMN IF NOT EXISTS delivery_date DATE
        """,
    )


def _am_create_incoterm_location_column(env):
    """
    Create column then in sale_stock and purchase_stock will fill it in pre,
    pr: https://github.com/odoo/odoo/pull/118954
    """
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_move
        ADD COLUMN IF NOT EXISTS incoterm_location CHARACTER VARYING
        """,
    )


def _am_uniquify_name(env):
    """
    Make move names unique per journal to satisfy the constraint v17 creates
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move SET name=name || ' [' || id || ']'
        FROM (
            SELECT array_agg(id) ids FROM account_move
            GROUP BY journal_id, name HAVING COUNT(id)>1
        ) duplicate_names
        WHERE account_move.id=ANY(duplicate_names.ids);
        """,
    )


def _account_report_update_figure_type(env):
    openupgrade.copy_columns(
        env.cr,
        {
            "account_report_column": [("figure_type", None, None)],
            "account_report_expression": [("figure_type", None, None)],
        },
    )
    old_column = openupgrade.get_legacy_name("figure_type")
    openupgrade.map_values(
        env.cr,
        old_column,
        "figure_type",
        [("none", "string")],
        False,
        "account_report_column",
    )
    openupgrade.map_values(
        env.cr,
        old_column,
        "figure_type",
        [("none", "string")],
        False,
        "account_report_expression",
    )


def _account_tax_repartition_line_merge_repartition_lines_m2o(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_tax_repartition_line
            ADD COLUMN IF NOT EXISTS document_type VARCHAR,
            ADD COLUMN IF NOT EXISTS tax_id INTEGER;
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_tax_repartition_line
            SET document_type = CASE
                WHEN invoice_tax_id IS NOT NULL THEN 'invoice'
                WHEN refund_tax_id IS NOT NULL THEN 'refund'
            END,
                tax_id = CASE
                WHEN invoice_tax_id IS NOT NULL THEN invoice_tax_id
                WHEN refund_tax_id IS NOT NULL THEN refund_tax_id
            END
        """,
    )


def _pre_create_early_pay_discount_computation(env):
    """Avoid triggering the computed method and fill the corresponding value from
    companies.
    """
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_payment_term
            ADD COLUMN IF NOT EXISTS early_pay_discount_computation VARCHAR
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_payment_term apt
        SET early_pay_discount_computation = rc.early_pay_discount_computation
        FROM res_company rc
        WHERE apt.company_id = rc.id
        AND apt.early_pay_discount_computation IS NULL
        AND rc.early_pay_discount_computation IS NOT NULL
        """,
    )


def _decouple_obsolete_tables(env):
    """
    Remove all foreign keys held by and pointed to template tables
    """
    obsolete_tables = [
        "account_account_template",
        "account_fiscal_position_account_template",
        "account_fiscal_position_tax_template",
        "account_fiscal_position_template",
        "account_group_template",
        "account_reconcile_model_line_template",
        "account_reconcile_model_template",
        "account_tax_repartition_line_template",
        "account_tax_template",
    ]
    openupgrade.remove_tables_fks(env.cr, obsolete_tables)
    env.cr.execute(
        """
        SELECT tc.table_name, tc.constraint_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.constraint_table_usage ctu
        ON tc.constraint_name=ctu.constraint_name
        WHERE ctu.table_name in %s
        AND tc.constraint_type='FOREIGN KEY'
        """,
        (tuple(obsolete_tables),),
    )
    for table, constraint in env.cr.fetchall():
        openupgrade.logged_query(
            env.cr, f"ALTER TABLE {table} DROP CONSTRAINT {constraint}"
        )


def _pre_create_account_report_active(env):
    """
    Precreate column with default value true, then switch back to false
    """
    env.cr.execute(
        """
        ALTER TABLE account_report ADD COLUMN active boolean DEFAULT true
        """
    )
    env.cr.execute(
        """
        ALTER TABLE account_report ALTER COLUMN active SET DEFAULT false
        """
    )


def _remove_obsolete_constraints(env):
    """
    Remove constraints that will be deleted at the end of the migration
    """
    table2constraints = {
        "account_account": ["code_company_uniq"],
        "account_fiscal_position_account": ["account_src_dest_uniq"],
        "account_tax": ["name_company_uniq", "template_name_company_uniq"],
    }
    for table, constraints in table2constraints.items():
        for constraint in constraints:
            openupgrade.delete_sql_constraint_safely(env, "account", table, constraint)


@openupgrade.migrate()
def migrate(env, version):
    _map_account_report_filter_account_type(env)
    _generic_coa_rename_xml_id(env)
    # Drop trigram index on name column of account.account
    # to avoid error when loading registry, it will be recreated
    openupgrade.logged_query(
        env.cr,
        """
        DROP INDEX IF EXISTS account_account_name_index;
        """,
    )
    openupgrade.rename_fields(env, _fields_renames)
    _convert_account_tax_description(env)
    _am_create_delivery_date_column(env)
    _am_create_incoterm_location_column(env)
    _am_uniquify_name(env)
    _account_report_update_figure_type(env)
    _account_tax_repartition_line_merge_repartition_lines_m2o(env)
    _pre_create_early_pay_discount_computation(env)
    _decouple_obsolete_tables(env)
    _pre_create_account_report_active(env)
    _remove_obsolete_constraints(env)
