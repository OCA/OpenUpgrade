# -*- coding: utf-8 -*-

from osv import osv
import pooler, logging
from openerp.openupgrade import openupgrade
log = logging.getLogger('OpenUpgrade')

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
        
        log.info("post-set-defaults.py now called")
        # this method called in a try block too
        pool = pooler.get_pool(cr.dbname)
        openupgrade.set_defaults(cr, pool, defaults)
        openupgrade.load_xml(cr, 'base', 'migrations/6.1.1.3/data/base_data.xml')
        openupgrade.load_xml(cr, 'base', 'migrations/6.1.1.3/data/base_security.xml')
    except Exception, e:
        log.info("Migration: error in post-set-defaults.py: %s" % e)
        raise
