# -*- coding: utf-8 -*-

import os
from osv import osv
import pooler, logging
from openerp.openupgrade import openupgrade

logger = logging.getLogger('OpenUpgrade')
me = os.path.realpath( __file__ )

force_defaults = {
    # False results in column value NULL
    # None value triggers a call to the model's default function 
    'ir.sequence': [
        ('implementation', 'no_gap'),
        ]
    }

def migrate(cr, version):
    try:
        logger.info("%s called", me)
        pool = pooler.get_pool(cr.dbname)
        openupgrade.set_defaults(cr, pool, force_defaults, force=True)
        openupgrade.load_data(cr, 'base', 'migrations/6.1.1.3/data/base_data.xml')
        openupgrade.load_data(cr, 'base', 'migrations/6.1.1.3/data/base_security.xml')
        openupgrade.load_data(cr, 'base', 'migrations/6.1.1.3/data/ir.model.access.csv')
    except Exception, e:
        raise osv.except_osv("OpenUpgrade", '%s: %s' % (me, e))
