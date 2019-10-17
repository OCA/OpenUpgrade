# Copyright 2019 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_field_renames = [
    ('hr.expense.sheet', 'hr_expense_sheet', 'responsible_id', 'user_id'),
]

_xmlid_renames = [
    ('hr_expense.property_rule_expense_employee',
     'hr_expense.ir_rule_hr_expense_employee'),
    ('hr_expense.property_rule_expense_manager',
     'hr_expense.ir_rule_hr_expense_manager'),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
    openupgrade.set_xml_ids_noupdate_value(
        env, 'hr_expense', ['hr_expense_template_refuse_reason'], True)
