# Copyright 2023 Tecnativa - Víctor Martínez
# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def _hr_expense_process(env):
    """Set amount_tax_company by ORM only when different currency."""
    env.cr.execute(
        """
        SELECT he.id
        FROM hr_expense he
        JOIN res_company rc ON rc.id = he.company_id
        WHERE rc.currency_id = he.currency_id
        """
    )
    env["hr.expense"].browse([x[0] for x in env.cr.fetchall()])._compute_amount_tax()


def _hr_expense_sheet_process(env):
    """With the hr.expense values already defined, we can now set the missing data."""
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_expense_sheet SET total_amount_taxes = (
            SELECT SUM(amount_tax_company)
            FROM hr_expense
            WHERE sheet_id = hr_expense_sheet.id
        )
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_expense_sheet
        SET untaxed_amount = (total_amount - total_amount_taxes)
        """,
    )


def _hr_expense_analytic_tag(env):
    """If table exists and there are any record with no distribution (used just as tag),
    we set the module hr_expense_analytic_tag to be installed.
    """
    if openupgrade.table_exists(env.cr, "account_analytic_tag_hr_expense_rel"):
        env.cr.execute(
            """SELECT COUNT(*)
            FROM account_analytic_tag_hr_expense_rel rel
            JOIN account_analytic_tag aat ON rel.account_analytic_tag_id = aat.id
            WHERE NOT aat.active_analytic_distribution
            """,
        )
        if env.cr.fetchone()[0]:
            openupgrade.logged_query(
                env.cr,
                """UPDATE ir_module_module
                SET state = 'to install'
                WHERE name = 'hr_expense_analytic_tag'""",
            )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "hr_expense", "16.0.2.0/noupdate_changes.xml")
    _hr_expense_process(env)
    _hr_expense_sheet_process(env)
    _hr_expense_analytic_tag(env)
    openupgrade.set_xml_ids_noupdate_value(
        env,
        "hr_expense",
        ["product_product_no_cost"],
        True,
    )
