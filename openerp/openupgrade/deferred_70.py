# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Therp BV (<http://therp.nl>)
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

"""
This module contains a set of functions that should be called at the end of the
migration. A migration may be run several times after corrections in the code
or the configuration, and there is no way for OpenERP to detect a succesful
result. Therefore, the functions in this module should be robust against
being run multiple times on the same database.
"""

import logging
from openerp import SUPERUSER_ID

logger = logging.getLogger("OpenUpgrade")

def sync_commercial_fields(cr, pool):
    """
    Take care of propagating the commercial fields
    in the new partner model.
    """
    partner_obj = pool.get('res.partner')
    partner_ids = partner_obj.search(
        cr, SUPERUSER_ID,
        [], 0, False, False, {'active_test': False})
    logger.info("Syncing commercial fields between %s partners",
                len(partner_ids))
    for partner_id in partner_ids:
        vals = partner_obj.read(
            cr, SUPERUSER_ID, partner_id, [], load='_classic_write')
        partner_obj._fields_sync(
            cr, SUPERUSER_ID, 
            partner_obj.browse(cr, SUPERUSER_ID, partner_id),
            vals)                     

def migrate_deferred(cr, pool):
    sync_commercial_fields(cr, pool)
