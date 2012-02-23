# -*- coding: utf-8 -*-

import os
from osv import osv
import logging
from openerp.openupgrade import openupgrade

logger = logging.getLogger('OpenUpgrade')
me = __file__

def move_account_numbers(cr):
    """ 
    The 'iban' field has been dropped. The IBAN number is now
    stored in the regular acc_number field.
    """
    if openupgrade.column_exists(cr, 'res_partner_bank', 'iban'):
        openupgrade.logged_query(
            cr, 
            "UPDATE res_partner_bank SET acc_number = iban WHERE state = 'iban'"
            )

def migrate(cr, version):
    try:
        logger.info("%s called", me)
        move_account_numbers(cr)
    except Exception, e:
        raise osv.except_osv("OpenUpgrade", '%s: %s' % (me, e))
