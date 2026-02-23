# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_added_fields = [
    ("taxable_supply_date", "account.move", "account_move", "date", None, "account"),
    (
        "deductible_amount",
        "account.move.line",
        "account_move_line",
        "float",
        None,
        "account",
        100,
    ),
    (
        "is_storno",
        "account.move.line",
        "account_move_line",
        "boolean",
        None,
        "account",
        False,
    ),
    (
        "no_followup",
        "account.move.line",
        "account_move_line",
        "boolean",
        None,
        "account",
        False,
    ),
    (
        "allow_foreign_vat",
        "account.report",
        "account_report",
        "boolean",
        None,
        "account",
        False,
    ),
]

_renamed_fields = [
    (
        "res.company",
        "res_company",
        "check_account_audit_trail",
        "restrictive_audit_trail",
    ),
]


_renamed_xmlids = [
    (
        "account_peppol_selfbilling.email_template_edi_self_billing_credit_note",
        "account.email_template_edi_self_billing_credit_note",
    ),
    (
        "account_peppol_selfbilling.email_template_edi_self_billing_invoice",
        "account.email_template_edi_self_billing_invoice",
    ),
]


def account_journal_invoice_reference_type(env):
    """
    Map account.journal#invoice_reference_type value 'none' to 'invoice'
    """
    openupgrade.copy_columns(
        env.cr, {"account_journal": [("invoice_reference_type", None, None)]}
    )
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("invoice_reference_type"),
        "invoice_reference_type",
        [("none", "invoice")],
        table="account_journal",
    )


def account_report(env):
    """
    Map account.report#default_opening_date_filter values 'previous_tax_period',
    'this_tax_period' to 'previous_return_period', 'this_return_period'
    Map account.report#filter_multi_company value 'disabled' to None
    """
    openupgrade.copy_columns(
        env.cr, {"account_report": [("default_opening_date_filter", None, None)]}
    )
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("default_opening_date_filter"),
        "default_opening_date_filter",
        [
            ("this_tax_period", "this_return_period"),
            ("previous_tax_period", "previous_return_period"),
        ],
        table="account_report",
    )
    openupgrade.copy_columns(
        env.cr, {"account_report": [("filter_multi_company", None, None)]}
    )
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("filter_multi_company"),
        "filter_multi_company",
        [
            ("disabled", False),
        ],
        table="account_report",
    )


def account_report_expression(env):
    """
    Map account.report.expression#date_scope value 'previous_tax_period' to
    'previous_return_period'
    """
    openupgrade.copy_columns(
        env.cr, {"account_report_expression": [("date_scope", None, None)]}
    )
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("date_scope"),
        "date_scope",
        [
            ("previous_tax_period", "previous_return_period"),
        ],
        table="account_report_expression",
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.add_fields(env, _added_fields)
    openupgrade.rename_fields(env, _renamed_fields)
    openupgrade.rename_xmlids(env.cr, _renamed_xmlids)
    account_journal_invoice_reference_type(env)
    account_report(env)
    account_report_expression(env)
