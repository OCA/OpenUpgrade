# Copyright 2020 Andrii Skrypka
# Copyright 2020 Opener B.V. (stefan@opener.amsterdam)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from psycopg2 import sql
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


def restore_res_lang_week_start(env):
    legacy_name = openupgrade.get_legacy_name('week_start')
    openupgrade.logged_query(
        env.cr,
        """
        SELECT id, %s
        FROM res_lang
        WHERE %s IS NOT NULL
        """ % (legacy_name, legacy_name),
    )
    grouped_by_week_start = {}
    for record in env.cr.fetchall():
        grouped_by_week_start.setdefault(record[1], []).append(record[0])
    for week_start, lang_ids in grouped_by_week_start.items():
        env['res.lang'].browse(lang_ids).write({'week_start': str(week_start)})


@openupgrade.migrate()
def migrate(env, version):
    fix_res_lang_url_code(env)
    restore_res_lang_week_start(env)
    openupgrade.load_data(env.cr, 'base', 'migrations/13.0.1.3/noupdate_changes.xml')
    fix_res_partner_image(env)

    # Populate missing binding_model_id values in ir_act_window
    openupgrade.logged_query(
        env.cr,
        """ UPDATE ir_act_window iaw
        SET binding_model_id = im.id
        FROM ir_model im
        WHERE binding_model_id IS NULL
            AND src_model IS NOT NULL
            AND iaw.src_model = im.model; """)
    # Convert obsolete 'action_form_only' binding type to binding_view_types
    openupgrade.logged_query(
        env.cr,
        """ UPDATE ir_actions
        SET binding_view_types = 'form', binding_type = 'action'
        WHERE binding_type = 'action_form_only' """)
    # Set new name column from old name column if missing
    openupgrade.logged_query(
        env.cr,
        sql.SQL(""" UPDATE ir_attachment
        SET name = {legacy_name}
        WHERE COALESCE(name, '') = ''
        AND COALESCE({legacy_name}, '') != '' """).format(
            legacy_name=sql.Identifier(
                openupgrade.get_legacy_name('name'))))
