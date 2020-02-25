# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def fix_res_lang_url_code(env):
    """ Url code is required. """
    for lang in env['res.lang'].with_context(active_test=False).search([('url_code', '=', False)]):
        lang.url_code = lang.iso_code or lang.code


def fix_res_partner_image(env):
    ResPartner = env['res.partner']
    attachments = env['ir.attachment'].search([
        ('res_model', '=', 'res.partner'),
        ('res_field', '=', 'image'),
        ('res_id', '!=', False),
    ])
    for attachment in attachments:
        ResPartner.browse(attachment.res_id).image_1920 = attachment.datas


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    fix_res_lang_url_code(env)
    openupgrade.load_data(env.cr, 'base', 'migrations/13.0.1.3/noupdate_changes.xml')
    fix_res_partner_image(env)
