# -*- coding: utf-8 -*-

import os
from osv import osv
import pooler, logging
from openerp.openupgrade import openupgrade

logger = logging.getLogger('OpenUpgrade')
me = os.path.realpath( __file__ )

obsolete_modules = [ 'smtpclient' ]

force_defaults = {
    # False results in column value NULL
    # None value triggers a call to the model's default function 
    'ir.sequence': [
        ('implementation', 'no_gap'),
        ]
    }

def mark_obsolete_modules(cr):
    """
    Remove modules that are known to be obsolete
    in this version of the OpenERP server.
    """
    openupgrade.logged_query(
        cr, """
        UPDATE
            ir_module_module
        SET 
            state='to remove'
        WHERE
            state='installed'
            AND name in %s
        """,
        (tuple(obsolete_modules),))

@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    openupgrade.set_defaults(cr, pool, force_defaults, force=True)
    openupgrade.load_data(cr, 'base', 'migrations/6.1.1.3/data/base_data.xml')
    openupgrade.load_data(cr, 'base', 'migrations/6.1.1.3/data/base_security.xml')
    openupgrade.load_data(cr, 'base', 'migrations/6.1.1.3/data/ir.model.access.csv')
    #force recreating module categories for all categories without xmlid
    #this fixes addons getting wrong category_ids assigned in case of
    #multiple categories with the same name
    cr.execute("""
        delete from ir_module_category where id not in 
        (select res_id from ir_model_data where model='ir.module.category')
    """)
    mark_obsolete_modules(cr)     
