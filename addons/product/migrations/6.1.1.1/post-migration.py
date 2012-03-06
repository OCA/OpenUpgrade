# -*- coding: utf-8 -*-
import os
from osv import osv
import logging
from openerp.openupgrade import openupgrade

logger = logging.getLogger('OpenUpgrade')
me = os.path.realpath( __file__ )

def migrate(cr, version):
    try:
        logger.info("%s called", me)
        openupgrade.load_xml(cr, 'product', 'migrations/6.1.1.1/data/product_security.xml')
    except Exception, e:
        raise osv.except_osv("OpenUpgrade", '%s: %s' % (me, e))
