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
import os
import base_calendar
from openerp.openupgrade import openupgrade
from imp import load_source

logger = logging.getLogger('OpenUpgrade')
me = __file__
MODULE = "crm"

def migrate(cr, version):
    if not version:
        return
    try:
        #base_calendar's migration script defines a function to migrate tables that inherit calendar_event
        base_calendar_migration=load_source('base_calendar_migration', os.path.join(base_calendar.__path__[0], 'migrations', '6.1.1.0', 'pre-migration.py'))
        base_calendar_migration.migrate_calendar_event_table(cr, 'crm_meeting')

        if openupgrade.table_exists(cr, 'res_partner_canal') and not openupgrade.table_exists(cr, 'crm_case_channel'):
            openupgrade.rename_tables(cr, [('res_partner_canal', 'crm_case_channel')])
            openupgrade.rename_models(cr, [('res.partner.canal', 'crm.case.channel')])
    except Exception, e:
        logger.error("%s: error in pre-migration.py: %s" % (MODULE, e))
        raise
