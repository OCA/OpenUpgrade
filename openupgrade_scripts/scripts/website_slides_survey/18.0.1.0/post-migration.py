# Copyright 2025 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def fill_slide_channel_partner_survey_certification_success(env):
    if not openupgrade.column_exists(
        env.cr, "slide_channel_partner", "survey_certification_success"
    ):
        return
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE slide_channel_partner scp
        SET survey_certification_success = TRUE
        WHERE (
            survey_certification_success IS NULL
            OR survey_certification_success = FALSE
        )
        AND EXISTS (
            SELECT 1
            FROM slide_slide_partner s
            WHERE s.survey_scoring_success = TRUE
            AND s.partner_id = scp.partner_id
            AND s.channel_id = scp.channel_id
        );
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_slide_channel_partner_survey_certification_success(env)
