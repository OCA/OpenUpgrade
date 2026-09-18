from openupgradelib import openupgrade


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    openupgrade.logged_query(
        cr,
        """
        ALTER TABLE account_analytic_plan
        ALTER COLUMN default_applicability TYPE jsonb
        USING CASE
            WHEN default_applicability IS NULL THEN NULL
            WHEN company_id IS NULL THEN jsonb_build_object(
                '1',
                default_applicability
            )
            ELSE jsonb_build_object(
                company_id::text,
                default_applicability
            )
        END
        """,
    )
