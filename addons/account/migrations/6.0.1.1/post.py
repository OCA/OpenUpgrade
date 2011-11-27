# -*- coding: utf-8 -*-

from osv import osv
import pooler, logging
log = logging.getLogger('migrate')
from openupgrade import openupgrade

defaults = {
    # False results in column value NULL
    # None value triggers a call to the model's default function 
    'account.fiscalyear': [
        ('company_id', None),
        ],    
    'account.journal': [
        ('company_id', None),
        ],    
    'account.analytic.account': [
        ('currency_id', None),
        ],    
    'account.analytic.journal': [
        ('company_id', None),
        ],    
    'account.invoice': [
        ('user_id', None),
        ],    
    }

def migrate(cr, version):
    try:
        log.info("post-set-defaults.py now called")
        # this method called in a try block too
        pool = pooler.get_pool(cr.dbname)
        openupgrade.set_defaults(cr, pool, defaults)
    except Exception, e:
        log.error("Migration: error in post.py: %s" % e)
        raise

