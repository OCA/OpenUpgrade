# -*- coding: utf-8 -*-

from osv import osv
import pooler, logging
from openerp.openupgrade import openupgrade

from openerp import SUPERUSER_ID

logger = logging.getLogger('OpenUpgrade')
me = __file__

def migrate(cr, version):
    try:
        logger.info("%s called", me)
        openupgrade.load_data(cr, 'mail', 'migrations/6.1.1.0/data/ir.model.access.csv')
    except Exception, e:
        raise osv.except_osv("OpenUpgrade", '%s: %s' % (me, e))
