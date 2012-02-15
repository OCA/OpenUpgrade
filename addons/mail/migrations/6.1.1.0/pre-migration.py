# -*- coding: utf-8 -*-

import os
from osv import osv
import logging
from openerp.openupgrade import openupgrade

logger = logging.getLogger('OpenUpgrade')
me = os.path.realpath( __file__ )

column_renames = {
    # this is a mapping per table from old column name
    # to new column name, e.g.
    #
    'mail_message': [
        ('name', 'subject'),
        ('message', 'body_text'),
        ],
    }

table_renames = [
    ('mailgate_thread', 'mail_thread'),
    ('mailgate_message', 'mail_message'),
    ]

def migrate(cr, version):
    try:
        logger.info("%s called", me)
        openupgrade.rename_tables(table_renames)
        openupgrade.rename_columns(column_renames)
    except Exception, e:
        raise osv.except_osv("OpenUpgrade", '%s: %s' % (me, e))
