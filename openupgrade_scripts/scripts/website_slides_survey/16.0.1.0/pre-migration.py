# Copyright 2025 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def _delete_sql_constraints(env):
    """Delete constraints to recreate it"""
    openupgrade.delete_sql_constraint_safely(
        env, "website_slides_survey", "slide_slide", "check_survey_id"
    )
    openupgrade.delete_sql_constraint_safely(
        env, "website_slides_survey", "slide_slide", "check_certification_preview"
    )


@openupgrade.migrate()
def migrate(env, version):
    _delete_sql_constraints(env)
