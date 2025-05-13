# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "hr_holidays", "18.0.1.6/noupdate_changes.xml")
    # Restore values from the temp field to the actual float field
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_leave SET request_hour_to = request_hour_to_float
        WHERE request_hour_to_float IS NOT NULL;
        UPDATE hr_leave SET request_hour_from = request_hour_from_float
        WHERE request_hour_from_float IS NOT NULL;

        """,
    )

    # Clean up temp column
    openupgrade.logged_query(
        env.cr,
        """
            ALTER TABLE hr_leave DROP COLUMN request_hour_to_float;
            ALTER TABLE hr_leave DROP COLUMN request_hour_from_float;

            """,
    )
