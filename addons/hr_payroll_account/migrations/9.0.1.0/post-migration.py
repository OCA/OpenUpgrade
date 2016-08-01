# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from psycopg2.extensions import AsIs
from openupgradelib import openupgrade


def set_tax_from_tax_code(cr, table, tax_column, tax_code_column=None):
    """Get some tax from a field that used to point to a tax code (now group).
    If the tax_code_colmn is not given, get_legacy_name(tax_code) will be used.
    """
    # TODO: propose to openupgradelib
    cr.execute(
        "update %(table)s t set %(tax_column)=tax.id "
        "from account_tax_group group "
        "join account_tax tax on tax.tax_group_id=group.id "
        "where group.id=%(tax_code_column)s",
        {
            'table': AsIs(table),
            'tax_column': AsIs(tax_column),
            'tax_code_column': AsIs(
                tax_code_column or openupgrade.get_legacy_name(tax_column)),
        }
    )


@openupgrade.migrate()
def migrate(cr, version):
    cr.execute(
        'update hr_payslip s set date=p.date_start '
        'from account_period p where p.id=s.period_id')
    set_tax_from_tax_code(cr, 'hr_salary_rule', 'account_tax_id')
