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
            check_chart = chart
            account_template = False
            while not account_template and check_chart:
                account_template = check_chart[chart_field]
                check_chart = check_chart.parent_id
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
                account = env['account.account'].search([
                    ('code', '=', code_acc),
                    ('company_id', '=', company.id),
                ], limit=1)
                # If there's already an account with the same code and company don't create it
                # as it is not allowed by "account_account_code_company_uniq" constraint.
                if not account:
                    tax_template_ref = {}
                    vals = chart._get_account_vals(
                        company, account_template, code_acc, tax_template_ref)
                    account = chart._create_records_with_xmlid(
                        "account.account", [(account_template, vals)], company)
                else:
                    # we add xmlid for such existing account
                    env["ir.model.data"].sudo()._update_xmlids(
                        [dict(xml_id=xml_id, noupdate=True, record=account)])
            company[company_field] = account.id


def update_mail_alias_for_moves(env):
    # Done here just in case alias customizations exist
    journals = env["account.journal"].with_context(
        active_test=False).search([("alias_id", "!=", False)])
    for journal in journals:
        alias_name = journal.alias_name
        journal.alias_id.unlink()
        journal._update_mail_alias({"alias_name": alias_name})


@openupgrade.migrate()
def migrate(env, version):
    add_default_account_data(env)
    update_mail_alias_for_moves(env)
