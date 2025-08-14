# Copyright 2025 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def _fill_pos_payment_employee(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE pos_payment pp
        SET employee_id = po.employee_id
        FROM pos_order po
        WHERE pp.pos_order_id = po.id
            AND pp.employee_id IS NULL AND po.employee_id IS NOT NULL
        """,
    )


def _fill_pos_session_employee(env):
    """
    Fill the employee_id in pos_session
    based on the employee related to the user who opened the session.
    Note: For open sessions this field is set every time an employee logs in to the POS.
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE pos_session ps
            SET employee_id = he.id
        FROM hr_employee he, pos_config pc
        WHERE ps.employee_id IS NULL
            AND ps.user_id = he.user_id
            AND pc.id = ps.config_id
            AND he.company_id = pc.company_id;
        """,
    )


def _fill_account_bank_statement_line_employee(env):
    """
    Fill the employee_id in account_bank_statement_line
    based on the employee related to the user who created the record.
    There is no reliable way to know which user actually performed the transaction,
    so this heuristic is used to populate the field.
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_bank_statement_line absl
            SET employee_id = he.id
        FROM hr_employee he, pos_session ps
        WHERE absl.employee_id IS NULL
            AND absl.create_uid = he.user_id
            AND he.company_id = absl.company_id
            AND ps.id = absl.pos_session_id
            AND absl.journal_id = ps.cash_journal_id;
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _fill_pos_payment_employee(env)
    _fill_pos_session_employee(env)
    _fill_account_bank_statement_line_employee(env)
