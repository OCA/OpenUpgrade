# -*- coding: utf-8 -*-

import pooler, logging
from openerp.openupgrade import openupgrade

logger = logging.getLogger('OpenUpgrade')
me = __file__
MODULE = "crm"

def migrate(cr, version):
    if not version:
        return
    try:
        #former versions added domains and contexts for crm.case.stage's type field - remove them
        openupgrade.load_data(cr, 'crm', 'migrations/6.1.1.0/data/crm_lead_view.xml')
    except Exception, e:
        logger.error("%s: error in post-migration.py: %s" % (MODULE, e))
        raise
