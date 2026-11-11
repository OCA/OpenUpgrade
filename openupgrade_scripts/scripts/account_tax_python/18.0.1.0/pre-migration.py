# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    if not openupgrade.column_exists(env.cr, "account_tax", "formula"):
        # don't break if some OU user already created the column, then
        # we assume they took care of the transformation too
        openupgrade.copy_columns(
            env.cr,
            {
                "account_tax": [("python_compute", "formula", None)],
            },
        )
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE account_tax
            SET formula=regexp_replace(formula, '\\s*result\\s*=\\s*', '')
            WHERE formula IS NOT NULL
            """,
        )
