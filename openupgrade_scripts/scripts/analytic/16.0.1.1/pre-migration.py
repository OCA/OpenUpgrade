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


def analytic_account_set_group_id_if_null(env):
    """
    We would like to fill for group_id column before start renaming it into plan_id
    """
    if not openupgrade.column_exists(
        env.cr, "account_analytic_group", "default_applicability"
    ):
        openupgrade.add_fields(
            env,
            [
                (
                    "default_applicability",
                    "account.analytic.group",
                    "account_analytic_group",
                    "selection",
                    "character varying",
                    "analytic",
                    False,
                ),
            ],
        )
    openupgrade.logged_query(
        env.cr,
        """
        WITH inserted_group AS (
            INSERT INTO account_analytic_group (name, default_applicability)
            SELECT 'Dummy Analytic Plan', 'unavailable'
            RETURNING id
        )
        UPDATE account_analytic_account aaa
        SET group_id = (
            SELECT id
            FROM inserted_group
            LIMIT 1
        )
        WHERE aaa.group_id IS NULL;
        """,
    )
    # Manually update parent_path for dummy plan that we have created
    # or else we will get error when accessing it
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_analytic_group
        SET parent_path = id || '/'
        WHERE name = 'Dummy Analytic Plan' AND
        default_applicability = 'unavailable' AND
        parent_path IS NULL
        """,
    )


def create_root_plan_and_prefill_value_for_analytic_plan(env):
    """
    Pre fill value for column root_plan_id using the logic
    in its compute method to avoid computed by ORM
    """
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
        UPDATE account_analytic_account AS aaa
        SET root_plan_id = (
            SELECT split_part(parent.parent_path, '/', 1)::integer
                FROM account_analytic_plan AS parent
                WHERE parent.id = aaa.plan_id
                AND parent.parent_path IS NOT NULL
            LIMIT 1
        )
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    analytic_account_set_group_id_if_null(env)
    openupgrade.rename_fields(env, _fields_renames)
    openupgrade.rename_models(env.cr, _models_renames)
    openupgrade.rename_tables(env.cr, _tables_renames)
    create_root_plan_and_prefill_value_for_analytic_plan(env)
