# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

xmlid_renames = [
    ('l10n_generic_coa.a_capital', 'l10n_generic_coa.capital'),
    ('l10n_generic_coa.a_dividends', 'l10n_generic_coa.dividends'),
    ('l10n_generic_coa.a_expense_finance', 'l10n_generic_coa.expense_finance'),
    ('l10n_generic_coa.a_expense_invest', 'l10n_generic_coa.expense_invest'),
    ('l10n_generic_coa.a_salary_expense', 'l10n_generic_coa.expense_salary'),
    ('l10n_generic_coa.cas', 'l10n_generic_coa.non_current_liabilities'),
    ('l10n_generic_coa.conf_a_expense', 'l10n_generic_coa.expense'),
    ('l10n_generic_coa.conf_a_pay', 'l10n_generic_coa.payable'),
    ('l10n_generic_coa.conf_a_recv', 'l10n_generic_coa.receivable'),
    ('l10n_generic_coa.conf_a_reserve_and_surplus', 'l10n_generic_coa.tax_payable'),
    ('l10n_generic_coa.conf_a_sale', 'l10n_generic_coa.income'),
    ('l10n_generic_coa.conf_cas', 'l10n_generic_coa.stock_valuation'),
    ('l10n_generic_coa.conf_cas_interim1', 'l10n_generic_coa.stock_in'),
    ('l10n_generic_coa.conf_cas_interim2', 'l10n_generic_coa.stock_out'),
    ('l10n_generic_coa.conf_cog', 'l10n_generic_coa.cost_of_goods_sold'),
    ('l10n_generic_coa.conf_iva', 'l10n_generic_coa.tax_received'),
    ('l10n_generic_coa.conf_ncas', 'l10n_generic_coa.non_current_assets'),
    ('l10n_generic_coa.conf_o_income', 'l10n_generic_coa.other_income'),
    ('l10n_generic_coa.conf_ova', 'l10n_generic_coa.tax_paid'),
    ('l10n_generic_coa.conf_prepayments', 'l10n_generic_coa.prepayments'),
    ('l10n_generic_coa.conf_stk', 'l10n_generic_coa.current_assets'),
    ('l10n_generic_coa.conf_xfa', 'l10n_generic_coa.fixed_assets'),
    ('l10n_generic_coa.exchange_fx_expense', 'l10n_generic_coa.expense_currency_exchange'),
    ('l10n_generic_coa.exchange_fx_income', 'l10n_generic_coa.income_currency_exchange'),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, xmlid_renames)
    openupgrade.set_xml_ids_noupdate_value(
        env,
        "l10n_generic_coa",
        [
            "configurable_chart_template",
            "purchase_tax_template",
            "sale_tax_template",
        ],
        False,
    )
