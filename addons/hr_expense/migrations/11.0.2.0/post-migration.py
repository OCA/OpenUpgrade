# Copyright 2017 Le Filament (<https://le-filament.com>)
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def set_expense_is_refused(env):
    """Set is_refused flag on expense when the expense sheet was
    previously on cancel state. Done on pre
    """
    openupgrade.logged_query(
        env.cr, """
        UPDATE hr_expense he
        SET is_refused = True
        FROM hr_expense_sheet hes
        WHERE hes.id = he.sheet_id
            AND hes.state = 'cancel'""",
    )


def set_aml_expense_id(env):
    """This fills the expense_id field on account.move.line in a imperfect
    way, but the one that previous data allows: only last account.move created
    per expense sheet will have the reference to an expense, and the expense
    reference might not be the correct.

    This will work perfectly though when one expense = one expense sheet.
    """
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_move_line aml
        SET expense_id = he.id
        FROM account_move am,
            hr_expense_sheet hes,
            hr_expense he
        WHERE aml.move_id = am.id
            AND hes.account_move_id = am.id
            AND he.sheet_id = hes.id""",
    )


@openupgrade.migrate()
def migrate(env, version):
    set_expense_is_refused(env)
    set_aml_expense_id(env)
    openupgrade.load_data(
        env.cr, 'hr_expense', 'migrations/11.0.2.0/noupdate_changes.xml',
    )
