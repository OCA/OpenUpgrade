# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_unlink_by_xmlid = [
    'gamification.mt_badge_granted',
]


def convert_image_attachments(env):
    mapping = {
        'gamification.badge': "image",
    }
    for model, field in mapping.items():
        Model = env[model]
        attachments = env['ir.attachment'].search([
            ('res_model', '=', model),
            ('res_field', '=', field),
            ('res_id', '!=', False),
        ])
        for attachment in attachments:
            Model.browse(attachment.res_id).image_1920 = attachment.datas


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.delete_records_safely_by_xml_id(env, _unlink_by_xmlid)
    openupgrade.load_data(env.cr, 'gamification', 'migrations/13.0.1.0/noupdate_changes.xml')
    openupgrade.delete_record_translations(
        env.cr, 'gamification', [
            'email_template_badge_received',
            'simple_report_template',
        ],
    )
    convert_image_attachments(env)
