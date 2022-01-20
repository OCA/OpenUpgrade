from openupgradelib import openupgrade


def delete_account_account(env):
    """Delete accounts not at v14"""
    openupgrade.logged_query(
        env.cr,
        """DELETE
        FROM account_account
        WHERE code IN ('154', '2288', '3331', '3338', '4111', '6112')""",
    )


@openupgrade.migrate()
def migrate(env, version):
    delete_account_account(env)
