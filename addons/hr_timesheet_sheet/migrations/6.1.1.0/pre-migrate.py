import logging
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
from openerp.openupgrade import openupgrade

logger = logging.getLogger('OpenUpgrade')

@openupgrade.migrate()
def migrate(cr, version):
    cr.execute("""select id, timesheet_range, name from res_company where 
               timesheet_range='year'""")
    for row in cr.fetchall():
        logger.warning('%s is configured for timesheet validation per year. '+
                       'This was deprecated so validation for %s is changed '+
                       'to monthly.', row[2], row[2])
    cr.execute("""update res_company set timesheet_range='month'
               where timesheet_range='year'""")
