# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def add_default_account_data(env):
    """v13 introduces some new accounts at company level. We need to ensure
    that the information is filled on existing companies for avoiding problems
    in  subsequent modules (like `point_of_sale`).

    Need to be on end-migration for making sure all chart of templates have
    their data loaded.
    """
    for company in env["res.company"].search([]):
        for chart_field, company_field in [
            ("default_pos_receivable_account_id",
             "account_default_pos_receivable_account_id"),
            ("default_cash_difference_expense_account_id",
             "default_cash_difference_expense_account_id"),
            ("default_cash_difference_income_account_id",
             "default_cash_difference_income_account_id"),
        ]:
            chart = company.chart_template_id
            account_template = chart[chart_field]
            if not account_template:
                continue
            tmpl_xml_id = account_template.get_external_id()[account_template.id]
            module, name = tmpl_xml_id.split('.', 1)
            xml_id = "%s.%s_%s" % (module, company.id, name)
            account = env.ref(xml_id, False)
            if not account:
                # Code copied from `generate_account` in `account.chart.template`
                # - can't call it directly as it loads all account templates -
                code_main = account_template.code and len(account_template.code) or 0
                code_acc = account_template.code or ""
                if code_main > 0 and code_main <= chart.code_digits:
                    code_acc = str(code_acc) + (
                        str("0" * (chart.code_digits - code_main)))
                tax_template_ref = {}
                vals = chart._get_account_vals(
                    company, account_template, code_acc, tax_template_ref)
                account = chart._create_records_with_xmlid(
                    "account.account", [(account_template, vals)], company)
            company[company_field] = account.id


@openupgrade.migrate()
def migrate(env, version):
    add_default_account_data(env)
