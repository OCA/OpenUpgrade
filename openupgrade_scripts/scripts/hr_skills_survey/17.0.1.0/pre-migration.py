# Copyright 2025 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.add_columns(
        env, [(False, "expiration_status", "char", "valid", "hr_resume_line")]
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_resume_line
        SET expiration_status = CASE
            WHEN date_end <= now() at time zone 'utc' THEN 'expired'
            WHEN date_end <= (now() - INTERVAL '3 MONTHS') at time zone 'utc'
                THEN 'expiring'
        END
        WHERE date_end IS NOT NULL
        """,
    )
