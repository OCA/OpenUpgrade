# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# Copyright 2021 ForgeFlow <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_column_renames = {
    'mail_mass_mailing_list_rel': [
        ('mail_mass_mailing_id', 'mailing_mailing_id'),
        ('mail_mass_mailing_list_id', 'mailing_list_id'),
    ],
    'mail_mass_mailing_contact_res_partner_category_rel': [
        ('mail_mass_mailing_contact_id', 'mailing_contact_id'),
    ],
}

_model_renames = [
    ('mail.mail.statistics', 'mailing.trace'),
    ('mail.mass_mailing', 'mailing.mailing'),
    ('mail.mass_mailing.contact', 'mailing.contact'),
    ('mail.mass_mailing.list', 'mailing.list'),
    ('mail.statistics.report', 'mailing.trace.report'),
    ('mail.mass_mailing.list_contact_rel', 'mailing.contact.subscription'),
    ('mail.mass_mailing.test', 'mailing.mailing.test'),
    ('mass.mailing.list.merge', 'mailing.list.merge'),
    ('mass.mailing.schedule.date', 'mailing.mailing.schedule.date'),
]

_table_renames = [
    ('mail_mail_statistics', 'mailing_trace'),
    ('mail_mass_mailing', 'mailing_mailing'),
    ('mail_mass_mailing_contact', 'mailing_contact'),
    ('mail_mass_mailing_list', 'mailing_list'),
    # many2many tables
    ('mail_mass_mailing_contact_res_partner_category_rel', 'mailing_contact_res_partner_category_rel'),
    ('mail_mass_mailing_contact_list_rel', 'mailing_contact_list_rel'),
    # transients
    ('mail_mass_mailing_test', 'mailing_mailing_test'),
    ('mass_mailing_list_merge', 'mailing_list_merge'),
    ('mass_mailing_schedule_date', 'mailing_mailing_schedule_date'),
]

_field_renames = [
    ('link.tracker.click', 'link_tracker_click', 'mail_stat_id', 'mailing_trace_id'),
    ('mailing.trace', 'mailing_trace', 'mass_mailing_campaign_id', 'campaign_id'),
    ('mail.mail', 'mail_mail', 'statistics_ids', 'mailing_trace_ids'),
    ('utm.campaign', 'utm_campaign', 'mass_mailing_ids', 'mailing_mail_ids'),
    ('mailing.mailing', 'mailing_mailing', 'statistics_ids', 'mailing_trace_ids'),
]

_xmlid_renames = [
    # ir.model.access
    ('mass_mailing.access_mass_mailing',
     'mass_mailing.access_mailing_mailing_mm_user'),
    ('mass_mailing.access_mass_mailing_system',
     'mass_mailing.access_mailing_mailing_system'),
    ('mass_mailing.access_mass_mailing_list',
     'mass_mailing.access_mailing_list_mm_user'),
    ('mass_mailing.access_mass_mailing_contact',
     'mass_mailing.access_mailing_contact_mm_user'),
    ('mass_mailing.access_mail_statistics_report',
     'mass_mailing.access_mailing_trace_report_mm_user'),
    ('mass_mailing.access_mail_mass_mailing_list_contact_rel',
     'mass_mailing.access_mailing_contact_subscription_mm_user'),
    ('mass_mailing.access_mail_mail_statistics_user',
     'mass_mailing.access_mailing_trace_user'),
    ('mass_mailing.access_mail_mail_statistics_mass_mailing_user',
     'mass_mailing.access_mailing_trace_mm_user'),
    ('mass_mailing.access_mass_mailing_stage',
     'mass_mailing.access_utm_stage'),
    ('mass_mailing.access_mass_mailing_tag',
     'mass_mailing.access_utm_tag_mass_mailing_campaign'),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_columns(env.cr, _column_renames)
    openupgrade.rename_models(env.cr, _model_renames)
    openupgrade.rename_tables(env.cr, _table_renames)
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
    openupgrade.set_xml_ids_noupdate_value(
        env,
        "mass_mailing",
        [
            "mass_mailing_mail_layout",
        ],
        True,
    )
