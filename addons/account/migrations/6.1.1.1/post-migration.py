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

from osv import osv
import pooler, logging
from openerp import SUPERUSER_ID
from openerp.openupgrade import openupgrade

logger = logging.getLogger('OpenUpgrade')
me = __file__

def write_account_report_type(cr):
    pool = pooler.get_pool(cr.dbname)
    type_obj = pool.get('account.account.type')
    cr.execute(
        "SELECT id, report_type_tmp FROM account_account_type "
        "WHERE report_type_tmp IS NOT NULL")
    for row in cr.fetchall():
        type_obj.write(
            cr, SUPERUSER_ID, row[0], {'report_type': row[1]})
    openupgrade.drop_columns(
        cr, [('account_account_type', 'report_type_tmp')])

def migrate(cr, version):
    try:
        logger.info("%s called", me)
        openupgrade.load_data(cr, 'account', 'migrations/6.1.1.1/data/data_account_type.xml')
        openupgrade.load_data(cr, 'account', 'migrations/6.1.1.1/data/account_financial_report_data.xml')
        openupgrade.load_data(cr, 'account', 'migrations/6.1.1.1/data/invoice_action_data.xml')
        openupgrade.load_data(cr, 'account', 'migrations/6.1.1.1/data/null_values.xml')
        write_account_report_type(cr)

    except Exception, e:
        raise osv.except_osv("BREAK", "OpenUpgrade", '%s: %s' % (me, e))
        raise osv.except_osv("OpenUpgrade", '%s: %s' % (me, e))
