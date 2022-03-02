# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade
import logging


_logger = logging.getLogger(__name__)


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
            try:
                Model.browse(attachment.res_id).image_1920 = attachment.datas
            except Exception as e:
                _logger.error(
                    "Error while recovering %s>%s for %s: %s",
                    model,
                    field,
                    attachment.res_id,
                    repr(e),
                )


@openupgrade.migrate()
def migrate(env, version):
    convert_image_attachments(env)
    openupgrade.load_data(env.cr, 'hr', 'migrations/13.0.1.1/noupdate_changes.xml')
