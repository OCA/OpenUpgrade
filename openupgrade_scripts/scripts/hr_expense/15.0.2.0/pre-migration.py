from openupgradelib import openupgrade


def _compute_currency_id_has_not_value(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_expense e
        SET currency_id = c.currency_id
        FROM res_company c
        WHERE e.currency_id IS NULL AND c.id = e.company_id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _compute_currency_id_has_not_value(env)
    openupgrade.logged_query(
        env.cr,
        "ALTER TABLE hr_expense_sheet ADD COLUMN IF NOT EXISTS payment_state varchar",
    )
