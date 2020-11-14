# Copyright 2020 Andrii Skrypka
# Copyright 2020 Opener B.V. (stefan@opener.amsterdam)
# Copyright 2019-2020 Tecnativa - Pedro M. Baeza
# Copyright 2020 ForgeFlow
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import pytz
from psycopg2 import sql
from datetime import datetime
from openupgradelib import openupgrade
from odoo import fields


def fix_res_partner_image(env):
    ResPartner = env['res.partner']
    attachments = env['ir.attachment'].search([
        ('res_model', '=', 'res.partner'),
        ('res_field', '=', 'image'),
        ('res_id', '!=', False),
    ])
    for attachment in attachments:
        ResPartner.browse(attachment.res_id).image_1920 = attachment.datas


def res_lang_week_start_map_values(env):
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("week_start"),
        "week_start",
        [(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5"), (6, "6"), (7, "7")],
        table="res_lang",
    )


def ir_actions_binding_type_views(env):
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
    openupgrade.logged_query(
        env.cr, """
        UPDATE ir_act_window
        SET binding_view_types = 'list' WHERE {column}""".format(
            column=openupgrade.get_legacy_name('multi')),
    )


def fill_ir_attachment_legacy_name(env):
    # Set new name column from old name column if missing
    openupgrade.logged_query(
        env.cr,
        sql.SQL(""" UPDATE ir_attachment
        SET name = {legacy_name}
        WHERE COALESCE(name, '') = ''
        AND COALESCE({legacy_name}, '') != '' """).format(
            legacy_name=sql.Identifier(
                openupgrade.get_legacy_name('name'))))


def fill_ir_cron_lastcall(env):
    """Fill with current date for avoiding notifs of past recurring events."""
    now = fields.Datetime.context_timestamp(env["ir.cron"], datetime.now())
    openupgrade.logged_query(
        env.cr,
        "UPDATE ir_cron SET lastcall = %s",
        (fields.Datetime.to_string(now.astimezone(pytz.UTC)),),
    )


def fill_arch_prev(env):
    """This field is a fallback to previous architecture in case of failure,
    so we should initially put the same as the current value.
    """
    openupgrade.logged_query(
        env.cr,
        "UPDATE ir_ui_view SET arch_prev = arch_db")


def delete_noupdate_records(env):
    openupgrade.delete_records_safely_by_xml_id(
        env, ["base.res_partner_rule", "base.module_website_form_editor",
              "base.SDD"]
    )


def company_missing_favicons(env):
    """If web_favicon was not installed, now Odoo gets no favicon by default,
    so we need to restore it.
    """
    Company = env["res.company"]
    Company.search([("favicon", "=", False)]).write({
        "favicon": Company._get_default_favicon(original=True)
    })


@openupgrade.migrate()
def migrate(env, version):
    res_lang_week_start_map_values(env)
    fix_res_partner_image(env)
    ir_actions_binding_type_views(env)
    fill_ir_cron_lastcall(env)
    fill_arch_prev(env)
    openupgrade.load_data(
        env.cr, 'base', 'migrations/13.0.1.3/noupdate_changes.xml')
    fill_ir_attachment_legacy_name(env)
    delete_noupdate_records(env)
    company_missing_favicons(env)
    # Activate back the noupdate flag on the group
    openupgrade.logged_query(
        env.cr, """
        UPDATE ir_model_data SET noupdate=True
        WHERE  module='base' AND name='group_user'""",
    )
