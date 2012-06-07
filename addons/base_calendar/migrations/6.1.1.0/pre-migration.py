# -*- coding: utf-8 -*-

import pooler, logging
from openerp.openupgrade import openupgrade

logger = logging.getLogger('OpenUpgrade')
me = __file__
MODULE = "base_calendar"

def migrate_calendar_event_table(cr, table_name):
    """migrates a table that inherited calendar_event
    @param cr: db cursor
    @param table_name: the table that inherited calendar_event
    """
    cr.execute("update %s set count=0, end_type='count' where end_type='forever'" % table_name)


def migrate(cr, version):
    if not version:
        return
    try:
        logger.info("%s called", me)
        migrate_calendar_event_table(cr, 'calendar_event')
    except Exception, e:
        logger.error("%s: error in pre-migration.py: %s" % (MODULE, e))
        raise
