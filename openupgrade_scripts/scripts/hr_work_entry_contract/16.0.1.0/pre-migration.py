from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    if not openupgrade.column_exists(env.cr, "hr_contract", "last_generation_date"):
        openupgrade.logged_query(
            env.cr,
            """
            ALTER TABLE hr_contract
            ADD COLUMN IF NOT EXISTS last_generation_date date;
            """,
        )
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE hr_contract
            SET last_generation_date = (
                SELECT MAX(date(create_date))
                FROM hr_work_entry
                WHERE contract_id = hr_contract.id
            )
            """,
        )
