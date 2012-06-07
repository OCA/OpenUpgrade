# -*- coding: utf-8 -*-

import pooler, logging
import os
import base_calendar
from openerp.openupgrade import openupgrade
from imp import load_source

logger = logging.getLogger('OpenUpgrade')
me = __file__
MODULE = "crm"

def migrate(cr, version):
    if not version:
        return
    try:
        #base_calendar's migration script defines a function to migrate tables that inherit calendar_event
        base_calendar_migration=load_source('base_calendar_migration', os.path.join(base_calendar.__path__[0], 'migrations', '6.1.1.0', 'pre-migration.py'))
        base_calendar_migration.migrate_calendar_event_table(cr, 'crm_meeting')

        if openupgrade.table_exists(cr, 'res_partner_canal') and not openupgrade.table_exists(cr, 'crm_case_channel'):
            openupgrade.rename_tables(cr, [('res_partner_canal', 'crm_case_channel')])
            openupgrade.rename_models(cr, [('res.partner.canal', 'crm.case.channel')])
    except Exception, e:
        logger.error("%s: error in pre-migration.py: %s" % (MODULE, e))
        raise
