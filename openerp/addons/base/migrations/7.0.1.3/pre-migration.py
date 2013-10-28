# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This migration script copyright (C) 2012-2013 Therp BV (<http://therp.nl>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

# Maybe: investigate impact of 'model' field on ir.translation
# Ignored: removal of integer_big which openerp 6.1 claims is currently unused

from openupgrade import openupgrade

module_namespec = [
    # This is a list of tuples (old module name, new module name)
    ('account_coda', 'l10n_be_coda'),
    ('base_crypt', 'auth_crypt'),
    ('mrp_subproduct', 'mrp_byproduct'),
    ('users_ldap', 'auth_ldap'),
    ('wiki', 'document_page'),
    # mgmtsystem
    ('wiki_environment_manual', 'document_page_environment_manual'),
    ('wiki_environmental_aspect', 'document_page_environmental_aspect'),
    ('wiki_quality_manual', 'document_page_quality_manual'),
    ('wiki_health_safety_manual', 'document_page_health_safety_manual'),
    ('wiki_procedure', 'document_page_procedure'),
    ('wiki_work_instructions', 'document_page_work_instructions'),
]

column_renames = {
    # login_date: field type changed as well, but
    # orm can map timestamp fields to date field
    'res_users': [
        ('date', 'login_date'),
        ('user_email', None),
        ], 
    'res_company': [
        ('logo', None),
    ]
}

xmlid_renames = []
model_renames = [
    ('ir.actions.url', 'ir.actions.act_url'),
    ]

def disable_demo_data(cr):
    """ Disables the renewed loading of demo data """
    openupgrade.logged_query(
        cr,
        "UPDATE ir_module_module SET demo = false")

def migrate_ir_attachment(cr):
    # Data is now stored in db_datas column and datas is a function field
    # like in the document module in 6.1. If the db_datas column already
    # exist, presume that this module was installed and do nothing.
    if not openupgrade.column_exists(cr, 'ir_attachment', 'db_datas'):
        openupgrade.rename_columns(
            cr, {'ir_attachment': [('datas', 'db_datas')]})

def update_base_sql(cr):
    """
    Inject snippets of openerp/addons/base/base.sql, needed
    to upgrade the base module.
    """
    cr.execute("""
CREATE TABLE ir_model_constraint (
    id serial NOT NULL,
    create_uid integer,
    create_date timestamp without time zone,
    write_date timestamp without time zone,
    write_uid integer,
    date_init timestamp without time zone,
    date_update timestamp without time zone,
    module integer NOT NULL references ir_module_module on delete restrict,
    model integer NOT NULL references ir_model on delete restrict,
    type character varying(1) NOT NULL,
    name character varying(128) NOT NULL
);
CREATE TABLE ir_model_relation (
    id serial NOT NULL,
    create_uid integer,
    create_date timestamp without time zone,
    write_date timestamp without time zone,
    write_uid integer,
    date_init timestamp without time zone,
    date_update timestamp without time zone,
    module integer NOT NULL references ir_module_module on delete restrict,
    model integer NOT NULL references ir_model on delete restrict,
    name character varying(128) NOT NULL
);  
""")

def create_users_partner(cr):
    """
    Users now have an inherits on res.partner.
    Transferred fields include lang, tz and email
    but these fields do not exist on the partner table
    at this point. We'll pick this up in the post
    script.

    If other modules define defaults on the partner
    model, their migration scripts should put them
    into place for these entries.

    If other modules set additional columns to
    required, the following will break. We may
    want to have a look at disabling triggers
    at that point,

    We'll create both the partner column and a custom column
    to track the partners we create here. These are not necessarily
    the same, especially if you have a custom module implementing
    similar behaviour for 6.1.
    """
    if not openupgrade.column_exists(
        cr, 'res_users', 'partner_id'):
        cr.execute(
            "ALTER TABLE res_users "
            "ADD column partner_id "
            " INTEGER")
        cr.execute(
            "ALTER TABLE res_users ADD FOREIGN KEY "
            "(partner_id) "
            "REFERENCES res_partner ON DELETE RESTRICT")
    cr.execute(
        "ALTER TABLE res_users "
        "ADD column openupgrade_7_created_partner_id "
        " INTEGER")
    cr.execute(
        "ALTER TABLE res_users ADD FOREIGN KEY "
        "(openupgrade_7_created_partner_id) "
        "REFERENCES res_partner ON DELETE SET NULL")
    cr.execute(
        "SELECT res_id FROM ir_model_data "
        "WHERE module='base' and name='user_root'")
    user_root = cr.fetchone()
    user_root_id = user_root and user_root[0] or 0
    cr.execute(
        "SELECT id, name, active FROM res_users "
        "WHERE partner_id IS NULL")
    for row in cr.fetchall():
        cr.execute(
            "INSERT INTO res_partner "
            "(name, active) "
            "VALUES(%s,%s) RETURNING id", row[1:])
        partner_id = cr.fetchone()[0]
        cr.execute(
            "UPDATE res_users "
            "SET partner_id = %s, "
            "openupgrade_7_created_partner_id = %s "
            "WHERE id = %s", (partner_id, partner_id, row[0]))
        if row[0] == user_root_id:
            # Insert XML ID so that the partner for the admin user
            # does not get created again when loading the data
            cr.execute(
                "INSERT INTO ir_model_data "
                "(res_id, model, module, name, noupdate) "
                "VALUES(%s, 'res.partner', 'base', 'partner_root', TRUE) ",
                (partner_id,))

def remove_obsolete_modules(cr):
    obsolete_modules = (
        'base_tools',
        )
    cr.execute(
        """
        UPDATE ir_module_module
        SET state = 'to remove'
        WHERE name in %s
        """, (obsolete_modules,))

@openupgrade.migrate()
def migrate(cr, version):
    disable_demo_data(cr)
    update_base_sql(cr)
    openupgrade.update_module_names(
        cr, module_namespec
        )
    openupgrade.drop_columns(cr, [('ir_actions_todo', 'action_id')])
    openupgrade.rename_columns(cr, column_renames)
    openupgrade.rename_xmlids(cr, xmlid_renames)
    openupgrade.rename_models(cr, model_renames)
    migrate_ir_attachment(cr)
    create_users_partner(cr)
    remove_obsolete_modules(cr)
