# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def convert_image_attachments(env):
    mapping = {
        'hr.employee': "image",
    }
    for model, field in mapping.items():
        Model = env[model]
        attachments = env['ir.attachment'].search([
            ('res_model', '=', model),
            ('res_field', '=', field),
            ('res_id', '!=', False),
        ])
        for attachment in attachments:
            # for not having dangling attachments
            attachment.res_field = "image_1920"
            Model.browse(attachment.res_id).image_1920 = attachment.datas


@openupgrade.migrate()
def migrate(env, version):
    convert_image_attachments(env)
    openupgrade.load_data(env.cr, 'hr', 'migrations/13.0.1.1/noupdate_changes.xml')
