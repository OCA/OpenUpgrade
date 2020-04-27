# Copyright 2019 Eficent <http://www.eficent.com>
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade
from psycopg2 import sql

_field_renames = [
    ('hr.expense.sheet', 'hr_expense_sheet', 'responsible_id', 'user_id'),
]

_xmlid_renames = [
    ('hr_expense.property_rule_expense_employee',
     'hr_expense.ir_rule_hr_expense_employee'),
    ('hr_expense.property_rule_expense_manager',
     'hr_expense.ir_rule_hr_expense_manager'),
]


def _recover_v8_expense_sheet_draft_state(env):
    """If this column exists, you are coming from v8 and this draft state
    can be recovered to its original state, having a safeguard that its
    current state is the mapped one and not other.
    """
    _table = 'hr_expense_sheet'
    _column = 'openupgrade_legacy_9_0_state'
    if not openupgrade.column_exists(env.cr, _table, _column):
        return
    openupgrade.logged_query(env.cr, sql.SQL("""
        UPDATE {table} SET {new} = 'draft'
        WHERE {old} = 'draft' AND {new} = 'submit'
    """).format(
        table=sql.Identifier(_table),
        old=sql.Identifier(_column),
        new=sql.Identifier('state'),
    ))


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
    _recover_v8_expense_sheet_draft_state(env)
    openupgrade.set_xml_ids_noupdate_value(
        env, 'hr_expense', ['hr_expense_template_refuse_reason'], True)
