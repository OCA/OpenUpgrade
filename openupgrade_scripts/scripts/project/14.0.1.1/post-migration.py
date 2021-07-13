# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def map_project_project_rating_status(env):
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("rating_status"),
        "rating_status",
        [("no", "stage")],
        table="project_project",
    )


def correct_fill_project_res_users_m2m_tables(env):
    # delete wrong defaults
    openupgrade.logged_query(
        env.cr,
        """
        DELETE FROM project_allowed_internal_users_rel;
        DELETE FROM project_allowed_portal_users_rel""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO project_allowed_internal_users_rel (
            project_project_id, res_users_id)
        SELECT pp.id, pp.create_uid
        FROM project_project pp
        JOIN res_users ru ON pp.create_uid = ru.id
        WHERE NOT ru.share""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO project_allowed_internal_users_rel (
            project_project_id, res_users_id)
        SELECT pp.id, ru.id
        FROM project_project pp
        JOIN res_users ru ON pp.partner_id = ru.partner_id
        WHERE pp.privacy_visibility = 'portal' AND NOT ru.share
        ON CONFLICT DO NOTHING""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO project_allowed_portal_users_rel (
            project_project_id, res_users_id)
        SELECT pp.id, ru.id
        FROM project_project pp
        JOIN res_users ru ON pp.partner_id = ru.partner_id
        WHERE pp.privacy_visibility = 'portal' AND ru.share""",
    )
    projects = env["project.project"].search([])
    for project in projects:
        project.allowed_user_ids |= project.message_follower_ids.partner_id.user_ids


def correct_fill_task_res_users_m2m_tables(env):
    openupgrade.logged_query(
        env.cr,
        """DELETE FROM project_task_res_users_rel""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO project_task_res_users_rel (
            project_task_id, res_users_id)
        SELECT pt.id, ru.id
        FROM project_task pt
        JOIN project_project pp ON pt.project_id = pp.id
        JOIN project_allowed_internal_users_rel rel
            ON rel.project_project_id = pp.id
        JOIN res_users ru ON rel.res_users_id = ru.id
        WHERE pp.privacy_visibility = 'followers' AND NOT ru.share""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO project_task_res_users_rel (
            project_task_id, res_users_id)
        SELECT pt.id, ru.id
        FROM project_task pt
        JOIN project_project pp ON pt.project_id = pp.id
        JOIN project_allowed_portal_users_rel rel
            ON rel.project_project_id = pp.id
        JOIN res_users ru ON rel.res_users_id = ru.id
        WHERE pp.privacy_visibility = 'portal' AND ru.share""",
    )
    tasks = env["project.task"].search([])
    for task in tasks:
        task.allowed_user_ids |= task.message_follower_ids.partner_id.user_ids


@openupgrade.migrate()
def migrate(env, version):
    map_project_project_rating_status(env)
    correct_fill_project_res_users_m2m_tables(env)
    correct_fill_task_res_users_m2m_tables(env)
    openupgrade.load_data(env.cr, "project", "14.0.1.1/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "project.msg_task_4",
            "project.project_project_data",
            "project.project_tag_data",
            "project.project_task_data_0",
            "project.project_task_data_1",
            "project.project_task_data_11",
            "project.project_task_data_12",
            "project.project_task_data_13",
            "project.project_task_data_14",
            "project.project_task_data_2",
            "project.project_task_data_4",
            "project.project_task_data_5",
            "project.project_task_data_6",
            "project.project_task_data_7",
            "project.project_task_data_9",
            "project.project_stage_data_0",
            "project.project_stage_data_1",
            "project.project_stage_data_2",
        ],
    )
    openupgrade.delete_record_translations(
        env.cr,
        "project",
        ["mail_template_data_project_task", "rating_project_request_email_template"],
    )
