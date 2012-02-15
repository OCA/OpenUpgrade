# -*- coding: utf-8 -*-

from osv import osv
import pooler, logging
from openerp.openupgrade import openupgrade

logger = logging.getLogger('OpenUpgrade')
me = os.path.realpath( __file__ )

defaults = {
    # False results in column value NULL
    # None value triggers a call to the model's default function 
    'res.currency': [
        ('position', 'after'),
        ],    
    'res.partner.address': [
        ('color', 0),
        ],    
    'res.partner': [
        ('color', 0),
        ],    
    }

def migrate(cr, version):
    try:
        logger.info("%s called", me)
        pool = pooler.get_pool(cr.dbname)
        openupgrade.set_defaults(cr, pool, defaults)
        openupgrade.load_xml(cr, 'base', 'migrations/6.1.1.3/data/base_data.xml')
        openupgrade.load_xml(cr, 'base', 'migrations/6.1.1.3/data/base_security.xml')
        openupgrade.load_xml(cr, 'base', 'migrations/6.1.1.3/data/ir.model.access.csv')
    except Exception, e:
        raise osv.except_osv("OpenUpgrade", '%s: %s' % (me, e))
