# -*- coding: utf-8 -*-
# Copyright 2017 bloopark systems (<http://bloopark.de>)
# Copyright 2017-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade
from odoo.tools import safe_eval
from psycopg2.extensions import AsIs

MAIL_SUBTYPES_PROJECT_MAPPING = {
    'project.mt_project_issue_new': 'project.mt_project_task_new',
    'project.mt_project_issue_blocked': 'project.mt_project_task_blocked',
    'project.mt_project_issue_ready': 'project.mt_project_task_ready',
    'project.mt_project_issue_stage': 'project.mt_project_task_stage',
}

MAIL_SUBTYPES_ISSUE_MAPPING = {
    'project.mt_issue_new': 'project.mt_task_new',
    'project.mt_issue_blocked': 'project.mt_task_blocked',
    'project.mt_issue_ready': 'project.mt_task_ready',
    'project.mt_issue_stage': 'project.mt_task_stage',
}


def set_default_values(env):
    """ Update with default values for new required fields """
    openupgrade.set_defaults(
        env.cr, env, {
            'project.task.type': [
                ('legend_blocked', None),
                ('legend_done', None),
                ('legend_normal', None)
            ]
        },
    )


def convert_issues(env):
    """As project_issue was removed, we need to reallocate issues in current
    structure. There are 2 options here:

    1. Create a new project for hosting the issues as tasks with the same name
       as the original one + ' (issues)'. This is the default option. Maximum
       information will be preserved, like the label used for issues, or the
       subtype followers.
    2. Convert issues into tasks in the same project. If there is an issue
       linked to a task, then the same task will be preserved for both records.

    This is controlled via a system parameter inserted in the DB prior to the
    migration with the key 'openupgrade.11.new_project_for_issues'. If it
    can be eval as True, then option 1 will be used.

    In both cases, it will be transferred as much information as possible from
    the issues to the tasks.
    """
    issue_project_column = openupgrade.get_legacy_name('issue_project_id')
    openupgrade.logged_query(
        env.cr, "ALTER TABLE project_project ADD COLUMN %s INTEGER",
        (AsIs(issue_project_column), ),
    )
    create_new_project = bool(safe_eval(
        env['ir.config_parameter'].sudo().get_param(
            'openupgrade.11.new_project_for_issues', '1',
        ),
    ))
    if create_new_project:
        env.cr.execute("""
            SELECT DISTINCT(pi.project_id) AS id, pp.label_issues
            FROM project_issue pi, project_project pp
            WHERE pi.project_id = pp.id""")
        for row in env.cr.dictfetchall():
            # Made by ORM, for taking benefit of the duplicate process
            # where followers and rest of the fields are also duplicated
            project = env['project.project'].browse(row['id'])
            new_project = project.copy({
                'name': project.name + ' (Issues)',
                'task_ids': False,
                'label_tasks': row['label_issues'],
            })
            # Track from what project this was duplicated
            env.cr.execute(
                "UPDATE project_project SET %s = %s WHERE id = %s",
                (AsIs(issue_project_column), new_project.id, project.id),
            )
            # Map followers subtypes at project level
            subtype_dict = {}
            for key, value in MAIL_SUBTYPES_PROJECT_MAPPING.items():
                try:  # Load only existing subtypes
                    subtype_dict[env.ref(key)] = env.ref(value)
                except Exception:  # pragma: no cover
                    pass
            for follower in project.message_follower_ids:
                new_follower = new_project.message_follower_ids.filtered(
                    lambda x: x.partner_id == follower.partner_id
                )
                for subtype in subtype_dict:
                    if subtype in follower.subtype_ids:
                        new_follower.subtype_ids = [
                            (4, subtype_dict[subtype].id)
                        ]
    # Create tasks from issues
    origin_issue_column = openupgrade.get_legacy_name('origin_issue_id')
    openupgrade.logged_query(
        env.cr, "ALTER TABLE project_task ADD COLUMN %s INTEGER",
        (AsIs(origin_issue_column), ),
    )
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO project_task (
            create_date, create_uid, write_date, write_uid,
            %(issue_column)s, project_id,
            active, color, company_id, date_start, date_end,
            date_deadline, description, kanban_state, name,
            partner_id, stage_id, user_id, email_from, email_cc,
            date_last_stage_update,
            priority
        )
        SELECT
            pi.create_date, pi.create_uid, pi.write_date, pi.write_uid,
            pi.id, COALESCE(pp.%(project_column)s, pp.id),
            pi.active, pi.color, pi.company_id, pi.date_open, pi.date_closed,
            pi.date_deadline, pi.description, pi.kanban_state, pi.name,
            pi.partner_id, pi.stage_id, pi.user_id, pi.email_from, pi.email_cc,
            pi.date_last_stage_update,
            CASE
                WHEN pi.priority='2' THEN '1'
                ELSE pi.priority
            END
        FROM project_issue pi,
            project_project pp
        WHERE pi.project_id = pp.id
        """, {
            'project_column': AsIs(issue_project_column),
            'issue_column': AsIs(origin_issue_column),
        },
    )
    # Issues tags
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO project_tags_project_task_rel
        (project_task_id, project_tags_id)
        SELECT pt.id, rel.project_tags_id
        FROM project_issue_project_tags_rel rel,
            project_task pt
        WHERE pt.%(issue_column)s = rel.project_issue_id""", {
            'issue_column': AsIs(origin_issue_column),
        }
    )
    # Issues followers - Switch existing ones
    # First change subtypes
    for old, new in MAIL_SUBTYPES_ISSUE_MAPPING.items():
        try:
            openupgrade.logged_query(
                env.cr, """
                UPDATE mail_followers_mail_message_subtype_rel
                SET mail_message_subtype_id = %s
                WHERE mail_message_subtype_id = %s
                """, (env.ref(new).id, env.ref(old).id)
            )
        except Exception:  # pragma: no cover
            pass
    # Now change owner of the follower
    openupgrade.logged_query(
        env.cr, """
        UPDATE mail_followers
        SET res_id = pt.id,
            res_model = 'project.task'
        FROM project_task pt
        WHERE res_model = 'project.issue' AND
            res_id = pt.%(issue_column)s
        """, {
            'issue_column': AsIs(origin_issue_column),
        },
    )
    # Move attachments to new records
    openupgrade.logged_query(
        env.cr, """
        UPDATE ir_attachment
        SET res_id = pt.id,
            res_model = 'project.task'
        FROM project_task pt
        WHERE res_model = 'project.issue' AND
            res_id = pt.%(issue_column)s
        """, {
            'issue_column': AsIs(origin_issue_column),
        },
    )
    # Move messages to new records
    openupgrade.logged_query(
        env.cr, """
        UPDATE mail_message
        SET res_id = pt.id,
            model = 'project.task'
        FROM project_task pt
        WHERE model = 'project.issue' AND
            res_id = pt.%(issue_column)s
        """, {
            'issue_column': AsIs(origin_issue_column),
        },
    )


def remove_mail_subtypes(env):
    openupgrade.delete_records_safely_by_xml_id(
        env, (list(MAIL_SUBTYPES_PROJECT_MAPPING.keys()) +
              list(MAIL_SUBTYPES_ISSUE_MAPPING.keys())),
    )


@openupgrade.migrate()
def migrate(env, version):
    set_default_values(env)
    if openupgrade.table_exists(env.cr, 'project_issue'):
        convert_issues(env)
    openupgrade.load_data(
        env.cr, 'project', 'migrations/11.0.1.1/noupdate_changes.xml'
    )
    openupgrade.delete_record_translations(
        env.cr, 'project', ['mail_template_data_module_install_project'],
    )
    remove_mail_subtypes(env)
