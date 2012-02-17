# -*- coding: utf-8 -*-

import os
from osv import osv
import logging
from openerp.openupgrade import openupgrade

logger = logging.getLogger('OpenUpgrade')
me = __file__

def migrate(cr, version):
    try:
        logger.info("%s called", me)
        if not openupgrade.column_exists(
            cr, 'account_bank_statement_line_move_rel', 'statement_line_id'):
            openupgrade.rename_columns(cr, {
                    # many2many table square dance
                    'account_bank_statement_line_move_rel': [
                        ('move_id', 'move_id_tmp'),
                        ('statement_id', 'move_id'),
                        ('move_id_tmp', 'statement_line_id'),
                        ],
                    })
        else:
            logger.info("%s: statement line / move relation table "
                        "columns have already been swapped", me)
        if not openupgrade.column_exists(
            cr, 'account_account_type', 'report_type_tmp'):
            openupgrade.rename_columns(cr, {
                    'account_account_type': [
                        # Report_type is now an unstored function field with a fnct_write.
                        # Preserve the column here to process in the post script 
                        ('report_type', 'report_type_tmp'),
                        ],
                    })
        else:
            logger.info("%s: account type table, column report type"
                        "has already been preserved", me)

    except Exception, e:
        raise osv.except_osv("OpenUpgrade", '%s: %s' % (me, e))
