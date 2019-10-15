# Copyright 2019 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.set_xml_ids_noupdate_value(
        env, 'hr_payroll', [
            'decimal_payroll',
            'decimal_payroll_rate',
            'contrib_register_employees',
            'structure_base',
            'hr_rule_basic',
            'hr_rule_net',
            'hr_rule_taxable',
            'ALW',
            'BASIC',
            'COMP',
            'DED',
            'GROSS',
            'NET',
        ], False)
