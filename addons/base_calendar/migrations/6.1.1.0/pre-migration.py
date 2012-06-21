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
