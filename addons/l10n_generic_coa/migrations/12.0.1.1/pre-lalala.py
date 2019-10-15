# Copyright 2019 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.set_xml_ids_noupdate_value(
        env, 'l10n_generic_coa', [
            'a_capital',
            'a_dividends',
            'a_expense_finance',
            'a_expense_invest',
            'a_salary_expense',
            'cas',
            'conf_a_expense',
            'conf_a_pay',
            'conf_a_recv',
            'conf_a_reserve_and_surplus',
            'conf_a_sale',
            'conf_cas',
            'conf_cas_interim1',
            'conf_cas_interim2',
            'conf_cog',
            'conf_iva',
            'conf_ncas',
            'conf_o_income',
            'conf_ova',
            'conf_prepayments',
            'conf_stk',
            'conf_xfa',
            'current_liabilities',
            'exchange_fx_expense',
            'exchange_fx_income',
        ], False)
