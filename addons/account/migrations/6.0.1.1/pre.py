# -*- coding: utf-8 -*-

from osv import osv
import pooler
import logging
from openupgrade import openupgrade

logger = logging.getLogger('migrate')

column_renames = {
    # this is a mapping per table from old column name
    # to new column name
    'account.invoice': [
        ('partner_bank', 'partner_bank_id'),
        ('number', 'internal_number'),
        ],
    }

def mgr_refund_journal_type(cr):
    # assign new refund journal types to journal.journal
    cr.execute('UPDATE account_journal SET type = "purchase_refund" ' +
               'where type = "purchase" and refund_journal = TRUE')
    cr.execute('UPDATE account_journal SET type = "sale_refund" ' +
               'where type = "sale" and refund_journal = TRUE')

def migrate(cr, version):
    try:
        pool = pooler.get_pool(cr.dbname)
        openupgrade.rename_columns(column_renames)
        mgr_refund_journal_type(cr)
    except Exception, e:
        log.error("Migration: error in pre.py: %s" % e)
        raise

