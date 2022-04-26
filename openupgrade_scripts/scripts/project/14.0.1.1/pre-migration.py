# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def _set_default_rating_status_period(env):
    openupgrade.logged_query(
        env.cr,
        "UPDATE project_project SET rating_status_period = 'monthly' WHERE "
        "rating_status_period IS NULL",
    )


def fast_fill_stored_calculated_fields(env):
    """Faster way"""
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE project_task
        ADD COLUMN partner_phone varchar,
        ADD COLUMN partner_email varchar""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE project_task pt
        SET partner_email = rp.email, partner_phone = rp.phone
        FROM res_partner rp
        WHERE pt.partner_id = rp.id""",
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(
        env.cr,
        {
            "project_project": [
                ("rating_status", None, None),
            ],
        },
    )
    openupgrade.rename_fields(
        env,
        [
            (
                "project.project",
                "project_project",
                "portal_show_rating",
                "rating_active",
            ),
        ],
    )
    openupgrade.rename_xmlids(
        env.cr,
        [
            ("project.access_partner_task user", "project.access_partner_task_user"),
        ],
    )
    _set_default_rating_status_period(env)
    # Manually create tables for avoiding the automatic launch of the compute or default
    # FK constraints and indexes will be added by ORM
    openupgrade.logged_query(
        env.cr,
        """CREATE TABLE project_allowed_internal_users_rel
        (project_project_id INTEGER, res_users_id INTEGER)""",
    )
    openupgrade.logged_query(
        env.cr,
        """CREATE TABLE project_allowed_portal_users_rel
        (project_project_id INTEGER, res_users_id INTEGER)""",
    )
    openupgrade.logged_query(
        env.cr,
        """CREATE TABLE project_task_res_users_rel
        (project_task_id INTEGER, res_users_id INTEGER)""",
    )
    fast_fill_stored_calculated_fields(env)
