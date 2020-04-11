# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_unlink_by_xmlid = [
    # ir.actions.act_url
    'website_slides.action_open_channels',
    # ir.rule
    'website_slides.rule_slide_channel_public',
    'website_slides.rule_slide_slide_public',
    # slide.channel
    'website_slides.channel_partial',
    'website_slides.channel_private',
    'website_slides.channel_public',
]


def convert_image_attachments(env):
    mapping = {
        'slide.slide': "image",
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
    convert_image_attachments(env)
    openupgrade.delete_records_safely_by_xml_id(env, _unlink_by_xmlid)
    openupgrade.load_data(env.cr, 'website_slides', 'migrations/13.0.2.0/noupdate_changes.xml')
    openupgrade.delete_record_translations(
        env.cr, 'website_slides', [
            'slide_template_published',
            'slide_template_shared',
        ],
    )
