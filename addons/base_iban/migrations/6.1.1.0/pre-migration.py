# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2012 Therp BV (<http://therp.nl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

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
