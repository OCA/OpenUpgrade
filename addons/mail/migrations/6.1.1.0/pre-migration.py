# -*- coding: utf-8 -*-

import os
from osv import osv
import logging
from openerp.openupgrade import openupgrade

logger = logging.getLogger('OpenUpgrade')
me = __file__

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

model_renames = [
    ('mailgate.message', 'mail.message'),
    ]

def migrate(cr, version):
    if not version:
        return
    try:
        logger.info("%s called", me)
        if openupgrade.table_exists(cr, 'mailgate_thread'):
            openupgrade.rename_tables(cr, table_renames)
            openupgrade.rename_columns(cr, column_renames)
            openupgrade.rename_models(cr, model_renames)
    except Exception, e:
        raise osv.except_osv("OpenUpgrade", '%s: %s' % (me, e))
