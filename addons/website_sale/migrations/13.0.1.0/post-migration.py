# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_unlink_by_xmlid = [
    # ir.rule
    'website_sale.payment_token_salesman_rule',
    'website_sale.payment_transaction_salesman_rule',
]


def convert_image_attachments(env):
    mapping = {
        'product.image': "image",
        'product.public.category': "image",
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
    openupgrade.load_data(env.cr, 'website_sale', 'migrations/13.0.1.0/noupdate_changes.xml')
    openupgrade.delete_record_translations(
        env.cr, 'website_sale', [
            'mail_template_sale_cart_recovery',
            'event_subscription',
        ],
    )
