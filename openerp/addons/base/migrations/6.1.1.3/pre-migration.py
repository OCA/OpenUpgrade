# -*- coding: utf-8 -*-
# TODO
# Removal of modules that are deprecated
# e.g. report_analytic_line (incorporated in hr_timesheet_invoice) in V6

import logging
from osv import osv
from openerp.openupgrade import openupgrade

logger = logging.getLogger('OpenUpgrade')

update_timezone_statement = """update "%(table)s" set "%(column)s"="%(column)s"-
(interval '1 second')*
extract(timezone from cast("%(column)s" as timestamp with time zone))"""

renames = {
    # this is a mapping per table from old column name
    # to new column name, e.g.
    #
    # 'ir_property': [
    #    ('value', 'value_reference'),
    #    ],
    }

module_namespec = [
    # This is a list of tuples (old module name, new module name)
    ('outlook', 'plugin_outlook'),
    ('thunderbird', 'plugin_thunderbird'),
    ('mail_gateway', 'mail'),
    ]

def fix_module_ids(cr):
    cr.execute(
        # courtesy of Guewen Baconnier (Camptocamp)
        # https://bugs.launchpad.net/openobject-server/+bug/906362/comments/4
        "UPDATE ir_model_data SET name = 'module_' || module, "
        "module = 'base' WHERE name = 'module_meta_information' "
        "AND model = 'ir.module.module'"
        )

def ir_actions_todo_state(cr):
    # Mapping obsolete states
    cr.execute(
        "UPDATE ir_actions_todo SET state = 'open' "
        "WHERE state in ('cancel', 'skip')"
        )

def res_users_email(cr):
    """ 
    Column 'user_email', which used to be a function
    is now replacing the 'email' field.
    """
    openupgrade.drop_columns(cr, [('res_users', 'user_email')])
    openupgrade.rename_columns(cr, {'res_users': [('email', 'user_email')]})

def set_main_company(cr):
    """ 
    Make sure that an XML ID base.main_company exists,
    so that we can safely import countries and currencies
    """
    cr.execute(
        "SELECT res_id FROM ir_model_data WHERE name = %s and model = %s",
        ('main_company', 'res.company'))
    if not cr.fetchone():
        cr.execute("SELECT id FROM res_company WHERE parent_id is NULL")
        row = cr.fetchone()
        if not row:
            osv.except_osv("OpenUpgrade", "No company defined")
        openupgrade.logged_query(cr,
            "INSERT INTO ir_model_data (name, module, name, res_id) "
            "VALUES (%s, %s, %s, %s)", 
            ('main_company', 'base', 'res.company', row[0]))

def add_serialization_field(cr):
    """ Add a new field property """
    openupgrade.logged_query(
        cr,
        "ALTER TABLE ir_model_fields ADD COLUMN serialization_field_id "
        "INTEGER REFERENCES ir_model_fields ON DELETE CASCADE")

def disable_demo_data(cr):
    """ Disables the renewed loading of demo data """
    openupgrade.logged_query(
        cr,
        "UPDATE ir_module_module SET demo = false")

def migrate_timestamps(cr):
    cr.execute("""
        select attname,relname from pg_class join pg_attribute 
            on pg_class.oid=pg_attribute.attrelid 
        where pg_attribute.atttypid in 
            (select oid from pg_type where typname='timestamp')
            and relkind='r'
    """)
    for row in cr.fetchall():
        logger.info('fixing UTC offset for %(table)s.%(column)s' %
                {'table': row[1], 'column': row[0]})
        cr.execute(update_timezone_statement % 
                {'table': row[1], 'column': row[0]})

@openupgrade.migrate()
def migrate(cr, version):
    migrate_timestamps(cr)
    add_serialization_field(cr)
    set_main_company(cr)
    openupgrade.rename_columns(cr, renames)
    res_users_email(cr)
    openupgrade.update_module_names(
        cr, module_namespec
        )
    fix_module_ids(cr)
    disable_demo_data(cr)
