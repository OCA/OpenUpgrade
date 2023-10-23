from openupgradelib import openupgrade

_fields_renames = [
    (
        "account.analytic.account",
        "account_analytic_account",
        "group_id",
        "plan_id",
    ),
    (
        "account.analytic.line",
        "account_analytic_line",
        "group_id",
        "plan_id",
    ),
]
_models_renames = [("account.analytic.group", "account.analytic.plan")]
_tables_renames = [("account_analytic_group", "account_analytic_plan")]


def analytic_account_set_plan_id_if_null(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_analytic_plan
        ADD COLUMN IF NOT EXISTS default_applicability VARCHAR
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO account_analytic_plan
        (name, default_applicability, complete_name)
        SELECT 'Legacy', 'optional', 'Legacy'
        RETURNING id
        """,
    )
    plan_id = env.cr.fetchone()[0]
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_analytic_account
        ADD COLUMN IF NOT EXISTS root_plan_id INTEGER;
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_analytic_account
        SET plan_id = %(plan_id)s, root_plan_id = %(plan_id)s
        WHERE plan_id IS NULL
        """,
        {"plan_id": plan_id},
    )
    # Manually update parent_path for legacy plan that we have created
    # or else we will get error when accessing it
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_analytic_plan
        SET parent_path = id || '/'
        WHERE id = %s
        """,
        (plan_id,),
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _fields_renames)
    openupgrade.rename_models(env.cr, _models_renames)
    openupgrade.rename_tables(env.cr, _tables_renames)
    analytic_account_set_plan_id_if_null(env)
