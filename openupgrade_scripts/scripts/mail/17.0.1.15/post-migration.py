# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_deleted_xml_records = [
    "mail.ir_rule_mail_channel_member_group_system",
    "mail.ir_rule_mail_channel_member_group_user",
    "mail.mail_channel_admin",
    "mail.mail_channel_rule",
]


def _discuss_channel_fill_allow_public_upload(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE discuss_channel
        SET allow_public_upload = True
        WHERE channel_type = 'livechat'
        """,
    )


def _fill_res_company_alias_domain_id(env):
    icp = env["ir.config_parameter"]

    domain = icp.get_param("mail.catchall.domain")
    if domain:
        openupgrade.logged_query(
            env.cr,
            f"""
            INSERT INTO mail_alias_domain (
                name, bounce_alias, catchall_alias, default_from)
            VALUES (
                '{domain}',
                '{icp.get_param("mail.bounce.alias") or "bounce"}',
                '{icp.get_param("mail.catchall.alias") or "catchall"}',
                '{icp.get_param("mail.default.from") or "notifications"}'
                )
            RETURNING id;
            """,
        )
        (alias_domain_id,) = env.cr.fetchone()
        openupgrade.logged_query(
            env.cr,
            f"""
            UPDATE res_company
                SET alias_domain_id = {alias_domain_id}
            WHERE alias_domain_id IS NULL;
            """,
        )
        openupgrade.logged_query(
            env.cr,
            f"""
            UPDATE mail_alias
                SET alias_domain_id = {alias_domain_id}
            WHERE alias_domain_id IS NULL;
            """,
        )


def _mail_alias_fill_alias_full_name(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE mail_alias
        SET
        alias_domain_id = mail_alias_domain.id,
        alias_full_name = CASE
            WHEN alias_name IS NOT NULL
            THEN alias_name || '@' || mail_alias_domain.name
            ELSE NULL
        END
        FROM mail_alias_domain
        """,
    )


def _mail_template_convert_report_template_m2o_to_m2m(env):
    openupgrade.m2o_to_x2m(
        env.cr,
        env["mail.template"],
        "mail_template",
        "report_template_ids",
        "report_template",
    )


def _fill_mail_message_outgoing(env):
    # set outgoing messages
    group = env.ref("base.group_user")
    openupgrade.logged_query(
        env.cr,
        f"""
        UPDATE mail_message mm
        SET message_type = 'email_outgoing'
        FROM mail_mail mail, res_partner rp
        JOIN res_users ru ON ru.partner_id = rp.id
        JOIN res_groups_users_rel rel ON rel.uid = ru.id
            AND rel.gid = {group.id}
        WHERE mm.message_type = 'email'
        AND mm.message_id like '%-openerp-' || mm.res_id || '-' || mm.model || '@%'
        AND (mm.author_id = rp.id OR mail.mail_message_id = mm.id)
        """,
    )


def _mail_activity_plan_template(env):
    """If the OCA mail_activity_plan module was installed, we create the
    mail.activity.plan.template records.
    """
    if not openupgrade.table_exists(env.cr, "mail_activity_plan_activity_type"):
        return
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO mail_activity_plan_template (
            plan_id,
            sequence,
            activity_type_id,
            summary,
            responsible_type,
            responsible_id,
            create_uid,
            create_date,
            write_uid,
            write_date
        ) SELECT rel.mail_activity_plan_id,
            10,
            detail.activity_type_id,
            detail.summary,
            CASE
              WHEN detail.user_id IS NOT NULL THEN 'other'
              ELSE 'on_demand'
            END AS responsible_type,
            detail.user_id,
            detail.create_uid,
            detail.create_date,
            detail.write_uid,
            detail.write_date
        FROM mail_activity_plan_mail_activity_plan_activity_type_rel AS rel
        LEFT JOIN mail_activity_plan_activity_type AS detail
            ON rel.mail_activity_plan_activity_type_id = detail.id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "mail", "17.0.1.15/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(
        env,
        _deleted_xml_records,
    )
    _discuss_channel_fill_allow_public_upload(env)
    _fill_res_company_alias_domain_id(env)
    _mail_alias_fill_alias_full_name(env)
    _mail_template_convert_report_template_m2o_to_m2m(env)
    _fill_mail_message_outgoing(env)
    _mail_activity_plan_template(env)
