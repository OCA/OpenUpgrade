# -*- coding: utf-8 -*-
# Copyright Stephane LE CORNEC
# Copyright 2017 Tecnativa - Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from openupgradelib import openupgrade


logger = logging.getLogger('OpenUpgrade')


# copied from pre-migration
column_copies = {
    'ir_actions': [
        ('help', None, None),
    ],
}


def align_partner_type_with_address_sync(cr):
    """The usage of use_parent_address is replaced by address type logic
    (see https://github.com/odoo/odoo/commit/43839a84), even if the field
    is only removed in Odoo 10.0.
    Addresses are now synced with the parent if the partner type is 'contact'.
    Therefore, set addresses of type 'other' to 'contact' if they had the
    `use_parent_address` flag in 8.0, and vice versa.
    """
    openupgrade.logged_query(
        cr,
        """
        UPDATE res_partner
        SET type = 'contact'
        WHERE type = 'other'
            AND use_parent_address
            AND parent_id IS NOT NULL;
        """)
    openupgrade.logged_query(
        cr,
        """
        UPDATE res_partner
        SET type = 'other'
        WHERE type = 'contact'
            AND use_parent_address IS NOT TRUE
            AND parent_id IS NOT NULL;
        """)


# company_type must match is_company
def match_company_type_to_is_company(cr):
    openupgrade.logged_query(cr, """
        UPDATE res_partner
        SET company_type = (CASE WHEN is_company THEN 'company' ELSE 'person' END)
        """)


# updates to ir_ui_view will not clear inherit_id
def clear_inherit_id(cr):
    "report.layout used to inherit from web.layout, we must explicitely clear this now"
    openupgrade.logged_query(cr, """
        UPDATE ir_ui_view v
        SET inherit_id = null
        FROM ir_model_data d
        WHERE d.res_id = v.id
        AND d.module = 'report' AND d.name = 'layout'
        """)


def rename_your_company(cr):
    openupgrade.logged_query(cr, """
        UPDATE res_company r
        SET name = 'My Company'
        FROM ir_model_data d
        WHERE d.res_id = r.id
        AND d.module = 'base' AND d.name = 'main_company'
        AND r.name = 'Your Company'
        """)


def set_filter_active(cr):
    openupgrade.logged_query(cr, """
        UPDATE ir_filters
        SET active = True
        """)


def assign_view_keys(env):
    """This is needed for website. Done through ORM as xml_id is a computed
    field, so no o(1) process can be done easily, and the number of these
    views is limited."""
    views = env['ir.ui.view'].search([
        ('type', '=', 'qweb'),
        ('key', '=', False),
    ])
    for view in views:
        view.key = view.xml_id


def populate_menu_action(env):
    """
    Populate the menu's action reference that was previously stored in
    ir_values. This fixes noupdate and manually created menu items for which
    the action is not (re)set when loading their data definition.
    """
    openupgrade.logged_query(
        env.cr,
        """UPDATE ir_ui_menu ium
        SET action = iv.value
        FROM ir_values iv
        WHERE iv.model = 'ir.ui.menu'
            AND iv.key = 'action'
            AND iv.key2 = 'tree_but_open'
            AND iv.res_id = ium.id
            AND ium.action IS NULL
        """)


def publish_attachments(env):
    """
    Attachments are only shown to anonymous users if the public flag is set
    """
    env.cr.execute(
        "update ir_attachment set public=True where res_model='ir.ui.view'"
    )


def cleanup_modules_post(env):
    # Remove noupdate cron in OCA/social/mass_mailing_sending_queue
    # It has been already moved to 'mass_mailing' module
    cron = env.ref('mass_mailing.cronjob', False)
    if cron:
        cron.unlink()


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    for table_name in column_copies.keys():
        for (old, new, field_type) in column_copies[table_name]:
            openupgrade.convert_field_to_html(
                env.cr, table_name, openupgrade.get_legacy_name(old), old
            )
    align_partner_type_with_address_sync(env.cr)
    match_company_type_to_is_company(env.cr)
    clear_inherit_id(env.cr)
    rename_your_company(env.cr)
    set_filter_active(env.cr)
    openupgrade.load_data(
        env.cr, 'base', 'migrations/9.0.1.3/noupdate_changes.xml',
    )
    assign_view_keys(env)
    populate_menu_action(env)
    publish_attachments(env)
    cleanup_modules_post(env)
