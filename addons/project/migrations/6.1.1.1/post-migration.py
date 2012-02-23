# -*- coding: utf-8 -*-

from osv import osv
import pooler, logging
from openerp.openupgrade import openupgrade

from openerp import SUPERUSER_ID

logger = logging.getLogger('OpenUpgrade')
me = __file__

defaults = {
    # False results in column value NULL
    # None value triggers a call to the model's default function 
    'project.task': [
        ('kanban_state', 'normal'),
        ],    
    }

def migrate(cr, version):
    try:
        logger.info("%s called", me)
        pool = pooler.get_pool(cr.dbname)
        openupgrade.set_defaults(cr, pool, defaults)
        openupgrade.load_data(cr, 'project', 'migrations/6.1.1.1/data/project_data.xml')
        openupgrade.load_data(cr, 'project', 'migrations/6.1.1.1/data/ir.model.access.csv')
    except Exception, e:
        raise osv.except_osv("OpenUpgrade", '%s: %s' % (me, e))
