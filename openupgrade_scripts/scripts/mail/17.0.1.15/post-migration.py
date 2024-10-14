# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_deleted_xml_records = [
    "mail.ir_rule_mail_channel_member_group_system",
    "mail.ir_rule_mail_channel_member_group_user",
    "mail.mail_channel_admin",
    "mail.mail_channel_rule",
    "mail.channel_all_employees",
    "mail.channel_member_general_channel_for_admin",
]


def _fill_res_company_alias_domain_id(env):
    icp = env["ir.config_parameter"]

    domain = icp.get_param("mail.catchall.domain")
    if domain:
        alias_domain_id = openupgrade.logged_query(
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
    # Because we fill same alias domain for every company so only need one here
    company = env["res.company"].search([], limit=1)
    if company.alias_domain_id:
        openupgrade.logged_query(
            env.cr,
            f"""
            UPDATE mail_alias
            SET alias_domain_id = {company.alias_domain_id.id},
                alias_full_name = CASE
                    WHEN alias_name IS NOT NULL
                    THEN alias_name || '@' || '{company.alias_domain_id.name}'
                    ELSE NULL
                END
            """,
        )
    else:
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE mail_alias
            SET alias_full_name = CASE
                WHEN alias_name IS NOT NULL THEN alias_name
                ELSE NULL
            END
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


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "mail", "17.0.1.15/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(
        env,
        _deleted_xml_records,
    )
    _fill_res_company_alias_domain_id(env)
    _mail_alias_fill_alias_full_name(env)
    _mail_template_convert_report_template_m2o_to_m2m(env)
