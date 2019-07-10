# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def fill_website_slide_google_app_key(env):
    key = env['ir.config_parameter'].sudo().get_param(
        'website_slides.google_app_key',
    )
    if key:
        env['website'].search([]).write({
            'website_slide_google_app_key': key,
        })


@openupgrade.migrate()
def migrate(env, version):
    fill_website_slide_google_app_key(env)
    openupgrade.delete_records_safely_by_xml_id(
        env, [
            'website_slides.google_app_key',
        ],
    )
    openupgrade.load_data(
        env.cr, 'website_slides', 'migrations/12.0.1.0/noupdate_changes.xml')
    openupgrade.delete_record_translations(
        env.cr, 'website_slides', [
            'slide_template_published',
            'slide_template_shared',
        ],
    )
